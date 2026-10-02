import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import traceback

# Conversion functions
def pdf_to_word(input_path, output_path):
    from pdf2docx import Converter
    cv = Converter(input_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()

def pdf_to_excel(input_path, output_path):
    import pdfplumber
    import pandas as pd
    with pdfplumber.open(input_path) as pdf:
        all_data = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_data.extend(table)
    if not all_data:
        raise Exception("No tables found in PDF")
    df = pd.DataFrame(all_data[1:], columns=all_data[0])
    df.to_excel(output_path, index=False)

# Add basic stubs for complex ones
def stub_conversion(input_path, output_path, msg="Conversion supported soon"):
    with open(output_path, "w") as f:
        f.write(f"This is a placeholder. {msg}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
            pdf_to_word(input_path, output_path)
        elif conversion_type == "pdf-to-excel":
            output_path = os.path.join(OUTPUT_DIR, output_filename + ".xlsx")
            pdf_to_excel(input_path, output_path)
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

# Mount static files for the frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
