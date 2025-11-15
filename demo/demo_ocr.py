"""
Demo script for Aircraft Journey Form Extractor OCR
Demonstrates the complete extraction, validation, and evaluation pipeline
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.src.core.mistral_client import MistralFormExtractor
from app.src.core.validator import FieldValidator
from app.src.core.ocr_evaluator import ocr_overall_evaluation
from app.src.utils.utils import read_json_to_dict


class OCRDemo:
    """Demo class for OCR extraction and evaluation"""
    
    def __init__(self):
        self.extractor = MistralFormExtractor()
        self.validator = FieldValidator()
        self.output_dir = Path("demo_output")
        self.output_dir.mkdir(exist_ok=True)
        
    def print_header(self, title: str):
        """Print formatted section header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")
    
    def print_field(self, name: str, value: Any, indent: int = 0):
        """Print formatted field"""
        spacing = "  " * indent
        print(f"{spacing}📋 {name:25s}: {value}")
    
    def extract_from_image(self, image_path: str) -> tuple[Dict[str, Any], str]:
        """
        Extract data from an image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (extracted_data_dict, raw_ocr_markdown)
        """
        self.print_header(f"📸 Processing Image: {Path(image_path).name}")
        
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        print("🔍 Running Mistral OCR extraction...")
        parsed_form, ocr_text = self.extractor.structured_ocr(image_path)
        
        # Convert to dictionary
        extracted_data = json.loads(parsed_form.json())
        
        print("✅ Extraction complete!\n")
        
        return extracted_data, ocr_text
    
    def display_extracted_data(self, data: Dict[str, Any]):
        """Display extracted data in a formatted way"""
        self.print_header("📋 Extracted Form Data")
        
        self.print_field("Upload ID", data.get("Upload_ID", "N/A"))
        self.print_field("Extracted At", data.get("Extracted_AT", "N/A"))
        print()
        
        # Aircraft Information
        print("  ✈️  Aircraft Information:")
        self.print_field("Model", data.get("Aircraft_Model", "N/A"), indent=2)
        self.print_field("Registration", data.get("Registration_Number", "N/A"), indent=2)
        print()
        
        # Flight Information
        print("  🛫 Flight Information:")
        self.print_field("Departure", data.get("Departure_Airport", "N/A"), indent=2)
        self.print_field("Arrival", data.get("Arrival_Airport", "N/A"), indent=2)
        print()
        
        # Operational Data
        print("  📊 Operational Data:")
        self.print_field("Crew Count", data.get("Crew", "N/A"), indent=2)
        self.print_field("Fuel", data.get("Fuel", "N/A"), indent=2)
        self.print_field("Load", data.get("Load", "N/A"), indent=2)
        print()
        
        # Defect Message
        print("  ⚠️  Maintenance:")
        defect = data.get("Defect_Message", "None")
        if defect and defect.strip() and defect.upper() not in ['N/A', 'NONE', 'NIL']:
            print(f"    ⚠️  Defect: {defect}")
        else:
            print(f"    ✅ No defects reported")
    
    def display_validation_results(self, validation_data: Dict[str, Any]):
        """Display validation results for each field"""
        self.print_header("🔍 Field Validation Results")
        
        for field_name, field_info in validation_data.items():
            confidence = field_info.get('confidence', 0)
            validated = field_info.get('validated', False)
            value = field_info.get('value')
            
            # Status indicator
            if confidence >= 0.9:
                status = "✅ EXCELLENT"
            elif confidence >= 0.7:
                status = "✓  GOOD"
            elif confidence >= 0.5:
                status = "⚠️  MEDIUM"
            else:
                status = "❌ LOW"
            
            print(f"\n  {field_name}:")
            print(f"    Value: {value}")
            print(f"    Status: {status} ({confidence:.1%} confidence)")
            print(f"    Validated: {'Yes' if validated else 'No'}")
            
            if field_info.get('validation_method'):
                print(f"    Method: {field_info['validation_method']}")
            
            if field_info.get('reason'):
                print(f"    ⚠️  Reason: {field_info['reason']}")
    
    def display_metadata(self, metadata: Dict[str, Any]):
        """Display overall metadata and summary"""
        self.print_header("📊 Overall Assessment")
        
        confidence = metadata.get('overall_confidence', 0)
        print(f"  Overall Confidence: {confidence:.1%}")
        print(f"  Fields Extracted:   {metadata.get('fields_extracted', 0)}/{metadata.get('total_fields', 0)}")
        print(f"  Fields Validated:   {metadata.get('fields_validated', 0)}/{metadata.get('total_fields', 0)}")
        print(f"  Human Review:       {'Required' if metadata.get('requires_human_review') else 'Not Required'}")
        
        flagged = metadata.get('flagged_fields', [])
        if flagged:
            print(f"\n  ⚠️  Flagged Fields: {', '.join(flagged)}")
        else:
            print(f"\n  ✅ All fields passed validation")
    
    def display_ocr_text(self, ocr_text: str):
        """Display raw OCR markdown"""
        self.print_header("📄 Raw OCR Output (Markdown)")
        print(ocr_text)
    
    def save_results(self, results: Dict[str, Any], filename_prefix: str):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"{filename_prefix}_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        return output_file
    
    def run_full_demo(self, image_path: str, ground_truth_path: str = None):
        """
        Run complete demo: extraction, validation, and optionally evaluation
        
        Args:
            image_path: Path to the form image
            ground_truth_path: Optional path to ground truth JSON for comparison
        """
        print("\n" + "🚀 " * 35)
        print("  AIRCRAFT JOURNEY FORM EXTRACTOR - OCR DEMO")
        print("🚀 " * 35)
        
        try:
            # Step 1: Extract from image
            extracted_data, ocr_text = self.extract_from_image(image_path)
            
            # Step 2: Display extracted data
            self.display_extracted_data(extracted_data)
            
            # Step 3: Display raw OCR text
            self.display_ocr_text(ocr_text)
            
            # Step 4: Validate and get comprehensive results
            if ground_truth_path and Path(ground_truth_path).exists():
                print(f"\n📖 Loading ground truth from: {ground_truth_path}")
                ground_truth = read_json_to_dict(ground_truth_path)
                
                if ground_truth:
                    # Run full evaluation with ground truth
                    comprehensive_results = ocr_overall_evaluation(
                        extracted_data, 
                        ground_truth, 
                        ocr_text
                    )
                    
                    # Display validation
                    self.display_validation_results(
                        comprehensive_results['data_validation']
                    )
                    
                    # Display metadata
                    self.display_metadata(comprehensive_results['metadata'])
                    
                    # Display accuracy metrics
                    self.display_accuracy_metrics(
                        comprehensive_results['data_assessment']
                    )
                    
                    # Save comprehensive results
                    filename = Path(image_path).stem
                    self.save_results(comprehensive_results, f"comprehensive_{filename}")
                else:
                    print("⚠️  Failed to load ground truth file")
            else:
                # Just validation without ground truth comparison
                print("\n📝 Running validation only (no ground truth provided)...")
                
                # Create a dummy ground truth (same as extracted) for validation
                validation_results = ocr_overall_evaluation(
                    extracted_data,
                    extracted_data,  # Use extracted as ground truth
                    ocr_text
                )
                
                self.display_validation_results(
                    validation_results['data_validation']
                )
                
                self.display_metadata(validation_results['metadata'])
                
                # Save results
                filename = Path(image_path).stem
                self.save_results(extracted_data, f"extracted_{filename}")
                # self.save_results(validation_results, f"evaluation_{filename}")
                
            
            self.print_header("✅ Demo Complete!")
            print("  Check the 'demo_output' folder for saved results.\n")
            
        except FileNotFoundError as e:
            print(f"\n❌ Error: {e}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    def display_accuracy_metrics(self, assessment: Dict[str, Any]):
        """Display accuracy metrics comparing OCR vs ground truth"""
        self.print_header("🎯 Accuracy Assessment (OCR vs Ground Truth)")
        
        # Skip Upload_ID
        upload_id = assessment.get('Upload_ID', 'N/A')
        print(f"  Upload ID: {upload_id}\n")
        
        fields = [k for k in assessment.keys() if k != 'Upload_ID']
        
        for field_name in fields:
            field_data = assessment[field_name]
            
            correct = field_data.get('Correct', 0)
            cer = field_data.get('CER', 0)
            wer = field_data.get('WER', 0)
            lev = field_data.get('Levenshtein', 0)
            
            status = "✅" if correct == 1.0 else "❌"
            
            print(f"  {status} {field_name}:")
            print(f"      Ground Truth: {field_data.get('Ground_Truth', 'N/A')}")
            print(f"      OCR Output:   {field_data.get('OCR_Output', 'N/A')}")
            print(f"      Accuracy:     {correct:.1%}")
            print(f"      CER:          {cer:.4f}")
            print(f"      WER:          {wer:.4f}")
            print(f"      Levenshtein:  {lev}")
            print()


def main():
    """Main entry point for demo script"""
    
    # Initialize demo
    demo = OCRDemo()
    
    # Example usage scenarios
    print("\n" + "="*70)
    print("  Demo Usage Examples")
    print("="*70)
    print("\n1. Extract from image only:")
    print("   python demo_ocr.py <image_path>")
    print("\n2. Extract and compare with ground truth:")
    print("   python demo_ocr.py <image_path> <ground_truth_json>")
    print("\n3. Interactive mode (no arguments):")
    print("   python demo_ocr.py")
    print("="*70 + "\n")
    
    # Check command line arguments
    if len(sys.argv) >= 2:
        # Command line mode
        image_path = sys.argv[1]
        ground_truth_path = sys.argv[2] if len(sys.argv) >= 3 else None
        
        demo.run_full_demo(image_path, ground_truth_path)
        
    else:
        # Interactive mode
        print("📝 Interactive Mode\n")
        
        # Get image path
        while True:
            image_path = input("Enter path to form image (or 'q' to quit): ").strip()
            
            if image_path.lower() == 'q':
                print("👋 Goodbye!")
                sys.exit(0)
            
            if Path(image_path).exists():
                break
            else:
                print(f"❌ File not found: {image_path}")
                print("Please try again.\n")
        
        # Get ground truth path (optional)
        ground_truth_path = input(
            "Enter path to ground truth JSON (or press Enter to skip): "
        ).strip()
        
        if not ground_truth_path:
            ground_truth_path = None
        elif not Path(ground_truth_path).exists():
            print(f"⚠️  Ground truth file not found: {ground_truth_path}")
            print("Continuing without ground truth...\n")
            ground_truth_path = None
        
        # Run demo
        demo.run_full_demo(image_path, ground_truth_path)


if __name__ == "__main__":
    main()
