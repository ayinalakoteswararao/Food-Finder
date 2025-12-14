from flask import Flask, render_template, request,jsonify,Response
import pandas as pd
from pathlib import Path
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from flask import jsonify
import warnings
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF 
from flask_mail import Mail, Message
import config

app = Flask(__name__)
# Load all configuration from config.py
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER
app.config['USE_MYSQL'] = config.USE_MYSQL
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_PORT'] = config.MYSQL_PORT
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
mail = Mail(app)
warnings.filterwarnings("ignore", category=Warning)

DATASET_FILENAMES = ["dataset.csv", "zomato.csv"]
selected_dataset_path = None


def load_dataset() -> pd.DataFrame:
    """Try multiple dataset files and encodings until one succeeds."""

    global selected_dataset_path
    base_dir = Path(__file__).resolve().parent
    attempted_paths = []

    for file_name in DATASET_FILENAMES:
        dataset_path = base_dir / file_name
        attempted_paths.append(dataset_path)
        if not dataset_path.exists():
            continue

        for encoding in ("utf-8", "latin1", "cp1252"):
            try:
                df = pd.read_csv(dataset_path, encoding=encoding)
                selected_dataset_path = dataset_path
                return df
            except UnicodeDecodeError:
                continue

    raise FileNotFoundError(
        "Could not load dataset. Checked: "
        + ", ".join(str(path) for path in attempted_paths)
    )


# Try to optionally load dataset from MySQL when configured. Falls back to CSV files.
if app.config.get('USE_MYSQL'):
    try:
        from db import init_db, fetch_restaurants_df
        init_db(app)
        raw_data = fetch_restaurants_df()
    except Exception as e:
        print("MySQL load failed, falling back to CSV:", e)
        raw_data = load_dataset()
else:
    # Load from CSV as before
    raw_data = load_dataset()
raw_data_frame = pd.DataFrame(raw_data)
raw_data_frame['rating'] = pd.to_numeric(raw_data_frame['rating'], errors='coerce')
raw_data_frame.dropna(inplace=True)
label_encoder = LabelEncoder()
food_rating_encoded = label_encoder.fit_transform(raw_data_frame['rating'])
numeric_columns = ['cost', 'id', 'rating']
numeric_data = raw_data_frame[numeric_columns]

for column in numeric_columns:
    numeric_data[column] = pd.to_numeric(numeric_data[column], errors='coerce')

numeric_data.dropna(inplace=True)
data_scaler = StandardScaler()
scaled_data_frame = data_scaler.fit_transform(numeric_data)

pca_model = PCA(n_components=2)
pca_model.fit(scaled_data_frame)

# Sample data for dropdowns
rating_values = sorted(raw_data_frame['rating'].unique(), reverse=True)
city_values = sorted(raw_data_frame['city'].unique(), reverse=False)
cost_values = sorted(raw_data_frame['cost'].unique(), reverse=False)

@app.route('/')
def home(): 
    return render_template('home.html')
 
@app.route('/homes')
def homes(): 
    return render_template('homes.html')

@app.route('/explore')
def explore():
    return render_template('explore.html', rating_values=rating_values, city_values=city_values, cost_values=cost_values)

@app.route('/process_data', methods=['POST'])
def process_data():
    try:
        min_rating = float(request.form.get('min_rating'))
        selected_city = request.form.get('selected_city')
        max_cost = float(request.form.get('max_cost'))
        selected_classifier = request.form.get('selected_classifier')

        filtered_data = raw_data_frame[(raw_data_frame['rating'] >= min_rating) &
                                       (raw_data_frame['city'] == selected_city) &
                                       (raw_data_frame['cost'] <= max_cost)]

        if not filtered_data.empty:
            # Apply PCA
            pca = PCA(n_components=2)  
            pca_data = pca.fit_transform(scaled_data_frame)

            # Transform filtered data using PCA
            filtered_pca_data = pca.transform(filtered_data[numeric_columns])
            filtered_pca_results = []
            for i, row in enumerate(filtered_data.iterrows()):
                filtered_pca_results.append({
                    "name": row[1]['name'],
                    "rating": row[1]['rating'],
                    "city": row[1]['city'],
                    "cost": row[1]['cost'],
                    "cuisine": row[1]['cuisine'],
                    "address": row[1]['address'],
                    "link": row[1]['link'],
                })

            return render_template('filtered_results.html', filtered_results=filtered_pca_results)

        else:
            return render_template('filtered_results.html', filtered_results=[], selected_classifier=selected_classifier)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/map_view', methods=['GET','POST'])
def map_view():
    # Get filter parameters from query string if coming from explore page
    min_rating = request.args.get('min_rating', type=float)
    selected_city = request.args.get('selected_city', type=str)
    max_cost = request.args.get('max_cost', type=float)
    
    return render_template('map_view.html', 
                         min_rating=min_rating,
                         selected_city=selected_city,
                         max_cost=max_cost)

@app.route('/download_pdf')
def download_pdf():
    """Generate and download PDF of filtered restaurants with professional formatting and icons"""
    # Get filter parameters
    min_rating = request.args.get('min_rating', type=float)
    selected_city = request.args.get('selected_city', type=str)
    max_cost = request.args.get('max_cost', type=float)
    
    # Start with all restaurants
    filtered_data = raw_data_frame.copy()
    
    # Apply filters
    if min_rating is not None:
        filtered_data = filtered_data[filtered_data['rating'] >= min_rating]
    
    if selected_city:
        filtered_data = filtered_data[filtered_data['city'] == selected_city]
    
    if max_cost is not None:
        filtered_data = filtered_data[filtered_data['cost'] <= max_cost]
    
    # Sort by rating (highest first)
    filtered_data = filtered_data.sort_values('rating', ascending=False)
    
    # Create PDF with enhanced formatting
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add header with background color effect
    pdf.set_fill_color(255, 107, 107)  # Red accent color
    pdf.rect(0, 0, 210, 35, 'F')

    # Title
    pdf.set_xy(10, 8)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "FOOD FINDER", 0, 1, 'L')

    # Subtitle/tagline
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, "Restaurant Results Report", 0, 1, 'L')
    pdf.ln(10)
    
    # Reset text color
    pdf.set_text_color(0, 0, 0)
    
    # Filter summary box
    pdf.set_font("Arial", '', 11)
    pdf.set_fill_color(248, 249, 250)
    pdf.set_draw_color(222, 226, 230)

    # Create filter summary
    filter_lines = [f"Results: {len(filtered_data)} restaurants"]

    if min_rating is not None:
        filter_lines.append(f"Min rating: {min_rating}+")
    if selected_city:
        filter_lines.append(f"City: {selected_city}")
    if max_cost is not None:
        filter_lines.append(f"Max cost: Rs.{int(max_cost)} for two")

    for line in filter_lines:
        pdf.cell(0, 8, line, border=1, ln=1, align='L', fill=True)

    pdf.ln(10)

    # Restaurant data header
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(255, 107, 107)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(70, 10, "Restaurant", 1, 0, 'L', True)
    pdf.cell(25, 10, "Rating", 1, 0, 'C', True)
    pdf.cell(35, 10, "Cuisine", 1, 0, 'L', True)
    pdf.cell(30, 10, "City", 1, 0, 'L', True)
    pdf.cell(30, 10, "Cost", 1, 1, 'R', True)
    
    # Reset colors for data
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 10)
    
    # Alternate row colors
    use_alt_fill = False
    
    for idx, row in filtered_data.iterrows():
        # Alternate background colors
        if use_alt_fill:
            pdf.set_fill_color(252, 252, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        use_alt_fill = not use_alt_fill
        
        name = str(row.get('name', ''))[:30]  # Truncate long names
        rating_value = float(row.get('rating', 0) or 0)
        full_stars = int(round(rating_value))
        if full_stars < 0:
            full_stars = 0
        if full_stars > 5:
            full_stars = 5
        stars_text = "*" * full_stars
        rating = f"{rating_value:.1f} ({stars_text})" if stars_text else f"{rating_value:.1f}"
        cuisine = str(row.get('cuisine', ''))[:20]  # Truncate long cuisine
        city = str(row.get('city', ''))[:15]  # Truncate long city
        cost = f"Rs.{int(row.get('cost', 0) or 0)}"
        
        pdf.cell(70, 8, name, 1, 0, 'L', True)
        pdf.cell(25, 8, rating, 1, 0, 'C', True)
        pdf.cell(35, 8, cuisine, 1, 0, 'L', True)
        pdf.cell(30, 8, city, 1, 0, 'L', True)
        pdf.cell(30, 8, cost, 1, 1, 'R', True)
    
    # Footer section
    pdf.ln(12)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(222, 226, 230)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 7, f"Generated: {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}", 0, 1, 'L', True)
    pdf.cell(0, 6, "Data source: Food Finder Restaurant Database", 0, 1, 'L', True)
    pdf.cell(0, 6, "Visit: www.foodfinder.com    Email: info@foodfinder.com", 0, 1, 'L', True)
    
    pdf.ln(6)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(255, 107, 107)
    pdf.cell(0, 8, '"Great food is the best ingredient for a happy life!"', 0, 1, 'C')
    
    # Generate PDF as bytes
    pdf_output = pdf.output(dest='S').encode('latin-1')
    
    # Create response
    response = Response(
        pdf_output,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': 'attachment; filename="food_finder_results.pdf"'
        }
    )
    
    return response

@app.route('/results', methods=['GET'])
def show_results():
    """Show filtered restaurant results"""
    # Get filter parameters
    min_rating = request.args.get('min_rating', type=float)
    selected_city = request.args.get('selected_city', type=str)
    max_cost = request.args.get('max_cost', type=float)
    
    # Start with all restaurants
    filtered_data = raw_data_frame.copy()
    
    # Apply filters
    if min_rating is not None:
        filtered_data = filtered_data[filtered_data['rating'] >= min_rating]
    
    if selected_city:
        filtered_data = filtered_data[filtered_data['city'] == selected_city]
    
    if max_cost is not None:
        filtered_data = filtered_data[filtered_data['cost'] <= max_cost]
    
    # Convert to list of dictionaries
    restaurants = []
    for idx, row in filtered_data.iterrows():
        restaurants.append({
            "name": str(row.get('name', '')),
            "rating": float(row.get('rating', 0)),
            "city": str(row.get('city', '')),
            "cost": float(row.get('cost', 0)),
            "cuisine": str(row.get('cuisine', '')),
            "address": str(row.get('address', '')),
            "link": str(row.get('link', ''))
        })
    
    # Sort by rating (highest first)
    restaurants.sort(key=lambda x: x['rating'], reverse=True)
    
    return render_template('results.html', restaurants=restaurants)

@app.route('/map_only', methods=['GET'])
def map_only():
    """Simple map-only view without restaurant markers"""
    return render_template('map_only.html')

@app.route('/google_maps_view', methods=['GET','POST'])
def google_maps_view():
    """Simple map view"""
    return render_template('google_maps_view.html')

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    """API endpoint to get restaurants, optionally filtered"""
    try:
        # Search parameter
        search_query = request.args.get('search', type=str)
        
        # Location-based filters
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', type=float)
        
        # Bounds-based filters
        lat_min = request.args.get('lat_min', type=float)
        lat_max = request.args.get('lat_max', type=float)
        lng_min = request.args.get('lng_min', type=float)
        lng_max = request.args.get('lng_max', type=float)
        
        # Regular filters
        min_rating = request.args.get('min_rating', type=float)
        selected_city = request.args.get('selected_city', type=str)
        max_cost = request.args.get('max_cost', type=float)
        
        # Start with all restaurants
        filtered_data = raw_data_frame.copy()
        
        # Apply search filter if provided
        if search_query:
            print(f"Search query: {search_query}")
            # Search in name, cuisine, city, and address
            search_mask = (
                filtered_data['name'].str.contains(search_query, case=False, na=False) |
                filtered_data['cuisine'].str.contains(search_query, case=False, na=False) |
                filtered_data['city'].str.contains(search_query, case=False, na=False) |
                filtered_data['address'].str.contains(search_query, case=False, na=False)
            )
            filtered_data = filtered_data[search_mask]
            print(f"After search filter: {len(filtered_data)} restaurants")
        
        # Apply location-based filters
        if lat is not None and lng is not None and radius is not None:
            # Filter by radius from user location
            print(f"Location filter: lat={lat}, lng={lng}, radius={radius}")
            
            # Get coordinates for all cities at once for performance
            city_coords_map = {}
            for city in filtered_data['city'].unique():
                city_coords_map[city] = get_city_coordinates(city)
            
            # Calculate distances vectorially for better performance
            distances = []
            for idx, row in filtered_data.iterrows():
                city = row.get('city', '')
                city_coords = city_coords_map.get(city)
                if city_coords:
                    dist = calculate_distance(lat, lng, city_coords[0], city_coords[1])
                    distances.append(dist)
                else:
                    distances.append(float('inf'))
            
            filtered_data['distance'] = distances
            filtered_data = filtered_data[filtered_data['distance'] <= radius]
            print(f"Filtered to {len(filtered_data)} restaurants within {radius}km")
            
        elif lat_min is not None and lat_max is not None and lng_min is not None and lng_max is not None:
            # Filter by map bounds
            print(f"Bounds filter: {lat_min},{lng_min} to {lat_max},{lng_max}")
            
            city_coords_map = {}
            for city in filtered_data['city'].unique():
                city_coords_map[city] = get_city_coordinates(city)
            
            in_bounds = []
            for idx, row in filtered_data.iterrows():
                city = row.get('city', '')
                city_coords = city_coords_map.get(city)
                if city_coords:
                    if (lat_min <= city_coords[0] <= lat_max and 
                        lng_min <= city_coords[1] <= lng_max):
                        in_bounds.append(True)
                    else:
                        in_bounds.append(False)
                else:
                    in_bounds.append(False)
            
            filtered_data = filtered_data[in_bounds]
            print(f"Filtered to {len(filtered_data)} restaurants in bounds")
        
        # Apply regular filters if provided
        if min_rating is not None:
            filtered_data = filtered_data[filtered_data['rating'] >= min_rating]
        if selected_city:
            filtered_data = filtered_data[filtered_data['city'] == selected_city]
        if max_cost is not None:
            filtered_data = filtered_data[filtered_data['cost'] <= max_cost]
        
        # Limit to first 50 restaurants for better performance (reduced from 100)
        if len(filtered_data) > 50:
            filtered_data = filtered_data.head(50)
        
        # Convert to list of dictionaries
        restaurants = []
        for idx, row in filtered_data.iterrows():
            restaurants.append({
                "name": str(row.get('name', '')),
                "rating": float(row.get('rating', 0)),
                "city": str(row.get('city', '')),
                "cost": float(row.get('cost', 0)),
                "cuisine": str(row.get('cuisine', '')),
                "address": str(row.get('address', '')),
                "link": str(row.get('link', ''))
            })
        
        # Sort by rating (highest first)
        restaurants.sort(key=lambda x: x['rating'], reverse=True)
        
        print(f"Returning {len(restaurants)} restaurants")
        return jsonify({"restaurants": restaurants})
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def get_city_coordinates(city_name):
    """Get coordinates for a city"""
    city_coordinates = {
        'Mumbai': (19.0760, 72.8777),
        'Delhi': (28.6139, 77.2090),
        'Bangalore': (12.9716, 77.5946),
        'Hyderabad': (17.3850, 78.4867),
        'Chennai': (13.0827, 80.2707),
        'Kolkata': (22.5726, 88.3639),
        'Pune': (18.5204, 73.8567),
        'Ahmedabad': (23.0225, 72.5714),
        'Jaipur': (26.9124, 75.7873),
        'Surat': (21.1702, 72.8311),
        # Andhra Pradesh cities (from your dataset)
        'Gudivada': (16.4404, 81.0485),
        'Guntur': (16.3067, 80.4365),
        'Kakinada': (16.9891, 82.2477),
        'Nellore': (14.4426, 79.9865),
        'Tirupati': (13.6288, 79.4192),
        'Visakhapatnam': (17.6868, 83.2185),
        'Vijayawada': (16.5062, 80.6480),
        # Handle specific area names in your dataset
        'Benz Circle and Auto Nagar,Vijayawada': (16.5062, 80.6480),
        'Governorpet,Vijayawada': (16.5062, 80.6480),
        # Other major cities
        'Bikaner': (28.0229, 73.3117),
        'Noida-1': (28.5355, 77.3910),
        'Indirapuram,Delhi': (28.6379, 77.3483),
        'BTM,Bangalore': (12.9115, 77.6095),
        'Rohini,Delhi': (28.7320, 77.0633),
        'Kothrud,Pune': (18.5081, 73.8057),
        'Indiranagar,Bangalore': (12.9794, 77.6408),
        'Electronic City,Bangalore': (12.8450, 77.6600),
        'Greater Kailash 2,Delhi': (28.5436, 77.2489),
        'Vashi,Mumbai': (19.0748, 73.0785),
        'Kukatpally,Hyderabad': (17.4849, 78.4163),
        'Viman Nagar,Pune': (18.5675, 73.9140),
        'Koramangala,Bangalore': (12.9345, 77.6226),
        'Laxmi Nagar,Delhi': (28.6420, 77.3160),
        'Gomti Nagar,Lucknow': (26.8467, 80.9462),
        'Malviya Nagar,Delhi': (28.5254, 77.2063),
        'HSR,Bangalore': (12.9081, 77.6474),
        'Madhapur,Hyderabad': (17.4485, 78.3915),
        'Wakad,Pune': (18.5984, 73.7673)
    }
    return city_coordinates.get(city_name)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    from math import radians, cos, sin, asin, sqrt
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers
    return c * r

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, validators
from flask_wtf.csrf import CSRFProtect


# Initialize CSRF protection and disable it for the entire app
csrf = CSRFProtect(app)
csrf.init_app(app)
app.config['WTF_CSRF_ENABLED'] = False
# Disable Flask sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

class ContactForm(FlaskForm):
    name = StringField('Name', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired()])
    message = TextAreaField('Message', [validators.DataRequired()])
    submit = SubmitField('Send')

# Contact route with CSRF protection and sessions disabled
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        try:
            msg_body = (
                "New Contact Form Submission\n"
                "A user submitted the contact form  details below.\n"
                "---------------------------\n\n"
                f"👤 Name: {name}\n"
                f"✉️ Email: {email}\n\n"
                f"💬 Message:\n{message}\n\n"
                "Sent via Food Finder contact form"
            )
            recipient = app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME')
            msg = Message(
                subject="📩 New Contact Form Submission - Food Finder",
                recipients=[recipient] if recipient else [],
                body=msg_body,
            )
            if recipient:
                mail.send(msg)
                flash('Message sent successfully!', 'success')
            else:
                flash('Email not configured on server. Message not sent.', 'danger')
        except Exception as e:
            warnings.warn(f"Error sending contact email: {e}")
            flash('Failed to send message. Please try again later.', 'danger')

        return redirect(url_for('contact'))

    return render_template('contact.html', form=form)

@app.route('/help')
def help_center():
    """Simple Help Center page"""
    return render_template('help.html')

@app.route('/privacy')
def privacy():
    """Simple Privacy & Terms page"""
    return render_template('privacy.html')

if __name__ == '__main__':
    app.run(debug=True)
