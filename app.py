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
                     'Kopiko', 'Skittles', 'Haldiram’s', 'Balaji', 'Pringles', 'Tropicana', 'Real Fruit Juice', 
                     'Mountain Dew', 'Sprite', 'Fanta', 'Thums Up', 'Creambell', 'Hershey’s', 'Oreo', 'Parle-G', 
                     'Monaco', 'Hide & Seek', 'Little Debbie', 'Marie Gold', 'Britannia Good Day', 'Tiger Biscuits', 
                     '50-50', 'Jim Jam', 'Sunfeast', 'ITC Yippee', 'Act II', 'Popcorn Time', 'Nescafe', 'Bru Gold', 
                     'Coca-Cola', 'Thumbs Up', 'Minute Maid', 'Paper Boat Aam Panna', 'Appy Fizz', 'Raw Pressery',
                     'Del Monte', 'Kissan Jam', 'Nutella', 'Bonn Bread', 'Weikfield', 'FunFoods', 'Betty Crocker',
                     'Kwality Wall’s', 'Keventers', 'Epigamia', 'Milky Mist', 'Sundrop', 'Veeba', 'Mapro', 
                     'Dukes Wafers', 'Milano', 'Hostess', 'McVities', 'Tata Tea', 'Lipton', 'Tetley', 'Twinings', 
                     'Horlicks', 'Bournvita', 'Complan', 'Boost'],
'Personal Care': ['Pantene', 'Dove', 'Colgate', 'NIVEA', 'Himalaya', 'Dettol', 'Lifebuoy', 'LUX', 'INTERNATIONAL LUX',
                  'Pears', 'Pears naturale', 'Clinic Plus', 'Head & Shoulders', 'Tresemmé', 'Biotique', 'Olay',
                  'Garnier', 'Lakme', 'WOW Shampoo', 'Herbal Essences', 'Cetaphil', 'Mamaearth', 'Gillette', 
                  'Old Spice', 'Axe', 'Beardo', 'Bombay Shaving Company', 'Wild Stone', 'Godrej Expert', 'Vasmol',
                  'VLCC', 'Fair & Lovely', 'Glow & Lovely', 'Pond’s', 'Lotus Herbals', 'Forest Essentials', 
                  'Kama Ayurveda', 'The Body Shop', 'St. Ives', 'Joy', 'Simple', 'Aveeno', 'Johnson’s Baby', 
                  'Sebamed', 'Neutrogena', 'Palmolive', 'Himalaya Neem Face Wash', 'Himalaya Baby Lotion',
                  'Park Avenue', 'Enchanteur', 'Nyle', 'Livon', 'Set Wet', 'Schwarzkopf', 'L’Oreal Paris', 
                  'Maybelline', 'Revlon', 'Cheryl’s Cosmeceuticals', 'Swiss Beauty', 'Nykaa', 'Colorbar', 
                  'Faces Canada', 'Renee Cosmetics', 'Sugar Cosmetics', 'WOW Skin Science', 'Khadi Naturals',
                  'Indulekha', 'Shahnaz Husain', 'Blue Heaven', 'Elle 18', 'Lakme Eyeconic', 'Huda Beauty', 
                  'Kay Beauty', 'Nycil', 'Boroline', 'Dabur Gulabari', 'Medimix', 'Margo', 'Cinthol', 
                  'Fiama', 'Soulflower', 'Moha', 'Biotique Bio', 'Vicco Turmeric', 'Himalaya Wellness', 
                  'Kaya Skin Clinic'],
'Household Items': ['Harpic', 'Lizol', 'Vim', 'Domex', 'Surf Excel', 'Tide', 'Ariel', 'Vanish', 'Wheel', 'Rin',
                    'Comfort', 'Ujala', 'Colin', 'Scotch-Brite', 'Gala', 'Prestige', 'Hawkins', 'Pigeon', 'Borosil',
                    'Godrej Aer', 'Ambi Pur', 'Odonil', 'Good Knight', 'All-Out', 'Mortein', 'Hit'],
'Baby Care': ['Pampers', 'Huggies', 'MamyPoko', 'Bella Baby', 'Himalaya Baby Care', 'Libero', 'Snuggy', 'Cerelac',
              'Nestle Nan Pro', 'Similac', 'Enfamil', 'Aptamil', 'Pediasure', 'Nestum', 'Johnson’s Baby', 
              'Sebamed', 'Aveeno Baby', 'Mothercare', 'Mee Mee', 'Chicco'],
'Electronics & Accessories': ['Apple', 'Samsung', 'Xiaomi', 'OnePlus', 'Vivo', 'Oppo', 'Realme', 'Nokia', 'Dell', 
                               'HP', 'Lenovo', 'ASUS', 'Acer', 'Sony', 'LG', 'Panasonic', 'TCL', 'boAt', 'Noise', 
                               'Garmin', 'Fitbit', 'Redmi', 'Motorola', 'iQOO']
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
