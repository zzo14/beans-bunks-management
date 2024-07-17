from flask import Flask
from flask import session
from flask import url_for
from flask import current_app
from flask import flash
from flask import redirect
import mysql.connector
import app.connect as connect
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import re
import pytz
import random
import string


dbconn = None
connection = None
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(
        user=connect.dbuser,
        password=connect.dbpass,
        host=connect.dbhost,
        database=connect.dbname,
        autocommit=False,
    )
    dbconn = connection.cursor()
    return dbconn, connection

def closeCursorAndConnection(dbconn, connection):
    dbconn.close()
    connection.close()

def allowed_file(file):
    """Check if the file is an allowed extension."""
    result = True
    if type(file) == list:
        for f in file:
            result = ( "." in f.filename and f.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS)
            if not result:
                break
    else:
        result = ( "." in file.filename and file.filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS)
    return result

def save_image(file):
    """save the image to the static folder"""
    filename = secure_filename(file.filename)
    timeStamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_name = f"{timeStamp}_{filename}"
    img_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    file.save(img_path)
    return unique_name

def verify_access(required_roles, redirect_page):
    """helper function to verify user accrss based on role"""
    if "loggedin" not in session:
        flash("Please login to access this page.", "danger")
        return redirect(url_for(redirect_page))
    if session.get("role") not in required_roles:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for(redirect_page))
    return None
    
def validate_form(form_data, required_fields, field_validations=None):
    """Validate the form data based on the required fields and field validations."""
    for field in required_fields:
        if not form_data.get(field):
            flash(f"{field} is required, please fill in all required fields.", "danger")
            return False
    if field_validations:
        for field, validation in field_validations.items():
            if validation is not None and not validation(form_data.get(field)):
                if field == "email":
                    flash("Please enter a valid email address.", "danger")
                elif field == "phone":
                    flash("Please enter a valid phone number.", "danger")
                elif field == "date":
                    flash("Please enter a valid date in the format YYYY-MM-DD.", "danger")
                elif field == "time":
                    flash("Please enter a valid time in the format HH:MM:SS.", "danger")
                elif field == "password":
                    flash("Password must contain at least 8 characters, one uppercase letter, one lowercase letter and one number.", "danger")
                elif field == "first_name" or field == "last_name":
                    flash("Name must contain only alphabetic characters.", "danger")
                else:
                    flash(f"{field} is invalid", "danger")
                return False
    return True

def validate_email(email):
    if email:
        if re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return True
    return False

def validate_phone(phone):
    if phone:
        if phone.isdigit() and 9 <= len(phone) <= 11:
            return True
    return False

def validate_date(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_password(password):
    if password:
        if len(password) >= 8 and re.search(r"[a-z]", password) and re.search(r"[A-Z]", password) and re.search(r"\d", password):
                return True
    return False

def validate_varchar(text):
    if text:
        if re.match(r'[A-Za-z]+', text):
            return True
    return False

def validate_text(text):
    if text:
        if re.match(r'[A-Za-z0-9\s]+', text):
            return True
    return False

def parse_time(time_str):
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            pass
    raise ValueError("No valid date format found")

def validate_time(time):
    try:
        parse_time(time)
        return True
    except ValueError:
        return False
    
def validate_decimal(decimal):
    if decimal:
        if re.match(r'[0-9]+(\.[0-9]+)?', decimal):
            return True
    return False

def get_nz_now():
    """Get the current time in New Zealand."""
    nz_time_zone = pytz.timezone('Pacific/Auckland')
    nz_time = datetime.now(nz_time_zone)
    return nz_time

def nz_time_filter(value, format='%d %B %Y %H:%M:%S'):
    """Jinja filter to format the time in New Zealand timezone."""
    if not value:
        return ''
    nz_time_zone = pytz.timezone('Pacific/Auckland')
    value = value.astimezone(nz_time_zone)
    return value.strftime(format)
  
def send_message_to_customer(customer_id, message):
    """Send a message to the customer."""
    cursor, conn = getCursor()
    try:
        # Insert the empty inquires into the inquiries table
        cursor.execute("""
            INSERT INTO inquiries (customer_id, inquiry_text, timestamp, status)
            VALUES (%s, '', CURRENT_TIMESTAMP, 'responded')
        """, (customer_id,))
        inquiry_id = cursor.lastrowid

        # Insert the message into the messages table
        cursor.execute("""
            INSERT INTO messages (sender_id, customer_id, inquiry_id, message_text, timestamp, status)
            VALUES (NULL, %s, %s, %s, CURRENT_TIMESTAMP, 'unread')
        """, (customer_id, inquiry_id, message))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error sending message to customer:", e)
        return False
    finally:
        closeCursorAndConnection(cursor, connection)

def generate_redemption_code():
    """Generate a random redemption code for the gift card."""
    code = 'GC' + ''.join(random.choices(string.digits, k=3))
    password = ''.join(random.choices(string.digits, k=4))
    return code, password

def format_timedelta(td):
    """Format the timedelta object into HH:MM."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"