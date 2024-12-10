import cv2
import easyocr
import pandas as pd
import numpy as np
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

# Function to process live camera feed
def process_camera_feed():
    cap = cv2.VideoCapture(0)  # Open the default camera (index 0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    print("Press 'q' to quit the live feed.")

    results = []

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame. Exiting...")
            break

        # Display the frame
        cv2.imshow("Live Camera Feed", frame)

        # Process the frame for brand detection (every 10th frame for performance)
        if cv2.waitKey(1) & 0xFF == ord('d'):  # Press 'd' to detect brands in the frame
            # Convert frame to grayscale for OCR
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Extract text using EasyOCR
            result = reader.readtext(gray_frame, detail=0)
            text = ' '.join(result)

            print(f"Extracted Text: {text}")  # Debug: Print extracted text for analysis

            # Detect brand names and categories using fuzzy matching
            detected_brand, detected_category = detect_brand(text, brands_categories)

            # Store the result
            results.append({
                "Frame": len(results) + 1,
                "Detected Brand": detected_brand,
                "Category": detected_category
            })

            print(f"Detected Brand: {detected_brand}, Category: {detected_category}")

        # Press 'q' to quit the camera feed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()

    # Create DataFrame from results and save to CSV
    if results:
        df = pd.DataFrame(results)
        output_csv = "live_camera_results.csv"
        df.to_csv(output_csv, index=False)
        print(f"Results saved to {output_csv}")
    else:
        print("No frames were processed.")

# Run the live camera processing function
if __name__ == "__main__":
    process_camera_feed()
