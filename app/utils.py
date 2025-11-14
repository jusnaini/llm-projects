import re
import json
import base64
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field

# Known IATA airport codes (subset for validation)
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

AIRCRAFT_FIELDS = [
    'Aircraft_Model', 
    'Registration_Number',
    'Departure_Airport', 
    'Arrival_Airport', 
    'Crew', 
    'Fuel', 
    'Load',
    'Defect_Message']

@dataclass
class FieldExtraction:
    """Represents an extracted field with metadata."""
    value: Any
    confidence: float
    validated: bool
    validation_method: Optional[str] = None
    reason: Optional[str] = None


class AircraftJourneyForm(BaseModel):
    """Pydantic model for Mistral structured output."""
    Upload_ID: str = Field(default="")
    Extracted_AT: str = Field(default="")
    Aircraft_Model: Optional[str] = None
    Registration_Number: Optional[str] = None
    Departure_Airport: Optional[str] = None
    Arrival_Airport: Optional[str] = None
    Crew: Optional[int] = None
    Fuel: Optional[str] = None
    Load: Optional[int] = None
    Defect_Message: Optional[str] = None


import json

def read_json_to_dict(filepath):
    """
    Reads a JSON file and returns its content as a Python dictionary.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        dict: A Python dictionary representing the JSON data.
              Returns None if the file is not found or if there's a JSON decoding error.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None