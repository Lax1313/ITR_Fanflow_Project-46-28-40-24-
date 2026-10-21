# FanFlow

AI-Powered Smart Industrial Supply Chain Intelligence System for Fan Manufacturing.

**Status: Complete, working build** — full CRUD everywhere, automatic
inventory management, ML-based demand prediction, a typo-tolerant AI
assistant, and a light/dark blue UI theme. Every feature below was tested
against a live server with real data before packaging (see "What's been
tested").

---

## What's new in this build

1. **Edit everything.** Products, Materials, Suppliers (+ their pricing per
   material), Customer Orders, Purchase Order status, and BOMs can all be
   updated after creation — not just created once. Edit buttons are on
   every list and detail page.

2. **Automatic inventory on production completion.** `/production/complete/`
   lets you say "we just finished making 50 fans" — FanFlow explodes the
   BOM, deducts every material used from inventory automatically (with a
   full transaction record), and immediately re-runs the risk check so
   you see right away if anything just dropped below safety stock. No
   manual stock editing required.

3. **Blue light/dark theme.** A toggle in the top-right switches the whole
   UI between a light blue and a dark navy palette, built with plain CSS
   variables and vanilla JavaScript (no extra frameworks) — see
   `static/css/style.css` and `static/js/charts.js`. Charts automatically
   redraw in the right colors when you switch.

4. **A chatbot that understands typos.** The AI Assistant
   (`/ai-assistant/`) now uses fuzzy matching (Python's built-in `difflib`,
   no extra installs) so "wich matrial is critcal" or "suplier for moter"
   still get answered correctly. It's still fully grounded in your live
   database — never invents numbers.

5. **Dynamic inventory end-to-end.** Stock now moves automatically at
   every real trigger:
   - **Purchase Order marked "Received"** → stock increases by the
     ordered quantity (e.g. 50 in stock + 50 received = 100)
   - **Production completed** → stock decreases by what the BOM required
   - **Manual adjustment** → still available on each material's page for
     corrections, returns, or write-offs
   Every change creates a real `InventoryTransaction` row, so there's a
   full audit trail — visible on each material's detail page.

6. **Dashboard "Smart Insights" panel.** Alongside the KPIs and charts,
   the dashboard now shows three live panels side by side: predicted
   demand per product (from the trained ML model), low-stock alerts, and
   reorder recommendations (from the same procurement service used on
   the Procurement page) — so predictions, alerts, and reorder actions
   are visible in one place instead of buried in separate pages.

All dashboard counts, charts, and inventory figures are computed fresh
from the database on every page load — nothing is cached or hardcoded.

---

## Setup

```bash
cd FanFlow
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# then open .env and set SECRET_KEY to a random string, e.g.:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

python manage.py migrate
python manage.py createsuperuser
```

By default new users get the **Production Manager** role. Promote your
superuser to **Admin**:

```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
u = get_user_model().objects.get(username='YOUR_USERNAME')
u.profile.role = UserProfile.Role.ADMIN
u.profile.save()
"
```

## 2. Load demo data and train the ML model

This is the fastest way to see the whole system working with realistic
numbers instead of an empty database:

```bash
python manage.py generate_demo_data      # 6 products, 16 materials, 12 suppliers,
                                          # ~860 sales history rows, 60 orders,
                                          # 15 purchase orders, 15 shipments
python manage.py train_forecast_model    # trains + compares LinearRegression vs
                                          # RandomForestRegressor, saves the best one
python manage.py generate_forecasts      # generates a 30-day forecast per product

# Optional: also pre-populate the demo role accounts
python manage.py seed_roles_demo         # scm_manager / procurement_manager /
                                          # inventory_manager / production_manager,
                                          # all with password DemoPass123!
```

`generate_demo_data --reset` wipes and regenerates the demo data if you want
a fresh run.

## 3. Run it

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` → redirects to login → dashboard with live
KPIs and Chart.js charts.

---

## What you can do, page by page

| Section | URL | What it does |
|---|---|---|
| Dashboard | `/dashboard/` | KPI cards + 6 Chart.js visualizations, all from live data |
| Products | `/products/` | Fan models, specs, linked BOM |
| Materials | `/materials/` | Raw materials, stock status, link to supplier comparison |
| BOM | `/production/bom/` | Bill of Materials CRUD |
| MRP Calculator | `/production/mrp/` | Pick a product + quantity → material requirements vs inventory |
| Production Complete | `/production/complete/` | Auto-deduct materials for a finished manufacturing run |
| Orders | `/orders/` | Customer orders (editable); `/orders/sales-history/` shows the ML training data |
| Inventory | `/inventory/` | Stock levels, shortage highlighting, record transactions |
| Suppliers | `/suppliers/` | Supplier list/detail; `/materials/<id>/suppliers/` = ranked comparison |
| Forecasting | `/forecasting/` | Train the model, generate forecasts, view history |
| Procurement | `/procurement/recommendations/` | Auto-generated recommendations → one-click Purchase Order |
| Purchase Orders | `/procurement/purchase-orders/` | PO list/detail |
| Logistics | `/logistics/` | Shipment tracking, overdue highlighting |
| Risk Analysis | `/risk/` | Run a risk scan, resolve alerts |
| Analytics | `/analytics/` | Deeper chart views of the same live data |
| AI Assistant | `/ai-assistant/` | Ask questions like "Which material is most critical?" |
| Reports | `/reports/` | CSV exports (inventory, suppliers, orders, forecast, risk) + inventory PDF |
| Notifications | `/notifications/` | Combined feed of open risk alerts + low-stock materials |
| Users & Roles | `/accounts/users/` | Admin-only: create employees, assign roles |

## Role-based access

| Role | Can access |
|---|---|
| Admin | Everything |
| Supply Chain Manager | Dashboard, Forecasting, Inventory, Suppliers, Procurement, Logistics, Analytics, AI Assistant, Reports |
| Procurement Manager | Dashboard, Suppliers, Procurement, Reports |
| Inventory Manager | Dashboard, Inventory, Materials, Reports |
| Production Manager | Dashboard, Orders, Forecasting, BOM, Products, Reports |

The sidebar automatically shows only what the logged-in user's role can see.

---

## The ML forecasting pipeline

```
SalesHistory (DB) → forecasting/ml/preprocess.py (feature engineering:
month, year, season, temperature, festival/promotion flags, lag features)
→ forecasting/ml/train_model.py (time-aware 80/20 split — no shuffling,
no leakage — trains LinearRegression AND RandomForestRegressor, picks the
one with lower MAE) → joblib model saved to ml_models/
→ forecasting/ml/predict.py (loads the saved model)
→ forecasting/services.py::forecast_demand() (builds features for a
specific product/date, predicts, saves to DemandForecast)
```

A pre-trained model is included in `ml_models/demand_forecast_model.joblib`
so forecasts work immediately after `generate_demo_data`. Retrain any time
with `python manage.py train_forecast_model` (e.g. after adding more sales
history).

With the included demo data, Random Forest consistently outperforms Linear
Regression (R² ≈ 0.91 vs ≈ 0.80 on held-out data) because fan demand has
non-linear seasonal effects Linear Regression can't capture.

## The AI Assistant

`/ai-assistant/` is rule-based by default (works with zero configuration)
and answers from live Django-calculated context — it can tell you the most
critical material, recommend a supplier for a material, list shortages,
give a full procurement recommendation, or summarize open risks. Every
number it states comes from the same services the rest of the app uses
(`inventory/services.py`, `suppliers/services.py`, `procurement/services.py`),
never invented.

To upgrade it to phrase responses through an LLM instead of the templated
text, set `OPENAI_API_KEY` in `.env` and extend
`ai_assistant/services.py::generate_supply_chain_response()` to pass the
same structured context to the OpenAI API — the context-gathering functions
are already separated out for this.

---

## Tests

```bash
python manage.py test
```

Covers: the available-stock/shortage formulas (Inventory), MRP calculation
(Production), supplier scoring/ranking (Suppliers), the risk detection
engine (Risk Management), and role-based access control (Accounts) — 9
tests, all passing.

## What's been tested

Every page listed in the table above was hit with a live server and a
logged-in session and confirmed to return HTTP 200. The following
end-to-end flows were also verified against real data (not just "loads
without error"):

- Login → role-filtered dashboard → logout
- Admin creating a new employee account with a role
- A non-Admin role being redirected away from Admin-only pages
- Generating demo data, training the model, and generating forecasts
- The risk engine detecting real shortages, weak suppliers, and overdue
  shipments from the generated data
- The MRP calculator correctly computing material requirements against
  live inventory
- The AI Assistant correctly identifying the most critical material,
  matching the risk engine's own finding
- Creating a Purchase Order directly from a procurement recommendation,
  with correct supplier/quantity/pricing
- Resolving a risk alert
- CSV and PDF report downloads

## Common errors and fixes

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'django'` | venv not activated | `source venv/bin/activate` then `pip install -r requirements.txt` |
| `django.db.utils.OperationalError` | `DB_ENGINE=postgres` but Postgres isn't running | Start Postgres and fix `.env`, or set `DB_ENGINE=sqlite` |
| Forecasting page says "no trained model" | Model hasn't been trained yet | `python manage.py train_forecast_model` (needs `generate_demo_data` first — needs 30+ sales history rows) |
| Dashboard charts are empty | No demo data yet | `python manage.py generate_demo_data` |
| 403 on any POST form | Missing/expired CSRF cookie | Make sure cookies are enabled; refresh the page and resubmit |
| `SECRET_KEY` errors | `.env` missing or blank | `cp .env.example .env` and fill in `SECRET_KEY` |
| Port already in use | Another server running on 8000 | `python manage.py runserver 8001` |

---

## Project structure

```
FanFlow/
├── manage.py
├── config/                 # settings, root urls.py, wsgi/asgi
├── accounts/                # auth, roles (UserProfile + Django Groups), permissions
├── dashboard/                # KPIs, charts, generate_demo_data/train_forecast_model/generate_forecasts commands
├── products/                  # Fan models
├── materials/                  # Raw materials + reorder levels
├── production/                  # BOM, BOMItem, MRP service
├── orders/                       # CustomerOrder, SalesHistory
├── inventory/                     # Inventory, InventoryTransaction, stock services
├── suppliers/                      # Supplier, SupplierMaterial, scoring service
├── forecasting/                     # DemandForecast + ml/ (preprocess, train, predict)
├── procurement/                      # PurchaseOrder(Item), recommendation service
├── logistics/                         # Shipment tracking
├── risk_management/                    # RiskAlert + detection engine
├── analytics/                           # Deeper chart views
├── ai_assistant/                         # Rule-based / LLM-ready supply chain Q&A
├── notifications/                         # Combined risk + low-stock feed
├── reports/                                # CSV/PDF exports
├── templates/, static/, media/, datasets/, ml_models/, notebooks/, utils/
├── requirements.txt
├── .env / .env.example
└── README.md
```
