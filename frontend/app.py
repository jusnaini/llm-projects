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
if 'edited_data' not in st.session_state:
    st.session_state.edited_data = None
if 'upload_id' not in st.session_state:
    st.session_state.upload_id = None
if 'uploaded_file_data' not in st.session_state:
    st.session_state.uploaded_file_data = None

uploaded_file = st.file_uploader("Upload Form (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption=f"📸 Preview: {uploaded_file.name}", use_container_width=True)
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
    
    if st.button("🔍 Extract Form Data"):
        with st.spinner("Extracting data... This may take a moment ⏳"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                response = requests.post(API_URL, files=files, timeout=30)
                
                if response.status_code == 200:
                    res = response.json()
                    if res.get("status") == "success":
                        st.success("✅ Extraction complete!")
                        
                        extracted_data = res["data"]
                        
                        # Generate unique upload ID if not present
                        if "Upload_ID" not in extracted_data or not extracted_data["Upload_ID"]:
                            upload_id = f"AJ-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
                            extracted_data["Upload_ID"] = upload_id
                        
                        # Store in session state
                        st.session_state.extracted_data = extracted_data
                        st.session_state.edited_data = extracted_data.copy()
                        st.session_state.upload_id = extracted_data["Upload_ID"]
                        
                    else:
                        st.error(f"❌ Extraction Error: {res.get('message', 'Unknown error')}")
                else:
                    st.error(f"❌ API Error: Status code {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection Error: Could not connect to backend. Make sure the server is running on http://localhost:8000")
                st.info("💡 Tip: Start the backend server with: `uvicorn main:app --reload`")
            except json.JSONDecodeError:
                st.error("❌ Invalid response from server")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")

# Display extracted data and editing interface
if st.session_state.extracted_data:
    extracted_data = st.session_state.extracted_data
    upload_id = st.session_state.upload_id
    
    # Display the extracted data
    st.write("### 📋 Extracted Data")
    st.json(extracted_data)
    
    # Allow editing
    st.write("### ✏️ Review & Edit Extracted Data")
    
    edited = {}
    for key, val in st.session_state.edited_data.items():
        edited[key] = st.text_input(
            key, 
            value=str(val) if val is not None else "",
            key=f"input_{key}"
        )
    
    # Update session state with edited data
    st.session_state.edited_data = edited
    
    # Single Save Button for both versions
    st.write("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("💾 Save All Data", type="primary", use_container_width=True):
            with st.spinner("Saving data to backend..."):
                try:
                    # Prepare data payloads
                    extracted_version = {
                        **st.session_state.extracted_data,
                        "version": "extracted",
                        "saved_at": datetime.now().isoformat(),
                        "file_name": st.session_state.uploaded_file_data['name'] if st.session_state.uploaded_file_data else "unknown"
                    }
                    edited_version = {
                        **st.session_state.edited_data,
                        "version": "edited",
                        "saved_at": datetime.now().isoformat(),
                        "file_name": st.session_state.uploaded_file_data['name'] if st.session_state.uploaded_file_data else "unknown"
                    }
                    
                    # Debug: Show what we're sending
                    with st.expander("🔍 Debug: Data being sent"):
                        st.write("**Extracted Version:**")
                        st.json(extracted_version)
                        st.write("**Edited Version:**")
                        st.json(edited_version)
                    
                    # Send to backend for saving
                    st.info("📤 Sending extracted data...")
                    res_extracted = requests.post(
                        "http://localhost:8000/save-extracted/", 
                        json=extracted_version,
                        timeout=10
                    )
                    
                    st.info("📤 Sending edited data...")
                    res_edited = requests.post(
                        "http://localhost:8000/save-edited/", 
                        json=edited_version,
                        timeout=10
                    )

                    st.info("📊 Evaluating OCR accuracy...")
                    res_eval = requests.post(
                        "http://localhost:8000/evaluate-ocr/",
                        json={
                            "extracted": extracted_version,
                            "edited": edited_version
                        },
                        timeout=15
                    )

                    if res_eval.status_code == 200:
                        eval_result = res_eval.json()
                        st.success("✅ Evaluation complete!")
                        st.write(f"Results saved at: `{eval_result.get('local_path')}`")
                        if 's3_result' in eval_result:
                            st.info(f"☁️ Uploaded to S3: {eval_result['s3_result']}")
                        st.dataframe(eval_result.get("sample", []))
                    else:
                        st.error(f"❌ Evaluation failed: {res_eval.text}")

                    # Upload the form file
                    st.info("📤 Sending uploaded form...")
                    if st.session_state.uploaded_file_data:
                        files = {
                            "file": (
                                st.session_state.uploaded_file_data['name'],
                                io.BytesIO(st.session_state.uploaded_file_data['data']),
                                st.session_state.uploaded_file_data['type']
                            )
                        }
                        data = {"upload_id": upload_id}
                        
                        res_uploaded = requests.post(
                            "http://localhost:8000/save-uploaded-form/",
                            files=files,
                            data=data,
                            timeout=10
                        )
                    else:
                        st.warning("⚠️ No file data found in session state")
                        res_uploaded = None
                    
                    # Debug: Show responses
                    with st.expander("🔍 Debug: Server responses"):
                        st.write(f"**Extracted Response ({res_extracted.status_code}):**")
                        st.json(res_extracted.json() if res_extracted.status_code == 200 else res_extracted.text)
                        st.write(f"**Edited Response ({res_edited.status_code}):**")
                        st.json(res_edited.json() if res_edited.status_code == 200 else res_edited.text)
                        if res_uploaded:
                            st.write(f"**Upload Response ({res_uploaded.status_code}):**")
                            st.json(res_uploaded.json() if res_uploaded.status_code == 200 else res_uploaded.text)
                    
                    # Check all responses
                    all_success = (
                        res_extracted.status_code == 200 and 
                        res_edited.status_code == 200 and 
                        (res_uploaded is None or res_uploaded.status_code == 200)
                    )
                    
                    if all_success:
                        st.success("✅ Data saved successfully on backend!")
                        
                        # Show save locations
                        extracted_result = res_extracted.json()
                        edited_result = res_edited.json()
                        
                        st.info(f"📁 Extracted saved to: `{extracted_result.get('local_path', 'N/A')}`")
                        st.info(f"📁 Edited saved to: `{edited_result.get('local_path', 'N/A')}`")
                        
                        if res_uploaded and res_uploaded.status_code == 200:
                            upload_result = res_uploaded.json()
                            st.info(f"📁 Form saved to: `{upload_result.get('local_path', 'N/A')}`")
                            if 's3_result' in upload_result:
                                st.info(f"☁️ Form uploaded to S3: `{upload_result['s3_result']}`")
                        
                        if 's3_result' in extracted_result:
                            st.info(f"☁️ Extracted uploaded to S3: `{extracted_result['s3_result']}`")
                        if 's3_result' in edited_result:
                            st.info(f"☁️ Edited uploaded to S3: `{edited_result['s3_result']}`")
                       
                    else:
                        st.error("❌ Failed to save data on backend.")
                        if res_extracted.status_code != 200:
                            st.error(f"Extracted save failed: {res_extracted.text}")
                        if res_edited.status_code != 200:
                            st.error(f"Edited save failed: {res_edited.text}")
                        if res_uploaded and res_uploaded.status_code != 200:
                            st.error(f"Upload save failed: {res_uploaded.text}")
                            
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend server!")
                    st.info("💡 Make sure the server is running: `uvicorn main:app --reload`")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. Server might be busy.")
                except Exception as e:
                    st.error(f"❌ Error saving data: {type(e).__name__}: {e}")
                    st.exception(e)  # Show full traceback
    
    with col2:
        # Download both as zip or individual files
        col2_sub1, col2_sub2 = st.columns(2)
        
        with col2_sub1:
            # Download extracted JSON
            json_str_extracted = json.dumps(
                {**st.session_state.extracted_data, "version": "extracted"}, 
                indent=2
            )
            st.download_button(
                label="📥 Download Extracted",
                data=json_str_extracted,
                file_name=f"{upload_id}_extracted.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2_sub2:
            # Download edited JSON
            json_str_edited = json.dumps(
                {**st.session_state.edited_data, "version": "edited"}, 
                indent=2
            )
            st.download_button(
                label="📥 Download Edited",
                data=json_str_edited,
                file_name=f"{upload_id}_edited.json", 
                mime="application/json",
                use_container_width=True
            )

# Add a reset button in sidebar to clear session state
with st.sidebar:
    st.write("---")
    if st.button("🔄 Reset Form"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.write("### 📋 Instructions")
    st.write("""
    1. Upload a form image (JPG, PNG)
    2. Click 'Extract Form Data'
    3. Review and edit if needed
    4. Save or download the results
    5. Click 'Reset Form' to clear current fields and extract another form
    """)
    
    if st.session_state.upload_id:
        st.write("---")
        st.write("**Current Session**")
        st.write(f"Upload ID: `{st.session_state.upload_id}`")
        st.write(f"Files will be saved as:")
        st.write(f"- `{st.session_state.upload_id}_extracted.json`")
        st.write(f"- `{st.session_state.upload_id}_edited.json`")
