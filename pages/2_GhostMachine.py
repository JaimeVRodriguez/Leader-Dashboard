# pages/2_GhostMachine_Input.py
import streamlit as st
import datetime
import requests
import os

HF_MODEL_ID = 'google/flan-t5-base'
API_URL = f'https://api-inference.huggingface.co/models/{HF_MODEL_ID}'

try:
    HF_API_TOKEN = st.secrets['HUGGINGFACE_API_TOKEN']
except KeyError:
    HF_API_TOKEN = os.environ.get('HUGGINGFACE_API_TOKEN')
    if not HF_API_TOKEN:
        st.error('Hugging Face API Token not found')
        HF_API_TOKEN = None


# --- Helper Function for API Call ---
def query_hf_narrative_generation(prompt_text, api_token):
    """Sends a prompt to Hugging Face API for text generation."""
    if not api_token:
        return {"error": "API Token is missing."}

    headers = {"Authorization": f"Bearer {api_token}"}
    response_obj = None

    # Define payload for text generation
    # Adjust parameters as needed for desired output style
    payload = {
       "inputs": prompt_text,
        "parameters": {
            "max_new_tokens": 75,      # Max tokens to GENERATE (adjust length)
            "do_sample": True,         # Use sampling for more 'creative' output
            "temperature": 0.7,        # Controls randomness (lower = more focused)
            "top_p": 0.9,              # Nucleus sampling
        }
    }

    try:
        response_obj = requests.post(API_URL, headers=headers, json=payload, timeout=30) # Increased timeout slightly
        response_obj.raise_for_status()
        # Text generation response format is often different
        return response_obj.json()

    # --- Error handling remains largely the same, but check response format ---
    except requests.exceptions.HTTPError as http_err:
        st.error(f"API Request failed with HTTP Status Code: {http_err.response.status_code}")
        error_details = f"Status Code: {http_err.response.status_code}"
        try:
            error_json = http_err.response.json()
            hf_error = error_json.get("error")
            estimated_time = error_json.get("estimated_time")
            warnings = error_json.get("warnings") # Sometimes warnings are returned

            detail_parts = []
            if hf_error:
                detail_parts.append(f"API Error: {hf_error}")
            if estimated_time:
                 detail_parts.append(f"Model may be loading (~{estimated_time:.0f}s wait suggested).")
            if warnings:
                 detail_parts.append(f"Warnings: {warnings}")
            if not detail_parts: # If no specific fields, show raw error if simple
                 detail_parts.append(f"Response: {error_json}")

            error_details = f"{error_details}. {' '.join(detail_parts)}"

        except requests.exceptions.JSONDecodeError:
            error_details = f"{error_details}. Could not parse error response body."
        except Exception as parse_err:
             error_details = f"{error_details}. Error parsing response: {parse_err}"
        return {"error": error_details}

    except requests.exceptions.RequestException as req_err:
        st.error(f"API Request failed: {req_err}")
        return {"error": f"Network or request error: {req_err}"}

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return {"error": f"An unexpected programming error occurred: {e}"}


st.set_page_config(page_title="GhostMachine Input", layout="centered")
st.title("👻 GhostMachine Data Input Form")

# Ensure the session state key exists
if 'ghost_data' not in st.session_state:
    st.session_state['ghost_data'] = {
        'initiative': '', 
        'metric_value': 0.0, 
        'metric_delta': 0.0,
        'milestone': [], 
        'risk': '',
        'initiative_summary': ''

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
    # --- Summarization Section ---
    col1_sum, col2_sum = st.columns([0.7, 0.3])
    with col1_sum:
        st.write("**Initiative Narrative (Auto-Generated):**") # Label updated
        st.text_area(
            "Generated Narrative", # Label updated
            value=st.session_state['ghost_data'].get('initiative_summary', 'Click "Generate Narrative" ->'), # Default text updated
            height=125,
            key="initiative_summary_display",
            disabled=True
        )
    with col2_sum:
        st.write("&nbsp;")
        generate_summary_disabled = not HF_API_TOKEN
        # UPDATE Button Text and Help Text
        if st.form_submit_button("✨ Generate Narrative", help="Uses AI to write a narrative from the bullet points above", disabled=generate_summary_disabled): # Button text updated
            if initiative_input.strip():
                # --- Construct the Prompt ---
                prompt = f"""Write a short narrative (2-3 sentences) for a status update based on these points for the GhostMachine team: {initiative_input} """
                # --- End Prompt Construction ---

                # --- DEBUG ---
                print("-" * 20)
                print(f"DEBUG: Prompt Sent to API:\n{prompt}")
                print("-" * 20)
                # --- End DEBUG ---

                with st.spinner("Generating narrative..."): # Spinner text updated
                    # --- Call the NEW function with the PROMPT ---
                    # Pass the constructed 'prompt', not a payload dictionary
                    generation_result = query_hf_narrative_generation(prompt, HF_API_TOKEN)
                    # --- End Call ---

                    # --- DEBUG ---
                    print("-" * 20)
                    print(f"DEBUG: Raw API Response Received:\n{generation_result}")
                    print("-" * 20)
                    # --- End DEBUG ---

                    # --- Process the result for TEXT GENERATION ---
                    generated_narrative = None # Initialize
                    if isinstance(generation_result, list) and generation_result:
                        # EXPECTING format: [{'generated_text': '...'}]
                        generated_narrative = generation_result[0].get('generated_text')
                    elif isinstance(generation_result, dict) and "error" in generation_result:
                        # Error already handled within the function, but display here
                        st.error(f"Narrative generation failed: {generation_result['error']}")
                    else: # Handle other unexpected formats if needed
                        st.error("Narrative generation failed. Unexpected response format.")
                        st.write("API Response:", generation_result) # Debugging

                    # If successful, update state and show toast
                    if generated_narrative:
                         # --- DEBUG ---
                         print("-" * 20)
                         print(f"DEBUG: Extracted Narrative:\n{generated_narrative}")
                         print("-" * 20)
                         # --- End DEBUG ---
                         st.session_state['ghost_data']['initiative_summary'] = generated_narrative.strip() # Store the result
                         st.toast("Narrative generated!") # Toast updated
                         st.rerun()
                    elif not (isinstance(generation_result, dict) and "error" in generation_result):
                         # Clear previous narrative only if no specific error was already shown
                         st.session_state['ghost_data']['initiative_summary'] = ""

            else:
                st.warning("Please enter some initiative points to generate a narrative.")
                st.session_state['ghost_data']['initiative_summary'] = ""

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