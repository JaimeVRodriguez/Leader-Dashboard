import streamlit as st
import datetime
import os
import json
import sqlalchemy
from hf_utils import query_hf_narrative_generation

st.set_page_config(page_title="GhostMachine Input", layout="centered")

# --- DATABASE CONNECTION ---
DB_URL = st.secrets.get("DATABASE_URL")
if not DB_URL:
    st.error("🚨 DATABASE_URL not found in Streamlit Secrets! Cannot connect to database.")
    st.stop()

try:
    conn = st.connection('postgres', type='sql', url=DB_URL)
except Exception as e:
    st.error(f"🚨 Failed to connect to the database: {e}")
    st.stop()

PROJECT_ID = 'ghostmachine_main'


# --- API CONNECTION ---
try:
    HF_API_TOKEN = st.secrets['HUGGINGFACE_API_TOKEN']
except KeyError:
    HF_API_TOKEN = os.environ.get('HUGGINGFACE_API_TOKEN')
    if not HF_API_TOKEN:
        st.error('Hugging Face API Token not found')
        HF_API_TOKEN = None

# --- LOAD DATA FUNCTION ---
def load_data_from_db():
    print(f"Attempting to load data for {PROJECT_ID}...")
    df = None
    try:
        query_string = """
            SELECT
                project_id, update_bullets, metric_value, metric_delta,
                milestones, risk, update_summary, last_updated
            FROM ghostmachine_data
            WHERE project_id = :proj_id
        """
        params = {'proj_id': PROJECT_ID}


        df = conn.query(query_string, params=params, ttl=0)

        if df is not None and not df.empty:
            project_data = df.iloc[0].to_dict()
            print(f"Raw data found: {project_data}")

            milestones = project_data.get('milestones')
            if milestones is None or milestones == {}:
                project_data['milestones'] = []
            elif isinstance(milestones, str):
                try: 
                    project_data['milestones'] = json.loads(milestones)
                except json.JSONDecodeError:
                    project_data['milestones'] = []

            defaults = {
                'update_bullets': '', 
                'metric_value': 0.0, 
                'metric_delta': 0.0,
                'risk': '', 
                'update_summary': '', 
                'milestones': []
            }
            session_data = {**defaults, **project_data}
            session_data['project_id'] = PROJECT_ID

            st.session_state['ghostmachine_data'] = session_data

        else:
            st.session_state['ghostmachine_data'] = {
                'project_id': PROJECT_ID, 
                'update_bullets': '', 
                'metric_value': 0.0,
                'metric_delta': 0.0, 
                'milestones': [], 
                'risk': '', 
                'update_summary': ''
            }

    except Exception as e:
        st.error(f"🚨 Error during data loading: {e}")
        import traceback
        traceback.print_exc()
        if 'ghostmachine_data' not in st.session_state:
             st.session_state['ghostmachine_data'] = {
                'project_id': PROJECT_ID, 
                'update_bullets': '', 
                'metric_value': 0.0,
                'metric_delta': 0.0, 
                'milestones': [], 
                'risk': '', 
                'update_summary': ''
            }

# --- LOAD DATA---
if 'ghostmachine_data' not in st.session_state:
    load_data_from_db()


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
        current_data = {
            'project_id': PROJECT_ID,
            'update_bullets': update_input,
            'metric_value': metric_val_input,
            'metric_delta': metric_delta_input,
            'milestones': st.session_state.ghostmachine_data.get('milestones', []),
            'risk': risk_input,
            'update_summary': st.session_state.ghostmachine_data.get('update_summary', ''),
            'last_updated': datetime.datetime.now(datetime.timezone.utc)
        }

        st.session_state['ghostmachine_data'] = current_data.copy()

        # --- SAVE TO DATABASE ---
        try:
            with conn.session as s: 
                sql_upsert = sqlalchemy.text("""
                    INSERT INTO ghostmachine_data (
                        project_id, update_bullets, metric_value, metric_delta, milestones, risk, update_summary, last_updated
                    ) VALUES (
                        :pid, :upbu, :mv, :md, :ms, :rsk, :upsum, :ts
                    )
                    ON CONFLICT (project_id) DO UPDATE SET
                        update_bullets = EXCLUDED.update_bullets,
                        metric_value = EXCLUDED.metric_value,
                        metric_delta = EXCLUDED.metric_delta,
                        milestones = EXCLUDED.milestones,
                        risk = EXCLUDED.risk,
                        update_summary = EXCLUDED.update_summary,
                        last_updated = EXCLUDED.last_updated;
                """)
                params = {
                    'pid': current_data['project_id'],
                    'upbu': current_data['update_bullets'],
                    'mv': current_data['metric_value'],
                    'md': current_data['metric_delta'],
                    'ms': current_data['milestones'],
                    'rsk': current_data['risk'],
                    'upsum': current_data['update_summary'],
                    'ts': current_data['last_updated']
                }
                s.execute(sql_upsert, params)
                s.commit()
            st.success("GhostMachine data saved successfully!")
            st.toast("Data saved!")
        except Exception as e:
            st.error(f"🚨 Failed to save data to PostgreSQL: {e}")

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