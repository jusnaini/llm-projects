"""
Aircraft Journey Form Extractor using Mistral OCR.
Converts handwritten aircraft journey forms into structured JSON.
"""

import base64
from pathlib import Path
from mistralai import Mistral, ImageURLChunk, TextChunk
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import os
from ..utils.utils import AircraftJourneyForm
from ..settings import MISTRAL_API_KEY
import uuid

class MistralFormExtractor:
    def __init__(self):
        """
        Initialize the Mistral extractor.
        
        Args:
            api_key: Mistral API key (defaults to env variable)
        """
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        print("✅ Mistral client initialized")

    def encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 data URL.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64-encoded data URL
        """
        image_file = Path(image_path)
        encoded_image = base64.b64encode(image_file.read_bytes()).decode()
        return f"data:image/jpeg;base64,{encoded_image}"

    def extract_ocr(self, image_path: str) -> str:
        # Step 1: OCR extraction
        print("Running Mistral OCR...")
        encoded = self.encode_image(image_path)
        response = self.client.ocr.process(
            document=ImageURLChunk(image_url=encoded),
            model="mistral-ocr-latest"
        )
        return response.pages[0].markdown

    def parse_to_json(self, ocr_text: str, image_data: str) -> AircraftJourneyForm:
        # Step 2: LLM parsing into structured JSON
        print("Parsing with Mistral LLM...")
        response = self.client.chat.parse(
            model="pixtral-12b-latest",
            messages=[
                {
                    "role": "user",
                    "content": [
                        ImageURLChunk(image_url=image_data),
                        TextChunk(text=f"Convert OCR text to JSON:\n{ocr_text}")
                    ]
                }
            ],
            response_format=AircraftJourneyForm,
            temperature=0
        )
        parsed = response.choices[0].message.parsed
        parsed.Upload_ID = f"AJ-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
        parsed.Extracted_AT = datetime.now().isoformat()
        return parsed
        
    def structured_ocr(self, image_path: str) -> Tuple[AircraftJourneyForm, str]:
        """
        Extract form data using Mistral OCR + LLM.
        
        Args:
            image_path: Path to form image
            
        Returns:
            Tuple of (parsed_form, raw_ocr_markdown)
        """
        image_file = Path(image_path)
        assert image_file.is_file(), "Provided image path does not exist."
        
        ocr_text = self.extract_ocr(image_path)
        encoded_image = self.encode_image(image_path)
        parsed_form = self.parse_to_json(ocr_text, encoded_image)
        
        return parsed_form,ocr_text
