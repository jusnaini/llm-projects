from .validator import FieldValidator
from typing import Optional, Dict, Any
from dataclasses import asdict
from .ocr_metrics import compute_accuracy, distance,char_error_rate,word_error_rate



AIRCRAFT_FIELDS = [
    'Aircraft_Model', 
    'Registration_Number', 
    'Departure_Airport', 
    'Arrival_Airport', 
    'Crew', 'Fuel', 'Load', 'Defect_Message']

def _get_data_validation (extracted: Dict[str,Any],ocr_text: str = ""):
    field_validator = FieldValidator()
    parsed_form = extracted
    
    # Validate each field
    registration = field_validator.validate_registration(parsed_form['Registration_Number'])
    aircraft_model = field_validator.validate_aircraft_model(parsed_form['Aircraft_Model'], ocr_text)
    departure = field_validator.validate_airport(parsed_form["Departure_Airport"], "departure")
    arrival = field_validator.validate_airport(parsed_form["Arrival_Airport"], "arrival")
    crew = field_validator.validate_numeric(parsed_form["Crew"], "crew", min_val=2, max_val=20, ocr_text=ocr_text)
    load = field_validator.validate_numeric(parsed_form["Load"], "load", min_val=0, max_val=500, ocr_text=ocr_text)
    fuel = field_validator.validate_fuel(parsed_form["Fuel"], ocr_text=ocr_text)
    defect_message = field_validator.validate_defect_message(parsed_form["Defect_Message"], ocr_text=ocr_text)

    return {
        'Aircraft_Model': asdict(aircraft_model),
        'Registration_Number': asdict(registration),
        'Departure_Airport': asdict(departure),
        'Arrival_Airport': asdict(arrival),
        'Crew': asdict(crew),
        'Fuel': asdict(fuel),
        'Load': asdict(load),
        'Defect_Message': asdict(defect_message)
        }

def _get_metrics_result (extracted: Dict[str, Any], edited: Dict[str, Any]):
    Upload_ID = extracted.get('Upload_ID')

    #  Initialize the result dictionary with Upload_ID
    result = {
        'Upload_ID': Upload_ID
    }

    # Add each field as a separate key in the result dictionary
    for key in AIRCRAFT_FIELDS:
        gt_val = str(edited.get(key, "") or "")
        ocr_val = str(extracted.get(key, "") or "")
        
        result[key] = {
            "Ground_Truth": gt_val,
            "OCR_Output": ocr_val,
            "Correct": compute_accuracy(gt_val, ocr_val),
            "Levenshtein": distance(gt_val, ocr_val),
            "CER": round(char_error_rate(gt_val, ocr_val), 4),
            "WER": round(word_error_rate(gt_val, ocr_val), 4),
        }

    return result


def ocr_overall_evaluation(extracted: Dict[str, Any], edited: Dict[str, Any], ocr_text: str = "") -> Dict[str, Any]:
    """
    Compare OCR vs. ground truth field by field and return comprehensive evaluation.
    
    Args:
        extracted: The OCR extracted data
        edited: The ground truth/edited data
        ocr_text: The raw OCR markdown text
        
    Returns:
        Dict containing extracted_data, data_validation, metadata, and results
    """

    data_validation = _get_data_validation(extracted,ocr_text)
    
    # Calculate overall metrics
    confidences = [f['confidence'] for f in data_validation.values() if f['value'] is not None]
    fields_validated = sum(1 for f in data_validation.values() if f['validated'])
    flagged_fields = [ name for name, field in data_validation.items() if field['value'] is not None and field['confidence'] < 0.7]
    
    results = _get_metrics_result(extracted,edited)

    OCR_OUTPUT_ALL_COMBINED = {
        'extracted_data' : extracted,
        'data_validation': data_validation,
        'data_assessment': results,
        'metadata': {
            'overall_confidence': sum(confidences) / len(confidences) if confidences else 0.0,
            'fields_extracted': sum(1 for f in data_validation.values() if f['value'] is not None),
            'fields_validated': fields_validated,
            'requires_human_review': len(flagged_fields) > 0 or len(confidences) == 0,
            'flagged_fields': flagged_fields,
            'total_fields': len(data_validation)
        },
        'raw_ocr_markdown': ocr_text,
        'schema_version': "1.0"
        }
    
    return OCR_OUTPUT_ALL_COMBINED

