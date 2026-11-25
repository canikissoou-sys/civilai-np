import streamlit as st

st.set_page_config(
    page_title="CivilAI Nepal",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ CivilAI Nepal")
st.subheader("Your AI Civil Engineering Assistant 🇳🇵")

st.write(
    "A smart platform for civil engineers, "
    "contractors and engineering students."
)

st.success("Welcome to CivilAI Nepal!")

tab1, tab2, tab3 = st.tabs([
    "Concrete Calculator",
    "Brickwork Calculator",
    "About Us"
])

with tab1:
    st.header("Concrete Volume Calculator")

    length = st.number_input("Length (m)", min_value=0.0, value=5.0)
    width = st.number_input("Width (m)", min_value=0.0, value=4.0)
    depth = st.number_input("Depth (m)", min_value=0.0, value=0.15)

    if st.button("Calculate Concrete"):
        volume = length * width * depth
        st.metric("Concrete Volume", f"{volume:.3f} m³")

with tab2:
    st.header("Brickwork Calculator")

    wall_length = st.number_input("Wall Length (m)", min_value=0.0, value=5.0)
    wall_height = st.number_input("Wall Height (m)", min_value=0.0, value=3.0)
    thickness = st.number_input("Wall Thickness (m)", min_value=0.0, value=0.23)

    if st.button("Calculate Brickwork"):
        volume = wall_length * wall_height * thickness
        bricks = volume * 500

        st.metric("Brickwork Volume", f"{volume:.3f} m³")
        st.metric("Approximate Bricks", f"{bricks:.0f}")

with tab3:
    st.header("About CivilAI Nepal")
    st.write("""
    CivilAI Nepal aims to simplify civil engineering.

    Our future features:
    - AI Engineering Assistant
    - BOQ Generator
    - Quantity Estimation
    - Construction Cost Estimation
    - Drawing Analysis
    """)

st.caption(
    "Educational prototype. Verify all estimates "
    "against project specifications and professional advice."
)
