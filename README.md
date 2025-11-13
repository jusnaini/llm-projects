# Aircraft Journey Form Extractor

A lightweight backend service that extracts structured data from handwritten aircraft journey summary forms using OCR and intelligent field parsing.

## 🎯 Executive Summary

## 📋 Assumptions & Scope

## 🏗️ Approach & Design Decisions


## 📦 Installation & Setup

## 🔌 API Specification



------------------
How It Works Now:
------------------
1. User uploads file → Frontend stores bytes in session state
2. Click "Extract" → Backend:
   1. Saves file locally to ../data/uploads/
   2. Runs OCR extraction
   3. delete save file (will re-save later)
   4. Returns extracted data + file info
3. On Frontend, the extracted data auto-filled for editing where user could edit all the extracted values
4. Click "Save All Data" → Backend:
   1. Saves extracted JSON locally and to S3 
   2. Saves edited JSON locally and to S3
   3. Re-saves the uploaded form with the Upload_ID name locally and to s3
5. At Backend also, the ocr performance was calculated and uploaded to S3 as .csv file for performance monitoring later



```sequence
project/
├── backend/
│   └── app/
│       ├── api/routes/          # ✅ Separated routes
│       ├── core/                # ✅ Config management
│       ├── models/              # ✅ Data models
│       ├── services/            # ✅ Business logic
│       │   ├── ocr/             # ✅ OCR logic isolated
│       │   ├── storage/         # ✅ Storage abstraction
│       │   └── metrics/         # ✅ Metrics calculation
│       └── utils/
├── frontend/
│   ├── components/              # ✅ Reusable UI components
│   └── utils/                   # ✅ API client
└── data/
```

Stremlit landing page: 
![alt text](docs/img/image.png)

Once user upload form:
![alt text](docs/img/image2.png)

Extraction and data saving:
![alt text](docs/img/image3.png)


