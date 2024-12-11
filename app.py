import streamlit as st
import cv2
import easyocr
from fuzzywuzzy import process
import csv
import os

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])

# List of brands and categories (same as before)
brands_categories = {
    'Food & Beverages': [...],  # Truncated for brevity
    'Personal Care': [...],
    'Household Items': [...],
    'Baby Care': [...],
    'Electronics & Accessories': [...]
}

# Function to detect brand and category
def detect_brand(text, brands_categories, threshold=70):
    detected_brands = []
    detected_category = None

    for category, brands in brands_categories.items():
        match, score = process.extractOne(text, brands)
        if score > threshold:
            detected_brands.append(match)
            detected_category = category
            break

    return detected_brands[0] if detected_brands else "N/A", detected_category if detected_category else "N/A"

# Main Streamlit App
def main():
    st.title("Real-Time Brand Detection")
    st.sidebar.header("Options")
    start_detection = st.sidebar.button("Start Detection")

    if start_detection:
        cap = cv2.VideoCapture(0)  # Open the camera
        if not cap.isOpened():
            st.error("Error: Unable to access the camera.")
            return

        results = []
        frame_no = 0
        last_detected = ""

        while True:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture frame.")
                break

            # Convert frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Extract text using EasyOCR
            result = reader.readtext(gray_frame, detail=0)
            text = ' '.join(result)

            # Detect brand and category
            detected_brand, detected_category = detect_brand(text, brands_categories)

            if detected_brand != last_detected:
                last_detected = detected_brand
                frame_no += 1
                results.append({
                    'Frame': frame_no,
                    'Detected Brand': detected_brand,
                    'Category': detected_category
                })

                # Display results
                st.write(f"**Frame {frame_no}**: Detected Brand: {detected_brand}, Category: {detected_category}")

            # Display video frame with annotations
            cv2.putText(frame, f"Brand: {detected_brand}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Category: {detected_category}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            st.image(frame, channels="BGR")

        cap.release()

if __name__ == "__main__":
    main()
