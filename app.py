from flask import Flask, render_template, Response, jsonify
import cv2
import easyocr
from fuzzywuzzy import process
import csv
import os

app = Flask(_name_)

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

results = []
last_detected = ""

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

def update_csv():
    with open('live_camera_results.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        for result in results:
            writer.writerow([result['Frame'], result['Detected Brand'], result['Category']])

def gen_frames():
    cap = cv2.VideoCapture(0)  # Open the default camera (index 0)
    frame_no = 0
    global last_detected

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert frame to grayscale for OCR
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Extract text using EasyOCR
        result = reader.readtext(gray_frame, detail=0)
        text = ' '.join(result)

        # Detect brand names and categories using fuzzy matching
        detected_brand, detected_category = detect_brand(text, brands_categories)

        if detected_brand != last_detected:
            last_detected = detected_brand
            frame_no += 1
            results.append({
                'Frame': frame_no,
                'Detected Brand': detected_brand,
                'Category': detected_category
            })
            update_csv()

        cv2.putText(frame, f"Brand: {detected_brand}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Category: {detected_category}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/results')
def results_endpoint():
    return jsonify({"results": results})

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')
port = int(os.environ.get("PORT", 5000))
if _name_ == "_main_":
    app.run(host="0.0.0.0", port=port, debug=True)
