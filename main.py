from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from processor import SCIFilter
import cv2
import numpy as np
import uvicorn
import os

app = FastAPI(title="IllumiRefine SCI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Deep Learning Model
# Note: Ensure the weights folder exists with the .pt file!
sci = SCIFilter(weights_path='weights/difficult.pt')

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    temp_input = "temp_sci_input.png"
    cv2.imwrite(temp_input, img)
    
    # Process with AI
    enhanced_img = sci.enhance(temp_input)
    
    _, encoded_img = cv2.imencode('.png', enhanced_img)
    if os.path.exists(temp_input):
        os.remove(temp_input)
        
    return Response(content=encoded_img.tobytes(), media_type="image/png")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)