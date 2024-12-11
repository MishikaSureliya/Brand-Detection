import streamlit as st
import easyocr
import pandas as pd
import numpy as np
from PIL import Image
from fuzzywuzzy import process
import os

# Initialize the EasyOCR reader
reader = easyocr.Reader(['en'])

# List of brands to detect and categorize by their type
brands_categories = {
    'Food & Beverages': ['Kurkure', 'Lays', 'Tedhe Medhe', 'Ruffles', 'Cadbury Dairy Milk', 'Bingo', 'Mad Angles',
                         'RUFFLES', 'Diamond', 'Kelloggs', 'CHOCOS', 'Priniti', 'Dairy Milk', 'Uncle Chipps', 'Nestle',
                         'Doritos', 'BRU', 'Pepsi', 'MAGGI', 'Magnum', 'Bisleri', 'Kinley', 'Himalayan', 'Bailley',
                         'Evian', 'Aquafina', 'Divya Jal', 'Patanjali', 'Qua', 'Rail Neer', 'Amul', 'Baskin Robbins',
                         'Havmor', 'Mother Dairy', 'Arun Ice Cream', 'Tata Sampann', 'Aashirvaad', 'Catch', 'Sunrise',
                         'Everest', 'Organic Tattva', 'MDH', 'Patanjali', 'Paper Boat', 'Urban Platter', 'Nutraj',
                         'Wingreens Schezwan', 'Kissan Knorr Schezwan', 'Ching’s Secret Schezwan', 'Gusto Foods Schezwan',
                         'Kopiko', 'Skittles'],
    'Personal Care': ['Pantene', 'Dove', 'Colgate', 'NIVEA', 'Himalaya', 'Dettol', 'Lifebuoy', 'LUX', 'INTERNATIONAL LUX',
                      'Pears', 'Pears naturale'],
    'Household Items': ['Harpic', 'Lizol', 'Vim']
}

# Function to detect brand names using fuzzy matching and categorize them
def detect_brand(text, brands_categories, threshold=70):
    detected_brands = []
    detected_category = None

    for category, brands in brands_categories.items():
        match, score = process.extractOne(text, brands)
        if score > threshold:  # Only consider it a match if the score is above threshold
            detected_brands.append(match)
            detected_category = category
            break  # Stop after finding the first match

    return detected_brands[0] if detected_brands else "N/A", detected_category if detected_category else "N/A"

# Streamlit app
def main():
    st.title("Image Text Extraction and Brand Categorization")

    uploaded_files = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    if uploaded_files:
        results = []

        for uploaded_file in uploaded_files:
            # Open the uploaded image
            image = Image.open(uploaded_file)

            # Display the image
            st.image(image, caption=f"Uploaded Image: {uploaded_file.name}", use_column_width=True)

            # Convert image to array
            img_array = np.array(image)

            # Extract text using EasyOCR
            result = reader.readtext(img_array, detail=0)
            extracted_text = ' '.join(result)

            # Display extracted text
            st.write(f"**Extracted Text from {uploaded_file.name}:** {extracted_text}")

            # Detect brand names and categories using fuzzy matching
            detected_brand, detected_category = detect_brand(extracted_text, brands_categories)

            # Append results
            results.append({
                "Image": uploaded_file.name,
                "Detected Brand": detected_brand,
                "Category": detected_category
            })

        # Display results as a DataFrame
        if results:
            df = pd.DataFrame(results)
            st.write("### Detected Brands and Categories:")
            st.dataframe(df)

            # Allow the user to download the results as a CSV file
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name='extracted_details.csv',
                mime='text/csv'
            )

if __name__ == "__main__":
    main()
