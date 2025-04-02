# pages/2_GhostMachine_Input.py
import streamlit as st
import datetime

st.set_page_config(page_title="GhostMachine Input", layout="centered")
st.title("👻 GhostMachine Data Input Form")

# Ensure the session state key exists
if 'ghost_data' not in st.session_state:
    st.session_state['ghost_data'] = {
        'initiative': "", 
        'metric_value': 0.0, 
        'metric_delta': 0.0,
        'milestone': [], 
        'risk': ""
    }
elif 'milestones' not in st.session_state.ghost_data or not isinstance(st.session_state.ghost_data['milestones'], list):
    st.session_state.ghost_data['milestones'] = []

st.markdown("Enter the latest information for the **GhostMachine** project below.")

# Use a form
with st.form("ghost_form"):
    st.subheader("Input Fields")
    initiative_input = st.text_area(
        "🚀 Launch Initiatives",
        value=st.session_state['ghost_data'].get('initiative', ''),
        height=100
    )
    metric_val_input = st.number_input(
        "📊 Key Metric Value",
        value=st.session_state['ghost_data'].get('metric_value', 0.0),
        format="%.2f"
    )
    metric_delta_input = st.number_input(
        "📈 Key Metric Delta (Change)",
        value=st.session_state['ghost_data'].get('metric_delta', 0.0),
        format="%.2f"
    )
    risk_input = st.text_area(
        "❓ Open Questions / Risks",
        value=st.session_state['ghost_data'].get('risk', ''),
        height=150
    )

    # Submit button
    submitted = st.form_submit_button("Save GhostMachine Data")

    if submitted:
        # Update session state
        st.session_state['ghost_data']['initiative'] = initiative_input
        st.session_state['ghost_data']['metric_value'] = metric_val_input
        st.session_state['ghost_data']['metric_delta'] = metric_delta_input
        st.session_state['ghost_data']['risk'] = risk_input

        st.success("GhostMachine data updated successfully!")
        st.toast("Data saved!")
        # st.query_params["updated"] = str(datetime.datetime.now())



# --- Milestone Management Section (Below the form) ---
st.markdown("---")
st.subheader("📅 Upcoming Milestones Management")

# Get the current list
milestone_list = st.session_state.ghost_data['milestones']

# --- Display Existing Milestones with Remove Buttons ---
st.write("**Current Milestones:**")
if not milestone_list:
    st.caption("No milestones added yet.")

# Sort by date before displaying
sorted_milestones = sorted(milestone_list, key=lambda m: m['date'])

indices_to_remove = []
for i, m in enumerate(sorted_milestones):
    col1, col2, col3 = st.columns([0.25, 0.6, 0.15])
    # Find the original index in the unsorted list to ensure correct removal
    original_index = milestone_list.index(m)
    with col1:
        st.write(m['date'].strftime('%Y-%m-%d')) # Display date
    with col2:
        st.write(m['desc']) # Display description
    with col3:
        # Use the original index in the key and for removal logic
        if st.button("Remove", key=f"remove_m_{original_index}", help=f"Remove milestone: {m['desc']}"):
            indices_to_remove.append(original_index)

# Remove items outside the loop (modify list while iterating is bad)
if indices_to_remove:
    # Remove in reverse order of original indices to avoid messing up subsequent indices
    indices_to_remove.sort(reverse=True)
    for index in indices_to_remove:
         st.session_state.ghost_data['milestones'].pop(index)
    st.toast("Milestone(s) removed.")
    st.rerun() # Rerun to update the display immediately



# --- Input for New Milestone ---
st.write("**Add New Milestone:**")
col_date, col_desc, col_add = st.columns([0.3, 0.55, 0.15])

with col_date:
    # Use session state to potentially preserve input if page reruns unexpectedly
    if 'new_m_date_gm' not in st.session_state:
        st.session_state.new_m_date_gm = datetime.date.today()
    new_milestone_date_gm = st.date_input("Date", value=st.session_state.new_m_date_gm, key="new_milestone_date_input_gm")

with col_desc:
    if 'new_m_desc_gm' not in st.session_state:
        st.session_state.new_m_desc_gm = ""
    new_milestone_desc_gm = st.text_input("Description", value=st.session_state.new_m_desc_gm, key="new_milestone_desc_input_gm", placeholder="Enter milestone detail")

with col_add:
    st.write(" &nbsp; ") # Add space for alignment
    if st.button("Add", key="add_milestone_button_gm"):
        if new_milestone_desc_gm: # Only add if description is not empty
            st.session_state.ghost_data['milestones'].append({
                'date': new_milestone_date_gm,
                'desc': new_milestone_desc_gm
            })
            # Clear the input fields by resetting their session state keys
            st.session_state.new_m_date_gm = datetime.date.today() # Reset date
            st.session_state.new_m_desc_gm = "" # Reset description
            st.success(f"Added milestone: {new_milestone_desc_gm}")
            st.toast("Milestone added!")
            st.rerun() # Rerun script to update the list display and clear inputs
        else:
            st.warning("Please enter a description for the milestone.")