# This is for the authentication blueprint
# Assigner: Patrick
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
from flask import Blueprint
from app.auth.models.userAuth import UserAuth
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.utils import getCursor, allowed_file, save_image, closeCursorAndConnection, validate_form, validate_email, validate_phone, validate_date, validate_password, validate_varchar, validate_text

auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static", static_url_path="/auth/static")

@auth_bp.before_request
def before_request():
    if "loggedin" in session and request.endpoint in ["auth.login", "auth.register"]:
        if session.get("role") == "customer":
            return redirect(url_for("home.home"))
        elif session.get("role") == "staff":
            return redirect(url_for("user_management.staff_dashboard"))
        elif session.get("role") == "manager":
            return redirect(url_for("user_management.manager_dashboard"))

# Login, Register and Logout
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    cursor, connection = getCursor()
    if request.method == "POST":
        if not validate_form(request.form, ["username", "password"]):
            return redirect(url_for("auth.login"))
        username = request.form.get("username")
        password = request.form.get("password")
        auth_query = ("SELECT * FROM auth WHERE username = %s AND is_active = 1 LIMIT 1")
        cursor.execute(auth_query, (username,))
        user_auth = cursor.fetchone()
        if user_auth and check_password_hash(user_auth[2], password):
            if user_auth[3] == "customer":
                user_query = ("SELECT first_name, last_name FROM customer WHERE customer_id = %s")
            elif user_auth[3] == "staff":
                user_query = ("SELECT first_name, last_name FROM staff WHERE staff_id = %s")
            elif user_auth[3] == "manager":
                user_query = ("SELECT first_name, last_name FROM manager WHERE manager_id = %s")
            else:
                flash("Invalid role, please contact the administrator.", "danger")
                return redirect(url_for("auth.login"))
            cursor.execute(user_query, (user_auth[0],))
            user_detals = cursor.fetchone()

            if user_detals:
                first_name, last_name = user_detals
                user_object = UserAuth(user_auth[0], user_auth[1], first_name, last_name, user_auth[3], user_auth[4])
                # Log the user in
                login_user(user_object)
                session.permanent = True
                session["loggedin"] = True
                session["id"] = user_auth[0]
                session["username"] = user_auth[1]
                session["role"] = user_auth[3]
                flash(f"Welcome back, {first_name}!", "success")
                return before_request()
        else:
            flash("Invalid username or password, please try again.", "danger")
            return redirect(url_for("auth.login"))
    closeCursorAndConnection(cursor, connection)
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    cursor, connection = getCursor()
    required_fields = ["username", "password", "first_name", "last_name", "phone", "date_of_birth", "address", "email"]
    field_validators = {
        "username": None,
        "password": validate_password,
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "phone": validate_phone,
        "date_of_birth": validate_date,
        "address": None,
        "email": validate_email
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("auth.register"))
        username = request.form.get("username")
        password = request.form.get("password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        address = request.form.get("address")
        date_of_birth = request.form.get("date_of_birth")
        # hash the password by using werkzeug.security
        hashed_password = generate_password_hash(password)

        try:
            # Insert INTO auth table
            query = "INSERT INTO auth (username, password_hash, role) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, hashed_password, "customer"))
            new_id = cursor.lastrowid
            query = """INSERT INTO customer (customer_id, first_name, last_name, phone, email, address, date_of_birth, date_joined) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(
                query,
                (
                    new_id,
                    first_name,
                    last_name,
                    phone,
                    email,
                    address,
                    date_of_birth,
                    datetime.now(),
                ),
            )
            query = """INSERT INTO loyalty_points (customer_id) VALUES (%s)"""
            cursor.execute(query, (new_id,))
            connection.commit()
            flash("Successfully registered!", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            connection.rollback()
            if "Duplicate entry" in str(e):
                flash("Username already exists, please try another one.", "danger")
            else:
                flash(f"An error occurred during registration: {e}. Please try again.", "danger")
            return redirect(url_for("auth.register"))
    closeCursorAndConnection(cursor, connection)
    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    # Remove session data, this will log the user out
    logout_user()
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    session.pop("role", None)
    # Redirect to login page
    return redirect(url_for("home.home"))