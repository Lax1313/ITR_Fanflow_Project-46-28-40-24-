import csv

from django.http import HttpResponse
from django.shortcuts import render

from accounts.decorators import section_required
from forecasting.models import DemandForecast
from inventory.models import Inventory
from inventory.services import calculate_available_stock
from orders.models import CustomerOrder
from risk_management.models import RiskAlert
from suppliers.models import Supplier


@section_required('reports')
def report_hub(request):
    return render(request, 'reports/hub.html')


def _csv_response(filename, header, rows):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return response


@section_required('reports')
def export_inventory_csv(request):
    rows = []
    for inv in Inventory.objects.select_related('material').all():
        rows.append([
            inv.material.name, inv.current_stock, inv.reserved_stock, inv.incoming_stock,
            calculate_available_stock(inv), inv.reorder_level, inv.safety_stock,
        ])
    return _csv_response('inventory_report.csv',
                          ['Material', 'Current Stock', 'Reserved', 'Incoming', 'Available', 'Reorder Level', 'Safety Stock'],
                          rows)


@section_required('reports')
def export_suppliers_csv(request):
    rows = [[s.name, s.location, s.quality_score, s.reliability_score, s.status] for s in Supplier.objects.all()]
    return _csv_response('supplier_performance_report.csv',
                          ['Supplier', 'Location', 'Quality Score', 'Reliability Score', 'Status'], rows)


@section_required('reports')
def export_orders_csv(request):
    rows = [
        [o.id, o.customer_name, o.product.name, o.quantity, o.region, o.status, o.order_date, o.required_delivery_date]
        for o in CustomerOrder.objects.select_related('product').all()
    ]
    return _csv_response('orders_report.csv',
                          ['Order ID', 'Customer', 'Product', 'Quantity', 'Region', 'Status', 'Order Date', 'Required Delivery'],
                          rows)


@section_required('reports')
def export_forecast_csv(request):
    rows = [
        [f.product.name, f.forecast_date, f.predicted_quantity, f.model_name, f.confidence_score]
        for f in DemandForecast.objects.select_related('product').all()
    ]
    return _csv_response('demand_forecast_report.csv',
                          ['Product', 'Forecast Date', 'Predicted Quantity', 'Model', 'Confidence Score'], rows)


@section_required('reports')
def export_risk_csv(request):
    rows = [
        [a.risk_type, a.severity, a.title, a.description, a.is_resolved, a.created_at]
        for a in RiskAlert.objects.all()
    ]
    return _csv_response('risk_report.csv',
                          ['Risk Type', 'Severity', 'Title', 'Description', 'Resolved', 'Created At'], rows)


@section_required('reports')
def export_inventory_pdf(request):
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Inventory Report — FanFlow", styles['Title']), Spacer(1, 12)]

    data = [['Material', 'Current', 'Available', 'Reorder Level', 'Safety Stock']]
    for inv in Inventory.objects.select_related('material').all():
        data.append([
            inv.material.name, str(inv.current_stock), str(calculate_available_stock(inv)),
            str(inv.reorder_level), str(inv.safety_stock),
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#212529')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return HttpResponse(buffer.read(), content_type='application/pdf', headers={
        'Content-Disposition': 'attachment; filename="inventory_report.pdf"'
    })
