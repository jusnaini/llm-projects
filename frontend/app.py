import streamlit as st
import requests
import json
import uuid
from datetime import datetime
from PIL import Image
import io

API_URL = "http://localhost:8000/extract/"

st.set_page_config(page_title="Aircraft Journey Form Extractor", layout="centered")

st.title("🛫 Aircraft Journey Form Extractor")
st.write("Upload a scanned aircraft journey form to extract structured information automatically.")

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
    st.session_state.ocr_text = None
if 'edited_data' not in st.session_state:
    st.session_state.edited_data = None
if 'upload_id' not in st.session_state:
    st.session_state.upload_id = None
if 'uploaded_file_data' not in st.session_state:
    st.session_state.uploaded_file_data = None

uploaded_file = st.file_uploader("Upload Form (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption=f"📸 Preview: {uploaded_file.name}", width="stretch")

    uploaded_file.seek(0)

    # Store file data in session state
    if st.session_state.uploaded_file_data is None:
        uploaded_file.seek(0)
        st.session_state.uploaded_file_data = {
            'name': uploaded_file.name,
            'type': uploaded_file.type,
            'data': uploaded_file.read()
        }
        uploaded_file.seek(0)

    if st.button("🔍 Extract Form Data", type="primary", width="stretch"):
        with st.spinner("Extracting data... This may take a moment ⏳"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                response = requests.post(API_URL, files=files, timeout=30)

                if response.status_code == 200:
                    res = response.json()
                    if res.get("status") == "success":
                        st.success("✅ Extraction complete!")

                        extracted_data = res["data"]
                        ocr_text = res["ocr_text"]

                        # Generate Upload ID if missing
                        if not extracted_data.get("Upload_ID"):
                            extracted_data["Upload_ID"] = (
                                f"AJ-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
                            )

                        # Store state
                        st.session_state.extracted_data = extracted_data
                        st.session_state.edited_data = extracted_data.copy()
                        st.session_state.upload_id = extracted_data["Upload_ID"]
                        st.session_state.ocr_text = ocr_text

                    else:
                        st.error(f"❌ Extraction Error: {res.get('message', 'Unknown error')}")
                else:
                    st.error(f"❌ API Error: Status code {response.status_code}")

            except requests.exceptions.RequestException:
                st.error("❌ Could not connect to backend at http://localhost:8000")
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON response from backend")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")

# --------------------------
# Display extracted data
# --------------------------
if st.session_state.extracted_data:
    extracted_data = st.session_state.extracted_data
    upload_id = st.session_state.upload_id
    ocr_text = st.session_state.ocr_text

    st.write("### 📋 Extracted Data")
    st.json(extracted_data)

    st.write("### ✏️ Review & Edit Extracted Data")

    edited = {}
    for key, val in st.session_state.edited_data.items():
        edited[key] = st.text_input(
            key,
            value=str(val) if val is not None else "",
            key=f"input_{key}",
            placeholder=f"Enter {key}"
        )

    st.session_state.edited_data = edited

    st.write("---")
    col1, col2 = st.columns([1, 1])

    # ---------------------------------
    # SAVE BUTTON (Extracted + Edited)
    # ---------------------------------
    with col1:
        if st.button("💾 Save All Data", type="primary", width="stretch"):
            with st.spinner("Saving..."):
                try:
                    extracted_version = {
                        **st.session_state.extracted_data,
                        "version": "extracted",
                        "saved_at": datetime.now().isoformat(),
                        "file_name": st.session_state.uploaded_file_data.get("name")
                    }
                    edited_version = {
                        **st.session_state.edited_data,
                        "version": "edited",
                        "saved_at": datetime.now().isoformat(),
                        "file_name": st.session_state.uploaded_file_data.get("name")
                    }

                    with st.expander("🔍 Debug: Data being sent"):
                        st.json(extracted_version)
                        st.json(edited_version)

                    # Save extracted
                    res_extracted = requests.post(
                        "http://localhost:8000/save-extracted/",
                        json=extracted_version,
                        timeout=10
                    )

                    # Save edited
                    res_edited = requests.post(
                        "http://localhost:8000/save-edited/",
                        json=edited_version,
                        timeout=10
                    )

                    # Evaluate OCR
                    res_eval = requests.post(
                        "http://localhost:8000/evaluate-ocr/",
                        json={
                            "extracted": extracted_version,
                            "edited": edited_version,
                            "ocr_text": ocr_text
                        },
                        timeout=15
                    )

                    if res_eval.status_code == 200:
                        st.success("✅ Evaluation complete!")
                    else:
                        st.error("❌ Evaluation failed")

                    # Upload form media
                    if st.session_state.uploaded_file_data:
                        files = {
                            "file": (
                                st.session_state.uploaded_file_data['name'],
                                io.BytesIO(st.session_state.uploaded_file_data['data']),
                                st.session_state.uploaded_file_data['type']
                            )
                        }
                        res_uploaded = requests.post(
                            "http://localhost:8000/save-uploaded-form/",
                            files=files,
                            data={"upload_id": upload_id},
                            timeout=10
                        )
                    else:
                        res_uploaded = None

                    with st.expander("🔍 Debug: Server responses"):
                        st.write("Extracted")
                        st.json(res_extracted.json())
                        st.write("Edited")
                        st.json(res_edited.json())
                        if res_uploaded:
                            st.write("Uploaded")
                            st.json(res_uploaded.json())

                    st.success("🎉 All data saved successfully")

                except Exception as e:
                    st.error(f"❌ Error saving data: {e}")

    # ---------------------------------
    # DOWNLOAD BUTTONS
    # ---------------------------------
    with col2:
        col_a, col_b = st.columns(2)

        with col_a:
            st.download_button(
                label="📥 Download Extracted",
                data=json.dumps({**extracted_data, "version": "extracted"}, indent=2),
                file_name=f"{upload_id}_extracted.json",
                mime="application/json",
                width="stretch"
            )

        with col_b:
            st.download_button(
                label="📥 Download Edited",
                data=json.dumps({**st.session_state.edited_data, "version": "edited"}, indent=2),
                file_name=f"{upload_id}_edited.json",
                mime="application/json",
                width="stretch"
            )

# ---------------------------------
# SIDEBAR: Reset + Instructions
# ---------------------------------
with st.sidebar:
    st.write("---")
    if st.button("🔄 Reset Form", width="stretch"):
        st.session_state.clear()
        st.rerun()

    st.write("### 📋 Instructions")
    st.write("""
    1. Upload a form image (JPG, PNG)  
    2. Click **Extract Form Data**  
    3. Review & edit the results  
    4. Save, download, or reset  
    """)

    if st.session_state.upload_id:
        st.write("---")
        st.write("**Session Info**")
        st.write(f"Upload ID: `{st.session_state.upload_id}`")
