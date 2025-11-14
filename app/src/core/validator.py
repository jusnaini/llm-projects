"""
backend/app/services/ocr/validator.py
Field validation logic extracted into separate module.
"""

import re
from typing import Dict, Optional
from dataclasses import asdict

from src.utils.utils import AircraftJourneyForm, FieldExtraction


class FieldValidator:
    """Validates extracted form fields."""
    
    # Known IATA airport codes (subset)
    IATA_CODES = {
        'KUL', 'SIN', 'BKK', 'CGK', 'MNL', 'HKG', 'PEK', 'PVG',
        'NRT', 'ICN', 'DEL', 'BOM', 'DXB', 'DOH', 'JFK', 'LAX',
        'LHR', 'CDG', 'FRA', 'AMS', 'SYD', 'MEL', 'AKL', 'DPS',
        'HAN', 'SGN', 'RGN', 'DAC', 'CMB', 'TPE', 'HND', 'KIX'
    }
    
    # Aircraft models (common ones)
    AIRCRAFT_MODELS = [
        'Boeing 737', 'Boeing 747', 'Boeing 777', 'Boeing 787',
        'Airbus A320', 'Airbus A330', 'Airbus A350', 'Airbus A380',
        'ATR 72', 'Bombardier CRJ', 'Embraer E190'
    ]
    
    def _estimate_confidence(
        self,
        field_value: any,
        ocr_text: str,
        validation_result: bool
    ) -> float:
        """Estimate confidence based on validation and OCR match."""
        if field_value is None:
            return 0.0
        
        confidence = 0.5
        
        if validation_result:
            confidence += 0.3
        
        field_str = str(field_value).upper()
        ocr_upper = ocr_text.upper()
        
        if field_str in ocr_upper:
            confidence += 0.2
        elif any(word in ocr_upper for word in field_str.split()):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def validate_registration(self, registration: Optional[str]) -> FieldExtraction:
        """Validate aircraft registration number."""
        if not registration:
            return FieldExtraction(None, 0.0, False, reason="no_value")
        
        # Pattern: 2-3 chars, hyphen, 3-5 chars (e.g., 9M-MLK)
        pattern = r'^[A-Z0-9]{1,3}-[A-Z0-9]{3,5}$'
        if re.match(pattern, registration.upper()):
            return FieldExtraction(
                registration, 0.9, True,
                validation_method="regex_pattern"
            )
        else:
            return FieldExtraction(
                registration, 0.6, False,
                validation_method="regex_pattern",
                reason="pattern_mismatch"
            )
    
    def validate_airport(
        self,
        airport: Optional[str],
        field_name: str
    ) -> FieldExtraction:
        """Validate airport IATA code."""
        if not airport:
            return FieldExtraction(None, 0.0, False, reason="no_value")
        
        airport_upper = airport.upper().strip()
        
        if len(airport_upper) != 3 or not airport_upper.isalpha():
            return FieldExtraction(
                airport, 0.5, False,
                validation_method="iata_format",
                reason="invalid_format"
            )
        
        if airport_upper in self.IATA_CODES:
            return FieldExtraction(
                airport_upper, 0.95, True,
                validation_method="iata_validation"
            )
        else:
            return FieldExtraction(
                airport, 0.6, False,
                validation_method="iata_validation",
                reason="unknown_code"
            )
    
    def validate_aircraft_model(
        self,
        model: Optional[str],
        ocr_text: str
    ) -> FieldExtraction:
        """Validate aircraft model."""
        if not model:
            return FieldExtraction(None, 0.0, False, reason="no_value")
        
        model_upper = model.upper()
        
        for known_model in self.AIRCRAFT_MODELS:
            if known_model.upper() in model_upper:
                confidence = self._estimate_confidence(model, ocr_text, True)
                return FieldExtraction(
                    model, confidence, True,
                    validation_method="known_model"
                )
        
        if re.search(r'(BOEING|AIRBUS)\s*[A]?\d{3}', model_upper):
            confidence = self._estimate_confidence(model, ocr_text, True)
            return FieldExtraction(
                model, confidence, True,
                validation_method="pattern_match"
            )
        
        confidence = self._estimate_confidence(model, ocr_text, False)
        return FieldExtraction(
            model, confidence, False,
            validation_method="unknown_model",
            reason="not_in_known_list"
        )
    
    def validate_numeric(
        self,
        value: Optional[int],
        field_name: str,
        min_val: int,
        max_val: int,
        ocr_text: str
    ) -> FieldExtraction:
        """Validate numeric field with range check."""
        if value is None:
            return FieldExtraction(None, 0.0, False, reason="no_value")
        
        if min_val <= value <= max_val:
            confidence = self._estimate_confidence(value, ocr_text, True)
            return FieldExtraction(
                value, confidence, True,
                validation_method=f"range_check_{min_val}_{max_val}"
            )
        else:
            return FieldExtraction(
                value, 0.4, False,
                validation_method=f"range_check_{min_val}_{max_val}",
                reason="out_of_range"
            )
    
    def validate_fuel(self, fuel: Optional[str], ocr_text: str) -> FieldExtraction:
        """Validate fuel field."""
        if not fuel:
            return FieldExtraction(None, 0.0, False, reason="no_value")
        
        if re.search(r'\d+', fuel):
            confidence = self._estimate_confidence(fuel, ocr_text, True)
            return FieldExtraction(
                fuel, confidence, True,
                validation_method="contains_numeric"
            )
        else:
            return FieldExtraction(
                fuel, 0.5, False,
                validation_method="format_check",
                reason="no_numeric_value"
            )
    
    def validate_defect_message(
        self,
        message: Optional[str],
        ocr_text: str
    ) -> FieldExtraction:
        """Validate defect message."""
        if not message or message.upper() in ['N/A', 'NONE', 'NIL']:
            return FieldExtraction(None, 0.0, False, reason="no_defect")
        
        if len(message) > 10:
            confidence = self._estimate_confidence(message, ocr_text, False) * 0.7
            return FieldExtraction(
                message, confidence, False,
                reason="freetext_low_confidence"
            )
        else:
            return FieldExtraction(
                message, 0.5, False,
                reason="too_short"
            )
   