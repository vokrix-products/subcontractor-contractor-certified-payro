from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os

def generate_wh347_pdf(record, output_path):
    """
    Creates a PDF that mimics the WH‑347 layout with project info and employee rows.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = styles['Title']
    elements.append(Paragraph("CERTIFIED PAYROLL REPORT (WH‑347)", title_style))
    elements.append(Spacer(1, 12))

    # Project / Contractor info from first employee
    if record['employees']:
        first = record['employees'][0]
        info_text = f"Project: {first['project']}<br/>Week Ending: {first['week_end_date']}"
    else:
        info_text = "Project: N/A<br/>Week Ending: N/A"
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Table header
    header = [
        "Employee Name", "SSN", "Classification", "Hours",
        "Base Rate", "Fringe Rate", "Fringe Amt", "Total Pay",
    ]
    data = [header]

    for emp in record['employees']:
        row = [
            emp['employee_name'],
            emp.get('ssn', ''),
            emp['classification'],
            f"{emp['hours_worked']:.2f}",
            f"${emp['base_rate']:.2f}",
            f"${emp['fringe_rate']:.2f}",
            f"${emp['fringe_amount']:.2f}",
            f"${emp['total_pay']:.2f}",
        ]
        data.append(row)

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(table)

    # Status note
    elements.append(Spacer(1, 18))
    elements.append(Paragraph(f"Status: {record['status']}", styles['Normal']))
    if record.get('warnings'):
        elements.append(Paragraph("Warnings:", styles['Normal']))
        for w in record['warnings']:
            elements.append(Paragraph(f"• {w}", styles['Normal']))
    if record.get('critical_errors'):
        elements.append(Paragraph("Critical Errors:", styles['Normal']))
        for e in record['critical_errors']:
            elements.append(Paragraph(f"• {e}", styles['Normal']))

    doc.build(elements)
