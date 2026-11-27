import math
import streamlit as st

from boq import render_boq_generator
from cost_estimator import render_cost_estimator


# ==========================================================
# CIVILAI NEPAL - MAIN APPLICATION
# ==========================================================

st.set_page_config(
    page_title="CivilAI Nepal",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# APPLICATION HEADER
# ==========================================================

st.title("🏗️ CivilAI Nepal")

st.subheader("Your AI Civil Engineering Assistant NP")

st.write(
    "Smart engineering tools for engineers, contractors "
    "and students in Nepal."
)

st.caption(
    "Engineering Technology for Nepal | CivilAI Nepal"
)


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #E6EDF7;
    }

    .info-card {
        background-color: rgba(80, 110, 150, 0.12);
        border: 1px solid rgba(150, 170, 200, 0.3);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(80, 110, 150, 0.10);
        border: 1px solid rgba(150, 170, 200, 0.2);
        padding: 12px;
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# FIVE SEPARATE APPLICATION TABS
# ==========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Concrete Calculator",
    "Brickwork Calculator",
    "AI Engineering Assistant",
    "BOQ Generator",
    "Cost Estimator"
])


# ==========================================================
# TAB 1 - CONCRETE CALCULATOR
# ==========================================================

with tab1:

    st.header("Concrete Volume Calculator")

    st.write(
        "Calculate concrete volume, cement, sand and "
        "aggregate requirements."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        length = st.number_input(
            "Length (m)",
            min_value=0.0,
            value=5.0,
            step=0.5,
            key="concrete_length"
        )

    with col2:
        width = st.number_input(
            "Width (m)",
            min_value=0.0,
            value=4.0,
            step=0.5,
            key="concrete_width"
        )

    with col3:
        depth = st.number_input(
            "Depth (m)",
            min_value=0.0,
            value=0.15,
            step=0.05,
            key="concrete_depth"
        )

    st.subheader("Concrete Mix Ratio")

    col1, col2, col3 = st.columns(3)

    with col1:
        cement_ratio = st.number_input(
            "Cement Ratio",
            min_value=1,
            value=1,
            step=1,
            key="cement_ratio"
        )

    with col2:
        sand_ratio = st.number_input(
            "Sand Ratio",
            min_value=0,
            value=1,
            step=1,
            key="sand_ratio"
        )

    with col3:
        aggregate_ratio = st.number_input(
            "Aggregate Ratio",
            min_value=0,
            value=2,
            step=1,
            key="aggregate_ratio"
        )

    dry_factor = st.number_input(
        "Dry Volume Factor",
        min_value=1.0,
        max_value=2.0,
        value=1.54,
        step=0.01,
        key="concrete_dry_factor"
    )

    cement_bag_volume = 0.0347

    if st.button(
        "Calculate Concrete",
        key="calculate_concrete",
        use_container_width=True
    ):

        if (
            length <= 0
            or width <= 0
            or depth <= 0
            or cement_ratio + sand_ratio + aggregate_ratio <= 0
        ):

            st.error("Please enter valid positive dimensions and mix ratios.")

        else:

            wet_volume = length * width * depth

            dry_volume = wet_volume * dry_factor

            total_ratio = (
                cement_ratio + sand_ratio + aggregate_ratio
            )

            cement_volume = (
                dry_volume * cement_ratio / total_ratio
            )

            sand_volume = (
                dry_volume * sand_ratio / total_ratio
            )

            aggregate_volume = (
                dry_volume * aggregate_ratio / total_ratio
            )

            cement_bags = cement_volume / cement_bag_volume

            st.divider()

            st.subheader("Concrete Calculation Results")

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Wet Concrete Volume",
                    f"{wet_volume:.3f} m³"
                )

                st.metric(
                    "Dry Material Volume",
                    f"{dry_volume:.3f} m³"
                )

                st.metric(
                    "Cement Required",
                    f"{cement_bags:.2f} bags"
                )

            with col2:

                st.metric(
                    "Sand Required",
                    f"{sand_volume:.3f} m³"
                )

                st.metric(
                    "Aggregate Required",
                    f"{aggregate_volume:.3f} m³"
                )

            st.info(
                "This is an approximate nominal-mix material estimate. "
                "Use an approved mix design and account for wastage, "
                "moisture and site conditions before construction."
            )


# ==========================================================
# TAB 2 - BRICKWORK CALCULATOR
# ==========================================================

with tab2:

    st.header("Brickwork Quantity Calculator")

    st.write(
        "Estimate bricks, mortar, cement and sand "
        "for masonry work."
    )

    st.subheader("Wall Dimensions")

    col1, col2, col3 = st.columns(3)

    with col1:

        wall_length = st.number_input(
            "Wall Length (m)",
            min_value=0.0,
            value=5.0,
            step=0.5,
            key="brick_wall_length"
        )

    with col2:

        wall_height = st.number_input(
            "Wall Height (m)",
            min_value=0.0,
            value=3.0,
            step=0.5,
            key="brick_wall_height"
        )

    with col3:

        wall_thickness = st.number_input(
            "Wall Thickness (m)",
            min_value=0.0,
            value=0.23,
            step=0.01,
            key="brick_wall_thickness"
        )

    st.subheader("Brick Dimensions")

    col1, col2, col3 = st.columns(3)

    with col1:

        brick_length = st.number_input(
            "Brick Length (mm)",
            min_value=1,
            value=190,
            key="brick_length"
        )

    with col2:

        brick_width = st.number_input(
            "Brick Width (mm)",
            min_value=1,
            value=90,
            key="brick_width"
        )

    with col3:

        brick_height = st.number_input(
            "Brick Height (mm)",
            min_value=1,
            value=90,
            key="brick_height"
        )

    mortar_joint = st.number_input(
        "Mortar Joint Thickness (mm)",
        min_value=0,
        value=10,
        key="mortar_joint"
    )

    st.subheader("Mortar Mix Ratio")

    col1, col2 = st.columns(2)

    with col1:

        mortar_cement = st.number_input(
            "Cement Ratio",
            min_value=1,
            value=1,
            key="mortar_cement"
        )

    with col2:

        mortar_sand = st.number_input(
            "Sand Ratio",
            min_value=1,
            value=6,
            key="mortar_sand"
        )

    mortar_dry_factor = st.number_input(
        "Mortar Dry Volume Factor",
        min_value=1.0,
        max_value=2.0,
        value=1.33,
        step=0.01,
        key="mortar_dry_factor"
    )

    if st.button(
        "Calculate Brickwork",
        key="calculate_brickwork",
        use_container_width=True
    ):

        if (
            wall_length <= 0
            or wall_height <= 0
            or wall_thickness <= 0
            or mortar_cement + mortar_sand <= 0
        ):

            st.error("Please enter valid wall dimensions and mix ratios.")

        else:

            wall_volume = (
                wall_length * wall_height * wall_thickness
            )

            actual_brick_volume = (
                (brick_length / 1000)
                * (brick_width / 1000)
                * (brick_height / 1000)
            )

            effective_brick_volume = (
                (brick_length + mortar_joint) / 1000
                * (brick_width + mortar_joint) / 1000
                * (brick_height + mortar_joint) / 1000
            )

            if effective_brick_volume <= 0:

                st.error("Invalid brick dimensions.")

            else:

                brick_count = math.ceil(
                    wall_volume / effective_brick_volume
                )

                total_actual_brick_volume = (
                    brick_count * actual_brick_volume
                )

                mortar_wet_volume = max(
                    0,
                    wall_volume - total_actual_brick_volume
                )

                mortar_dry_volume = (
                    mortar_wet_volume * mortar_dry_factor
                )

                total_mortar_ratio = (
                    mortar_cement + mortar_sand
                )

                cement_volume = (
                    mortar_dry_volume
                    * mortar_cement
                    / total_mortar_ratio
                )

                sand_volume = (
                    mortar_dry_volume
                    * mortar_sand
                    / total_mortar_ratio
                )

                cement_bags = cement_volume / 0.0347

                st.divider()

                st.subheader("Brickwork Results")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Wall Volume",
                        f"{wall_volume:.3f} m³"
                    )

                    st.metric(
                        "Estimated Bricks",
                        f"{brick_count:,}"
                    )

                    st.metric(
                        "Wet Mortar Volume",
                        f"{mortar_wet_volume:.3f} m³"
                    )

                with col2:

                    st.metric(
                        "Cement Required",
                        f"{cement_bags:.2f} bags"
                    )

                    st.metric(
                        "Sand Required",
                        f"{sand_volume:.3f} m³"
                    )

                    st.metric(
                        "Dry Mortar Volume",
                        f"{mortar_dry_volume:.3f} m³"
                    )

                st.warning(
                    "Approximate calculation only. Openings, bond pattern, "
                    "breakage, wastage and actual masonry specifications "
                    "must be considered separately."
                )


# ==========================================================
# TAB 3 - AI ENGINEERING ASSISTANT
# ==========================================================

with tab3:

    st.header("AI Engineering Assistant")

    st.write(
        "Ask questions about civil engineering, construction, "
        "materials, estimation and engineering concepts."
    )

    st.info(
        "AI responses require a working OpenAI API key and "
        "available API billing credits."
    )

    try:

        from openai import OpenAI

        api_key = st.secrets.get("OPENAI_API_KEY", "")

    except ImportError:

        OpenAI = None
        api_key = ""

    except Exception:

        OpenAI = None
        api_key = ""

    if "civilai_chat_history" not in st.session_state:

        st.session_state.civilai_chat_history = []

    if st.button(
        "Clear Chat History",
        key="clear_civilai_chat"
    ):

        st.session_state.civilai_chat_history = []
        st.rerun()

    for message in st.session_state.civilai_chat_history:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    question = st.chat_input(
        "Ask your civil engineering question..."
    )

    if question:

        st.session_state.civilai_chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):

            st.markdown(question)

        if OpenAI is None:

            st.error(
                "The OpenAI Python package is unavailable. "
                "Check your requirements.txt."
            )

        elif not api_key:

            st.error(
                "API key not found. Add OPENAI_API_KEY "
                "in Streamlit Secrets."
            )

        else:

            try:

                client = OpenAI(api_key=api_key)

                with st.chat_message("assistant"):

                    with st.spinner("CivilAI is thinking..."):

                        response = client.chat.completions.create(
                            model="gpt-4.1-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are CivilAI Nepal, a helpful "
                                        "civil engineering assistant. "
                                        "Explain engineering topics clearly. "
                                        "Use SI units and Nepal context "
                                        "where relevant. Never replace "
                                        "professional engineering judgment "
                                        "or approved structural designs."
                                    )
                                }
                            ] + st.session_state.civilai_chat_history,
                            temperature=0.3
                        )

                        answer = (
                            response.choices[0].message.content
                        )

                        st.markdown(answer)

                st.session_state.civilai_chat_history.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:

                st.error(
                    "The AI service could not respond. "
                    "Check API billing, key permissions and connectivity."
                )

                st.caption(
                    f"Technical information: {str(error)[:300]}"
                )


# ==========================================================
# TAB 4 - BOQ GENERATOR
# ==========================================================

with tab4:

    render_boq_generator()


# ==========================================================
# TAB 5 - PROJECT COST ESTIMATOR
# ==========================================================

with tab5:

    render_cost_estimator()


# ==========================================================
# APPLICATION FOOTER
# ==========================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:10px;">
        <b>CivilAI Nepal</b><br>
        Engineering Technology for Nepal<br>
        <small>
        Professional Civil Engineering Tools
        </small>
    </div>
    """,
    unsafe_allow_html=True
)
