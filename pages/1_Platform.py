import streamlit as st
import datetime # To add a timestamp

st.set_page_config(page_title="Vortex Input", layout="centered")
st.title("🖥️ Platform Data Input Form")

if 'platform_data' not in st.session_state:
    st.session_state['platform_data'] = {
        'initiative': '',
        'metric_value': 0.0,
        'metric_delta': 0.0,
        'milestone': [],
        'risk': ''
    }
elif 'milestones' not in st.session_state.platform_data or not isinstance(st.session_state.platform_data['milestones'], list):
    st.session_state.platform_data['milestones'] = []

st.markdown("Enter the latest information for the **Platform** project below.")

with st.form('platform_form'):
    st.subheader('Input Fields')
    initiative_input = st.text_area(
        "🚀 Launch Initiatives",
        value=st.session_state['platform_data'].get('initiative', ''),
        height=100
    )
    metric_val_input = st.number_input(
        "📊 Key Metric Value",
        value=st.session_state['platform_data'].get('metric_value', 0.0),
        format='%.2f'
    )
    metric_delta_input = st.number_input(
        "📈 Key Metric Delta (Change)",
        value=st.session_state['platform_data'].get('metric_delta', 0.0),
        format="%.2f"
    )
    risk_input = st.text_area(
        "❓ Open Questions / Risks",
        value=st.session_state['platform_data'].get('risk', ''),
        height=150
    )

    submitted = st.form_submit_button('Save Platform Data')