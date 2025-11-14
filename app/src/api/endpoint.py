from fastapi import HTTPException, UploadFile
from typing import Dict, Any
import shutil
import json
from pathlib import Path
import os
import pandas as pd
from ..core.ocr_evaluator import ocr_overall_evaluation

from ..core.mistral_client import MistralFormExtractor
from ..utils.aws_utils import upload_file_to_s3_folder, upload_json_to_s3_folder, upload_dataframe_to_s3_folder
from ..core.ocr_metrics import calculate_ocr_metrics
from .request import EvaluationRequest

# Configuration
class Config:
    UPLOAD_DIR = Path("../data/uploads")
    EXTRACTED_DIR = Path("../data/extracted")
    EDITED_DIR = Path("../data/edited")
    RESULTS_DIR = Path("../data/results")
    
    EXTRACTED_PREFIX = "ocr_results/extracted"
    EDITED_PREFIX = "ocr_results/edited"
    RESULTS_PREFIX = "ocr_results/results"
    UPLOAD_PREFIX = "uploads"
    
    def __init__(self):
        # Create directories
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
        self.EDITED_DIR.mkdir(parents=True, exist_ok=True)
        self.RESULTS_DIR.mkdir(parents=True, exist_ok=True)

config = Config()
extractor = MistralFormExtractor()

class EndpointHandler:
    """Handles business logic for all endpoints"""
    
    @staticmethod
    async def health_check():
        return {"status": "online", "message": "Aircraft Journey Form Extractor API"}
    
    @staticmethod
    async def extract_form(file: UploadFile):
        try:
            print(f"📥 Received file: {file.filename}")
            
            # Save uploaded file temporarily
            file_path = config.UPLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            print(f"💾 Saved to: {file_path}")
            
            # Run extraction
            print("🔍 Running OCR extraction...")
            result, ocr_text = extractor.structured_ocr(str(file_path))
            
            # Convert to dict
            result_dict = json.loads(result.json())
            
            print(f"✅ Extraction successful!")
            
            # Clean up temporary file
            EndpointHandler._cleanup_file(file_path)
            
            return {
                "status": "success", 
                "data": result_dict,
                "ocr_text":ocr_text, # to generate comprehensive result
            }
        except Exception as e:
            print(f"❌ Error in extract_form: {type(e).__name__}: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def save_extracted_data(data: Dict[str, Any]):  
        try:
            print(f"📥 Received save-extracted request")
            print(f"📦 Data keys: {list(data.keys())}")  
            
            upload_id = data.get("Upload_ID", "unknown")
            version = data.get("version", "extracted")
            
            # Save locally
            local_path = EndpointHandler._save_json_locally(
                data, config.EXTRACTED_DIR, f"{upload_id}_{version}.json"
            )
            
            # Upload to S3
            s3_uri = await EndpointHandler._upload_json_to_s3(
                data, f"{config.EXTRACTED_PREFIX}/{upload_id}.json"
            )
            
            return {
                "status": "success",
                "message": f"{version} data saved and uploaded",
                "local_path": str(local_path),
                "s3_result": s3_uri
            }
        except Exception as e:
            print(f"❌ Error in save_extracted_data: {type(e).__name__}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def save_edited_data(data: Dict[str, Any]): 
        try:
            print(f"📥 Received save-edited request")
            print(f"📦 Data keys: {list(data.keys())}")  
            
            upload_id = data.get("Upload_ID", "unknown")
            version = data.get("version", "edited")
            
            # Save locally
            local_path = EndpointHandler._save_json_locally(
                data, config.EDITED_DIR, f"{upload_id}_{version}.json"
            )
            
            # Upload to S3
            s3_uri = await EndpointHandler._upload_json_to_s3(
                data, f"{config.EDITED_PREFIX}/{upload_id}.json"
            )
            
            return {
                "status": "success",
                "message": f"{version} data saved and uploaded",
                "local_path": str(local_path),
                "s3_result": s3_uri
            }
        except Exception as e:
            print(f"❌ Error in save_edited_data: {type(e).__name__}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def evaluate_ocr_results(data: EvaluationRequest):
        try:
            print("📊 Received evaluate-ocr request")
            
            extracted = data.extracted
            edited = data.edited
            ocr_text = data.ocr_text
            
            if not extracted or not edited:
                raise ValueError("Missing extracted or edited data in request")
            
            # Extract Upload_ID from the data
            upload_id = extracted.get("Upload_ID") or edited.get("Upload_ID", "unknown")
            print(f"Evaluating OCR accuracy for Upload_ID={upload_id}")
                     
            # Run evaluation with extracted, edited, and ocr_text
            # This should return your rich structure with extracted_data, data_validation, metadata, results
            evaluation_results = ocr_overall_evaluation(extracted, edited, ocr_text)
            
            print(f"✅ Evaluation complete! Result keys: {list(evaluation_results.keys())}")
            
            # Save the rich evaluation results as JSON
            json_filename = f"{upload_id}_evaluation.json"
            json_path = config.RESULTS_DIR / json_filename
            
            with open(json_path, "w") as f:
                json.dump(evaluation_results, f, indent=2)
            
            print(f"✅ Evaluation JSON saved locally at {json_path}")
            
            # Upload JSON to S3
            s3_json_uri = None
            try:
                s3_key = f"{config.RESULTS_PREFIX}/{json_filename}"
                print(f"☁️ Uploading JSON to S3: {s3_key}")
                s3_json_uri = upload_json_to_s3_folder(
                    json.dumps(evaluation_results), 
                    s3_key=s3_key
                )
                print(f"✅ S3 JSON upload successful: {s3_json_uri}")
            except Exception as s3_error:
                print(f"⚠️ S3 JSON upload failed: {s3_error}")
                s3_json_uri = f"S3 upload failed: {s3_error}"
            
            # Return summary
            return {
                "status": "success",
                "upload_id": upload_id,
                "local_path": str(json_path),
                "s3_result": s3_json_uri,
                "metadata": evaluation_results.get('metadata', {}),
                "sample": evaluation_results.get('results', {})
            }
            
        except Exception as e:
            print(f"❌ Error in evaluate_ocr_results: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=str(e))
                
    @staticmethod
    async def save_uploaded_form(file: UploadFile, upload_id: str):
        try:
            print(f"📥 Received save-uploaded-form request")
            print(f"File: {file.filename}, Upload ID: {upload_id}")
            
            # Save locally with upload_id as name
            output_filename = f"{upload_id}_{file.filename}"
            output_path = config.UPLOAD_DIR / output_filename
            
            print(f"💾 Saving locally to: {output_path}")
            
            with open(output_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            print(f"✅ Local save successful!")
            
            # Upload to S3
            s3_uri = None
            try:
                s3_key = f"{config.UPLOAD_PREFIX}/{output_filename}"
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
    
    # Helper methods
    @staticmethod
    def _save_json_locally(data: Dict[str, Any], directory: Path, filename: str) -> Path:
        """Save JSON data to local directory"""
        output_path = directory / filename
        print(f"💾 Saving to: {output_path}")
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Local save successful!")
        return output_path
    
    @staticmethod
    async def _upload_json_to_s3(data: Dict[str, Any], s3_key: str) -> str:
        """Upload JSON data to S3"""
        try:
            print(f"☁️ Uploading to S3: {s3_key}")
            s3_uri = upload_json_to_s3_folder(json.dumps(data), s3_key=s3_key)
            print(f"✅ S3 upload successful: {s3_uri}")
            return s3_uri
        except Exception as s3_error:
            print(f"⚠️ S3 upload failed (non-critical): {s3_error}")
            return f"S3 upload failed: {str(s3_error)}"
    
    @staticmethod
    def _cleanup_file(file_path: Path):
        """Clean up temporary file"""
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️ Deleted: {file_path}")
            except OSError as e:
                print(f"❌ Error deleting {file_path}: {e}")