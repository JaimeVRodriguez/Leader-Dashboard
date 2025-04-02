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

