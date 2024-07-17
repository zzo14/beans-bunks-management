# This is for the System management blueprint
# Assigner: Mavis, Patrick
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import Blueprint
from flask import request
from flask import flash
from datetime import datetime, timedelta
from app.utils import getCursor, closeCursorAndConnection, verify_access, validate_form, validate_varchar, validate_text, validate_decimal, validate_date, validate_time, generate_redemption_code

system_management_bp = Blueprint("system_management", __name__, template_folder="templates", static_folder="static", static_url_path="/system_management/static")

@system_management_bp.before_request
def before_request():
    endpoint_access = {
        'system_management.system_dash': (['manager'], 'home.home'),
        'system_management.manage_categories': (['manager'], 'home.home'),
        'system_management.manage_products': (['manager'], 'home.home'),
        'system_management.manage_giftcards': (['manager'], 'home.home'),
        'system_management.manage_opening_hours': (['manager'], 'home.home'),
        'system_management.reports': (['manager'], 'home.home'),
        'system_management.promotions_dashboard': (['manager'], 'home.home'),
        'system_management.manage_promotions': (['manager'], 'home.home'),
        'system_management.manage_customer_promotions': (['manager'], 'home.home')
    }

    if request.endpoint in endpoint_access:
        roles, redirect_url = endpoint_access[request.endpoint]
        return verify_access(roles, redirect_url)

@system_management_bp.route('/')
def system_dash():
    """Display the system dashboard with categories, products, gift cards, and opening hours"""
    cursor, connection = getCursor()
    active_tab = request.args.get('tab', 'categories')
    try:
        cursor.execute("SELECT * FROM product_category")
        categories = cursor.fetchall()

        cursor.execute("""SELECT p.product_id, p.name, p.description, p.price, p.is_available, 
                                 pc.category_id, pc.name AS category 
                          FROM product p 
                          JOIN product_category pc ON p.category_id = pc.category_id""")
        products = cursor.fetchall()

        cursor.execute("""SELECT gc.gift_card_id, gc.type_id, gc.redemption_code, gc.gift_card_password, 
                                 gc.current_balance, gc.issue_date, gc.expiry_date, gct.description 
                          FROM gift_cards gc 
                          JOIN gift_card_types gct ON gc.type_id = gct.type_id ORDER BY gc.expiry_date""")
        giftcards = cursor.fetchall()

        cursor.execute("SELECT * FROM gift_card_types")
        giftcard_types = cursor.fetchall()

        cursor.execute("""SELECT id, days, TIME_FORMAT(open_time, '%H:%i'), TIME_FORMAT(close_time, '%H:%i') 
                          FROM opening_hours ORDER BY id""")
        hours = cursor.fetchall()

        cursor.execute("""SELECT p.product_id, p.name AS product_name,
                                 IFNULL(AVG(r.rating), 0) AS average_rating,
                                 COUNT(r.review_id) AS total_reviews
                          FROM product p
                          LEFT JOIN product_reviews r ON p.product_id = r.product_id
                          GROUP BY p.product_id
                          ORDER BY average_rating DESC, p.product_id""")
        product_reviews = cursor.fetchall()
        reviews_data = {}
        for review in product_reviews:
            product_id = review[0]
            review_query = """SELECT r.review_id, r.customer_id, 
                                     CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
				                     r.rating, r.feedback, r.review_date, r.is_visible
                              FROM product_reviews r
                              JOIN customer c ON r.customer_id = c.customer_id
                              WHERE r.product_id = %s AND r.feedback != '';"""
            cursor.execute(review_query, (product_id,))
            reviews = cursor.fetchall()
            reviews_data[product_id] = reviews
    finally:
        closeCursorAndConnection(cursor, connection)
    return render_template("system.html", categories=categories, products=products, giftcards=giftcards, 
                                          giftcard_types=giftcard_types, hours=hours, active_tab=active_tab,
                                          product_reviews=product_reviews, reviews_data=reviews_data)

@system_management_bp.route('/categories', methods=['POST'])
def manage_categories():
    """Manage product categories (add, edit, delete)"""
    cursor, connection = getCursor()
    required_fields = ['name']
    field_validators = {'name': validate_varchar}
    
    action = request.form.get('action')
    category_id = request.form.get('category_id')
    name = request.form.get('name')

    if action != 'delete' and not validate_form(request.form, required_fields, field_validators):
        return redirect(url_for('system_management.system_dash', tab='categories'))

    try:
        if action == 'add': # Add a new category
            cursor.execute("SELECT COUNT(*) FROM product_category WHERE name = %s", (name,))
            if cursor.fetchone()[0] > 0:
                flash("A category with the same name already exists. Please choose a different name.", "danger")
                return redirect(url_for("system_management.system_dash", tab='categories'))
            
            cursor.execute("INSERT INTO product_category (name) VALUES (%s)", (name.capitalize(),))
            connection.commit()
            flash("Category added successfully!", "success")
        
        elif action == 'edit': # Edit an existing category
            cursor.execute("UPDATE product_category SET name = %s WHERE category_id = %s", (name.capitalize(), category_id))
            connection.commit()
            flash("Category updated successfully!", "success")
        
        elif action == 'delete': # Delete an existing category
            cursor.execute("DELETE FROM product_category WHERE category_id = %s", (category_id,))
            connection.commit()
            flash("Category deleted successfully!", "success")
    
    except Exception as e:
        print(f"Error: {e} at manage_categories")
        flash("Failed to perform the action. Please try again.", "danger")
    
    finally:
        closeCursorAndConnection(cursor, connection)
    
    return redirect(url_for('system_management.system_dash', tab='categories'))

@system_management_bp.route('/products', methods=['POST'])
def manage_products():
    """Manage products (add, edit, delete)"""
    cursor, connection = getCursor()
    required_fields = ['name', 'description', 'price', 'category_id']
    field_validators = {
        'name': validate_varchar,
        'description': validate_text,
        'price': validate_decimal,
        'category_id': None
    }
    
    action = request.form.get('action')
    product_id = request.form.get('product_id')
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    category_id = request.form.get('category_id')
    is_available = request.form.get('is_available', 1)

    if action != 'delete' and not validate_form(request.form, required_fields, field_validators):
        return redirect(url_for('system_management.system_dash', tab='products'))

    try:
        if action == 'add':
            cursor.execute("SELECT COUNT(*) FROM product WHERE name = %s", (name,))
            if cursor.fetchone()[0] > 0:
                flash("A product with the same name already exists. Please choose a different name.", "danger")
                return redirect(url_for("system_management.system_dash", tab='products'))
            
            cursor.execute(
                "INSERT INTO product (name, description, price, category_id, is_available) VALUES (%s, %s, %s, %s, %s)", 
                (name.capitalize(), description, price, category_id, is_available)
            )
            connection.commit()
            flash("Product added successfully!", "success")
        
        elif action == 'edit':
            cursor.execute(
                "UPDATE product SET name = %s, description = %s, price = %s, category_id = %s, is_available = %s WHERE product_id = %s", 
                (name.capitalize(), description, price, category_id, is_available, product_id)
            )
            connection.commit()
            flash("Product updated successfully!", "success")
        
        elif action == 'delete':
            cursor.execute("DELETE FROM product WHERE product_id = %s", (product_id,))
            connection.commit()
            flash("Product deleted successfully!", "success")
    
    except Exception as e:
        print(f"Error: {e} at manage_products")
        flash("Failed to perform the action. Please try again.", "danger")
    
    finally:
        closeCursorAndConnection(cursor, connection)
    
    return redirect(url_for('system_management.system_dash', tab='products'))

@system_management_bp.route('/giftcards', methods=['POST'])
def manage_giftcards():
    """Manage gift cards and gift card"""
    cursor, connection = getCursor()
    required_fields = ['type_id', 'current_balance', 'issue_date']
    field_validators = {
        'type_id': None,
        'current_balance': validate_decimal,
        'issue_date': validate_date
    }

    action = request.form.get('action')
    gift_card_id = request.form.get('gift_card_id')
    type_id = request.form.get('type_id')
    current_balance = request.form.get('current_balance')
    issue_date = request.form.get('issue_date')
    expiry_date = request.form.get('expiry_date')

    # manage gift card types
    if action == 'manage_types':
        type_action = request.form.get('type_action')

        if type_action.startswith('edit_type'):
            index = int(type_action.split('_')[-1])
            type_id = request.form.get(f'type_id_{index}')
            amount = request.form.get(f'amount_{index}')
            description = request.form.get(f'description_{index}')

            try:
                # fetch current amount to update product price
                cursor.execute("SELECT amount FROM gift_card_types WHERE type_id = %s", (type_id,))
                current_amount = cursor.fetchone()[0]

                cursor.execute("UPDATE gift_card_types SET amount = %s, description = %s WHERE type_id = %s", (amount, description, type_id))
                cursor.execute("UPDATE product SET name = %s, price = %s, description = %s WHERE name LIKE %s", 
                              (f'Gift Card - ${amount}', amount, description, f'Gift Card - ${current_amount}%'))
                connection.commit()
                flash("Gift card type updated successfully!", "success")
            except Exception as e:
                print(f"Error updating gift card type and product: {e}")
                flash("Failed to update gift card type and product.", "danger")

        elif type_action.startswith('delete_type'):
            index = int(type_action.split('_')[-1])
            type_id = request.form.get(f'type_id_{index}')

            try:
                # fetch current amount to update product price
                cursor.execute("SELECT amount FROM gift_card_types WHERE type_id = %s", (type_id,))
                current_amount = cursor.fetchone()[0]

                cursor.execute("DELETE FROM gift_card_types WHERE type_id = %s", (type_id,))
                cursor.execute("DELETE FROM product WHERE name LIKE %s", (f'Gift Card - ${current_amount}%',))
                connection.commit()
                flash("Gift card type deleted successfully!", "success")
            except Exception as e:
                print(f"Error deleting gift card type and product: {e}")
                flash("Failed to delete gift card type and product.", "danger")

        elif type_action == 'add_type':
            amount = request.form.get('new_amount')
            description = request.form.get('new_description')

            if amount and description:
                try:
                    cursor.execute("INSERT INTO gift_card_types (amount, description) VALUES (%s, %s)", (amount, description))
                    gift_card_type_id = cursor.lastrowid
                    cursor.execute("INSERT INTO product (name, description, price, category_id, image, is_available, is_inventory) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                                   (f'Gift Card - ${amount}.00', description, amount, 6, f'gc_{gift_card_type_id}.jpg', 1, 0))
                    connection.commit()
                    flash("New gift card type added successfully!", "success")
                except Exception as e:
                    print(f"Error adding new gift card type and product: {e}")
                    flash("Failed to add new gift card type and product.", "danger")
            else:
                flash("Please fill in the required fields for the new type.", "danger")

        return redirect(url_for('system_management.system_dash', tab='giftcards'))

    # manage gift card
    else:
        if not issue_date:
            issue_date_obj = datetime.now()
        else:
            issue_date_obj = datetime.strptime(issue_date, '%Y-%m-%d')

        if not expiry_date:
            expiry_date_obj = issue_date_obj.replace(year=issue_date_obj.year + 2)
            expiry_date = expiry_date_obj.strftime('%Y-%m-%d')

        if action != 'delete' and not validate_form(request.form, required_fields, field_validators):
            flash("Form validation failed. Please check the input values.", "danger")
            return redirect(url_for('system_management.system_dash', tab='giftcards'))

        try:
            if action == 'add':
                cursor.execute("SELECT MAX(gift_card_id) FROM gift_cards")
                max_id = cursor.fetchone()[0]
                new_id = (max_id or 0) + 1
                redemption_code, gift_card_password = generate_redemption_code()

                cursor.execute("INSERT INTO gift_cards (gift_card_id, type_id, redemption_code, gift_card_password, current_balance, issue_date, expiry_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                               (new_id, type_id, redemption_code, gift_card_password, current_balance, issue_date_obj.strftime('%Y-%m-%d'), expiry_date))
                connection.commit()
                flash("Gift card added successfully!", "success")

            elif action == 'edit':
                cursor.execute("UPDATE gift_cards SET type_id = %s, current_balance = %s, issue_date = %s, expiry_date = %s WHERE gift_card_id = %s",
                               (type_id, current_balance, issue_date_obj.strftime('%Y-%m-%d'), expiry_date, gift_card_id))
                connection.commit()
                flash("Gift card updated successfully!", "success")

            elif action == 'delete':
                cursor.execute("DELETE FROM gift_cards WHERE gift_card_id = %s", (gift_card_id,))
                connection.commit()
                flash("Gift card deleted successfully!", "success")

        except Exception as e:
            print(f"Error: {e} at manage_giftcards")
            flash(f"Failed to perform the action due to error: {e}", "danger")

        finally:
            closeCursorAndConnection(cursor, connection)

        return redirect(url_for('system_management.system_dash', tab='giftcards'))

@system_management_bp.route('/opening_hours', methods=['GET', 'POST'])
def manage_opening_hours():
    """Manage opening hours"""
    cursor, connection = getCursor()
    required_fields = ['days', 'open_time', 'close_time']
    field_validators = {
        'days': validate_varchar, 
        'open_time': validate_time, 
        'close_time': validate_time
        }
    
    if request.method == 'POST':
        action = request.form.get('action')
        hour_id = request.form.get('hour_id')
        days = request.form.get('days')
        open_time = request.form.get('open_time')
        close_time = request.form.get('close_time')

        if action != 'delete' and not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for('system_management.system_dash', tab='opening_hours'))

        try:
            if action == 'add':
                cursor.execute("INSERT INTO opening_hours (days, open_time, close_time) VALUES (%s, %s, %s)", (days, open_time, close_time))
                connection.commit()
                flash("Opening hours added successfully!", "success")
            
            elif action == 'edit':
                cursor.execute("UPDATE opening_hours SET days = %s, open_time = %s, close_time = %s WHERE id = %s", (days, open_time, close_time, hour_id))
                connection.commit()
                flash("Opening hours updated successfully!", "success")
            
            elif action == 'delete':
                cursor.execute("DELETE FROM opening_hours WHERE id = %s", (hour_id,))
                connection.commit()
                flash("Opening hours deleted successfully!", "success")
        
        except Exception as e:
            print(f"Error: {e} at manage_opening_hours")
            flash("Failed to perform the action. Please try again.", "danger")
        
        finally:
            closeCursorAndConnection(cursor, connection)

        return redirect(url_for('system_management.system_dash', tab='opening_hours'))

@system_management_bp.route('/update_review_visibility', methods=['POST'])
def update_review_visibility():
    """Update the visibility of a product review"""
    cursor, connection = getCursor()
    review_id = request.form.get('review_id')
    is_visible = request.form.get('is_visible')
    model_id = request.form.get('model_id')
    print(f"review_id: {review_id}, is_visible: {is_visible}, model_id: {model_id}")
    try:
        cursor.execute("UPDATE product_reviews SET is_visible = %s WHERE review_id = %s", (is_visible, review_id))
        connection.commit()
        flash("Review is hidden successfully!", "success") if is_visible == '0' else flash("Review is shown successfully!", "success")
    except Exception as e:
        print(f"Error: {e} at review_management")
        flash("Failed to perform the action. Please try again.", "danger")
    finally:
        closeCursorAndConnection(cursor, connection)
    print(f'checkReviewsModal{model_id}')
    return redirect(url_for('system_management.system_dash', tab='reviews', open_modal=f'checkReviewsModal{model_id}'))

@system_management_bp.route("/reports", methods=["GET"])
def reports():
    """Display reports on payment details, financial revenue, product sales, popular products, 
       accommodation data, promotion feedback, gift card data, and product reviews"""
    payment_datails = fetch_payment_datails()
    financial_revenue = fetch_financial_data()
    product_sales = fetch_product_sales()
    popular_products = fetch_popular_products()
    monthly_accommodation_data, room_type_accommodation_data = fetch_accommodation_data()
    promo_effectiveness, promo_usages = fetch_promotion_feedback_data()
    gift_card_sales_data, gift_card_usage_data, gift_card_transaction_data = fetch_gift_card_data()
    product_reviews, top_reviews = fetch_product_review()
    return render_template("reports.html", 
                            payment_datails=payment_datails, 
                            financial_revenue=financial_revenue, 
                            product_sales=product_sales,
                            popular_products=popular_products,
                            monthly_accommodation_data=monthly_accommodation_data,
                            room_type_accommodation_data=room_type_accommodation_data,
                            promo_effectiveness=promo_effectiveness,
                            promo_usages=promo_usages,
                            gift_card_sales_data=gift_card_sales_data,
                            gift_card_usage_data=gift_card_usage_data,
                            gift_card_transaction_data=gift_card_transaction_data,
                            product_reviews=product_reviews, top_reviews=top_reviews)

def fetch_payment_datails():
    """Fetch payment details for orders and bookings"""
    cursor, connection = getCursor()
    query = """
        SELECT "Order" AS reference, op.order_payment_id, op.amount, op.payment_method, op.payment_status, 
                op.payment_date AS payment_date,
            c.customer_id, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, c.email, c.phone
        FROM order_payment op
        JOIN orders o ON op.order_id = o.order_id
        JOIN customer c ON o.customer_id = c.customer_id
        UNION ALL
        SELECT "Booking" AS reference, bp.booking_payment_id, bp.amount, bp.payment_method, bp.payment_status, 
                bp.payment_date AS payment_date,
                c.customer_id, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, c.email, c.phone
        FROM booking_payment bp
        JOIN bookings b ON bp.booking_id = b.booking_id
        JOIN customer c ON b.customer_id = c.customer_id
        ORDER BY payment_date;"""
    cursor.execute(query)
    payment_datails = cursor.fetchall()
    closeCursorAndConnection(cursor, connection)
    return payment_datails

def fetch_financial_data():
    """Fetch financial revenue data"""
    cursor, connection = getCursor()
    query = """
        SELECT year, month, payment_method, SUM(revenue) as revenue
        FROM (
                SELECT YEAR(op.payment_date) AS year, MONTH(op.payment_date) AS month, op.payment_method, op.amount AS revenue
                FROM order_payment op
                UNION ALL
                SELECT YEAR(bp.payment_date) AS year, MONTH(bp.payment_date) AS month, bp.payment_method, bp.amount AS revenue
                FROM booking_payment bp
                ) as combined_payments
        GROUP BY year, month, payment_method
        ORDER BY year, month, payment_method"""
    cursor.execute(query)
    financial_revenue = cursor.fetchall()
    closeCursorAndConnection(cursor, connection)
    return financial_revenue

def fetch_product_sales():
    """Fetch product sales data"""
    cursor, connection = getCursor()
    query = """
        SELECT p.product_id, p.name AS product_name, SUM(od.quantity) AS sales_quantity, 
                SUM(od.quantity * (p.price + COALESCE(pv.additional_cost, 0))) AS total_revenue,
                pc.name AS category_name
        FROM order_details od
        LEFT JOIN order_variations ov ON od.order_detail_id = ov.order_detail_id
        LEFT JOIN product_variations pv ON ov.variation_id = pv.variation_id
        JOIN product p ON od.product_id = p.product_id
        JOIN product_category pc ON p.category_id = pc.category_id
        GROUP BY p.product_id, p.name, pc.name
        ORDER BY total_revenue DESC;"""
    cursor.execute(query)
    product_sales = cursor.fetchall()
    closeCursorAndConnection(cursor, connection)
    return product_sales

def fetch_popular_products():
    """Fetch popular products data"""
    cursor, connection = getCursor()
    query = """
        SELECT p.product_id, p.name AS product_name, SUM(od.quantity) AS sales_quantity
        FROM order_details od
        JOIN product p ON od.product_id = p.product_id
        GROUP BY p.product_id, p.name
        ORDER BY sales_quantity DESC
        LIMIT 10;"""
    cursor.execute(query)
    popular_products = cursor.fetchall()
    closeCursorAndConnection(cursor, connection)
    return popular_products

def fetch_accommodation_data():
    """Fetch accommodation data"""
    cursor, connection = getCursor()
    monthly_query = """ 
        SELECT YEAR(b.check_in_date) AS year, MONTH(b.check_in_date) AS month,
                COUNT(*) AS booking_count, SUM(b.price) AS total_revenue
        FROM bookings b
        WHERE b.status IN ('Confirmed', 'Completed')
        GROUP BY YEAR(b.check_in_date), MONTH(b.check_in_date)
        ORDER BY YEAR(b.check_in_date), MONTH(b.check_in_date);"""
    cursor.execute(monthly_query)
    monthly_accommodation_data = cursor.fetchall()

    room_type_query = """
        SELECT r.type AS room_type, COUNT(*) AS booking_count, YEAR(b.check_in_date) AS year, SUM(bp.amount) as Revenue
        FROM bookings b
        JOIN room r ON b.room_id = r.room_id
        JOIN booking_payment bp ON bp.booking_id = b.booking_id
        WHERE b.status IN ('Confirmed', 'Completed')
        GROUP BY r.type, YEAR(b.check_in_date)
        ORDER BY booking_count DESC;"""
    cursor.execute(room_type_query)
    room_type_accommodation_data = cursor.fetchall()
    closeCursorAndConnection(cursor, connection)
    return monthly_accommodation_data, room_type_accommodation_data

def fetch_promotion_feedback_data():
    """Fetch promotion feedback data"""
    cursor, connection = getCursor()
    promotion_effectiveness_query = """
        SELECT p.promo_id, p.promo_code, COUNT(cp.promo_id) AS usage_count, p.discount_rate
        FROM customer_promos cp
        JOIN promotions p ON cp.promo_id = p.promo_id
        GROUP BY p.promo_id, p.promo_code, p.description, p.discount_rate
        ORDER BY p.promo_id;"""
    cursor.execute(promotion_effectiveness_query)
    promotion_effectiveness = cursor.fetchall()

    promotion_usage_query = """
        SELECT p.promo_code, p.description, CONCAT(ROUND((1 - p.discount_rate) * 100, 2), '%'),
                CONCAT(c.first_name, ' ', c.last_name) AS customer_name, cp.used_date
        FROM customer_promos cp
        JOIN customer c ON c.customer_id = cp.customer_id
        JOIN promotions p ON p.promo_id = cp.promo_id;"""
    cursor.execute(promotion_usage_query)
    promotion_usage_data = cursor.fetchall()
    closeCursorAndConnection(cursor, connection)
    return promotion_effectiveness, promotion_usage_data

def fetch_gift_card_data():
    """Fetch gift card data"""
    cursor, connection = getCursor()
    sales_query = """
        SELECT gcty.type_id, gcty.amount, gcty.description, SUM(gct.amount) AS total_sales
        FROM gift_card_transactions gct
        JOIN gift_cards gc ON gct.gift_card_id = gc.gift_card_id
        JOIN gift_card_types gcty ON gc.type_id = gcty.type_id
        WHERE gct.transaction_type = 'Top-Up'
        GROUP BY gcty.type_id, gcty.description
        ORDER BY total_sales DESC;"""
    cursor.execute(sales_query)
    gift_card_sales_data = cursor.fetchall()

    # fetch gift card usage data
    usage_query = """
        SELECT gcty.amount, COUNT(gc.gift_card_id) AS total_count
        FROM gift_cards gc
        JOIN gift_card_types gcty ON gc.type_id = gcty.type_id
        GROUP BY gcty.amount;"""
    cursor.execute(usage_query)
    gift_card_usage_data = cursor.fetchall()

    # fetch gift card balance data
    transaction_query = """
        SELECT gc.gift_card_id, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, gc.issue_date, gc.expiry_date, 
               gcty.amount as origin_amount, gc.current_balance, gct.transaction_type, gct.amount, gct.transaction_date
        FROM gift_card_transactions gct
        JOIN gift_cards gc ON gct.gift_card_id = gc.gift_card_id
        JOIN customer c ON c.customer_id = gct.customer_id
        JOIN gift_card_types gcty ON gc.type_id = gcty.type_id
        WHERE gct.transaction_type = 'Redemption';"""
    cursor.execute(transaction_query)
    gift_card_transaction_data = cursor.fetchall()
    closeCursorAndConnection(cursor, connection)
    return gift_card_sales_data, gift_card_usage_data, gift_card_transaction_data

def fetch_product_review():
    """Fetch product reviews data"""
    cursor, connection = getCursor()
    query = """
        SELECT p.product_id, p.name, p.price,
                COALESCE(pr.average_rating, 0) AS average_rating, 
                COALESCE(pr.total_ratings, 0) AS total_ratings
            FROM product p
            LEFT JOIN (
                SELECT 
                    product_id, 
                    AVG(rating) AS average_rating,
                    COUNT(*) AS total_ratings
                FROM product_reviews
                GROUP BY product_id
            ) pr ON p.product_id = pr.product_id
            ORDER BY average_rating DESC, total_ratings DESC"""
    cursor.execute(query)
    product_reviews = cursor.fetchall()

    query = """
            SELECT p.product_id, p.name, p.price,
                COALESCE(pr.average_rating, 0) AS average_rating, 
                COALESCE(pr.total_ratings, 0) AS total_ratings
            FROM product p
            LEFT JOIN (
                SELECT 
                    product_id, 
                    AVG(rating) AS average_rating,
                    COUNT(*) AS total_ratings
                FROM product_reviews
                GROUP BY product_id
            ) pr ON p.product_id = pr.product_id
            ORDER BY average_rating DESC
            LIMIT 10"""
    cursor.execute(query)
    top_reviews = cursor.fetchall()
    closeCursorAndConnection(cursor, connection)
    return product_reviews, top_reviews

@system_management_bp.route('/promotions_dashboard')
def promotions_dashboard():
    """Display the promotions dashboard with promotions, customer promotions, loyalty rewards, and reward rules"""
    cursor, connection = getCursor()
    active_tab = request.args.get('tab', 'promotions')
    promotions = []
    customer_promotions = []
    loyalty_rewards = []
    reward_rules = []
    try:
        cursor.execute("SELECT * FROM promotions")
        promotions = cursor.fetchall()

        cursor.execute("""
            SELECT cp.customer_promo_id, cp.customer_id, cp.promo_id, cp.used_date, 
                   c.first_name, c.last_name, p.promo_code 
            FROM customer_promos cp 
            JOIN customer c ON cp.customer_id = c.customer_id 
            JOIN promotions p ON cp.promo_id = p.promo_id
        """)
        customer_promotions = cursor.fetchall()

        cursor.execute("""SELECT customer_id, first_name, last_name FROM customer
                          WHERE first_name NOT LIKE '%Admin%' 
                          AND last_name NOT LIKE '%Admin%';""")
        customers = cursor.fetchall()

        cursor.execute("""
            SELECT lp.customer_id, lp.total_earned, lp.total_spent, lp.current_balance, 
                    c.first_name, c.last_name 
            FROM loyalty_points lp 
            JOIN customer c ON lp.customer_id = c.customer_id
            JOIN auth a ON a.id = c.customer_id
            WHERE a.is_active != 0;
        """)
        loyalty_rewards = cursor.fetchall()

        cursor.execute("""SELECT gct.amount, per.description, per.points_required, per.rule_id
                          FROM point_exchange_rules per
                          JOIN gift_card_types gct ON gct.type_id = per.gift_card_type_id;""")
        reward_rules = cursor.fetchall()

        cursor.execute("SELECT * FROM gift_card_types;")
        gift_card_types = cursor.fetchall()
    
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        closeCursorAndConnection(cursor, connection)
        
    return render_template("promotions.html", promotions=promotions, customer_promotions=customer_promotions, 
                                              customers = customers, loyalty_rewards=loyalty_rewards, 
                                              reward_rules=reward_rules, active_tab=active_tab, gift_card_types=gift_card_types)

@system_management_bp.route('/promotions', methods=['GET', 'POST'])
def manage_promotions():
    """Manage promotions (add, edit, delete)"""
    cursor, connection = getCursor()
    required_fields = ['promo_code', 'description', 'discount_rate']
    field_validators = {
        'promo_code': validate_text,
        'description': validate_text,
        'discount_rate': validate_decimal,
        'start_date': None,
        'end_date': None,
    }
    
    if request.method == 'POST':
        action = request.form.get('action')
        promo_id = request.form.get('promo_id')
        promo_code = request.form.get('promo_code')
        description = request.form.get('description')
        discount_rate = 1 - float(request.form.get('discount_rate')) if request.form.get('discount_rate') else None
        start_date = request.form.get('start_date') or None
        end_date = request.form.get('end_date') or None

        if action != 'delete' and not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("system_management.promotions_dashboard", tab='promotions'))
        
        if discount_rate:
            try:
                discount_rate = float(discount_rate)
                if not (0 <= discount_rate <= 1):
                    flash("Discount rate must be between 0 and 1.", "danger")
                    return redirect(url_for("system_management.promotions_dashboard", tab='promotions'))
            except ValueError:
                flash("Invalid discount rate.", "danger")
                return redirect(url_for("system_management.promotions_dashboard", tab='promotions'))

        try:
            if action == 'add':
                cursor.execute("SELECT COUNT(*) FROM promotions WHERE promo_code = %s", (promo_code,))
                existing_promo_count = cursor.fetchone()[0]
                if existing_promo_count > 0:
                    flash("A promotion with the same code already exists. Please choose a different code.", "danger")
                    return redirect(url_for("system_management.promotions_dashboard", tab='promotions'))
                
                cursor.execute("""
                    INSERT INTO promotions (promo_code, description, discount_rate, start_date, end_date) 
                    VALUES (%s, %s, %s, %s, %s)
                    """, (promo_code, description, discount_rate, start_date, end_date))
                connection.commit()
                flash("Promotion added successfully!", "success")
            
            elif action == 'edit':
                cursor.execute("""
                    UPDATE promotions 
                    SET promo_code = %s, description = %s, discount_rate = %s, start_date = %s, end_date = %s
                    WHERE promo_id = %s
                    """, (promo_code, description, discount_rate, start_date, end_date, promo_id))
                connection.commit()
                flash("Promotion updated successfully!", "success")
            
            elif action == 'delete':
                cursor.execute("DELETE FROM promotions WHERE promo_id = %s", (promo_id,))
                connection.commit()
                flash("Promotion deleted successfully!", "success")
        
        except Exception as e:
            print(f"Error: {e} at manage_promotions")
            flash("Failed to perform the action. Please try again.", "danger")
        
        finally:
            closeCursorAndConnection(cursor, connection)
        return redirect(url_for("system_management.promotions_dashboard", tab='promotions'))
    
    try:
        query = "SELECT * FROM promotions"
        cursor.execute(query)
        promotions = cursor.fetchall()
    finally:
        closeCursorAndConnection(cursor, connection)
    
    return redirect(url_for("system_management.promotions_dashboard", tab='promotions'))

@system_management_bp.route('/customer_promotions', methods=['GET', 'POST'])
def manage_customer_promotions():
    """Manage customer promotions (add, edit, delete)"""
    cursor, connection = getCursor()
    required_fields = ['customer_id', 'promo_id']
    field_validators = {
        'customer_id': None,
        'promo_id': None
    }
    
    if request.method == 'POST':
        action = request.form.get('action')
        customer_promo_id = request.form.get('customer_promo_id')
        customer_id = request.form.get('customer_id')
        promo_id = request.form.get('promo_id')
        used_date = request.form.get('used_date')

        if action != 'delete' and not validate_form(request.form, required_fields, field_validators):
            return redirect(url_for("system_management.promotions_dashboard", tab='customer_promotions'))

        try:
            if action == 'add':
                cursor.execute("INSERT INTO customer_promos (customer_id, promo_id) VALUES (%s, %s)", 
                               (customer_id, promo_id))
                connection.commit()
                flash("Customer promotion added successfully!", "success")
            
            elif action == 'edit':
                if used_date and used_date > str(datetime.today()):
                    flash("The used date cannot be in the future.", "danger")
                else:
                    cursor.execute("UPDATE customer_promos SET customer_id = %s, promo_id = %s WHERE customer_promo_id = %s", 
                                   (customer_id, promo_id, customer_promo_id))
                    connection.commit()
                    flash("Customer promotion updated successfully!", "success")
            
            elif action == 'delete':
                cursor.execute("DELETE FROM customer_promos WHERE customer_promo_id = %s", (customer_promo_id,))
                connection.commit()
                flash("Customer promotion deleted successfully!", "success")
        
        except Exception as e:
            print(f"Error: {e} at manage_customer_promotions")
            flash("Failed to perform the action. Please try again.", "danger")
        
        finally:
            closeCursorAndConnection(cursor, connection)
        
        return redirect(url_for("system_management.promotions_dashboard", tab='customer_promotions'))
    
    try:
        query = """
            SELECT cp.customer_promo_id, cp.customer_id, cp.promo_id, cp.used_date, 
                   c.first_name, c.last_name, p.promo_code 
            FROM customer_promos cp 
            JOIN customer c ON cp.customer_id = c.customer_id 
            JOIN promotions p ON cp.promo_id = p.promo_id
        """
        cursor.execute(query)
        customer_promotions = cursor.fetchall()

        cursor.execute("SELECT customer_id, first_name, last_name FROM customer")
        customers = cursor.fetchall()

        cursor.execute("SELECT promo_id, promo_code FROM promotions")
        promotions = cursor.fetchall()
    finally:
        closeCursorAndConnection(cursor, connection)
    
    return redirect(url_for("system_management.promotions_dashboard", tab='customer_promotions'))

@system_management_bp.route('/loyalty_rewards', methods=['GET', 'POST'])
def manage_loyalty_rewards():
    """Manage loyalty rewards (add, edit, delete)"""
    cursor, connection = getCursor()
    required_fields_loyalty = ['customer_id', 'total_earned', 'total_spent']
    field_validators_loyalty = {
        'customer_id': None,
        'total_earned': validate_decimal,
        'total_spent': validate_decimal
    }
    
    required_fields_rule = ['points_cost']
    field_validators_rule = {
        'points_cost': validate_decimal
    }
    
    if request.method == 'POST':
        action = request.form.get('action')
        customer_id = request.form.get('customer_id')
        total_earned = request.form.get('total_earned')
        total_spent = request.form.get('total_spent')
        promo_id = request.form.get('promo_id')
        rule_id = request.form.get('rule_id')
        gift_card_amount = request.form.get('gift_card_amount')
        points_description = request.form.get('points_description')
        points_cost = request.form.get('points_cost')

        if action in ['add_loyalty', 'edit_loyalty'] and not validate_form(request.form, required_fields_loyalty, field_validators_loyalty):
            return redirect(url_for('system_management.promotions_dashboard', tab='loyalty_rewards'))

        if action in ['add_rule', 'edit_rule'] and not validate_form(request.form, required_fields_rule, field_validators_rule):
            return redirect(url_for('system_management.promotions_dashboard', tab='loyalty_rewards'))

        try:
            if action == 'add_loyalty':
                cursor.execute("INSERT INTO loyalty_points (customer_id, total_earned, total_spent) VALUES (%s, %s, %s)", 
                               (customer_id, total_earned, total_spent))
                connection.commit()
                flash("Loyalty points added successfully!", "success")
            
            elif action == 'edit_loyalty':
                cursor.execute("UPDATE loyalty_points SET total_earned = %s, total_spent = %s WHERE customer_id = %s", 
                               (total_earned, total_spent, customer_id))
                connection.commit()
                flash("Loyalty points updated successfully!", "success")
            
            elif action == 'delete_loyalty':
                cursor.execute("DELETE FROM loyalty_points WHERE customer_id = %s", (customer_id,))
                connection.commit()
                flash("Loyalty points deleted successfully!", "success")
            
            elif action == 'add_rule':
                cursor.execute("UPDATE promotions SET points_cost = %s WHERE promo_id = %s", 
                               (points_cost, promo_id))
                connection.commit()
                flash("Reward rule added successfully!", "success")
            
            elif action == 'edit_rule':
                cursor.execute("UPDATE point_exchange_rules SET points_required = %s, gift_card_type_id = %s, description = %s WHERE rule_id = %s", 
                               (points_cost, gift_card_amount, points_description, rule_id))
                connection.commit()
                flash("Reward rule updated successfully!", "success")
            
            elif action == 'delete_rule':
                cursor.execute("UPDATE promotions SET points_cost = NULL WHERE promo_id = %s", (promo_id,))
                connection.commit()
                flash("Reward rule deleted successfully!", "success")
        
        except Exception as e:
            print(f"Error: {e} at manage_loyalty_points")
            flash("Failed to perform the action. Please try again.", "danger")
        
        finally:
            closeCursorAndConnection(cursor, connection)
        
        return redirect(url_for('system_management.promotions_dashboard', tab='loyalty_rewards'))