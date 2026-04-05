from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime
from io import BytesIO


def risk_suggestion(percent):
    if percent >= 70:
        return (
            "The predicted dropout likelihood is significantly high. "
            "Immediate intervention is strongly recommended. "
            "Frequent academic check-ins, one-to-one counseling, and "
            "parental involvement can help prevent withdrawal."
        )
    elif percent >= 30:
        return (
            "The student displays moderate dropout risk. "
            "Motivational programs, stress-management strategies, "
            "and academic mentoring can improve stability."
        )
    else:
        return (
            "The student is currently at low risk of dropping out. "
            "Continued engagement and academic encouragement "
            "are recommended to sustain positive progress."
        )


def generate_pdf(data_dict, percent, risk_message):
    # Remove emojis to avoid black box issue in PDF
    clean_risk_message = risk_message.encode('ascii', 'ignore').decode('ascii')

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    y = height - 50

    # ======= HEADER =======
    p.setFillColor(colors.HexColor("#0D2A78"))
    p.rect(0, height - 70, width, 70, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(30, height - 45, "Dropout Risk Assessment Report")

    p.setFont("Helvetica", 10)
    p.drawRightString(width - 30, height - 45,
                      f"{datetime.now().strftime('%Y-%m-%d   %H:%M:%S')}")

    p.setFillColor(colors.black)
    y -= 90

    # ======= RISK SCORE =======
    if percent >= 70:
        box_color = colors.red
    elif percent >= 30:
        box_color = colors.orange
    else:
        box_color = colors.green

    p.setFillColor(box_color)
    p.roundRect(30, y, 200, 50, 10, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(45, y + 15, f"Risk Score: {percent}%")
    y -= 60

    # ======= SUMMARY =======
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(30, y, "Summary")
    y -= 20

    p.setFont("Helvetica", 12)
    p.drawString(30, y, clean_risk_message)
    y -= 30

    # ======= STUDENT DETAILS TABLE =======
    p.setFont("Helvetica-Bold", 14)
    p.drawString(30, y, "Student Information")
    y -= 25

    student_data = [["Feature", "Value"]]
    student_data.insert(1, ["Student Name", data_dict.get("student_name", "N/A")])

    for k, v in data_dict.items():
        if k.lower() != "student_name":
            student_data.append([k.replace("_", " ").title(), str(v)])

    table = Table(student_data, colWidths=[200, 300])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D2A78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke)
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 30, y - table._height)
    y -= table._height + 30

    # ======= RECOMMENDATIONS =======
    suggestions = risk_suggestion(percent)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(30, y, "Recommendations")
    y -= 25

    text_obj = p.beginText(30, y)
    text_obj.setFont("Helvetica", 11)
    text_obj.setLeading(16)

    for sentence in suggestions.split(". "):
        text_obj.textLine("• " + sentence.strip())
    p.drawText(text_obj)

    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(colors.grey)
    p.drawString(30, 30,
                 "This report is generated using AI — for academic support purposes only.")

    p.save()
    buffer.seek(0)
    return buffer
