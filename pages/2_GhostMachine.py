import streamlit as st
import datetime
import os
from hf_utils import query_hf_narrative_generation

st.set_page_config(page_title="GhostMachine Input", layout="centered")

try:
    HF_API_TOKEN = st.secrets['HUGGINGFACE_API_TOKEN']
except KeyError:
    HF_API_TOKEN = os.environ.get('HUGGINGFACE_API_TOKEN')
    if not HF_API_TOKEN:
        st.error('Hugging Face API Token not found')
        HF_API_TOKEN = None


st.title("👻 GhostMachine Data Input Form")

if 'ghostmachine_data' not in st.session_state:
    st.session_state['ghostmachine_data'] = {
        'update_bullets': '', 
        'metric_value': 0.0, 
        'metric_delta': 0.0,
        'milestone': [], 
        'risk': '',
        'update_summary': ''

    }
elif 'milestones' not in st.session_state.ghostmachine_data or not isinstance(st.session_state.ghostmachine_data['milestones'], list):
    st.session_state.ghostmachine_data['milestones'] = []

st.markdown("Enter the latest information for the **GhostMachine** project below.")

# --- INPUT FORM ---
with st.form("ghostmachine_form"):
    st.subheader("Input Fields")
    update_input = st.text_area(
        "🚀 Projects Updates",
        value=st.session_state['ghostmachine_data'].get('update_bullets', ''),
        height=100
    )
    # --- SUMMARIZATION SECTION ---
    col1_sum, col2_sum = st.columns([0.7, 0.3])
    with col1_sum:
        st.write("**Project Update Narrative (Auto-Generated):**")
        st.text_area(
            "Generated Update",
            value=st.session_state['ghostmachine_data'].get('update_summary', 'Click "Generate Update" ->'),
            height=125,
            key="update_summary_display",
            disabled=True
        )
    with col2_sum:
        st.write("&nbsp;")
        generate_summary_disabled = not HF_API_TOKEN
        if st.form_submit_button("✨ Generate Update", help="Uses AI to write a narrative from the bullet points above", disabled=generate_summary_disabled):
            if update_input.strip():
                prompt = f"""Write a short narrative for a status update based on these points for the GhostMachine team: {update_input} """

                with st.spinner("Generating update..."):
                    generation_result = query_hf_narrative_generation(prompt, HF_API_TOKEN)

                    generated_update = None
                    if isinstance(generation_result, list) and generation_result:
                        generated_update = generation_result[0].get('generated_text')
                    elif isinstance(generation_result, dict) and "error" in generation_result:
                        st.error(f"Update generation failed: {generation_result['error']}")
                    else:
                        st.error("Update generation failed. Unexpected response format.")
                        st.write("API Response:", generation_result)

                    if generated_update:
                         st.session_state['ghostmachine_data']['update_summary'] = generated_update.strip() 
                         st.toast("Update generated!") 
                         st.rerun()
                    elif not (isinstance(generation_result, dict) and "error" in generation_result):
                         st.session_state['ghostmachine_data']['update_summary'] = ""

            else:
                st.warning("Please enter some update points to generate a narrative.")
                st.session_state['ghostmachine_data']['update_summary'] = ''

    metric_val_input = st.number_input(
        "📊 Key Metric Value",
        value=st.session_state['ghostmachine_data'].get('metric_value', 0.0),
        format="%.2f"
    )
    metric_delta_input = st.number_input(
        "📈 Key Metric Delta (Change)",
        value=st.session_state['ghostmachine_data'].get('metric_delta', 0.0),
        format="%.2f"
    )
    risk_input = st.text_area(
        "❓ Open Questions / Risks",
        value=st.session_state['ghostmachine_data'].get('risk', ''),
        height=150
    )

    submitted = st.form_submit_button("Save GhostMachine Data")

    if submitted:
        st.session_state['ghostmachine_data']['update_bullets'] = update_input
        st.session_state['ghostmachine_data']['metric_value'] = metric_val_input
        st.session_state['ghostmachine_data']['metric_delta'] = metric_delta_input
        st.session_state['ghostmachine_data']['risk'] = risk_input

        st.success("GhostMachine data updated successfully!")
        st.toast("Data saved!")


# --- MILESTIONE MANAGEMENT ---
st.markdown("---")
st.subheader("📅 Upcoming Milestones Management")

milestone_list = st.session_state.ghostmachine_data['milestones']

st.write("**Current Milestones:**")
if not milestone_list:
    st.caption("No milestones added yet.")

sorted_milestones = sorted(milestone_list, key=lambda m: m['date'])

indices_to_remove = []
for i, m in enumerate(sorted_milestones):
    col1, col2, col3 = st.columns([0.25, 0.6, 0.15])
    original_index = milestone_list.index(m)
    with col1:
        st.write(m['date'].strftime('%Y-%m-%d'))
    with col2:
        st.write(m['desc'])
    with col3:
        if st.button("Remove", key=f"remove_m_{original_index}", help=f"Remove milestone: {m['desc']}"):
            indices_to_remove.append(original_index)

if indices_to_remove:
    indices_to_remove.sort(reverse=True)
    for index in indices_to_remove:
         st.session_state.ghostmachine_data['milestones'].pop(index)
    st.toast("Milestone(s) removed.")
    st.rerun()

st.write("**Add New Milestone:**")
col_date, col_desc, col_add = st.columns([0.3, 0.55, 0.15])

with col_date:
    if 'new_m_date_gm' not in st.session_state:
        st.session_state.new_m_date_gm = datetime.date.today()
    new_milestone_date_gm = st.date_input("Date", value=st.session_state.new_m_date_gm, key="new_milestone_date_input_gm")

with col_desc:
    if 'new_m_desc_gm' not in st.session_state:
        st.session_state.new_m_desc_gm = ""
    new_milestone_desc_gm = st.text_input("Description", value=st.session_state.new_m_desc_gm, key="new_milestone_desc_input_gm", placeholder="Enter milestone detail")

with col_add:
    st.write(" &nbsp; ") 
    if st.button("Add", key="add_milestone_button_gm"):
        if new_milestone_desc_gm:
            st.session_state.ghostmachine_data['milestones'].append({
                'date': new_milestone_date_gm,
                'desc': new_milestone_desc_gm
            })
            st.session_state.new_m_date_gm = datetime.date.today() 
            st.session_state.new_m_desc_gm = "" 
            st.success(f"Added milestone: {new_milestone_desc_gm}")
            st.toast("Milestone added!")
            st.rerun()
        else:
            st.warning("Please enter a description for the milestone.")