import cv2
from PIL import Image
import io
import os
import base64
import numpy as np
from image_to_textbase64 import image_to_textbase64
from textclass import textclass
from query import query_info

def preprocess_frame(frame, target_size=(224, 224)):
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Resize the frame
    frame_resized = cv2.resize(frame_rgb, target_size)
    
    # Normalize the frame
    frame_normalized = frame_resized / 255.0
    
    return frame_normalized

def video_to_text(video_path, prompt, query=''):
    threshold=0.5
    max_frames=10
    cap = cv2.VideoCapture(video_path)
    
    analysis = ''
    frame_count = 0
    processed_frames = 0

    # Read the first frame
    ret, prev_frame = cap.read()
    if not ret:
        print("Failed to open video.")
        return

    # Convert the first frame to HSV color space
    prev_hist = cv2.calcHist([cv2.cvtColor(prev_frame, cv2.COLOR_BGR2HSV)], [0, 1, 2], None, [50, 60, 60], [0, 180, 0, 256, 0, 256])
    cv2.normalize(prev_hist, prev_hist)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the current frame to HSV color space
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        curr_hist = cv2.calcHist([hsv_frame], [0, 1, 2], None, [50, 60, 60], [0, 180, 0, 256, 0, 256])
        cv2.normalize(curr_hist, curr_hist)

        # Compute histogram comparison using correlation
        hist_diff = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_CORREL)
        
        # Check if the difference exceeds the threshold
        if hist_diff < threshold:  # lower value indicates higher difference
            # Preprocess the frame
            frame_preprocessed = preprocess_frame(frame)

            # Save the frames
            frame_filename = os.path.join('test_frames', f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_filename, frame)
            
            # Convert the preprocessed frame to an image
            image = Image.fromarray((frame_preprocessed * 255).astype(np.uint8))
            
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            # image.show() # Convert back to uint8 for display


            # Get the analysis for the frame
            if query:
                analysis += image_to_textbase64(img_base64, query) + ' '
            else:
                analysis += image_to_textbase64(img_base64, prompt) + ' '
            
            processed_frames += 1
            if processed_frames >= max_frames:
                break

        # Update previous histogram and frame number
        prev_hist = curr_hist
        frame_count += 1
    
    cap.release()

    # Get the category from the analysis
    if query:
        print(analysis)
        data = query_info(analysis)
    else:
        data = textclass(analysis)
    
    return data