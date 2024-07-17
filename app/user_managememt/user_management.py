# This is for the customer and staff accounts management blueprint
# Assigner: Eleine, Mavis
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import Blueprint
from flask import request
from flask import flash
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import getCursor, closeCursorAndConnection, verify_access, validate_form, validate_email, validate_phone, validate_date, validate_password, validate_varchar, validate_text, get_nz_now, send_message_to_customer, generate_redemption_code
import re

user_management_bp = Blueprint("user_management", __name__, template_folder="templates", static_folder="static", static_url_path="/user_management/static")

@user_management_bp.before_request
def before_request():
    endpoint_access = { 
        "user_management.customer_list": (["manager"], url_for("auth.login")),
        "user_management.add_customer": (["manager"], url_for("auth.login")),
        "user_management.update_customer": (["manager"], url_for("auth.login")),
        "user_management.delete_user": (["manager"], url_for("auth.login")),
        "user_management.staff_list": (["manager"], url_for("auth.login")),
        "user_management.add_staff": (["manager"], url_for("auth.login")),
        "user_management.update_staff": (["manager"], url_for("auth.login")),
        "user_management.delete_user": (["manager"], url_for("auth.login")),
        "user_management.recover_user": (["manager"], url_for("auth.login")),
        "user_management.redeem_points": (["customer"], url_for("auth.login")),
    }
    if request.endpoint in endpoint_access:
        roles, redirect_url = endpoint_access[request.endpoint]
        return verify_access(roles, redirect_url)

# staff and customer management
@user_management_bp.route("/customer_list", methods=['GET','POST'])
def customer_list():
    """get the list of customer"""
    cursor, connection = getCursor()
    query = """SELECT a.id, a.username, c.first_name, c.last_name, c.phone, c.email, c.address, c.date_of_birth, 
                      c.date_joined, a.is_active
               FROM customer c
               JOIN auth a ON c.customer_id = a.id 
               WHERE a.role = 'customer'
                     AND a.username NOT LIKE '%admin%'
                     AND c.first_name NOT LIKE '%Admin%' 
                     AND c.last_name NOT LIKE '%Admin%';""" 
    cursor.execute(query)
    customers = cursor.fetchall()
    return render_template("manager_customer_list.html", customers=customers)

@user_management_bp.route("/add_customer", methods=['GET','POST'])
def add_customer():
    """Add a new customer to the database."""
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
            return redirect(url_for("user_management.customer_list"))
     
        username = request.form.get("username")
        password = request.form.get("password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        date_of_birth = request.form.get("date_of_birth")
        address = request.form.get("address")
        email = request.form.get("email")

        hashed_password = generate_password_hash(password)
        try:
            # Insert into the auth table
            user_query = """INSERT INTO auth (username, password_hash, role, is_active) 
                            VALUES (%s, %s, "customer", 1)"""
            cursor.execute(user_query, (username, hashed_password))
            customerID = cursor.lastrowid

            # Insert into the customer table
            customer_query = """INSERT INTO customer (customer_id, first_name, last_name, phone, email, address, date_of_birth, date_joined) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(customer_query, (customerID, first_name.capitalize(), last_name.capitalize(), phone, email, address, date_of_birth, datetime.now()))

            connection.commit()
            flash("Successfully registered!", "success")
            return redirect(url_for("user_management.customer_list"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at user_management.add_customer")
            if "Duplicate entry" in str(e):
                flash("Username already exists, please try a different username.", "danger")
            else:
                flash("Registration failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection(cursor, connection)

    return redirect(url_for("user_management.customer_list"))

@user_management_bp.route("/update_customer", methods=['GET','POST'])
def update_customer():
    """update the customer profile"""
    cursor, connection = getCursor()
    required_fields = ["customer_id", "first_name", "last_name", "phone", "email", "address", "date_of_birth" ]
    field_validators = {
        "customer_id": None,
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "phone": validate_phone,
        "email": validate_email,
        "address": None,
        "date_of_birth": validate_date
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators): # validate the form
            return redirect(url_for("user_management.customer_list"))
        customer_id = request.form.get("customer_id")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        address = request.form.get("address")
        date_of_birth = request.form.get("date_of_birth")    
        try:
            query = """UPDATE customer SET first_name = %s, last_name = %s,
                              phone = %s, email = %s, address = %s, date_of_birth = %s
                       WHERE customer_id = %s"""
            cursor.execute(query, (first_name.capitalize(), last_name.capitalize(), phone, email, address, date_of_birth, customer_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("Successfully updated!", "success")
                return redirect(url_for("user_management.customer_list"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at user_management.customer_list")
            flash("Update failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection(cursor, connection)
    return redirect(url_for("user_management.customer_list"))

@user_management_bp.route("/staff_list", methods=['GET','POST'])
def staff_list():
    """get the list of staff"""
    cursor, connection = getCursor()
    query = """SELECT a.id, a.username, s.first_name, s.last_name, s.position, s.email, s.phone, s.address, a.is_active
               FROM staff s
               JOIN auth a ON s.staff_id = a.id 
               WHERE a.role = 'staff';"""
    cursor.execute(query)
    staffs = cursor.fetchall()
    return render_template("manager_staff_list.html", staffs=staffs)

@user_management_bp.route("/add_staff", methods=['GET','POST'])
def add_staff():
    """Add a new staff to the database."""
    cursor, connection = getCursor()
    required_fields = ["username", "password", "first_name", "last_name", "position", "email", "phone", "address"]
    field_validators = {
        "username": None,
        "password": validate_password,
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "position": validate_varchar,
        "email": validate_email,
        "phone": validate_phone,
        "address": None,
    }

    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("user_management.staff_list"))
        
        username = request.form.get("username")
        password = request.form.get("password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        position = request.form.get("position")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        

        hashed_password = generate_password_hash(password)
        try:
            # Insert into the auth table
            user_query = """INSERT INTO auth (username, password_hash, role, is_active) 
                            VALUES (%s, %s, "staff", 1)"""
            cursor.execute(user_query, (username, hashed_password))
            staffID = cursor.lastrowid

            # Insert into the staff table
            staff_query = """INSERT INTO staff (staff_id, first_name, last_name, position, phone, email, address) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(staff_query, (staffID, first_name.capitalize(), last_name.capitalize(), position, phone, email, address))

            connection.commit()
            flash("Successfully registered!", "success")
            return redirect(url_for("user_management.staff_list"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at user_management.add_staff")
            if "Duplicate entry" in str(e):
                flash("Username already exists, please try a different username.", "danger")
            else:
                flash("Registration failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection(cursor, connection)

    return redirect(url_for("user_management.staff_list"))

@user_management_bp.route("/update_staff", methods=['GET','POST'])
def update_staff():
    """update the staff profile"""
    cursor, connection = getCursor()
    required_fields = ["staff_id", "first_name", "last_name", "position", "phone", "email", "address"]
    field_validators = {
        "staff_id": None,
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "position": validate_varchar,
        "email": validate_email,
        "phone": validate_phone,
        "address": None,
    }
    if request.method == "POST":
        if not validate_form(request.form, required_fields, field_validators): # validate the form
            return redirect(url_for("user_management.staff_list"))
        staff_id = request.form.get("staff_id")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        position = request.form.get("position")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        try:
            query = """UPDATE staff SET first_name = %s, last_name = %s, position = %s,
                              phone = %s, email = %s, address = %s
                       WHERE staff_id = %s"""
            cursor.execute(query, (first_name.capitalize(), last_name.capitalize(), position, phone, email, address, staff_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("Successfully updated!", "success")
                return redirect(url_for("user_management.staff_list"))
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at user_management.staff_list")
            flash("Update failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection(cursor, connection)
    return redirect(url_for("user_management.staff_list"))

@user_management_bp.route("/delete_user", methods=['GET','POST'])
def delete_user():
    """delete the user"""
    cursor, connection = getCursor()
    if request.method == "POST":
        # delete the user by setting the status to '0'
        user_id = request.form.get("id")
        user_type = request.form.get("role")
        url = url_for("user_management.customer_list") if user_type == "customer" else url_for("user_management.staff_list") # redirect to the correct page by user type

        try:
            query = "UPDATE auth SET is_active = 0 WHERE id = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("User is successfully deleted!", "success")
                return redirect(url)
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at user_management.delete_user")
            flash("Failed to delete. Please try again.", "danger")
        finally:
            closeCursorAndConnection(cursor, connection)
    return redirect(url)

@user_management_bp.route("/recover_user", methods=['GET','POST'])
def recover_user():
    """recover the user"""
    cursor, connection = getCursor()
    if request.method == "POST":
        # recover the user by setting the status to '1'
        user_id = request.form.get("id")
        user_type = request.form.get("role")
        url = url_for("user_management.customer_list") if user_type == "customer" else url_for("user_management.staff_list") # redirect to the correct page by user type
        try:
            query = "UPDATE auth SET is_active = 1 WHERE id = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            affected = cursor.rowcount
            if affected > 0:
                flash("User is successfully recovered!", "success")
                return redirect(url)
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at user_management.recover_user")
            flash("Recover failed. Please try again.", "danger")
        finally:
            closeCursorAndConnection(cursor, connection)
    return redirect(url)

@user_management_bp.route("/customer_dashboard")
def customer_dashboard():
    """Display the customer dashboard."""
    if 'loggedin' not in session or session.get('role') != 'customer':
        flash("You must be logged in to view the dashboard.", "danger") 
        return redirect(url_for('auth.login'))

    user_id = session.get('id')
    cursor, conn = getCursor()

    try:
        # fetch the points required for the gift card
        cursor.execute("""
                       SELECT p.points_required, g.amount
                       FROM point_exchange_rules p
                       JOIN gift_card_types g ON g.type_id = p.gift_card_type_id""") 
        rule_info = cursor.fetchone()
        points_required, gift_card_amount = rule_info

        # fetch the customer's information
        cursor.execute("""
            SELECT a.username, c.first_name, c.last_name, lp.current_balance
            FROM auth AS a
            JOIN customer AS c ON a.id = c.customer_id
            JOIN loyalty_points AS lp ON c.customer_id = lp.customer_id
            WHERE a.id = %s
        """, (user_id,))
        user_info = cursor.fetchone()
        
        query = """
        SELECT news_id, title, content, publish_time 
        FROM news 
        ORDER BY publish_time DESC 
        LIMIT 2
        """
        cursor.execute(query)
        news_list = cursor.fetchall()

        # Simulating categories
        categories = ["Events", "Updates", "Offers"]
        
        # Transform data to match template needs and include categories
        transformed_news = [
            {
                'id': news[0],
                'title': news[1],
                'content': news[2],
                'publish_time': news[3].strftime("%d-%m-%y"),
                'category': categories[i % len(categories)],  # Assigning categories in a round-robin fashion
                'summary': news[2][:100] + '...' if len(news[2]) > 100 else news[2]  # Truncate summary if too long
            }
        for i, news in enumerate(news_list)]

        if user_info:
            return render_template('customer_dashboard.html', 
                                    username=user_info[0], first_name=user_info[1], 
                                    last_name=user_info[2], loyalty_points=user_info[3], 
                                    points_required=points_required, gift_card_amount=gift_card_amount,
                                    news_list=transformed_news)  
        else:
            flash("No customer information found.", "danger")  
            return redirect(url_for('home.home'))
    except Exception as e:
        flash("Error retrieving your dashboard data: {}".format(e), "danger")  
        return redirect(url_for('home.home'))
    finally:
        closeCursorAndConnection(cursor, conn)

@user_management_bp.route("/customer_profile")
def customer_profile():
    """Display the customer profile."""
    if 'loggedin' not in session or session.get('role') != 'customer':
        return redirect(url_for('auth.login'))

    user_id = session.get('id')
    cursor, connection = getCursor()

    try:
        cursor.execute('SELECT * FROM customer WHERE customer_id = %s', (user_id,))
        customer = cursor.fetchone()
        print("Fetched customer data:", customer)

        if customer:

            customer_list = list(customer)
            if isinstance(customer[6], datetime):
                customer_list[6] = customer[6].strftime('%Y-%m-%d')  
            if isinstance(customer[7], datetime):
                customer_list[7] = customer[7].strftime('%Y-%m-%d') 

            return render_template('customer_profile.html', customer=customer_list)
        else:
            return render_template('customer_profile.html', error="No user details found.")
    except Exception as e:
        print("Error:", e)  
        return render_template('customer_profile.html', error=str(e))
    finally:
        cursor.close()
        connection.close()

@user_management_bp.route("/updatecustomer_profile", methods=['GET', 'POST'])
def updatecustomer_profile():
    """Update the customer profile."""
    if 'loggedin' not in session or session.get('role') != 'customer':
        return redirect(url_for('auth.login'))

    user_id = session.get('id')
    cursor, connection = getCursor()

    required_fields = ["first_name", "last_name", "phone", "email", "address", "date_of_birth"]
    field_validators = {
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "phone": validate_phone,
        "email": validate_email,
        "address": None,
        "date_of_birth": validate_date
    }

    if request.method == 'POST':
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("user_management.updatecustomer_profile"))
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        date_of_birth = request.form.get('date_of_birth')
        current_password = request.form.get('current_password')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if datetime.strptime(date_of_birth, "%Y-%m-%d").date() > get_nz_now().date():
            flash("The date of birth cannot be in the future.", "danger")
            return redirect(url_for("user_management.updatecustomer_profile"))

        # Password update logic
        if password:
            if password != confirm_password:
                flash("New password do not match, please try again!", "danger")
                return redirect(url_for("user_management.updatecustomer_profile"))

            if not validate_password(password):
                flash("Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.", "danger")
                return redirect(url_for("user_management.updatecustomer_profile"))

            # Check if current password is provided and valid
            if not current_password:
                flash("Current password is required to set a new password.", "danger")
                return redirect(url_for("user_management.updatecustomer_profile"))

            cursor.execute("SELECT password_hash FROM auth WHERE id = %s", (user_id,))
            stored_password_hash = cursor.fetchone()[0]

            if not check_password_hash(stored_password_hash, current_password):
                flash("Current password is incorrect, please try again!", "danger")
                return redirect(url_for("user_management.updatecustomer_profile"))

            # Update password if current password is valid
            hashed_password = generate_password_hash(password)
            cursor.execute("UPDATE auth SET password_hash = %s WHERE id = %s", (hashed_password, user_id))
            connection.commit()

        # Database update operations
        try:
            update_query = """
            UPDATE customer SET
            first_name = %s, last_name = %s, phone = %s, email = %s, address = %s, date_of_birth = %s
            WHERE customer_id = %s
            """
            update_data = (first_name, last_name, phone, email, address, date_of_birth, user_id)
            cursor.execute(update_query, update_data)
            connection.commit()

            flash("Your profile has been updated successfully!", "success")
        except Exception as e:
            connection.rollback()
            flash(f"Failed to update profile: {str(e)}", "danger")
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('user_management.customer_profile'))

    else:
        cursor.execute("SELECT first_name, last_name, phone, email, address, date_of_birth FROM customer WHERE customer_id = %s", (user_id,))
        customer = cursor.fetchone()
        cursor.close()
        connection.close()

        if customer:
            customer_dict = {
                'first_name': customer[0],
                'last_name': customer[1],
                'phone': customer[2],
                'email': customer[3],
                'address': customer[4],
                'date_of_birth': customer[5] if isinstance(customer[5], date) else customer[5]
            }
            print("Fetched customer data:", customer_dict)
            return render_template('updatecustomer_profile.html', customer=customer_dict)
        else:
            flash('No customer details found.', 'error')
            return redirect(url_for('user_management.customer_profile'))

@user_management_bp.route("/staff_dashboard")
def staff_dashboard():
    """Display the staff dashboard."""
    if 'loggedin' not in session or session.get('role') != 'staff':
        flash("You must be logged in with the appropriate staff credentials to view the dashboard.", "warning")  # Flash a warning message
        return redirect(url_for('auth.login'))

    user_id = session.get('id')
    cursor, conn = getCursor()

    try:
        cursor.execute("""
            SELECT a.username, s.first_name, s.last_name 
            FROM auth AS a
            JOIN staff AS s ON a.id = s.staff_id 
            WHERE a.id = %s
        """, (user_id,))
        staff_info = cursor.fetchone()
        if staff_info:
            return render_template('staff_dashboard.html', username=staff_info[0], first_name=staff_info[1], last_name=staff_info[2])
        else:
            flash("No staff information found.", "danger")  
            return redirect(url_for('home.home'))
    except Exception as e:
        flash(f"Error retrieving your dashboard data: {e}", "danger")  
        return redirect(url_for('home.home'))
    finally:
        closeCursorAndConnection(cursor, conn)

@user_management_bp.route("/staff_profile")
def staff_profile():
    """Display the staff profile."""
    if 'loggedin' not in session or session.get('role') != 'staff':
        return redirect(url_for('auth.login'))

    user_id = session.get('id')
    cursor, connection = getCursor()

    try:
        cursor.execute('SELECT * FROM staff WHERE staff_id = %s', (user_id,))
        staff = cursor.fetchone()
        print("Fetched staff data:", staff) 

        if staff:
            return render_template('staff_profile.html', staff=staff)
        else:
            return render_template('staff_profile.html', error="No staff details found.")
    except Exception as e:
        print("Error:", e) 
        return render_template('staff_profile.html', error=str(e))
    finally:
        cursor.close()
        connection.close()

@user_management_bp.route("/updatestaff_profile", methods=['GET', 'POST'])
def updatestaff_profile():
    """Update the staff profile."""
    if 'loggedin' not in session or session.get('role') != 'staff':
        return redirect(url_for('auth.login'))

    user_id = session.get('id')
    cursor, connection = getCursor()

    required_fields = ["first_name", "last_name", "email", "phone", "address"]
    field_validators = {
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "email": validate_email,
        "phone": validate_phone,
        "address": None,
    }

    if request.method == 'POST':
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("user_management.updatestaff_profile"))
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        current_password = request.form.get('current_password')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # validate password
        if password or confirm_password:
            if password != confirm_password:
                flash("New password do not match, please try again!", "danger")
                return redirect(url_for("user_management.updatestaff_profile"))
            if not validate_password(password):
                flash('Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.', 'danger')
                return redirect(url_for("user_management.updatestaff_profile"))

            # Check if current password is provided and valid
            if not current_password:
                flash("Current password is required to set a new password.", 'danger')
                return redirect(url_for("user_management.updatestaff_profile"))

            cursor.execute("SELECT password_hash FROM auth WHERE id = %s", (user_id,))
            stored_password_hash = cursor.fetchone()[0]

            if not check_password_hash(stored_password_hash, current_password):
                flash("Current password is incorrect, please try again!", 'danger')
                return redirect(url_for("user_management.updatestaff_profile"))

            # Update password if current password is valid
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                UPDATE auth SET
                password_hash = %s
                WHERE id = %s
            """, (hashed_password, user_id))
            connection.commit()

        # Update staff info
        cursor.execute("""
            UPDATE staff SET
            first_name = %s, last_name = %s, email = %s, phone = %s, address = %s
            WHERE staff_id = %s
        """, (first_name, last_name, email, phone, address, user_id))
        connection.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_management.staff_profile'))

    else:
        cursor.execute('SELECT first_name, last_name, position, email, phone, address FROM staff WHERE staff_id = %s', (user_id,))
        staff = cursor.fetchone()
        cursor.close()
        connection.close()

        if staff:
            return render_template('updatestaff_profile.html', staff={
                'first_name': staff[0],
                'last_name': staff[1],
                'position': staff[2],
                'email': staff[3],
                'phone': staff[4],
                'address': staff[5]
            })
        else:
            flash('No staff details found.', 'danger')
            return redirect(url_for('user_management.staff_profile'))

@user_management_bp.route("/manager_dashboard")
def manager_dashboard():
    """Display the manager dashboard."""
    if 'loggedin' not in session or session.get('role') != 'manager':
        flash("You must be logged in to view the manager dashboard.", "warning") 
        return redirect(url_for('auth.login'))

    user_id = session.get('id')
    cursor, conn = getCursor()

    try:
        cursor.execute("""
            SELECT a.username, m.first_name, m.last_name 
            FROM auth AS a
            JOIN manager AS m ON a.id = m.manager_id
            WHERE a.id = %s
        """, (user_id,))
        manager_info = cursor.fetchone()
        if manager_info:
            return render_template('manager_dashboard.html', username=manager_info[0], first_name=manager_info[1], last_name=manager_info[2])
        else:
            flash("No manager information found.", "danger")  
            return redirect(url_for('home.home'))
    except Exception as e:
        flash("Error retrieving your dashboard data: {}".format(e), "danger")  
        return redirect(url_for('home.home'))
    finally:
        closeCursorAndConnection(cursor, conn)
    
@user_management_bp.route("/manager_profile")
def manager_profile():
    """Display the manager profile."""
    if 'loggedin' not in session or session.get('role') != 'manager':
        return redirect(url_for('auth.login'))

    user_id = session.get('id')
    cursor, connection = getCursor()

    try:
        cursor.execute('SELECT * FROM manager WHERE manager_id = %s', (user_id,))
        manager = cursor.fetchone()
        print("Fetched manager data:", manager) 

        if manager:
            return render_template('manager_profile.html', manager=manager)
        else:
            return render_template('manager_profile.html', error="No manager details found.")
    except Exception as e:
        print("Error:", e) 
        return render_template('manager_profile.html', error=str(e))
    finally:
        cursor.close()
        connection.close()


@user_management_bp.route("/updatemanager_profile", methods=['GET', 'POST'])
def updatemanager_profile():
    """Update the manager profile."""
    if 'loggedin' not in session or session.get('role') != 'manager':
        return redirect(url_for('auth.login'))

    cursor, connection = getCursor()
    user_id = session.get('id')

    required_fields = ["first_name", "last_name", "phone", "email"]
    field_validators = {
        "first_name": validate_varchar,
        "last_name": validate_varchar,
        "phone": validate_phone,
        "email": validate_email,
    }

    if request.method == 'POST':
        if not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("user_management.updatemanager_profile"))
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        position = request.form.get('position')
        phone = request.form.get('phone')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # validate password
        if password or confirm_password:
            if password != confirm_password:
                flash("New password do not match, please try again!", "danger")
                return redirect(url_for("user_management.updatemanager_profile"))
            if not validate_password(password):
                flash('Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.', 'danger')
                return redirect(url_for("user_management.updatemanager_profile"))

            # Check if current password is provided and valid
            if not current_password:
                flash("Current password is required to set a new password.", 'danger')
                return redirect(url_for("user_management.updatemanager_profile"))

            cursor.execute("SELECT password_hash FROM auth WHERE id = %s", (user_id,))
            stored_password_hash = cursor.fetchone()[0]

            if not check_password_hash(stored_password_hash, current_password):
                flash("Current password is incorrect, please try again!", 'danger')
                return redirect(url_for("user_management.updatemanager_profile"))

            # Update password if current password is valid
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                UPDATE auth SET
                password_hash = %s
                WHERE id = %s
            """, (hashed_password, user_id))
            connection.commit()

        # Update manager info
        try:
            cursor.execute("""
                UPDATE manager SET
                first_name = %s, last_name = %s, phone = %s, email = %s
                WHERE manager_id = %s
            """, (first_name, last_name, phone, email, user_id))
            connection.commit()

            flash('Profile updated successfully!', 'success')

        except Exception as e:
            connection.rollback()
            flash('Failed to update profile. Please try again. Error: ' + str(e), 'danger')
            print(f"Error: {e} at updatemanager_profile")

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('user_management.manager_profile'))

    else:
        # Fetch current manager data for GET request
        cursor.execute('SELECT first_name, last_name, position, phone, email FROM manager WHERE manager_id = %s', (user_id,))
        manager = cursor.fetchone()
        cursor.close()
        connection.close()

        if manager:
            return render_template('updatemanager_profile.html', manager={
                'first_name': manager[0],
                'last_name': manager[1],
                'position': manager[2],
                'phone': manager[3],
                'email': manager[4],
            })
        else:
            flash('No manager details found.', 'danger')
            return redirect(url_for('user_management.manager_profile'))

@user_management_bp.route("/redeem_points", methods=['POST'])
def redeem_points():
    """Redeem points for a gift card."""
    user_id = session.get('id')
    cursor, conn = getCursor()
    today = get_nz_now()

    try:
        # fetch current points
        cursor.execute("SELECT current_balance FROM loyalty_points WHERE customer_id = %s", (user_id,))
        current_points = cursor.fetchone()[0]

        # fetch the points required for the gift card
        cursor.execute("""
                       SELECT p.rule_id, p.points_required, p.gift_card_type_id, g.amount
                       FROM point_exchange_rules p
                       JOIN gift_card_types g ON g.type_id = p.gift_card_type_id""") 
        rule_info = cursor.fetchone()
        rule_id, points_required, gift_card_type_id, gift_card_amount = rule_info

        if current_points >= points_required:
            # deduct the points from the customer's account
            cursor.execute("UPDATE loyalty_points SET total_spent = total_spent + %s WHERE customer_id = %s", (points_required, user_id))
            cursor.execute("INSERT INTO point_exchange_transactions (customer_id, rule_id) VALUES (%s, %s)", (user_id, rule_id))

            # generate a redemption code
            redemption_code, password = generate_redemption_code()
            # generate a new gift card
            cursor.execute("""
                INSERT INTO gift_cards (type_id, redemption_code, gift_card_password, current_balance, issue_date, expiry_date) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (gift_card_type_id, redemption_code, password, gift_card_amount, today, today.replace(year=today.year + 2)))
            gift_card_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO gift_card_transactions (gift_card_id, transaction_type, amount, transaction_date, customer_id) 
                VALUES (%s, %s, %s, %s, %s)""", (gift_card_id, 'Top-Up', gift_card_amount, today, user_id))
            conn.commit()
            message = f"<br>Your ${gift_card_amount} gift card code is: <strong>{redemption_code}</strong>. <br>And pin is: <strong>{password}</strong>. <br>Please keep this information safe."
            message_result = send_message_to_customer(user_id, message)
            if message_result:
                flash("Gift card redeemed successfully. Check your messages for your Gift Card Details.", "success")
        else:
            flash("Not enough points to redeem the gift card.", "danger")
    except Exception as e:
        conn.rollback()
        flash("Error processing your request: {}".format(e), "danger")
    finally:
        closeCursorAndConnection(cursor, conn)
    
    return redirect(url_for('user_management.customer_dashboard'))