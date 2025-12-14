# 🍽️ Food Finder

 <p align="center">
   Smart restaurant discovery web app built with Flask.
 </p>

 <p align="center">
   <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python">
   <img src="https://img.shields.io/badge/Flask-Web%20App-green?logo=flask" alt="Flask">
   <img src="https://img.shields.io/badge/Database-CSV%20%7C%20MySQL-orange" alt="Database">
 </p>

Food Finder is a Flask-based web application that helps you discover restaurants and make better dining decisions.

You can explore restaurants by rating, city, and cost, view results on a map, download a nicely formatted PDF report, and access the data through a JSON API. The app can use either CSV files or a MySQL database as its data source.

---

## 📚 Table of Contents

- [✨ Features](#features)
- [🧱 Tech Stack](#tech-stack)
- [🚀 Getting Started](#getting-started)
- [⚙️ Configuration](#configuration)
- [💾 Data Storage Options](#data-storage-options)
- [🏃‍♂️ Running the App Locally](#running-the-app-locally)
- [🔌 API Usage](#api-usage)
- [📄 PDF Reports](#pdf-reports)
- [❓ Contact, Help & Privacy](#contact-help--privacy)
- [🛠️ Development Notes](#development-notes)
- [📞 Support](#support)

---

## ✨ Features

- **Restaurant discovery**
  - Filter by minimum rating, city, and maximum cost
  - See detailed info: name, rating, cuisine, address, price, and link

- **Explore page** (`/explore`)
  - User-friendly dropdowns for rating, city, and cost
  - Displays filtered restaurant results

- **Map views**
  - `/map_view` – map + filters
  - `/map_only` – simple map-only view
  - `/google_maps_view` – basic Google Maps style view

- **JSON API** (`/api/restaurants`)
  - Get restaurant data as JSON
  - Supports search text, rating/city/cost filters, and basic location/bounds filtering

- **PDF export** (`/download_pdf`)
  - Generate a professional-looking PDF report of filtered restaurants
  - Includes summary, table of results, and formatted rating stars

- **Contact & help pages**
  - `/contact` – contact form that can send emails via SMTP (Flask-Mail)
  - `/help` – basic help/FAQ page
  - `/privacy` – simple privacy & terms page

- **Flexible data storage**
  - CSV-based by default (`dataset.csv`, `zomato.csv`)
  - Optional MySQL database backend for production

---

## 🧱 Tech Stack

- **Backend**: Python, Flask
- **Data & ML**: pandas, scikit-learn (StandardScaler, PCA)
- **Database**:
  - CSV files (default)
  - MySQL (via SQLAlchemy + PyMySQL) – optional
- **Forms & email**: Flask-WTF, Flask-Mail
- **Visualization & reports**: matplotlib, seaborn, FPDF
- **Frontend**: Jinja2 templates, HTML, CSS, JavaScript

Key entry point: `app.py`.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/food-finder.git
cd food-finder
```

(Adjust the folder name if your repository is named differently.)

### 2. Create and activate a virtual environment (Windows)

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

Install the required Python packages:

```bash
pip install flask pandas scikit-learn matplotlib seaborn fpdf flask-mail flask-wtf sqlalchemy pymysql
```

If you plan to use MySQL as the data source, make sure MySQL Server is installed and running.

---

## ⚙️ Configuration

All configuration lives in `config.py`.

### Application & database

Key settings:

- `USE_MYSQL` –
  - `False`: use CSV files (`dataset.csv`, `zomato.csv`) located beside `app.py`
  - `True`: use a MySQL database instead
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB` – MySQL connection details
- `SECRET_KEY` – Flask secret key (should be a strong random string)

When `USE_MYSQL = True`, the app reads from your `food_finder` database (see `schema.sql` and `DATA_STORAGE.md`).

### Email (contact form)

Configure these values for the contact form (`/contact`) to send emails:

- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USE_TLS`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`

If you do not want to send emails in development, you can leave dummy values or disable sending in `app.py`.

### Important security note

`config.py` contains **sensitive information** (database password, email password, secret key). Before pushing to GitHub or deploying to production:

- Do **not** commit real passwords or secrets.
- Add `config.py` to `.gitignore`, and/or
- Load secrets from environment variables instead of hardcoding them.

See `DATA_STORAGE.md` for additional security and storage details.

---

## 💾 Data Storage Options

Details are explained in `DATA_STORAGE.md`. Summary:

### Option 1: CSV files (default)

- Files: `dataset.csv`, `zomato.csv`
- Location: same folder as `app.py`
- Data is loaded into a pandas `DataFrame` at startup.
- Read-only for the app (changes are not written back to CSV).

### Option 2: MySQL database

- Database name: `food_finder`
- Main table: `restaurants`
- Schema and setup steps: see `schema.sql`, `DATA_STORAGE.md`, and `db.py`.
- Use scripts such as `import_data.py` to import CSV data into MySQL.

---

## 🏃‍♂️ Running the App Locally

From the project directory:

```bash
python app.py
```

By default the app runs in debug mode on:

- `http://127.0.0.1:5000/` or `http://localhost:5000/`

Useful routes:

- `/` – Home page
- `/explore` – Explore/filter restaurants
- `/results` – View filtered list of restaurants
- `/map_view` – Map with filters
- `/map_only` – Simple map view
- `/google_maps_view` – Alternate map view
- `/download_pdf` – Download PDF report of filtered restaurants
- `/contact` – Contact form
- `/help` – Help/FAQ
- `/privacy` – Privacy & terms

---

## 🔌 API Usage

### Endpoint

- `GET /api/restaurants`

### Query parameters (optional)

- `search` – text search in name, cuisine, city, address
- `min_rating` – minimum rating (e.g. `4.0`)
- `selected_city` – city name
- `max_cost` – maximum cost value
- `lat`, `lng`, `radius` – filter by distance from a point (in km)
- `lat_min`, `lat_max`, `lng_min`, `lng_max` – filter by map bounds

### Example request

```bash
curl "http://localhost:5000/api/restaurants?min_rating=4&selected_city=Vijayawada&max_cost=800"
```

Example JSON response (structure):

```json
{
  "restaurants": [
    {
      "name": "Restaurant Name",
      "rating": 4.5,
      "city": "City Name",
      "cost": 500,
      "cuisine": "Indian",
      "address": "Full address here",
      "link": "https://example.com/restaurant"
    }
  ]
}
```

---

## 📄 PDF Reports

You can download a PDF report of the current filtered results via:

- `GET /download_pdf`

Supported query parameters (same as `/results` and `/api/restaurants`):

- `min_rating`
- `selected_city`
- `max_cost`

Example:

```bash
http://localhost:5000/download_pdf?min_rating=4&selected_city=Vijayawada&max_cost=800
```

The generated report includes:

- Header with app title and subtitle
- Filter summary (rating, city, cost)
- Table of restaurants with rating, cuisine, city, and cost
- Footer with generated date/time and app info

---

## ❓ Contact, Help & Privacy

- `/contact` – send a message to the configured email address (requires valid email config)
- `/help` – basic help/FAQ
- `/privacy` – privacy and terms information

---

## 🛠️ Development Notes

- Core application logic: `app.py`
- Templates: `templates/` (HTML/Jinja2)
- Static assets: `static/` (images, CSS, JS)
- Database helpers: `db.py`
- Configuration: `config.py`
- Data/documentation: `DATA_STORAGE.md`, `schema.sql`, `dataset.csv`, `zomato.csv`

For production deployments:

- Set `DEBUG = False` in `config.py`.
- Use a production-ready WSGI server (e.g. gunicorn or uWSGI behind Nginx).
- Store secrets in environment variables, not in the repository.

---
## 📞 Support

For support, email `ayinalakoteswararao@gmail.com` or open an issue in this GitHub repository.

---

Made with ❤️ by **Ayinala-KoteswaraRao**
