# Fix the path for relative imports
# import sys 
# import os
# sys.path.append(os.path.dirname(__file__))
import sys
from pathlib import Path

# Add the project root (app/src) to PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .router import router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(title="Aircraft Journey Form Extractor API")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include router
    app.include_router(router)
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)