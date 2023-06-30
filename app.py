import os
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from werkzeug.utils import secure_filename
import regex as re
import cv2
import numpy as np
import torch

    
apple = "CPU is available"

# Check if CUDA is available
if torch.cuda.is_available():
    device = torch.device("cuda")
    apple = "GPU is available"
else:
    device = torch.device("cpu")

app = FastAPI()

origins = [
    "https://vercel-front-end-git-main-rahilkapa.vercel.app", "https://vercel-front-end-git-main-rahilkapa.vercel.app/predictorform.html", "https://vercel-front-end-git-main-rahilkapa.vercel.app/videoupload.html"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOADS_DIR = "uploads"


@app.post("/results")
async def results(file: UploadFile = File(...)):
    # Extract the filename from the UploadFile object

    filename = secure_filename(file.filename)

    # Prepare the path to save the uploaded image
    save_path = os.path.join(UPLOADS_DIR, filename)

    # Save the uploaded image to the specified path
    with open(save_path, "wb") as buffer:
        buffer.write(await file.read())

    # Prepare the command to call the inference script
    print(save_path)
    cmd = f'python3 recognize-anything/inference_ram.py --image {save_path} --pretrained recognize-anything/pretrained/ram_swin_large_14m.pth'

    # Call the model for inference
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    predicted_object = result.stdout.strip()

    index = predicted_object.find("Image Tags:")
    print(predicted_object)

    print("hello")
    
    if index != -1:
        predicted_object = predicted_object[index+len("Image Tags:"):].strip()
        # Remove Mandarin characters using Unicode range
        predicted_object = re.sub(r'[\u4e00-\u9fff|:/]+', '', predicted_object)

    


    return {"predicted_object": predicted_object + apple}





@app.post("/video_results")
async def video_results(file: UploadFile = File(...)):
    # Extract the filename from the UploadFile object
    filename = secure_filename(file.filename)

    # Prepare the path to save the uploaded video
    save_path = os.path.join(UPLOADS_DIR, filename)

    # Save the uploaded video to the specified path
    with open(save_path, "wb") as buffer:
        buffer.write(await file.read())

    # Open the video file
    cap = cv2.VideoCapture(save_path)
    predictions = []

    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(total_frames)

    while True:
        # Read frame from video
        ret, frame = cap.read()

        # If the frame was not read correctly, then we have reached the end of the video (or there's an issue)
        if not ret:
            break

        if frame_count % 200 == 0:
            # Save frame as a temporary image to run the prediction model
            frame_path = f"{UPLOADS_DIR}/frame{frame_count}.jpg"
            cv2.imwrite(frame_path, frame)

            # Prepare the command to call the inference script
            cmd = f'python3 recognize-anything/inference_ram.py --image {frame_path} --pretrained recognize-anything/pretrained/ram_swin_large_14m.pth'

            # Call the model for inference
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            predicted_object = result.stdout.strip()

            index = predicted_object.find("Image Tags:")
            if index != -1:
                predicted_object = predicted_object[index+len("Image Tags:"):].strip()
                # Remove Mandarin characters using Unicode range
                predicted_object = re.sub(r'[\u4e00-\u9fff|:/]+', '', predicted_object)

            predictions.append({"frame": frame_count, "predicted_object": predicted_object})

        frame_count += 1

    # Release the video file
    cap.release()

    # Remove the uploaded video file
    os.remove(save_path)

    return {"predictions": predictions}

