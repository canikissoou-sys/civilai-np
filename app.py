import streamlit as st
from openai import OpenAI
from boq import render_boq_generator
st.set_page_config(
    page_title="CivilAI Nepal",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ CivilAI Nepal")
st.subheader("Your AI Civil Engineering Assistant 🇳🇵")

st.write(
    "Smart engineering tools for engineers, "
    "contractors and students in Nepal."
)

# Engineering tools
tab1, tab2, tab3 = st.tabs([
    "Concrete Calculator",
    "Brickwork Calculator",
    "AI Engineering Assistant"
    "BOQ Generator"
])

with tab1:
    st.header("Concrete Volume Calculator")

    length = st.number_input(
        "Length (m)", min_value=0.0, value=5.0
    )
    width = st.number_input(
        "Width (m)", min_value=0.0, value=4.0
    )
    depth = st.number_input(
        "Depth (m)", min_value=0.0, value=0.15
    )

    if st.button("Calculate Concrete"):
        volume = length * width * depth
        st.success(f"Concrete volume: {volume:.3f} m³")

with tab2:
    st.header("Brickwork Calculator")

    wall_length = st.number_input(
        "Wall Length (m)", min_value=0.0, value=5.0
    )
    wall_height = st.number_input(
        "Wall Height (m)", min_value=0.0, value=3.0
    )
    thickness = st.number_input(
        "Wall Thickness (m)", min_value=0.0, value=0.23
    )

    if st.button("Calculate Brickwork"):
        volume = wall_length * wall_height * thickness
        bricks = volume * 500

        st.success(f"Brickwork volume: {volume:.3f} m³")
        st.info(f"Approximate bricks: {bricks:.0f}")

with tab3:
    st.header("🤖 CivilAI Engineering Assistant")

    st.write(
        "Ask questions about civil engineering, "
        "construction, estimation and materials."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    prompt = st.chat_input(
        "Ask your civil engineering question..."
    )

    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                api_key = st.secrets["OPENAI_API_KEY"]
                client = OpenAI(api_key=api_key)

                response = client.responses.create(
                    model="gpt-4.1-mini",
                    instructions="""
                    You are CivilAI Nepal, an assistant
                    specializing in civil engineering.

                    Help users understand:
                    - Concrete and construction materials
                    - Quantity estimation
                    - BOQ preparation
                    - Surveying
                    - Building construction
                    - Engineering calculations
                    - Nepal construction practices

                    Explain formulas and calculations step
                    by step. Use metric units by default.

                    Never invent Nepal Building Code clauses,
                    material prices or engineering standards.
                    Clearly state assumptions and uncertainties.

                    Never certify structural safety or replace
                    a qualified professional engineer.
                    """,
                    input=prompt,
                    max_output_tokens=700
                )

                answer = response.output_text

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception:
                st.error(
                    "AI response is currently unavailable. "
                    "Please check API billing, API key and "
                    "internet connection."
                )

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

st.divider()

st.caption(
    "CivilAI Nepal | Engineering technology for Nepal 🇳🇵"
)
st.caption(
    "Educational assistance only. Verify engineering "
    "calculations and designs with qualified professionals."
)
with tab4:
    render_boq_generator()
