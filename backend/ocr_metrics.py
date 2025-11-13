# metrics_utils.py
import csv
from typing import Dict, Any, List
from Levenshtein import distance
import jiwer
import boto3
from io import StringIO
import os


def char_error_rate(gt: str, pred: str) -> float:
    """Compute Character Error Rate (CER)."""
    gt, pred = gt or "", pred or ""
    if len(gt) == 0:
        return 1.0 if len(pred) > 0 else 0.0
    return distance(gt, pred) / len(gt)


def word_error_rate(gt: str, pred: str) -> float:
    """Compute Word Error Rate (WER)."""
    gt, pred = gt or "", pred or ""
    if len(gt) == 0:
        return 1.0 if len(pred) > 0 else 0.0
    return jiwer.wer(gt, pred)


def compute_accuracy(gt: str, pred: str) -> float:
    """Exact match accuracy."""
    return 1.0 if (gt or "").strip().lower() == (pred or "").strip().lower() else 0.0


def calculate_ocr_metrics(extracted: Dict[str, Any], edited: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compare OCR vs. ground truth field by field."""
    results = []
    upload_id = extracted.get("Upload_ID", "unknown")
    
    # Skip these fields
    skip_fields = ["Upload_ID", "Extracted_AT", "version", "saved_at", "file_name"]

    for key in edited.keys():
        if key in skip_fields:
            continue

        gt_val = str(edited.get(key, "") or "")
        ocr_val = str(extracted.get(key, "") or "")

        results.append({
            "Upload_ID": upload_id,
            "Field": key,
            "Ground_Truth": gt_val,
            "OCR_Output": ocr_val,
            "Correct": compute_accuracy(gt_val, ocr_val),
            "Levenshtein": distance(gt_val, ocr_val),
            "CER": round(char_error_rate(gt_val, ocr_val), 4),
            "WER": round(word_error_rate(gt_val, ocr_val), 4),
        })
    
    return results

