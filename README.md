# Aircraft Journey Form Extractor

A prototype system that converts handwritten aircraft journey forms into structured JSON using OCR and LLM technology.

---

## 🎯 Overview

**Problem**: Aircraft journey forms are filled out (mostly handwritten) after every flight and uploaded to maintenance portals. These need to be converted to structured data for downstream systems.

**Solution**: Automated extraction pipeline using Mistral's OCR + LLM to convert images → JSON with human-in-the-loop validation.

**Deliverable**: Working prototype that processes form images one at a time and outputs structured JSON. The system can handle multiple forms sequentially through the UI.

---

---

## 📋 Scope

### What This Does
- Extracts 8 key fields: Aircraft Model, Registration, Departure/Arrival Airports, Crew, Fuel, Load, Defect Message
- Validates extracted data (IATA codes, aircraft models, numeric ranges)
- Provides UI for human review and correction
- Calculates accuracy metrics (CER, WER, Levenshtein distance)
- Saves data locally and to AWS S3 (optional)
- Accept only image format

### What This Doesn't Do
- Batch processing (processes one image at a time)
- Concurrent multi-image extraction
- Production monitoring/logging
- CI/CD pipeline
- Authentication/authorization
- Image preprocessing (rotation, noise reduction)

---

## 🎓 Assumptions & Limitations

**Assumptions**
- Image input (JPEG,JPG,PNG) and uploaded to the system
- Images are reasonably clear (not heavily damaged)
- Handwriting is legible (even if messy)
- Forms are already oriented correctly
- Internet connection available
- Valid Mistrail API credentials


**Limitations**
- Single image processing (no batch optimization)
- Require internet connection
- API cost/Token limitation

---
  
## 🏗️ Architecture & Design Choices

### Architecture Overview

```sequence
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Streamlit  │────▶│   FastAPI    │────▶│   Mistral   │
│   Frontend  │◀────│   Backend    │◀────│  OCR + LLM  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              ┌──────────┐  ┌──────────┐
              │  Local   │  │ AWS S3   │
              │  Storage │  │  Bucket  │
              └──────────┘  └──────────┘
```

### Key Architectural Decisions
#### 1. Mistral OCR + LLM
**Core Approach: Two-Stage OCR + LLM Pipeline**
- `Mistral OCR (mistral-ocr-latest)` - Raw text extraction with ~90% accuracy
- `Mistral LLM (pixtral-12b-latest)` - Structured parsing with contextual understanding

**Why This Approach?**
- `Mistral OCR` demonstrates superior handwriting recognition vs traditional OCR
- `Contextual LLM` parsing intelligently and do interpretation (e.g: corrects common errors) 
- `End-to-end pipeline` reduces complexity vs multi-tool chains
- `High accuracy `justifies the API cost (do cost analysis here) 

#### 2. FastAPI + Streamlit
The assignment asks for "minimal working path," but forms have ambiguous/missing fields that need human review. So I built:
- **FastAPI**: Stateless API for extraction, validation, and metrics
- **Streamlit**: Simple UI for human-in-the-loop correction
- **Trade-off**: More code complexity, but realistic workflow for production use


### 🔧 Summary of technical stack choices & justification

| **Layer**| **Technology**      |  **Purpose**                        | **Justification** |
|----------|---------------------|-------------------------------------|--------------------|
| Frontend | Streamlit           |  Rapid UI prototyping, data editing | Rapid prototyping, built-in session state, perfect for internal tools |
| Backend  | FastAPI	            |  High-performance async API         | Async support, automatic OpenAPI docs, type safety via Pydantic |
| OCR/LLM  | Mistral AI          |	Advanced handwriting recognition   | State-of-the-art vision model with native OCR support; structured output via JSON schema |
| Storage  | AWS S3 + Local      |	Dual persistence strategy          | Redundancy; local for dev/debugging, S3 for production durability |
| Metrics  | Levenshtein + jiwer |	OCR accuracy evaluation            | Industry-standard OCR quality metrics |
| Data	  | Pydantic	         |  Type-safe data validation          ||



---

## 📂 Project Structure

```
app/src/
├── core/
│   ├── mistral_client.py    # OCR + LLM extraction
│   ├── validator.py          # Field validation logic
│   ├── ocr_evaluator.py      # Metrics compilation
│   └── ocr_metrics.py        # CER/WER calculations
├── api/
│   ├── main.py               # FastAPI app
│   ├── router.py             # Route definitions
│   ├── endpoint.py           # Business logic
│   └── request.py            # Pydantic schemas
├── utils/
│   ├── aws_utils.py          # S3 operations
│   └── utils.py              # Shared utilities
└── settings.py               # Configuration

frontend/
└── app.py                    # Streamlit UI

demo/
└── demo_ocr.py            # Core extraction demo
```

---

## 🔌 API Specification

| Endpoints | Method                | 	Endpoint	Description    |
| --------- | -----------------     |  ----------------------  |
|POST       |	/extract/	         | Upload form image, return structured JSON |
|POST       |	/save-extracted/     | Save OCR-extracted data |
|POST       |	/save-edited/	      | Save human-corrected data |
|POST       |	/evaluate-ocr/	      | Compare OCR vs ground truth with metrics and compile all evaluation data |
|POST       |	/save-uploaded-form/	| Store original form file |


## 🔄 Processing Pipeline

**Phase 1: OCR Extraction**
1. Image Upload → Base64 Encoding → Mistral OCR
2. Raw Text (Markdown) → Mistral LLM → Structured JSON
3. Auto-generate Upload_ID & Timestamps

**Phase 2: Data Validation**
1. Field-by-field validation (IATA codes, aircraft models, etc.)
2. Confidence scoring based on validation results
3. Quality flags for human review

**Phase 3: User Interaction**
1. Frontend displays extracted data
2. User edits/corrects fields
3. Both versions preserved (extracted + edited)

**Phase 4: Evaluation & Storage**
1. Compare extracted vs edited data
2. Calculate accuracy metrics (CER, WER, Levenshtein)
3. Save all artifacts (local + S3)
4. Generate comprehensive evaluation report




---

## 📊 Performance

**Sample Results** (from provided test image):

The system successfully extracted all 8 fields from the sample aircraft journey form:

```json
{
  "Aircraft_Model": "Airbus A320",
  "Registration_Number": "9M-XX1",
  "Departure_Airport": "KUL",
  "Arrival_Airport": "SIN",
  "Crew": 4,
  "Fuel": "12k",
  "Load": 150,
  "Defect_Message": null
}
```

**Validation Results**:
- All extracted fields passed validation rules
- IATA codes validated correctly (KUL, SIN)
- Registration format matched expected pattern
- Numeric fields within reasonable ranges

**Processing Time**: ~3-5 seconds per form (OCR + LLM parsing)

**Accuracy Metrics**:
The system includes CER (Character Error Rate), WER (Word Error Rate), and Levenshtein distance calculations to compare OCR output against ground truth when human corrections are provided.

**Limitations of Current Testing**:
- Tested on 1 sample form only (limited dataset)
- Need more diverse samples to validate performance across:
  - Different handwriting styles
  - Varying image quality
  - Different aircraft types
  - Edge cases (missing/ambiguous fields)

---


## 📦 Installation & Setup


### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd aircraft-journey-extractor
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create Required Directories [Optional]
```bash
# Create data directories
mkdir -p data/uploads
mkdir -p data/extracted
mkdir -p data/edited
mkdir -p data/results

```

## Environment Configuration

### 1. Create `.env` File
Create a `.env` file in the project root directory:

```bash
touch .env
```

### 2. Add Environment Variables
Open `.env` and add the following variables:

```env
# Mistral AI Configuration (Required)
MISTRAL_API_KEY=your_mistral_api_key_here

# AWS Configuration (Optional - for S3 storage)
AWS_ACCESS_KEY=your_aws_access_key_here
AWS_SECRET_KEY=your_aws_secret_key_here
BUCKET_NAME=your_s3_bucket_name
REGION_NAME=ap-southeast-1

# Application Configuration (Optional)
DEBUG=False
LOG_LEVEL=INFO
```

### 3. Configuration Notes

#### Mistral API Key (Required)
```env
MISTRAL_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxx
```

#### AWS Credentials (Optional)
If you want to use S3 for storage:
```env
AWS_ACCESS_KEY=AKIAXXXXXXXXXX
AWS_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx
BUCKET_NAME=aircraft-journey-forms
REGION_NAME=ap-southeast-1
```

**Note:** The application works without AWS credentials - files will be stored locally only.

### 4. Verify Environment Variables
```bash
# Check if .env file is properly loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Mistral Key:', 'SET' if os.getenv('MISTRAL_API_KEY') else 'NOT SET')"
```

## Running the Application

### Option 1: Run Backend and Frontend Separately (Recommended)

#### Terminal 1 - Start Backend API
```bash
# Navigate to project root
cd /path/to/aircraft-journey-extractor

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start FastAPI backend (run from root)
cd aircraft-journey-extractor
uvicorn app.src.api.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Terminal 2 - Start Streamlit Frontend
```bash
# Navigate to project root
cd /path/to/aircraft-journey-extractor

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start Streamlit frontend
cd frontend
streamlit run app.py
```

You should see:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Option 2: Quick Start Script
Create a `start.sh` script (macOS/Linux):

```bash
#!/bin/bash

# Start backend
cd app/src/api && uvicorn main:app --reload --port 8000 &

# Wait for backend to start
sleep 3

# Start frontend
cd frontend && streamlit run app.py
```

Make it executable:
```bash
chmod +x start.sh
./start.sh
```

## Verification

### 1. Check Backend API
Open browser and navigate to:
- API Health Check: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

Expected response:
```json
{
  "status": "online",
  "message": "Aircraft Journey Form Extractor API"
}
```

### 2. Check Frontend
Open browser and navigate to:
- Streamlit App: http://localhost:8501

You should see the "Aircraft Journey Form Extractor" interface.

### 3. Test with Sample Image
1. Upload a test form image
2. Click "Extract Form Data"
3. Verify extracted data appears
4. Edit if needed
5. Click "Save All Data"

## Troubleshooting

### Common Issues

#### 1. Missing MISTRAL_API_KEY Error
```
EnvironmentError: Missing MISTRAL_API_KEY in environment variables
```

**Solution:**
- Verify `.env` file exists in project root
- Check `MISTRAL_API_KEY` is set correctly
- Restart the backend server

#### 2. Module Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
pip install -r requirements.txt
```

#### 3. Port Already in Use
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn main:app --port 8001
```

#### 4. AWS Credentials Not Found (Non-Critical)
```
❌ AWS credentials not found.
```

**Solution:**
- If you don't need S3 storage, ignore this warning
- Otherwise, add AWS credentials to `.env` file

#### 5. Connection Refused (Frontend → Backend)
```
❌ Connection Error: Could not connect to backend
```

**Solution:**
- Ensure backend is running on http://localhost:8000
- Check backend logs for errors
- Verify no firewall blocking port 8000

### Debugging Tips

#### Enable Debug Mode
Add to `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

#### Check Backend Logs
```bash
# View backend console output
# Logs appear in terminal where uvicorn is running
```

#### Test API Directly
```bash
# Test extraction endpoint
curl -X POST "http://localhost:8000/extract/" \
  -H "accept: application/json" \
  -F "file=@/path/to/test_image.jpg"
```
### 📊 Sample Output
```JSON
{
  "extracted_data": {
    "Upload_ID": "AJ-20251114-203901-7f8bdabe",
    "Extracted_AT": "2025-11-14T20:39:01.473560",
    "Aircraft_Model": "Airbus A320",
    "Registration_Number": "9M-XX1",
    "Departure_Airport": "KUL",
    "Arrival_Airport": "SIN",
    "Crew": 4,
    "Fuel": "12k",
    "Load": 150,
    "Defect_Message": null
  },
  "data_validation": {
    "Aircraft_Model": {
      "value": "Airbus A320",
      "confidence": 1.0,
      "validated": true,
      "validation_method": "known_model"
    },
    "Arrival_Airport": {
      "value": "SIN",
      "confidence": 0.95,
      "validated": true,
      "validation_method": "iata_validation",
      "original_ocr": "$IN",
      "correction_applied": true
    }
  },
  "data_validation": {..},
  "metadata": {
    "overall_confidence": 0.911,
    "fields_extracted": 8,
    "fields_validated": 7,
    "requires_human_review": false,
    "flagged_fields": []
  }
}
```

## Additional Resources
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Streamlit Documentation**: https://docs.streamlit.io
- **Mistral AI Documentation**: https://docs.mistral.ai
- **AWS S3 Setup**: https://docs.aws.amazon.com/s3



Stremlit landing page: 
![alt text](docs/img/image.png)

Once user upload form:
![alt text](docs/img/image2.png)

Extraction, review and data saving:
![alt text](docs/img/image3.png)


