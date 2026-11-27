import streamlit as st
import pandas as pd
import io
import csv
import html

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
# CIVILAI NEPAL - PROFESSIONAL BOQ GENERATOR
# ==========================================================

CURRENCY = "NPR"

DEFAULT_ITEMS = [
    {
        "Description": "Site clearance",
        "Unit": "m2",
        "Quantity": 100.0,
        "Rate (NPR)": 50.0
    },
    {
        "Description": "Earth excavation",
        "Unit": "m3",
        "Quantity": 20.0,
        "Rate (NPR)": 800.0
    },
    {
        "Description": "PCC work",
        "Unit": "m3",
        "Quantity": 5.0,
        "Rate (NPR)": 9500.0
    },
    {
        "Description": "RCC work",
        "Unit": "m3",
        "Quantity": 10.0,
        "Rate (NPR)": 15000.0
    },
    {
        "Description": "Brick masonry",
        "Unit": "m3",
        "Quantity": 15.0,
        "Rate (NPR)": 12000.0
    },
    {
        "Description": "Plaster work",
        "Unit": "m2",
        "Quantity": 100.0,
        "Rate (NPR)": 450.0
    }
]


def money(value):
    """Format a number in Nepalese Rupees."""
    return f"{CURRENCY} {value:,.2f}"


def safe_text(value):
    """Safely format user-entered text for PDF paragraphs."""
    return html.escape(str(value or ""))


def calculate_boq(items, contingency_percent, overhead_percent, vat_percent):
    """Calculate BOQ amounts and project totals."""

    items = items.copy()

    items["Quantity"] = pd.to_numeric(
        items["Quantity"], errors="coerce"
    ).fillna(0)

    items["Rate (NPR)"] = pd.to_numeric(
        items["Rate (NPR)"], errors="coerce"
    ).fillna(0)

    items["Amount (NPR)"] = (
        items["Quantity"] * items["Rate (NPR)"]
    )

    subtotal = float(items["Amount (NPR)"].sum())

    contingency = subtotal * contingency_percent / 100
    overhead = subtotal * overhead_percent / 100

    taxable_amount = subtotal + contingency + overhead
    vat = taxable_amount * vat_percent / 100

    grand_total = taxable_amount + vat

    return {
        "items": items,
        "subtotal": subtotal,
        "contingency": contingency,
        "overhead": overhead,
        "taxable_amount": taxable_amount,
        "vat": vat,
        "grand_total": grand_total
    }


def create_boq_pdf(
    project_name,
    client_name,
    location,
    prepared_by,
    date_text,
    calculation,
    contingency_percent,
    overhead_percent,
    vat_percent
):
    """Create a professional BOQ PDF report."""

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CivilAITitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#12345A"),
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "CivilAISubtitle",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#526477"),
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#12345A"),
        spaceBefore=9,
        spaceAfter=6
    )

    normal_style = ParagraphStyle(
        "SmallText",
        parent=styles["Normal"],
        fontSize=8,
        leading=11
    )

    elements = []

    elements.append(Paragraph("CIVILAI NEPAL", title_style))
    elements.append(
        Paragraph(
            "PROFESSIONAL BILL OF QUANTITIES",
            subtitle_style
        )
    )

    elements.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=colors.HexColor("#12345A")
        )
    )

    elements.append(Spacer(1, 8))

    elements.append(
        Paragraph("PROJECT INFORMATION", heading_style)
    )

    project_data = [
        ["Project Name", safe_text(project_name)],
        ["Client / Organization", safe_text(client_name)],
        ["Project Location", safe_text(location)],
        ["Prepared By", safe_text(prepared_by)],
        ["Preparation Date", safe_text(date_text)]
    ]

    project_table = Table(
        project_data,
        colWidths=[42 * mm, 135 * mm]
    )

    project_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1),
             colors.HexColor("#EAF0F6")),
            ("TEXTCOLOR", (0, 0), (0, -1),
             colors.HexColor("#12345A")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
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
        Paragraph("BILL OF QUANTITIES", heading_style)
    )

    table_data = [[
        "S.N.",
        "Description",
        "Unit",
        "Quantity",
        "Rate (NPR)",
        "Amount (NPR)"
    ]]

    for index, row in calculation["items"].iterrows():
        table_data.append([
            str(len(table_data)),
            Paragraph(
                safe_text(row["Description"]),
                normal_style
            ),
            safe_text(row["Unit"]),
            f'{row["Quantity"]:,.3f}',
            f'{row["Rate (NPR)"]:,.2f}',
            f'{row["Amount (NPR)"]:,.2f}'
        ])

    boq_table = Table(
        table_data,
        colWidths=[
            10 * mm,
            62 * mm,
            15 * mm,
            25 * mm,
            30 * mm,
            35 * mm
        ],
        repeatRows=1
    )

    boq_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#12345A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#F3F6F9")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    elements.append(boq_table)
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph("PROJECT COST SUMMARY", heading_style)
    )

    summary_data = [
        ["Description", "Percentage", "Amount (NPR)"],
        ["BOQ Subtotal", "-", money(calculation["subtotal"])],
        [
            "Contingency",
            f"{contingency_percent:.2f}%",
            money(calculation["contingency"])
        ],
        [
            "Overhead",
            f"{overhead_percent:.2f}%",
            money(calculation["overhead"])
        ],
        [
            "Taxable Amount",
            "-",
            money(calculation["taxable_amount"])
        ],
        [
            "VAT",
            f"{vat_percent:.2f}%",
            money(calculation["vat"])
        ],
        [
            "GRAND TOTAL",
            "-",
            money(calculation["grand_total"])
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[85 * mm, 35 * mm, 57 * mm]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#12345A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("BACKGROUND", (0, -1), (-1, -1),
             colors.HexColor("#DCE8F5")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, -1), (-1, -1),
             colors.HexColor("#12345A")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
        ])
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 18))

    elements.append(
        Paragraph("NOTES AND DECLARATION", heading_style)
    )

    elements.append(
        Paragraph(
            "1. This BOQ is a preliminary cost estimate based on "
            "the quantities and rates entered by the user.<br/>"
            "2. Rates, specifications, measurement rules and "
            "applicable taxes must be verified before tendering "
            "or construction.<br/>"
            "3. This report is not a substitute for approved "
            "engineering drawings, specifications or professional "
            "verification.",
            normal_style
        )
    )

    elements.append(Spacer(1, 25))

    signature_data = [
        ["Prepared By", "Checked By", "Approved By"],
        ["__________________", "__________________", "__________________"]
    ]

    signature_table = Table(
        signature_data,
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

    document.build(elements)

    return buffer.getvalue()


def create_csv(items):
    """Create CSV data for spreadsheet software."""

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "S.N.",
        "Description",
        "Unit",
        "Quantity",
        "Rate (NPR)",
        "Amount (NPR)"
    ])

    for number, (_, row) in enumerate(items.iterrows(), start=1):
        writer.writerow([
            number,
            row["Description"],
            row["Unit"],
            row["Quantity"],
            row["Rate (NPR)"],
            row["Amount (NPR)"]
        ])

    return output.getvalue().encode("utf-8-sig")


def render_boq_generator():

    st.header("Professional BOQ Generator")

    st.caption(
        "Prepare construction cost estimates with editable "
        "quantities, rates and downloadable reports."
    )

    # ------------------------------------------------------
    # PROJECT INFORMATION
    # ------------------------------------------------------

    st.subheader("1. Project Information")

    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input(
            "Project Name",
            placeholder="Example: Residential Building"
        )

        client_name = st.text_input(
            "Client / Organization",
            placeholder="Enter client name"
        )

        location = st.text_input(
            "Project Location",
            placeholder="Example: Kathmandu, Nepal"
        )

    with col2:
        prepared_by = st.text_input(
            "Prepared By",
            placeholder="Engineer / Estimator name"
        )

        date_text = st.date_input(
            "Preparation Date"
        )

    st.divider()

    # ------------------------------------------------------
    # BOQ ITEMS
    # ------------------------------------------------------

    st.subheader("2. BOQ Items")

    st.info(
        "Edit the sample items, change quantities and rates, "
        "or add new rows using the table."
    )

    if "civilai_boq_items" not in st.session_state:
        st.session_state.civilai_boq_items = pd.DataFrame(
            DEFAULT_ITEMS
        )

    edited_items = st.data_editor(
        st.session_state.civilai_boq_items,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="civilai_boq_editor",
        column_config={
            "Description": st.column_config.TextColumn(
                "Work Description",
                required=True
            ),
            "Unit": st.column_config.TextColumn(
                "Unit",
                help="Example: m, m2, m3, kg, No."
            ),
            "Quantity": st.column_config.NumberColumn(
                "Quantity",
                min_value=0.0,
                format="%.3f"
            ),
            "Rate (NPR)": st.column_config.NumberColumn(
                "Rate (NPR)",
                min_value=0.0,
                format="%.2f"
            )
        }
    )

    st.session_state.civilai_boq_items = edited_items

    # ------------------------------------------------------
    # ADDITIONAL COSTS
    # ------------------------------------------------------

    st.divider()
    st.subheader("3. Additional Cost Settings")

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

    # ------------------------------------------------------
    # CALCULATIONS
    # ------------------------------------------------------

    calculation = calculate_boq(
        edited_items,
        contingency_percent,
        overhead_percent,
        vat_percent
    )

    st.divider()
    st.subheader("4. BOQ Calculation Results")

    st.dataframe(
        calculation["items"],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Quantity": st.column_config.NumberColumn(
                format="%.3f"
            ),
            "Rate (NPR)": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Amount (NPR)": st.column_config.NumberColumn(
                format="%.2f"
            )
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "BOQ Subtotal",
            money(calculation["subtotal"])
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
            "Estimated Grand Total",
            money(calculation["grand_total"])
        )

    # ------------------------------------------------------
    # DOWNLOAD REPORTS
    # ------------------------------------------------------

    st.divider()
    st.subheader("5. Download Professional Reports")

    valid_items = calculation["items"]

    pdf_bytes = create_boq_pdf(
        project_name,
        client_name,
        location,
        prepared_by,
        str(date_text),
        calculation,
        contingency_percent,
        overhead_percent,
        vat_percent
    )

    csv_bytes = create_csv(valid_items)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Download BOQ PDF",
            data=pdf_bytes,
            file_name="CivilAI_Nepal_Professional_BOQ.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col2:
        st.download_button(
            label="Download BOQ CSV",
            data=csv_bytes,
            file_name="CivilAI_Nepal_BOQ.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.caption(
        "CivilAI Nepal | Professional Civil Engineering Tools"
    )
