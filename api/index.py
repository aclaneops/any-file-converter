import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel serverless functions only allow writing to /tmp
UPLOAD_DIR = "/tmp/uploads"
OUTPUT_DIR = "/tmp/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def stub_conversion(input_path, output_path, msg="Conversion supported soon"):
    with open(output_path, "w") as f:
        f.write(f"This is a placeholder. {msg}")

@app.post("/api/convert")
async def convert_file(file: UploadFile = File(...), conversion_type: str = Form(...)):
    try:
        input_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}_converted"
        
        if conversion_type == "pdf-to-word":
            output_path = os.path.join(OUTPUT_DIR, output_filename + ".docx")
            stub_conversion(input_path, output_path, "PDF to Word is temporarily disabled on Vercel to prevent crashes.")
        elif conversion_type == "pdf-to-excel":
            output_path = os.path.join(OUTPUT_DIR, output_filename + ".xlsx")
            stub_conversion(input_path, output_path, "PDF to Excel is temporarily disabled due to Vercel memory limits.")
        elif conversion_type == "word-to-ppt":
            output_path = os.path.join(OUTPUT_DIR, output_filename + ".pptx")
            stub_conversion(input_path, output_path, "Word to PPT requires advanced parsing.")
        elif conversion_type == "ppt-to-word":
            output_path = os.path.join(OUTPUT_DIR, output_filename + ".docx")
            stub_conversion(input_path, output_path, "PPT to Word requires extracting slide text.")
        elif conversion_type == "image-to-word":
            output_path = os.path.join(OUTPUT_DIR, output_filename + ".docx")
            stub_conversion(input_path, output_path, "Requires Tesseract OCR installed on the system.")
        elif conversion_type == "compress":
            # Simple mockup for compression (just copy for now)
            output_path = os.path.join(OUTPUT_DIR, "compressed_" + file.filename)
            shutil.copy(input_path, output_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported conversion type")
            
        return FileResponse(output_path, filename=os.path.basename(output_path))
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
