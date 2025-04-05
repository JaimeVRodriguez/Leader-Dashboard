import streamlit as st
import requests

HF_MODEL_ID = 'google/flan-t5-base'
API_URL = f'https://api-inference.huggingface.co/models/{HF_MODEL_ID}'

# --- API HELPER FUNCTION ---
def query_hf_narrative_generation(prompt_text, api_token):
    """Sends a prompt to Hugging Face API for text generation."""
    if not api_token:
        return {"error": "API Token is missing."}

    headers = {"Authorization": f"Bearer {api_token}"}
    response_obj = None

    payload = {
       "inputs": prompt_text,
        "parameters": {
            "max_new_tokens": 75,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9,
        }
    }

    try:
        response_obj = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response_obj.raise_for_status()
        return response_obj.json()

    # --- ERROR HANDLING ---
    except requests.exceptions.HTTPError as http_err:
        st.error(f"API Request failed with HTTP Status Code: {http_err.response.status_code}")
        error_details = f"Status Code: {http_err.response.status_code}"
        try:
            error_json = http_err.response.json()
            hf_error = error_json.get("error")
            estimated_time = error_json.get("estimated_time")
            warnings = error_json.get("warnings")

            detail_parts = []
            if hf_error:
                detail_parts.append(f"API Error: {hf_error}")
            if estimated_time:
                 detail_parts.append(f"Model may be loading (~{estimated_time:.0f}s wait suggested).")
            if warnings:
                 detail_parts.append(f"Warnings: {warnings}")
            if not detail_parts: 
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