# app.py
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Division Sync",
    page_icon="📊",
    layout="wide"
)

DB_URL = st.secrets.get('DATABASE_URL')
if not DB_URL:
    st.error('🚨 DATABASE_URL not found in Streamlit Secrets! Cannot connect to database.')
    st.stop()

try:
    conn = st.connection('postgres', type='sql', url=DB_URL)
except Exception as e:
    st.error(f'🚨 Failed to connect to the database: {e}')
    st.stop()

st.title("AI Division Leader Sync Dashboard")
st.caption(f"Data shown reflects the current session. Last updated: {st.query_params.get('updated', 'N/A')}")

# --- Initialize Session State ---
# Initialize if they don't exist yet
if 'vortex_data' not in st.session_state:
    st.session_state['vortex_data'] = {
        'update_bullets': "Default Vortex Update",
        'metric_value': 0.0,
        'metric_delta': 0.0,
        'milestone': [],
        'risk': "No risks entered yet.",
        'update_summary': ''
    }

if 'ghostmachine_data' not in st.session_state:
    st.session_state['ghostmachine_data'] = {
        'update_bullets': "Default GhostMachine Initiative",
        'metric_value': 0.0,
        'metric_delta': 0.0,
        'milestone': [],
        'risk': "No risks entered yet.",
        'update_summary': ''
    }

if 'platform_data' not in st.session_state:
    st.session_state['platform_data'] = {
        'initiative': 'Default Platform Initiative',
        'metric_value': 0.0,
        'metric_delta': 0.0,
        'milestone': [],
        'risk': 'No risks entered yet.'
    }

# --- Display Area ---
st.markdown("---")

# --- Platform Dashboard Section ---
st.header('Platform')
with st.expander('Project Status', expanded=False):
    p_data = st.session_state['platform_data']

    row1_platform = st.columns(2)
    row2_platform = st.columns(2)

    with row1_platform[0]:
        tile1_p = st.container(height=250, border=True)
        tile1_p.subheader("Launch Initiatives")
        tile1_p.write(p_data.get('initiative', 'N/A'))

    with row1_platform[1]:
        tile2_p = st.container(height=250, border=True)
        tile2_p.subheader('Performance Metrics')
        tile2_p.metric('Key Metric',
                       value=p_data.get('metric_value', 0.0),
                       delta=p_data.get('metric_delta', 0.0))

    with row2_platform[0]:
        tile3_p = st.container(height=250, border=True)
        tile3_p.subheader("📅 Upcoming Milestones")
        milestones_list = p_data.get('milestones', [])
        if milestones_list:
            sorted_milestones = sorted(milestones_list, key=lambda m: m['date'])
            for i, m in enumerate(sorted_milestones):
                date_str = m['date'].strftime('%Y-%m-%d')
                tile3_p.write(f"**{date_str}:** {m['desc']}")
        else:
            tile3_p.write('No milesones entered yet.')

    with row2_platform[1]:
        title4_p = st.container(height=250, border=True)
        title4_p.subheader("❓ Blockers / Risks")
        title4_p.write(p_data.get('risk', 'N/A'))



# --- Vortex Dashboard Section ---
st.header("Vortex")
with st.expander("Project Status", expanded=False):
    v_data = st.session_state['vortex_data'] # Shortcut

    row1_vortex = st.columns(2)
    row2_vortex = st.columns(2)

    with row1_vortex[0]:
        tile1_v = st.container(height=250, border=True)
        tile1_v.subheader("🚀 Launch Initiatives")
        tile1_v.write(v_data.get('update_summary', 'N/A'))

    with row1_vortex[1]:
        tile2_v = st.container(height=250, border=True)
        tile2_v.subheader("📊 Performance Metrics")
        tile2_v.metric("Key Metric",
                    value=v_data.get('metric_value', 0.0),
                    delta=v_data.get('metric_delta', 0.0))

    with row2_vortex[0]:
        tile3_v = st.container(height=250, border=True)
        tile3_v.subheader("📅 Upcoming Milestones")
        milestones_list = v_data.get('milestones', []) # Get the list
        if milestones_list:
            # Sort by date before displaying (optional)
            sorted_milestones = sorted(milestones_list, key=lambda m: m['date'])
            for i, m in enumerate(sorted_milestones):
                # Use strftime for consistent date formatting
                date_str = m['date'].strftime('%Y-%m-%d') # Or '%m/%d/%Y'
                tile3_v.write(f"**{date_str}:** {m['desc']}")
        else:
            tile3_v.write("No milestones entered yet.")

    with row2_vortex[1]:
        tile4_v = st.container(height=250, border=True)
        tile4_v.subheader("❓ Blockers / Risks")
        tile4_v.write(v_data.get('risk', 'N/A'))


# --- GhostMachine Dashboard Section ---
st.header("GhostMachine")
with st.expander("Project Status", expanded=False):
    g_data = st.session_state['ghostmachine_data'] # Shortcut

    row1_ghost = st.columns(2)
    row2_ghost = st.columns(2)

    with row1_ghost[0]:
        tile1_g = st.container(height=250, border=True)
        tile1_g.subheader("🚀 Project Updates")
        tile1_g.write(g_data.get('update_summary', 'N/A'))

    with row1_ghost[1]:
        tile2_g = st.container(height=250, border=True)
        tile2_g.subheader("📊 Performance Metrics")
        tile2_g.metric("Key Metric",
                    value=g_data.get('metric_value', 0.0),
                    delta=g_data.get('metric_delta', 0.0))

    with row2_ghost[0]:
        tile3_g = st.container(height=250, border=True)
        tile3_g.subheader("📅 Upcoming Milestones")
        milestones_list = g_data.get('milestones', []) # Get the list
        if milestones_list:
            sorted_milestones = sorted(milestones_list, key=lambda m: m['date'])
            for i, m in enumerate(sorted_milestones):
                date_str = m['date'].strftime('%Y-%m-%d')
                tile3_g.write(f"**{date_str}:** {m['desc']}")
        else:
            tile3_g.write("No milestones entered yet.")

    with row2_ghost[1]:
        tile4_g = st.container(height=250, border=True)
        tile4_g.subheader("❓ Blockers / Risks")
        tile4_g.write(g_data.get('risk', 'N/A'))


# --- Platform Dashboard Section ---
st.header('Platform')
with st.expander('Project Status', expanded=False):
    p_data = st.session_state['platform_data']

    row1_platform = st.columns(2)
    row2_platform = st.columns(2)

    with row1_platform[0]:
        tile1_p = st.container(height=250, border=True)
        tile1_p.subheader("Launch Initiatives")
        tile1_p.write(p_data.get('initiative', 'N/A'))

    with row1_platform[1]:
        tile2_p = st.container(height=250, border=True)
        tile2_p.subheader('Performance Metrics')
        tile2_p.metric('Key Metric',
                       value=p_data.get('metric_value', 0.0),
                       delta=p_data.get('metric_delta', 0.0))

st.sidebar.success("Select a project data entry page.")