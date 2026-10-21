"""
FanFlow AI Assistant.

Rewritten to be typo-tolerant: uses Python's built-in difflib (no extra
packages needed) to fuzzy-match both the person's INTENT (what they're
asking about) and any MATERIAL/PRODUCT/SUPPLIER names they mention, even
if they're misspelled -- e.g. "wich matrial is critcal" or "moter" for
"motor" both still work.

Flow (Section 34 of the original spec):
    User Question -> Django View -> Business Logic -> Database Query
    -> Structured Context -> Response -> Django Template

Rules (Section 35):
  - Never invent database values. All numbers come from the same services
    the rest of the app uses (inventory/suppliers/procurement/risk).
  - If no OPENAI_API_KEY is configured, answer directly from that same
    structured context via templated text -- fully functional with zero
    external API key.
"""
import difflib
import os
import re
from decimal import Decimal

from inventory.models import Inventory
from inventory.services import calculate_available_stock
from materials.models import Material
from procurement.services import generate_procurement_recommendation
from products.models import Product
from risk_management.models import RiskAlert
from suppliers.services import recommended_supplier_for_material


# ---------------------------------------------------------------------
# Fuzzy helpers
# ---------------------------------------------------------------------

def _normalize(text):
    return re.sub(r'[^a-z0-9\s]', '', text.lower()).strip()


def _fuzzy_contains(text, keywords, cutoff=0.65):
    """
    Returns True if the meaning of `text` likely matches one of the
    `keywords` phrases, tolerating typos -- checks each word of the
    keyword phrase individually against every word in the question, so
    word order and misspellings don't break intent detection.
    """
    norm_text = _normalize(text)
    if any(kw in norm_text for kw in keywords):
        return True

    text_words = [w for w in norm_text.split() if len(w) >= 3]
    if not text_words:
        return False

    for kw in keywords:
        kw_words = kw.split()
        if all(
            any(
                abs(len(kw_word) - len(tw)) <= 2
                and difflib.SequenceMatcher(None, kw_word, tw).ratio() >= cutoff
                for tw in text_words
            )
            for kw_word in kw_words
        ):
            return True
    return False


STOPWORDS = {
    'hello', 'hi', 'hey', 'thanks', 'thank', 'please', 'help', 'yes', 'no',
    'ok', 'okay', 'good', 'morning', 'evening', 'there', 'you', 'the', 'and',
}


def _fuzzy_match_name(text, names, cutoff=0.8):
    """
    Finds the object name (material/product/supplier) most likely being
    referred to in `text`, tolerating typos -- compares each word of the
    question against each word of every known name (e.g. "moter" still
    matches "Motor Assembly" via the word "Motor"). Very short words
    (<=3 chars) require an exact match, and common greeting/filler words
    are excluded, to avoid false positives like "hello" matching "Shell".
    """
    norm_text = _normalize(text)
    for name in names:
        if _normalize(name) in norm_text:
            return name

    text_words = [w for w in norm_text.split() if w not in STOPWORDS]
    if not text_words:
        return None

    best_name, best_score = None, 0.0
    for name in names:
        for name_word in _normalize(name).split():
            if len(name_word) <= 3:
                score = 1.0 if name_word in text_words else 0.0
            else:
                score = max(
                    (
                        difflib.SequenceMatcher(None, name_word, tw).ratio()
                        for tw in text_words
                        if abs(len(name_word) - len(tw)) <= 2
                    ),
                    default=0.0,
                )
                if score < cutoff:
                    score = 0.0
            if score > best_score:
                best_score, best_name = score, name
    return best_name


# ---------------------------------------------------------------------
# Context builders -- the ONLY source of numbers the assistant uses.
# ---------------------------------------------------------------------

def _most_critical_material():
    worst, worst_shortage = None, Decimal('0')
    for inv in Inventory.objects.select_related('material').all():
        available = calculate_available_stock(inv)
        shortage = inv.reorder_level - available
        if shortage > worst_shortage:
            worst_shortage, worst = shortage, inv
    if not worst:
        return None
    return {
        'material': worst.material,
        'required': worst.reorder_level,
        'available': calculate_available_stock(worst),
        'shortage': worst_shortage,
    }


def _best_supplier_for(material_name):
    material = Material.objects.filter(name__iexact=material_name).first()
    if not material:
        return None
    best = recommended_supplier_for_material(material)
    if not best:
        return None
    return {
        'material': material,
        'supplier': best['supplier'],
        'overall_score': best['overall_score'],
        'lead_time_days': best['supplier_material'].lead_time_days,
    }


def _open_risk_summary():
    return list(RiskAlert.objects.filter(is_resolved=False).order_by('-severity', '-created_at')[:5])


def _shortage_summary():
    shortages = []
    for inv in Inventory.objects.select_related('material').all():
        available = calculate_available_stock(inv)
        if available < inv.reorder_level:
            shortages.append({
                'material': inv.material, 'available': available,
                'reorder_level': inv.reorder_level, 'shortage': inv.reorder_level - available,
            })
    return shortages


def _material_stock_status(material_name):
    material = Material.objects.filter(name__iexact=material_name).first()
    if not material:
        return None
    inv, _ = Inventory.objects.get_or_create(material=material)
    return {
        'material': material, 'available': calculate_available_stock(inv),
        'reorder_level': inv.reorder_level, 'current_stock': inv.current_stock,
    }


# ---------------------------------------------------------------------
# Intent keyword sets (fuzzy-matched, so typos still hit the right intent)
# ---------------------------------------------------------------------

INTENT_KEYWORDS = {
    'critical_material': ['most critical', 'biggest shortage', 'worst shortage', 'critical material'],
    'supplier_recommend': ['which supplier', 'best supplier', 'recommend supplier', 'supplier for', 'who should we buy'],
    'shortage_list': ['shortage', 'short on', 'need to buy', 'need to order', 'low stock', 'running low', 'what is short'],
    'procurement_advice': ['recommend', 'procure', 'purchase', 'should we order', 'reorder'],
    'risk_summary': ['risk', 'alert', 'danger', 'warning'],
    'stock_check': ['how much stock', 'stock of', 'available stock', 'how many do we have', 'current stock'],
}


def generate_supply_chain_response(question, context=None):
    """
    Main entry point. Fuzzy-matches intent AND entity names so typos in
    either don't break the assistant. Returns (response_text, context_used).
    """
    if not question or not question.strip():
        return ("Please type a question -- for example, \"Which material is most critical?\"", "")

    norm_q = _normalize(question)
    if norm_q in ('hi', 'hello', 'hey', 'hi there', 'hello there'):
        return ("Hello! Ask me about material shortages, supplier recommendations, "
                 "stock levels, or open risk alerts -- I'll answer from your live data.", "")
    if norm_q in ('thanks', 'thank you', 'thankyou', 'ok', 'okay'):
        return ("You're welcome! Let me know if you need anything else.", "")

    material_names = list(Material.objects.values_list('name', flat=True))
    matched_material = _fuzzy_match_name(question, material_names)

    # --- Most critical material ---
    if _fuzzy_contains(question, INTENT_KEYWORDS['critical_material']):
        result = _most_critical_material()
        if not result:
            return ("All materials currently have sufficient stock relative to their reorder levels.", "")
        text = (
            f"{result['material'].name} is currently the most critical material.\n\n"
            f"Required (reorder level): {result['required']}\n"
            f"Available: {result['available']}\n"
            f"Shortage: {result['shortage']}"
        )
        return text, str(result)

    # --- Which supplier for <material>? ---
    if _fuzzy_contains(question, INTENT_KEYWORDS['supplier_recommend']) or (
        matched_material and _fuzzy_contains(question, ['supplier', 'suplier', 'vendor'])
    ):
        if not matched_material:
            return (
                "Which material are you asking about? For example: "
                "\"Which supplier should we choose for motors?\"", ""
            )
        result = _best_supplier_for(matched_material)
        if not result:
            return (f"No supplier is currently registered for '{matched_material}'.", "")
        text = (
            f"{result['supplier'].name} is recommended for {result['material'].name} "
            f"because it has the highest overall supplier score "
            f"({result['overall_score']}/100) and a lead time of "
            f"{result['lead_time_days']} days among suppliers capable of meeting the requirement."
        )
        return text, str(result)

    # --- Stock check for a specific material ---
    if matched_material and _fuzzy_contains(question, INTENT_KEYWORDS['stock_check']):
        result = _material_stock_status(matched_material)
        text = (
            f"{result['material'].name}: current stock {result['current_stock']}, "
            f"available {result['available']}, reorder level {result['reorder_level']}."
        )
        return text, str(result)

    # --- Shortage list ---
    if _fuzzy_contains(question, INTENT_KEYWORDS['shortage_list']) and not matched_material:
        shortages = _shortage_summary()
        if not shortages:
            return ("No materials are currently below their reorder level.", "")
        lines = [
            f"- {s['material'].name}: available {s['available']}, reorder level {s['reorder_level']}, shortage {s['shortage']}"
            for s in shortages
        ]
        return "The following materials are below their reorder level:\n\n" + "\n".join(lines), str(shortages)

    # --- Procurement recommendation for a specific material ---
    if matched_material and _fuzzy_contains(question, INTENT_KEYWORDS['procurement_advice']):
        material = Material.objects.filter(name__iexact=matched_material).first()
        rec = generate_procurement_recommendation(material) if material else None
        if not rec:
            return (f"{matched_material} doesn't currently need procurement -- available stock is above safety stock.", "")
        supplier_text = rec['recommended_supplier'].name if rec['recommended_supplier'] else 'No supplier available'
        text = (
            f"Procurement recommendation for {rec['material'].name}:\n\n"
            f"Recommended supplier: {supplier_text}\n"
            f"Recommended quantity: {rec['recommended_quantity']}\n"
            f"Estimated cost: {rec['estimated_cost']}\n"
            f"Risk level: {rec['risk_level']}\n"
            f"Reason: {rec['reason']}"
        )
        return text, str(rec)

    # --- Open risk alerts ---
    if _fuzzy_contains(question, INTENT_KEYWORDS['risk_summary']):
        alerts = _open_risk_summary()
        if not alerts:
            return ("There are no open risk alerts right now.", "")
        lines = [f"- [{a.severity}] {a.title}" for a in alerts]
        return "Open risk alerts:\n\n" + "\n".join(lines), str(alerts)

    # --- If we matched a material but no clear intent, give a general summary ---
    if matched_material:
        result = _material_stock_status(matched_material)
        text = (
            f"Here's what I have on {result['material'].name}: current stock "
            f"{result['current_stock']}, available {result['available']}, "
            f"reorder level {result['reorder_level']}. Ask me about shortages, "
            f"the best supplier, or a procurement recommendation for it."
        )
        return text, str(result)

    # --- Fallback ---
    return (
        "I can answer questions about: the most critical material, "
        "which supplier to choose for a material, current shortages, stock "
        "levels for a specific material, procurement recommendations, and "
        "open risk alerts. Try, for example, \"Which material is most critical?\" "
        "or \"Which supplier should we choose for motors?\" (typos are okay!)",
        "",
    )


def is_llm_configured():
    return bool(os.getenv('OPENAI_API_KEY'))
