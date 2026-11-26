import streamlit as st
import csv
import io

def render_boq_generator():
    st.header("📋 Construction BOQ Generator")
    st.write("Prepare a preliminary construction Bill of Quantities.")

    st.info(
        "Enter estimated quantities and rates in NPR. "
        "Rates should be checked against current local market prices."
    )

    project_name = st.text_input("Project Name")
    client_name = st.text_input("Client / Owner Name")
    location = st.text_input("Project Location")

    st.subheader("Work Items")

    items = [
        ("Site clearance", "m²"),
        ("Earthwork excavation", "m³"),
        ("PCC work", "m³"),
        ("RCC work", "m³"),
        ("Reinforcement steel", "kg"),
        ("Brick masonry", "m³"),
        ("Internal plaster", "m²"),
        ("Flooring", "m²"),
        ("Painting", "m²"),
    ]

    boq_rows = []
    subtotal = 0.0

    for i, (item, unit) in enumerate(items):
        with st.expander(item, expanded=(i == 0)):
            col1, col2 = st.columns(2)

            with col1:
                quantity = st.number_input(
                    f"Quantity ({unit})",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key=f"qty_{i}"
                )

            with col2:
                rate = st.number_input(
                    "Rate (NPR)",
                    min_value=0.0,
                    value=0.0,
                    step=100.0,
                    key=f"rate_{i}"
                )

            amount = quantity * rate
            subtotal += amount

            boq_rows.append({
                "Description": item,
                "Unit": unit,
                "Quantity": quantity,
                "Rate (NPR)": rate,
                "Amount (NPR)": amount
            })

    st.divider()
    st.subheader("Cost Summary")

    contingency_percent = st.number_input(
        "Contingency (%)",
        min_value=0.0,
        value=0.0,
        step=1.0
    )

    vat_percent = st.number_input(
        "VAT (%)",
        min_value=0.0,
        value=13.0,
        step=1.0
    )

    contingency = subtotal * contingency_percent / 100
    taxable_amount = subtotal + contingency
    vat = taxable_amount * vat_percent / 100
    grand_total = taxable_amount + vat

    st.dataframe(boq_rows, use_container_width=True)

    st.metric("Subtotal", f"NPR {subtotal:,.2f}")
    st.metric("Contingency", f"NPR {contingency:,.2f}")
    st.metric("VAT", f"NPR {vat:,.2f}")

    st.success(f"Estimated Grand Total: NPR {grand_total:,.2f}")

    st.caption(
        "Preliminary estimate only. Confirm applicable VAT, "
        "tax treatment, specifications and market rates before use."
    )

    if st.button("Prepare BOQ CSV"):
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["CivilAI Nepal - Preliminary BOQ"])
        writer.writerow(["Project", project_name])
        writer.writerow(["Client", client_name])
        writer.writerow(["Location", location])
        writer.writerow([])
        writer.writerow([
            "Description", "Unit", "Quantity",
            "Rate (NPR)", "Amount (NPR)"
        ])

        for row in boq_rows:
            writer.writerow(row.values())

        writer.writerow([])
        writer.writerow(["Subtotal", subtotal])
        writer.writerow(["Contingency", contingency])
        writer.writerow(["VAT", vat])
        writer.writerow(["Grand Total", grand_total])

        st.download_button(
            "⬇️ Download BOQ CSV",
            data=output.getvalue().encode("utf-8-sig"),
            file_name="CivilAI_Nepal_BOQ.csv",
            mime="text/csv"
        )
