from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from mistral_client import MistralFormExtractor
from pydantic import BaseModel
import shutil
import json
from pathlib import Path
from aws_utils import upload_file_to_s3_folder, upload_json_to_s3_folder , upload_dataframe_to_s3_folder
from typing import Optional, Dict, Any
import pandas as pd

from dotenv import load_dotenv
import os
from ocr_metrics import calculate_ocr_metrics



load_dotenv()

app = FastAPI(title="Aircraft Journey Form Extractor API")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to save data locally
UPLOAD_DIR = Path("../data/uploads")
EXTRACTED_DIR = Path("../data/extracted")
EDITED_DIR = Path("../data/edited")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
EDITED_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_DIR = Path("../data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Directory to save data in S3
EXTRACTED_PREFIX = "ocr_results/extracted"
EDITED_PREFIX = "ocr_results/edited"
RESULTS_PREFIX = "ocr_results/results"
UPLOAD_PREFIX = "uploads"


# Initialize extractor
extractor = MistralFormExtractor()


# Pydantic models for request validation
class FormData(BaseModel):
    Upload_ID: Optional[str] = None
    version: Optional[str] = None
    saved_at: Optional[str] = None
    file_name: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "online", "message": "Aircraft Journey Form Extractor API"}


@app.post("/extract/")
async def extract_form(file: UploadFile = File(...)):
    """
    Receive uploaded file, run OCR extraction, return structured JSON.
    """
    try:
        print(f"📥 Received file: {file.filename}")
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"💾 Saved to: {file_path}")
        
        # Run extraction
        print("🔍 Running OCR extraction...")
        result, _ = extractor.structured_ocr(str(file_path))
        
        # Convert to dict
        result_dict = json.loads(result.json())
        
        print(f"✅ Extraction successful!")
        
        # Delete temporay saved file
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except OSError as e:
                print(f"Error deleting {file_path}: {e}")
        
        return {
            "status": "success", 
            "data": result_dict
        }
    except Exception as e:
        print(f"❌ Error in extract_form: {type(e).__name__}: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/save-extracted/")
async def save_extracted_data(data: Dict[str, Any]):
    """
    Save original extracted form data (unedited).
    """
    try:
        print(f"📥 Received save-extracted request")
        print(f"Data keys: {list(data.keys())}")
        
        # Save locally
        upload_id = data.get("Upload_ID", "unknown")
        version = data.get("version", "extracted")
        
        print(f"Upload ID: {upload_id}, Version: {version}")
        output_filename = f"{upload_id}_{version}.json"
        output_path = EXTRACTED_DIR / output_filename
        print(f"💾 Saving to: {output_path}")
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Extracted data saved successfully!")
        
        # Upload to S3
        s3_uri = None
        try:
            s3_key = f"{EXTRACTED_PREFIX}/{upload_id}.json"
            print(f"☁️ Uploading to S3: {s3_key}")
            s3_uri = upload_json_to_s3_folder(json.dumps(data), s3_key=s3_key)
            print(f"✅ S3 upload successful: {s3_uri}")
        except Exception as s3_error:
            print(f"⚠️ S3 upload failed (non-critical): {s3_error}")
            s3_uri = f"S3 upload failed: {str(s3_error)}"
        
        return {
            "status": "success",
            "message": f"{version} data saved and uploaded",
            "local_path": str(output_path),
            "s3_result": s3_uri
        }
    except Exception as e:
        print(f"❌ Error in save_extracted_data: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/save-edited/")
async def save_edited_data(data: Dict[str, Any]):
    """
    Save edited form data (with user corrections).
    """
    try:
        print(f"📥 Received save-edited request")
        print(f"Data keys: {list(data.keys())}")
        
        # Save locally
        upload_id = data.get("Upload_ID", "unknown")
        version = data.get("version", "edited")
        
        print(f"Upload ID: {upload_id}, Version: {version}")
        
        output_filename = f"{upload_id}_{version}.json"
        output_path = EDITED_DIR / output_filename
        
        print(f"💾 Saving locally to: {output_path}")
      
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Local save successful!")
        
        #  Upload to S3
        s3_uri = None
        try:
            s3_key = f"{EDITED_PREFIX}/{upload_id}.json"
            print(f"☁️ Uploading to S3: {s3_key}")
            s3_uri = upload_json_to_s3_folder(json.dumps(data), s3_key=s3_key)
            print(f"✅ S3 upload successful: {s3_uri}")
        except Exception as s3_error:
            print(f"⚠️ S3 upload failed (non-critical): {s3_error}")
            s3_uri = f"S3 upload failed: {str(s3_error)}"
        
        return {
            "status": "success",
            "message": f"{version} data saved and uploaded",
            "local_path": str(output_path),
            "s3_result": s3_uri
        }
    except Exception as e:
        print(f"❌ Error in save_edited_data: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate-ocr/")
async def evaluate_ocr_results(data: Dict[str, Any]):
    """
    Compare OCR (extracted) vs edited (ground truth) data.
    Compute metrics and upload results to S3.
    """
    try:
        print("📊 Received evaluate-ocr request")
        extracted = data.get("extracted")
        edited = data.get("edited")

        if not extracted or not edited:
            raise ValueError("Missing extracted or edited data in request")

        upload_id = edited.get("Upload_ID", "unknown")
        print(f"Evaluating OCR accuracy for Upload_ID={upload_id}")

        # Run evaluation
        results = calculate_ocr_metrics(extracted, edited)

        # Save locally
        df = pd.DataFrame(results)
        local_path = RESULTS_DIR / f"{upload_id}_result.csv"
        df.to_csv(local_path, index=False)
        print(f"✅ Results saved locally at {local_path}")

        # Upload to S3
        s3_uri = None
        try:
            # s3_key = f"{RESULTS_PREFIX}/{upload_id}_result.csv"
            # serialize_json = "\n\n".join(json.dumps(data, indent=2) for data in results) 
            # s3_uri = upload_json_to_s3_folder(json.dumps(results, indent=2), s3_key=s3_key)
            # s3_uri = upload_json_to_s3_folder(serialize_json, s3_key=s3_key)
            s3_uri = upload_dataframe_to_s3_folder(df, RESULTS_PREFIX,f"{upload_id}_result.csv")
            print(f"☁️ Uploaded results to S3: {s3_uri}")
        except Exception as s3_error:
            print(f"⚠️ S3 upload failed: {s3_error}")
            s3_uri = f"S3 upload failed: {s3_error}"

        return {
            "status": "success",
            "upload_id": upload_id,
            "record_count": len(results),
            "local_path": str(local_path),
            "s3_result": s3_uri,
            "sample": results[:5],
        }

    except Exception as e:
        print(f"❌ Error in evaluate_ocr_results: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/save-uploaded-form/")
async def save_uploaded_form(
    file: UploadFile = File(...),
    upload_id: str = Form(...)):
    """
    Save uploaded form image/PDF to local storage and S3.
    This is for re-uploading or explicitly saving the form file.
    """
    try:
        print(f"📥 Received save-uploaded-form request")
        print(f"File: {file.filename}, Upload ID: {upload_id}")
        
        # Get file extension
        file_ext = os.path.splitext(file.filename)[1]
        
        # Save locally with upload_id as name
        output_filename = f"{upload_id}_{file.filename}"
        output_path = UPLOAD_DIR / output_filename
        
        print(f"💾 Saving locally to: {output_path}")
        
        with open(output_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Local save successful!")
        
        # Upload to S3
        s3_uri = None
        try:
            s3_key = f"{UPLOAD_PREFIX}/{output_filename}"
            print(f"☁️ Uploading to S3: {s3_key}")
            s3_uri = upload_file_to_s3_folder(str(output_path), s3_key)
            print(f"✅ S3 upload successful: {s3_uri}")
        except Exception as s3_error:
            print(f"⚠️ S3 upload failed (non-critical): {s3_error}")
            s3_uri = f"S3 upload failed: {str(s3_error)}"
        
        return {
            "status": "success",
            "message": "Uploaded form saved successfully",
            "local_path": str(output_path),
            "s3_result": s3_uri,
            "filename": output_filename
        }
    except Exception as e:
        print(f"❌ Error in save_uploaded_form: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
