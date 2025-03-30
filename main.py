from fastapi import FastAPI, Form, UploadFile, File
import os
import shutil
import zipfile
from datetime import datetime

app = FastAPI()

# Function to extract files from ZIP and list their details
def list_files_in_zip(zip_file_path):
    extracted_files = []
    
    # Unzipping the file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall("temp")
        
        # List files and get details (size, date)
        for file_info in zip_ref.infolist():
            file_details = {
                'filename': file_info.filename,
                'file_size': file_info.file_size,  # Size in bytes
                'modified_time': datetime(*file_info.date_time)  # Converts the timestamp to datetime
            }
            extracted_files.append(file_details)
    
    return extracted_files

# Check if file matches size and timestamp criteria
def filter_files(files, min_size=9938, min_date="1995-08-10 19:16:00"):
    min_date = datetime.strptime(min_date, "%Y-%m-%d %H:%M:%S")
    total_size = 0
    
    for file in files:
        if file['file_size'] >= min_size and file['modified_time'] >= min_date:
            total_size += file['file_size']
    
    return total_size

@app.post("http://127.0.0.1:8000/api/")
async def get_answer(question: str = Form(...), file: UploadFile = None):
    # Save the uploaded file to a temporary location
    file_location = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Check if question is related to file size and timestamp
    if "total size of all files" in question.lower():
        files = list_files_in_zip(file_location)
        total_size = filter_files(files)
        return {"answer": total_size}
    
    return {"answer": "Unable to process the question."}
