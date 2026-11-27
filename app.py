import streamlit as st
import math

from boq import render_boq_generator

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="CivilAI Nepal",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ CivilAI Nepal")
st.subheader("Your AI Civil Engineering Assistant NP")

st.write(
    "Smart engineering tools for engineers, contractors "
    "and students in Nepal."
)


# ---------------- FOUR MAIN TABS ----------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Concrete Calculator",
    "Brickwork Calculator",
    "AI Engineering Assistant",
    "BOQ Generator"
    "Project Cost Estimator"
])


# ---------------- TAB 1: CONCRETE CALCULATOR ----------------

with tab1:

    st.header("Concrete Volume Calculator")

    col1, col2, col3 = st.columns(3)

    with col1:
        length = st.number_input(
            "Length (m)",
            min_value=0.0,
            value=5.0,
            step=0.5
        )

    with col2:
        width = st.number_input(
            "Width (m)",
            min_value=0.0,
            value=4.0,
            step=0.5
        )

    with col3:
        depth = st.number_input(
            "Depth (m)",
            min_value=0.0,
            value=0.15,
            step=0.05
        )

    if st.button("Calculate Concrete", key="concrete_calc"):

        wet_volume = length * width * depth
        dry_volume = wet_volume * 1.54

        st.success("Concrete calculation completed!")

        st.metric(
            "Wet Concrete Volume",
            f"{wet_volume:.3f} m³"
        )

        st.metric(
            "Dry Material Volume",
            f"{dry_volume:.3f} m³"
        )

        st.info(
            "Dry volume uses an approximate factor of 1.54. "
            "Actual material requirements depend on mix design."
        )

        st.subheader("Material Estimation")

        cement_ratio = st.number_input(
            "Cement ratio",
            min_value=0.1,
            value=1.0,
            key="cement_ratio"
        )

        sand_ratio = st.number_input(
            "Sand ratio",
            min_value=0.1,
            value=1.5,
            key="sand_ratio"
        )

        aggregate_ratio = st.number_input(
            "Aggregate ratio",
            min_value=0.1,
            value=3.0,
            key="aggregate_ratio"
        )

        total_ratio = (
            cement_ratio + sand_ratio + aggregate_ratio
        )

        cement_volume = dry_volume * cement_ratio / total_ratio
        sand_volume = dry_volume * sand_ratio / total_ratio
        aggregate_volume = dry_volume * aggregate_ratio / total_ratio

        cement_bags = cement_volume / 0.0347

        a, b, c = st.columns(3)

        a.metric("Cement", f"{cement_bags:.2f} bags")
        b.metric("Sand", f"{sand_volume:.3f} m³")
        c.metric("Aggregate", f"{aggregate_volume:.3f} m³")

        st.caption(
            "Illustrative nominal mix estimate only. "
            "Use an approved mix design for structural concrete."
        )


# ---------------- TAB 2: BRICKWORK CALCULATOR ----------------

with tab2:

    st.header("Brickwork Quantity Calculator")

    col1, col2, col3 = st.columns(3)

    with col1:
        wall_length = st.number_input(
            "Wall length (m)",
            min_value=0.0,
            value=5.0
        )

    with col2:
        wall_height = st.number_input(
            "Wall height (m)",
            min_value=0.0,
            value=3.0
        )

    with col3:
        wall_thickness = st.number_input(
            "Wall thickness (m)",
            min_value=0.0,
            value=0.23
        )

    st.subheader("Brick Dimensions")

    col1, col2, col3 = st.columns(3)

    with col1:
        brick_length = st.number_input(
            "Brick length (mm)",
            min_value=1,
            value=190
        )

    with col2:
        brick_width = st.number_input(
            "Brick width (mm)",
            min_value=1,
            value=90
        )

    with col3:
        brick_height = st.number_input(
            "Brick height (mm)",
            min_value=1,
            value=90
        )

    mortar_joint = st.number_input(
        "Mortar joint thickness (mm)",
        min_value=0,
        value=10
    )

    if st.button("Calculate Brickwork"):

        wall_volume = (
            wall_length * wall_height * wall_thickness
        )

        effective_length = (
            brick_length + mortar_joint
        ) / 1000

        effective_width = (
            brick_width + mortar_joint
        ) / 1000

        effective_height = (
            brick_height + mortar_joint
        ) / 1000

        effective_brick_volume = (
            effective_length
            * effective_width
            * effective_height
        )

        if effective_brick_volume > 0:

            brick_count = math.ceil(
                wall_volume / effective_brick_volume
            )

            actual_brick_volume = (
                brick_count
                * brick_length / 1000
                * brick_width / 1000
                * brick_height / 1000
            )

            mortar_wet_volume = max(
                0,
                wall_volume - actual_brick_volume
            )

            mortar_dry_volume = mortar_wet_volume * 1.33

            st.success("Brickwork calculation completed!")

            st.metric(
                "Wall Volume",
                f"{wall_volume:.3f} m³"
            )

            st.metric(
                "Estimated Bricks",
                f"{brick_count:,} pieces"
            )

            st.metric(
                "Wet Mortar Volume",
                f"{mortar_wet_volume:.3f} m³"
            )

            st.metric(
                "Dry Mortar Volume",
                f"{mortar_dry_volume:.3f} m³"
            )

            st.caption(
                "Approximate estimate. Openings, breakage, "
                "bond pattern and actual site dimensions "
                "must be considered separately."
            )


# ---------------- TAB 3: AI ENGINEERING ASSISTANT ----------------

with tab3:

    st.header("AI Civil Engineering Assistant")

    st.write(
        "Ask questions about construction, estimation, "
        "materials and civil engineering."
    )

    if OpenAI is None:

        st.error(
            "OpenAI library is unavailable. "
            "Please check requirements.txt."
        )

    else:

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        for message in st.session_state.chat_messages:

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input(
            "Ask your civil engineering question..."
        )

        if prompt:

            st.session_state.chat_messages.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("user"):
                st.markdown(prompt)

            try:

                if "OPENAI_API_KEY" not in st.secrets:
                    st.error(
                        "OpenAI API key is missing. "
                        "Please configure Streamlit Secrets."
                    )

                else:

                    client = OpenAI(
                        api_key=st.secrets["OPENAI_API_KEY"]
                    )

                    messages = [
                        {
                            "role": "system",
                            "content": (
                                "You are CivilAI Nepal, a helpful "
                                "civil engineering assistant. "
                                "Explain calculations clearly. "
                                "Use SI units and NPR when relevant. "
                                "Do not invent Nepal government rates, "
                                "codes or standards. State assumptions "
                                "and advise professional verification "
                                "for structural safety."
                            )
                        }
                    ]

                    messages.extend(
                        st.session_state.chat_messages
                    )

                    with st.chat_message("assistant"):

                        with st.spinner("Thinking..."):

                            response = (
                                client.chat.completions.create(
                                    model="gpt-4.1-mini",
                                    messages=messages
                                )
                            )

                            answer = (
                                response.choices[0]
                                .message.content
                            )

                            st.markdown(answer)

                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": answer
                    })

            except Exception as error:

                st.error(
                    "AI response unavailable. Check API billing, "
                    "API key and internet connection."
                )

                st.caption(str(error))

        if st.button("Clear Chat"):
            st.session_state.chat_messages = []
            st.rerun()


# ---------------- TAB 4: BOQ GENERATOR ----------------

with tab4:

    render_boq_generator()


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "CivilAI Nepal | Engineering Technology for Nepal"
)

st.caption(
    "Educational assistance only. Verify all calculations, "
    "designs, quantities and rates with qualified professionals."
)
with tab5:
    render_cost_estimator()
