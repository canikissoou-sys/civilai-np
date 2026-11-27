import csv
import html
import io
from datetime import date

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

APP_NAME = "CIVILAI NEPAL"
PROJECT_TYPES = [
    "Residential Building",
    "Commercial Building",
    "Institutional Building",
    "Mixed-Use Building",
    "Other Building Project",
]

DEFAULT_BREAKDOWN = [
    {"Work Category": "Site preparation and earthwork", "Percentage": 5.0},
    {"Work Category": "Foundation and substructure", "Percentage": 10.0},
    {"Work Category": "RCC structural framework", "Percentage": 25.0},
    {"Work Category": "Brickwork and masonry", "Percentage": 8.0},
    {"Work Category": "Roofing and waterproofing", "Percentage": 5.0},
    {"Work Category": "Doors and windows", "Percentage": 7.0},
    {"Work Category": "Flooring and finishing", "Percentage": 15.0},
    {"Work Category": "Painting and decoration", "Percentage": 7.0},
    {"Work Category": "Electrical installation", "Percentage": 7.0},
    {"Work Category": "Plumbing and sanitation", "Percentage": 6.0},
    {"Work Category": "External development", "Percentage": 5.0},
]


def money(value):
    return f"NPR {float(value):,.2f}"


def calculate_project_cost(
    total_area,
    rate_per_sqft,
    breakdown,
    contingency_percent,
    overhead_percent,
    vat_percent,
):
    """Calculate a preliminary area-based project cost estimate."""
    data = breakdown.copy()
    data["Percentage"] = pd.to_numeric(
        data["Percentage"], errors="coerce"
    ).fillna(0.0)
    data["Estimated Cost (NPR)"] = (
        float(total_area)
        * float(rate_per_sqft)
        * data["Percentage"]
        / 100.0
    )

    base_cost = float(total_area) * float(rate_per_sqft)
    contingency = base_cost * float(contingency_percent) / 100.0
    overhead = base_cost * float(overhead_percent) / 100.0
    taxable_amount = base_cost + contingency + overhead
    vat = taxable_amount * float(vat_percent) / 100.0

    return {
        "base_cost": base_cost,
        "breakdown": data,
        "contingency": contingency,
        "overhead": overhead,
        "taxable_amount": taxable_amount,
        "vat": vat,
        "grand_total": taxable_amount + vat,
    }


def create_estimate_pdf(
    project_name,
    project_type,
    client,
    location,
    prepared_by,
    floors,
    area_per_floor,
    total_area,
    rate,
    calculation,
    contingency_percent,
    overhead_percent,
    vat_percent,
):
    """Create a downloadable PDF report in memory."""
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="CivilAI Nepal Project Cost Estimate",
        author=APP_NAME,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CivilAITitle",
        parent=styles["Title"],
        fontSize=19,
        leading=23,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=5,
    )
    subtitle_style = ParagraphStyle(
        "CivilAISubtitle",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "CivilAISectionHeading",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=10,
        spaceAfter=6,
    )
    small_style = ParagraphStyle(
        "CivilAISmall",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
    )

    safe = lambda value: html.escape(str(value or ""))
    story = [
        Paragraph(APP_NAME, title_style),
        Paragraph("PROFESSIONAL PROJECT COST ESTIMATE", subtitle_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#17365D")),
        Spacer(1, 9),
        Paragraph("1. PROJECT INFORMATION", heading_style),
    ]

    project_rows = [
        ["Project Name", safe(project_name)],
        ["Project Type", safe(project_type)],
        ["Client / Organization", safe(client)],
        ["Project Location", safe(location)],
        ["Prepared By", safe(prepared_by)],
        ["Number of Floors", str(floors)],
        ["Area per Floor", f"{area_per_floor:,.2f} sq.ft."],
        ["Total Built-up Area", f"{total_area:,.2f} sq.ft."],
        ["Rate per sq.ft.", money(rate)],
        ["Estimate Date", date.today().strftime("%d %B %Y")],
    ]
    project_table = Table(project_rows, colWidths=[48 * mm, 130 * mm])
    project_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF0F6")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#17365D")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([project_table, Spacer(1, 10)])
    story.append(Paragraph("2. CONSTRUCTION COST BREAKDOWN", heading_style))

    breakdown_rows = [["S.N.", "Work Category", "Share (%)", "Estimated Cost (NPR)"]]
    for index, row in calculation["breakdown"].reset_index(drop=True).iterrows():
        breakdown_rows.append([
            str(index + 1),
            Paragraph(safe(row["Work Category"]), small_style),
            f"{float(row['Percentage']):.2f}",
            f"{float(row['Estimated Cost (NPR)']):,.2f}",
        ])

    breakdown_table = Table(
        breakdown_rows,
        colWidths=[12 * mm, 83 * mm, 25 * mm, 58 * mm],
        repeatRows=1,
    )
    breakdown_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F9")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([breakdown_table, Spacer(1, 10)])
    story.append(Paragraph("3. PROJECT COST SUMMARY", heading_style))

    summary_rows = [
        ["Description", "Amount (NPR)"],
        ["Base Construction Cost", money(calculation["base_cost"])],
        [f"Contingency ({contingency_percent:.2f}%)", money(calculation["contingency"])],
        [f"Overhead ({overhead_percent:.2f}%)", money(calculation["overhead"])],
        ["Taxable Amount", money(calculation["taxable_amount"])],
        [f"VAT ({vat_percent:.2f}%)", money(calculation["vat"])],
        ["GRAND TOTAL", money(calculation["grand_total"])],
    ]
    summary_table = Table(summary_rows, colWidths=[105 * mm, 73 * mm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DCE6F1")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([summary_table, Spacer(1, 12)])
    story.append(Paragraph("4. IMPORTANT NOTES", heading_style))
    note = (
        "This is an indicative preliminary estimate based on the entered "
        "built-up area, unit rate and cost allocation percentages. It is not "
        "a measured bill of quantities or a detailed quantity take-off. "
        "Actual costs depend on drawings, specifications, site conditions, "
        "structural system, materials, labour and local market rates. "
        "Verify quantities, rates, applicable taxes and project-specific "
        "calculation rules with a qualified engineer or quantity surveyor "
        "before using this estimate for a tender or contract."
    )
    story.append(Paragraph(note, small_style))
    story.append(Spacer(1, 22))

    signatures = [
        ["Prepared By", "Checked By", "Approved By"],
        ["________________", "________________", "________________"],
    ]
    signature_table = Table(signatures, colWidths=[59 * mm, 59 * mm, 59 * mm])
    signature_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(signature_table)

    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(15 * mm, 10 * mm, "CivilAI Nepal | Project Cost Estimate")
        canvas.drawRightString(195 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    return buffer.getvalue()


def create_estimate_csv(calculation):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["CivilAI Nepal - Project Cost Estimate"])
    writer.writerow([])
    writer.writerow(["Construction Work Category", "Percentage", "Estimated Cost (NPR)"])
    for _, row in calculation["breakdown"].iterrows():
        writer.writerow([
            row["Work Category"],
            float(row["Percentage"]),
            float(row["Estimated Cost (NPR)"]),
        ])
    writer.writerow([])
    writer.writerow(["Project Cost Summary", "Amount (NPR)"])
    writer.writerow(["Base Construction Cost", calculation["base_cost"]])
    writer.writerow(["Contingency", calculation["contingency"]])
    writer.writerow(["Overhead", calculation["overhead"]])
    writer.writerow(["Taxable Amount", calculation["taxable_amount"]])
    writer.writerow(["VAT", calculation["vat"]])
    writer.writerow(["Grand Total", calculation["grand_total"]])
    return output.getvalue().encode("utf-8-sig")


def render_cost_estimator():
    st.header("Project Cost Estimator")
    st.caption("Preliminary building construction cost estimation in Nepal.")
    st.info(
        "Enter a verified local construction rate. The example rate is "
        "only a placeholder and is not a published Nepal market rate."
    )

    st.subheader("1. Project Information")
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Project Name", key="ce_project_name")
        project_type = st.selectbox("Project Type", PROJECT_TYPES, key="ce_project_type")
        client = st.text_input("Client / Organization", key="ce_client")
    with col2:
        location = st.text_input("Project Location", key="ce_location")
        prepared_by = st.text_input("Prepared By", key="ce_prepared_by")

    st.divider()
    st.subheader("2. Building Area and Rate")
    col1, col2 = st.columns(2)
    with col1:
        floors = st.number_input("Number of Floors", min_value=1, max_value=100, value=2, step=1, key="ce_floors")
        area_per_floor = st.number_input("Built-up Area per Floor (sq.ft.)", min_value=0.0, value=1000.0, step=50.0, key="ce_area")
    with col2:
        rate_per_sqft = st.number_input("Construction Rate (NPR/sq.ft.)", min_value=0.0, value=3500.0, step=100.0, key="ce_rate")
        total_area = float(floors) * float(area_per_floor)
        st.metric("Total Built-up Area", f"{total_area:,.2f} sq.ft.")

    st.divider()
    st.subheader("3. Construction Cost Allocation")
    if "ce_breakdown_data" not in st.session_state:
        st.session_state["ce_breakdown_data"] = pd.DataFrame(DEFAULT_BREAKDOWN)

    edited_breakdown = st.data_editor(
        st.session_state["ce_breakdown_data"],
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="ce_breakdown_editor",
        column_config={
            "Work Category": st.column_config.TextColumn("Work Category", required=True),
            "Percentage": st.column_config.NumberColumn(
                "Percentage (%)", min_value=0.0, max_value=100.0, format="%.2f"
            ),
        },
    )
    st.session_state["ce_breakdown_data"] = edited_breakdown

    if edited_breakdown.empty:
        st.error("Add at least one construction work category.")
        return
    if edited_breakdown["Work Category"].fillna("").astype(str).str.strip().eq("").any():
        st.error("Every work category must have a name.")
        return

    percentage_total = pd.to_numeric(
        edited_breakdown["Percentage"], errors="coerce"
    ).fillna(0.0).sum()
    allocation_valid = abs(float(percentage_total) - 100.0) <= 0.01
    if allocation_valid:
        st.success("Cost allocation totals 100%.")
    else:
        st.warning(f"Cost allocation totals {percentage_total:.2f}%. It must total exactly 100%.")

    st.divider()
    st.subheader("4. Additional Estimate Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        contingency_percent = st.number_input("Contingency (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5, key="ce_contingency")
    with col2:
        overhead_percent = st.number_input("Overhead (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5, key="ce_overhead")
    with col3:
        vat_percent = st.number_input("VAT (%)", min_value=0.0, max_value=100.0, value=13.0, step=0.5, key="ce_vat")

    if not allocation_valid:
        st.info("Correct the allocation percentages to see the estimate and download reports.")
        return
    if total_area <= 0 or rate_per_sqft <= 0:
        st.warning("Enter a positive total building area and a positive construction rate.")
        return

    calculation = calculate_project_cost(
        total_area,
        rate_per_sqft,
        edited_breakdown,
        contingency_percent,
        overhead_percent,
        vat_percent,
    )

    st.divider()
    st.subheader("5. Estimated Project Cost")
    col1, col2, col3 = st.columns(3)
    col1.metric("Base Cost", money(calculation["base_cost"]))
    col2.metric("Taxable Amount", money(calculation["taxable_amount"]))
    col3.metric("Estimated Grand Total", money(calculation["grand_total"]))

    summary = pd.DataFrame([
        {"Description": "Base Construction Cost", "Amount (NPR)": calculation["base_cost"]},
        {"Description": "Contingency", "Amount (NPR)": calculation["contingency"]},
        {"Description": "Overhead", "Amount (NPR)": calculation["overhead"]},
        {"Description": "Taxable Amount", "Amount (NPR)": calculation["taxable_amount"]},
        {"Description": "VAT", "Amount (NPR)": calculation["vat"]},
        {"Description": "GRAND TOTAL", "Amount (NPR)": calculation["grand_total"]},
    ])
    st.dataframe(summary, hide_index=True, use_container_width=True)

    st.subheader("Detailed Cost Breakdown")
    st.dataframe(calculation["breakdown"], hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("6. Download Reports")
    pdf_bytes = create_estimate_pdf(
        project_name,
        project_type,
        client,
        location,
        prepared_by,
        floors,
        area_per_floor,
        total_area,
        rate_per_sqft,
        calculation,
        contingency_percent,
        overhead_percent,
        vat_percent,
    )
    csv_bytes = create_estimate_csv(calculation)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download PDF Report",
            data=pdf_bytes,
            file_name="CivilAI_Nepal_Project_Estimate.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "Download CSV Report",
            data=csv_bytes,
            file_name="CivilAI_Nepal_Project_Estimate.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.caption(
        "Preliminary estimate only. Confirm applicable VAT, contingency, "
        "overhead and project-specific calculation rules before tender or contract use."
    )
