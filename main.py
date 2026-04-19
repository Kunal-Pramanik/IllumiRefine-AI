from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from processor import HomomorphicFilter
import cv2
import numpy as np
import uvicorn
import os

app = FastAPI(title="IllumiRefine API")

# Enable CORS (Cross-Origin Resource Sharing) 
# This is required so your React frontend (Vercel) can talk to this API (Hugging Face)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize your filter engine
hf = HomomorphicFilter(gl=0.5, gh=1.5, d0=40)

@app.get("/")
def read_root():
    return {"message": "Low-Light Enhancement API is Live!"}

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    # 1. Read the uploaded file bytes
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 2. Save temporarily to process
    temp_input = "temp_api_input.png"
    cv2.imwrite(temp_input, img)
    
    # 3. Run the enhancement engine [cite: 14, 23]
    enhanced_img = hf.enhance(temp_input)
    
    # 4. Convert the processed image back to bytes to send via HTTP
    _, encoded_img = cv2.imencode('.png', enhanced_img)
    
    # Cleanup temporary file
    if os.path.exists(temp_input):
        os.remove(temp_input)
        
    return Response(content=encoded_img.tobytes(), media_type="image/png")

if __name__ == "__main__":
    # Port 8000 is standard for local development
    uvicorn.run(app, host="0.0.0.0", port=8000)