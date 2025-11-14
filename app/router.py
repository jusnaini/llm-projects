from fastapi import APIRouter, UploadFile, File, Form, Body
from typing import Dict, Any

from endpoint import EndpointHandler
from request import EvaluationRequest

# Create router
router = APIRouter()

@router.get("/")
async def root():
    """Health check endpoint"""
    return await EndpointHandler.health_check()

@router.post("/extract/")
async def extract_form(file: UploadFile = File(...)):
    """
    Receive uploaded file, run OCR extraction, return structured JSON.
    """
    return await EndpointHandler.extract_form(file)

@router.post("/save-extracted/")
async def save_extracted_data(data: Dict[str, Any] = Body(...)):  # Add Body(...) here!
    """
    Save original extracted form data (unedited).
    """
    return await EndpointHandler.save_extracted_data(data)

@router.post("/save-edited/")
async def save_edited_data(data: Dict[str, Any] = Body(...)):  # Add Body(...) here!
    """
    Save edited form data (with user corrections).
    """
    return await EndpointHandler.save_edited_data(data)

@router.post("/evaluate-ocr/")
async def evaluate_ocr_results(data: EvaluationRequest):
    """
    Compare OCR (extracted) vs edited (ground truth) data.
    Compute metrics and upload results to S3.
    """
    return await EndpointHandler.evaluate_ocr_results(data)

@router.post("/save-uploaded-form/")
async def save_uploaded_form(
    file: UploadFile = File(...),
    upload_id: str = Form(...)):
    """
    Save uploaded form image/PDF to local storage and S3.
    This is for re-uploading or explicitly saving the form file.
    """
    return await EndpointHandler.save_uploaded_form(file, upload_id)