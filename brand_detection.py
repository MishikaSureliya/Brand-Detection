import easyocr
import cv2
import pandas as pd
import numpy as np
from PIL import Image
import os
from fuzzywuzzy import process

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

# Extract details from images in a specified folder
def extract_details_from_images(image_folder):
    results = []

    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('png', 'jpg', 'jpeg')):
            print(f"Processing: {filename}")

            # Read the image
            image_path = os.path.join(image_folder, filename)
            image = Image.open(image_path)
            img = np.array(image)

            # Extract text using EasyOCR
            result = reader.readtext(img, detail=0)
            text = ' '.join(result)

            print(f"Extracted Text: {text}")  # Debug: Print extracted text for analysis

            # Detect brand names and categories using fuzzy matching
            detected_brand, detected_category = detect_brand(text, brands_categories)

            # Store the result
            results.append({
                "Image": filename,
                "Detected Brand": detected_brand,
                "Category": detected_category
            })

    # Create DataFrame from results
    df = pd.DataFrame(results)
    print(df)
    return df

# Example usage
if __name__ == "__main__":
    # Path to the folder containing images
    image_folder = "path_to_your_images_folder"

    if not os.path.exists(image_folder):
        print(f"Error: The folder '{image_folder}' does not exist.")
    else:
        df = extract_details_from_images(image_folder)

        # Save results to a CSV file
        output_csv = "extracted_details.csv"
        df.to_csv(output_csv, index=False)
        print(f"Results saved to {output_csv}")
