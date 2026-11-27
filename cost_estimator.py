import streamlit as st
import pandas as pd
import io
import csv
import html

from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)


# ==========================================================
# CIVILAI NEPAL - PROFESSIONAL PROJECT COST ESTIMATOR
# ==========================================================

APP_NAME = "CIVILAI NEPAL"

PROJECT_TYPES = [
    "Residential Building",
    "Commercial Building",
    "Institutional Building",
    "Mixed-Use Building",
    "Other Building Project"
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


def safe_text(value):
    return html.escape(str(value or ""))


# ==========================================================
# COST CALCULATION
# ==========================================================

def calculate_project_cost(
    total_area,
    rate_per_sqft,
    breakdown,
    contingency_percent,
    overhead_percent,
    vat_percent
):

    base_cost = total_area * rate_per_sqft

    breakdown = breakdown.copy()

    breakdown["Percentage"] = pd.to_numeric(
        breakdown["Percentage"],
        errors="coerce"
    ).fillna(0)

    breakdown["Estimated Cost (NPR)"] = (
        base_cost * breakdown["Percentage"] / 100
    )

    contingency = base_cost * contingency_percent / 100

    overhead = base_cost * overhead_percent / 100

    taxable_amount = base_cost + contingency + overhead

    vat = taxable_amount * vat_percent / 100

    grand_total = taxable_amount + vat

    return {
        "base_cost": base_cost,
        "breakdown": breakdown,
        "contingency": contingency,
        "overhead": overhead,
        "taxable_amount": taxable_amount,
        "vat": vat,
        "grand_total": grand_total
    }


# ==========================================================
# PDF REPORT
# ==========================================================

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
    vat_percent
):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="CivilAI Nepal Project Cost Estimate",
        author="CivilAI Nepal"
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=19,
        leading=23,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "SubtitleCustom",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=10,
        spaceAfter=6
    )

    small_style = ParagraphStyle(
        "SmallCustom",
        parent=styles["Normal"],
        fontSize=8,
        leading=11
    )

    elements = []

    elements.append(
        Paragraph(APP_NAME, title_style)
    )

    elements.append(
        Paragraph(
            "PROFESSIONAL PROJECT COST ESTIMATE",
            subtitle_style
        )
    )

    elements.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#17365D")
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph("1. PROJECT INFORMATION", heading_style)
    )

    project_data = [
        ["Project Name", safe_text(project_name)],
        ["Project Type", safe_text(project_type)],
        ["Client / Organization", safe_text(client)],
        ["Location", safe_text(location)],
        ["Prepared By", safe_text(prepared_by)],
        ["Number of Floors", str(floors)],
        ["Area per Floor", f"{area_per_floor:,.2f} sq.ft."],
        ["Total Built-up Area", f"{total_area:,.2f} sq.ft."],
        ["Estimation Date", date.today().strftime("%d %B %Y")]
    ]

    project_table = Table(
        project_data,
        colWidths=[48 * mm, 130 * mm]
    )

    project_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1),
             colors.HexColor("#EAF0F6")),
            ("TEXTCOLOR", (0, 0), (0, -1),
             colors.HexColor("#17365D")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    elements.append(project_table)
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph("2. CONSTRUCTION COST BREAKDOWN", heading_style)
    )

    table_data = [
        [
            "S.N.",
            "Construction Work Category",
            "Share (%)",
            "Estimated Cost (NPR)"
        ]
    ]

    for index, row in calculation["breakdown"].iterrows():

        table_data.append([
            str(len(table_data)),
            Paragraph(
                safe_text(row["Work Category"]),
                small_style
            ),
            f'{row["Percentage"]:.2f}',
            f'{row["Estimated Cost (NPR)"]:,.2f}'
        ])

    breakdown_table = Table(
        table_data,
        colWidths=[
            12 * mm,
            83 * mm,
            25 * mm,
            58 * mm
        ],
        repeatRows=1
    )

    breakdown_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#17365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white,
                colors.HexColor("#F2F5F9")
            ]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    elements.append(breakdown_table)
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph("3. PROJECT COST SUMMARY", heading_style)
    )

    summary_data = [
        ["Description", "Amount (NPR)"],
        ["Base Construction Cost", money(calculation["base_cost"])],
        [
            f"Contingency ({contingency_percent:.2f}%)",
            money(calculation["contingency"])
        ],
        [
            f"Overhead ({overhead_percent:.2f}%)",
            money(calculation["overhead"])
        ],
        ["Taxable Amount", money(calculation["taxable_amount"])],
        [
            f"VAT ({vat_percent:.2f}%)",
            money(calculation["vat"])
        ],
        ["GRAND TOTAL", money(calculation["grand_total"])]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[105 * mm, 73 * mm]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#17365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1),
             colors.HexColor("#DCE6F1")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
        ])
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 14))

    elements.append(
        Paragraph("4. IMPORTANT NOTES", heading_style)
    )

    note = (
        "This report provides an approximate preliminary project "
        "cost estimate based on the built-up area and user-entered "
        "unit rate. The construction cost allocation percentages "
        "are planning assumptions, not measured BOQ quantities. "
        "Actual costs depend on drawings, specifications, site "
        "conditions, structural system, materials, labour and "
        "local market rates. Verify all assumptions with a qualified "
        "civil engineer or quantity surveyor before tendering or "
        "construction. VAT and other taxes must be confirmed under "
        "applicable Nepalese rules."
    )

    elements.append(
        Paragraph(note, small_style)
    )

    elements.append(Spacer(1, 24))

    signatures = [
        ["Prepared By", "Checked By", "Approved By"],
        ["________________", "________________", "________________"]
    ]

    signature_table = Table(
        signatures,
        colWidths=[59 * mm, 59 * mm, 59 * mm]
    )

    signature_table.setStyle(
        TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 8)
        ])
    )

    elements.append(signature_table)

    def footer(canvas, document):

        canvas.saveState()

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)

        canvas.drawString(
            15 * mm,
            10 * mm,
            "CivilAI Nepal | Project Cost Estimate"
        )

        canvas.drawRightString(
            195 * mm,
            10 * mm,
            f"Page {document.page}"
        )

        canvas.restoreState()

    doc.build(
        elements,
        onFirstPage=footer,
        onLaterPages=footer
    )

    return buffer.getvalue()


# ==========================================================
# CSV REPORT
# ==========================================================

def create_estimate_csv(calculation):

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "CivilAI Nepal - Project Cost Estimate"
    ])

    writer.writerow([])

    writer.writerow([
        "Construction Work Category",
        "Percentage",
        "Estimated Cost (NPR)"
    ])

    for _, row in calculation["breakdown"].iterrows():

        writer.writerow([
            row["Work Category"],
            row["Percentage"],
            row["Estimated Cost (NPR)"]
        ])

    writer.writerow([])

    writer.writerow(["Project Cost Summary", "Amount (NPR)"])

    writer.writerow([
        "Base Construction Cost",
        calculation["base_cost"]
    ])

    writer.writerow([
        "Contingency",
        calculation["contingency"]
    ])

    writer.writerow([
        "Overhead",
        calculation["overhead"]
    ])

    writer.writerow([
        "Taxable Amount",
        calculation["taxable_amount"]
    ])

    writer.writerow([
        "VAT",
        calculation["vat"]
    ])

    writer.writerow([
        "Grand Total",
        calculation["grand_total"]
    ])

    return output.getvalue().encode("utf-8-sig")


# ==========================================================
# STREAMLIT USER INTERFACE
# ==========================================================

def render_cost_estimator():

    st.header("Project Cost Estimator")

    st.caption(
        "Professional preliminary building construction "
        "cost estimation for projects in Nepal."
    )

    st.info(
        "Enter your project's built-up area and a verified "
        "local construction rate per square foot."
    )

    # ------------------------------------------------------
    # PROJECT DETAILS
    # ------------------------------------------------------

    st.subheader("1. Project Information")

    col1, col2 = st.columns(2)

    with col1:

        project_name = st.text_input(
            "Project Name",
            placeholder="Example: Residential Building"
        )

        project_type = st.selectbox(
            "Project Type",
            PROJECT_TYPES
        )

        client = st.text_input(
            "Client / Organization"
        )

    with col2:

        location = st.text_input(
            "Project Location",
            placeholder="Example: Kathmandu, Nepal"
        )

        prepared_by = st.text_input(
            "Prepared By"
        )

    st.divider()

    # ------------------------------------------------------
    # AREA AND RATE
    # ------------------------------------------------------

    st.subheader("2. Building Area and Construction Rate")

    col1, col2 = st.columns(2)

    with col1:

        floors = st.number_input(
            "Number of Floors",
            min_value=1,
            max_value=100,
            value=2,
            step=1
        )

        area_per_floor = st.number_input(
            "Built-up Area per Floor (sq.ft.)",
            min_value=0.0,
            value=1000.0,
            step=50.0
        )

    with col2:

        rate_per_sqft = st.number_input(
            "Construction Rate (NPR/sq.ft.)",
            min_value=0.0,
            value=3500.0,
            step=100.0,
            help="Replace the example rate with a verified local rate."
        )

        total_area = floors * area_per_floor

        st.metric(
            "Total Built-up Area",
            f"{total_area:,.2f} sq.ft."
        )

    st.caption(
        "The sample rate is for demonstrating the calculator only. "
        "It is not a verified Nepal market rate."
    )

    st.divider()

    # ------------------------------------------------------
    # COST BREAKDOWN
    # ------------------------------------------------------

    st.subheader("3. Construction Cost Allocation")

    st.write(
        "Edit the percentage allocated to each construction category. "
        "All percentages must total exactly 100%."
    )

    if "civilai_cost_breakdown" not in st.session_state:

        st.session_state.civilai_cost_breakdown = pd.DataFrame(
            DEFAULT_BREAKDOWN
        )

    edited_breakdown = st.data_editor(
        st.session_state.civilai_cost_breakdown,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="civilai_cost_breakdown_editor",
        column_config={
            "Work Category": st.column_config.TextColumn(
                "Construction Work Category",
                required=True
            ),
            "Percentage": st.column_config.NumberColumn(
                "Percentage (%)",
                min_value=0.0,
                max_value=100.0,
                format="%.2f"
            )
        }
    )

    st.session_state.civilai_cost_breakdown = edited_breakdown

    percentage_total = pd.to_numeric(
        edited_breakdown["Percentage"],
        errors="coerce"
    ).fillna(0).sum()

    if abs(percentage_total - 100.0) > 0.01:

        st.warning(
            f"Your cost allocation currently totals "
            f"{percentage_total:.2f}%. It must total 100%."
        )

        allocation_valid = False

    else:

        st.success(
            "Cost allocation is valid: 100%."
        )

        allocation_valid = True

    st.divider()

    # ------------------------------------------------------
    # ADDITIONAL COSTS
    # ------------------------------------------------------

    st.subheader("4. Additional Cost Settings")

    col1, col2, col3 = st.columns(3)

    with col1:

        contingency_percent = st.number_input(
            "Contingency (%)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.5
        )

    with col2:

        overhead_percent = st.number_input(
            "Overhead (%)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.5
        )

    with col3:

        vat_percent = st.number_input(
            "VAT (%)",
            min_value=0.0,
            max_value=100.0,
            value=13.0,
            step=0.5
        )

    st.divider()

    # ------------------------------------------------------
    # CALCULATE AND DISPLAY
    # ------------------------------------------------------

    st.subheader("5. Project Cost Calculation")

    if not allocation_valid:

        st.error(
            "Correct the cost allocation percentages to continue."
        )

        return

    if total_area <= 0 or rate_per_sqft <= 0:

        st.warning(
            "Enter a positive building area and construction rate."
        )

        return

    calculation = calculate_project_cost(
        total_area,
        rate_per_sqft,
        edited_breakdown,
        contingency_percent,
        overhead_percent,
        vat_percent
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Base Construction Cost",
            money(calculation["base_cost"])
        )

        st.metric(
            "Contingency",
            money(calculation["contingency"])
        )

        st.metric(
            "Overhead",
            money(calculation["overhead"])
        )

    with col2:

        st.metric(
            "Taxable Amount",
            money(calculation["taxable_amount"])
        )

        st.metric(
            "VAT",
            money(calculation["vat"])
        )

        st.metric(
            "Estimated Project Cost",
            money(calculation["grand_total"])
        )

    st.subheader("Detailed Cost Breakdown")

    st.dataframe(
        calculation["breakdown"],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Percentage": st.column_config.NumberColumn(
                format="%.2f%%"
            ),
            "Estimated Cost (NPR)": st.column_config.NumberColumn(
                format="NPR %.2f"
            )
        }
    )

    st.divider()

    # ------------------------------------------------------
    # DOWNLOAD REPORTS
    # ------------------------------------------------------

    st.subheader("6. Download Project Estimate")

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
        vat_percent
    )

    csv_bytes = create_estimate_csv(calculation)

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "Download PDF Report",
            data=pdf_bytes,
