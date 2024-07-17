# This is for the order inventory blueprint
# Assigner: Letitia
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import Blueprint
from flask import request, jsonify
from flask import flash
from datetime import datetime
from app.utils import getCursor, closeCursorAndConnection, verify_access, validate_form, validate_varchar, validate_text, validate_date, allowed_file, save_image, get_nz_now, generate_redemption_code, send_message_to_customer 
import random
from app.accommodation.models.room import Room
from decimal import Decimal, ROUND_HALF_UP
import re

order_inventory_bp = Blueprint("order_inventory", __name__, template_folder="templates", static_folder="static", static_url_path="/order_inventory/static")

# Before request hook to verify access based on endpoint and roles
@order_inventory_bp.before_request
def before_request():
    endpoint_access = {
        "order_inventory.inventory": (["staff", "manager"], "home.home"),
        "order_inventory.add_product": (["staff", "manager"], "home.home"),
        "order_inventory.edit_product": (["staff", "manager"], "home.home"),
        "order_inventory.delete_product": (["staff", "manager"], "home.home"),
        "order_inventory.manage_orders": (["staff", "manager"], "home.home"),
        "order_inventory.update_order_status": (["staff", "manager"], "home.home"),
    }
    if request.endpoint in endpoint_access:
        roles, redirect_url = endpoint_access[request.endpoint]
        return verify_access(roles, redirect_url)

# Route for displaying inventory
@order_inventory_bp.route("/inventory")
def inventory():
    cursor, connection = getCursor() 
    today = get_nz_now().strftime('%Y-%m-%d')     # get current date
    cursor.execute("""
        SELECT 
            p.product_id, p.name, p.description, p.price, p.image, p.is_available, pc.category_id, 
            pc.name AS category, i.inventory_id, i.stock_level, i.last_replenishment_date 
        FROM product p 
        JOIN product_category pc ON p.category_id = pc.category_id 
        JOIN inventory i ON p.product_id = i.product_id 
        WHERE p.is_inventory = 1
        ORDER BY 
            CASE 
                WHEN i.stock_level <= 10 THEN 0 
                ELSE 1 
            END, 
        i.inventory_id;""")     # fetch inventory details
    inventory_data = cursor.fetchall()

    low_stock_items = [item for item in inventory_data if item[9] < 10]
    out_of_stock_items = [item[0] for item in inventory_data if item[9] == 0]  # get product_ids of out of stock items
    
    if low_stock_items:
        flash("Some items are running low on stock. Please replenish them soon.", "warning")
    
    if out_of_stock_items:
        cursor.execute("""
            UPDATE product 
            SET is_available = 0 
            WHERE product_id IN (%s)""" % ','.join(['%s'] * len(out_of_stock_items)), tuple(out_of_stock_items))
        connection.commit()
    
    cursor.execute("SELECT * FROM product_category WHERE name != 'Coffee' OR name != 'coffee';") # fetch category details
    categories = cursor.fetchall()
    
    return render_template('inventory.html', inventory=inventory_data, categories=categories, today=today)

# Route for adding a new product    
@order_inventory_bp.route("/add_product", methods=['GET', 'POST'])
def add_product():
    cursor, connection = getCursor()
    required_fields = ['name', 'description', 'price', 'category_id', 'stock_level', 'last_replenishment_date']
    field_validators = {
        'name': validate_varchar,
        'description': validate_text,
        'price': None,
        'category_id': None,
        'stock_level': None,
        'last_replenishment_date': validate_date
    }
    if request.method == 'POST':
        if not validate_form(request.form, required_fields, field_validators):
            return redirect (url_for ('order_inventory.inventory'))
        # Retrieve form data
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        category_id = request.form.get("category_id")
        image = request.files.get("image")
        stock_level = request.form.get("stock_level")
        last_replenishment_date = request.form.get("last_replenishment_date")
        
        cursor.execute("SELECT COUNT(*) FROM product WHERE name = %s", (name,)) # check for existing product name
        existing_product_count = cursor.fetchone()[0]
        if existing_product_count > 0:
            flash("A product with the same name already exists. Please choose a different name.", "danger")
            return redirect(url_for("order_inventory.inventory"))
        
        if image.filename != "": # check if the file is empty
            if not allowed_file(image):
                flash("Uploaded file is not a valid image. Only JPG, JPEG, PNG and GIF files are allowed.", "danger")
                return redirect(url_for("order_inventory.inventory"))
            else:
                image_path = save_image(image)
        else:
            image_path = "no-image.jpg"
        
        try:
            # Insert new product into the product table
            cursor.execute("INSERT INTO product (name, description, price, category_id, image, is_available, is_inventory) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                           (name.capitalize(), description.capitalize(), price, category_id, image_path, 1, 1))               # add new product in product table
            connection.commit()
            product_id = cursor.lastrowid              # retrieve the generated product_id
            cursor.execute("INSERT INTO inventory (product_id, stock_level, last_replenishment_date) VALUES (%s, %s, %s)", 
                           (product_id, stock_level, last_replenishment_date))             # add new product in inventory table
            connection.commit()
            flash ("Product added successfully!", "success")             # success message
            return redirect(url_for("order_inventory.inventory"))
        except Exception as e:
            print(f"Error adding product: {e}")
            flash ("Failed to add a new product. Please try again.", "danger")             # danger message
            return redirect(url_for("order_inventory.inventory"))
        finally:
            closeCursorAndConnection(cursor, connection)
    return redirect(url_for("order_inventory.inventory"))

# Route for editing a product
@order_inventory_bp.route("/edit_product", methods=['GET', 'POST'])
def edit_product():
    cursor, connection = getCursor()
    required_fields = ["product_id",'name', 'description', 'price', 'category_id', 'stock_level', 'last_replenishment_date']
    field_validators = {
        "product_id": None,
        'name': validate_varchar,
        'description': validate_text,
        'price': None,
        'category_id': None,
        'stock_level': None,
        'last_replenishment_date': validate_date
    }
    if request.method == 'POST':
        if not validate_form(request.form, required_fields, field_validators):
            return redirect (url_for ('order_inventory.inventory'))
        
        # Retrieve form data
        product_id = request.form.get("product_id")
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        category_id = request.form.get("category_id")
        image = request.files.get("image")
        stock_level = request.form.get("stock_level")
        last_replenishment_date = request.form.get("last_replenishment_date")
        is_available = request.form.get("is_available")

        cursor.execute("SELECT name FROM product WHERE product_id = %s", (product_id,))               # retrieve current product name
        current_name = cursor.fetchone()[0]
        if name != current_name:
            cursor.execute("SELECT COUNT(*) FROM product WHERE name = %s", (name,))             # check for existing product name
            existing_product_count = cursor.fetchone()[0]
            if existing_product_count > 0:
                flash("A product with the same name already exists. Please choose a different name.", "danger")
                return redirect(url_for("order_inventory.inventory"))
        
        image_path = None
        if 'image' in request.files and request.files['image'].filename:                  # check if a file is uploaded
            image = request.files['image']
            if not allowed_file(image):
                flash("Uploaded file is not a valid image. Only JPG, JPEG, PNG and GIF files are allowed.", "danger")
                return redirect(url_for("order_inventory.inventory"))
            else:
                image_path = save_image(image)
                cursor.execute('UPDATE product SET image = %s WHERE product_id = %s', (image_path, product_id))             # update product image

        try:
            # update product information in the database
            cursor.execute("""
                UPDATE product 
                SET name = %s, description = %s, price = %s, category_id = %s, is_available = %s, is_inventory = %s
                WHERE product_id = %s
            """, (name.capitalize(), description.capitalize(), price, category_id, is_available, 1, product_id))
            
            # update inventory information in the database
            cursor.execute("""
                UPDATE inventory 
                SET stock_level = %s, last_replenishment_date = %s 
                WHERE product_id = %s
            """, (stock_level, last_replenishment_date, product_id))
            
            connection.commit()
            flash ("Product updated successfully!", "success")             # success message
            return redirect(url_for("order_inventory.inventory"))
        except Exception as e:
            print(f"Error editing product: {e}")
            flash ("Failed to update the product. Please try again.", "danger")             # danger message
            return redirect(url_for("order_inventory.inventory"))
        finally:
            closeCursorAndConnection(cursor, connection)
    return redirect(url_for("order_inventory.inventory"))

# Route for deleting a product
@order_inventory_bp.route("/delete_product", methods=['GET', 'POST'])
def delete_product():
    cursor, connection = getCursor()
    if request.method == 'POST':
        product_id = request.form.get("product_id")
        
        if not product_id:
            flash("Product ID is missing.", "danger")
            return redirect(url_for("order_inventory.inventory"))
        
        try:
            cursor.execute("DELETE FROM product WHERE product_id = %s", (product_id,))               # delete product in database
            connection.commit()
            flash("Product deleted successfully!", "success")             # success message
        except Exception as e:
            print(f"Error deleting product: {e}")                      
            flash("Failed to delete product. Please try again.", "danger")                # danger message
        finally:
            closeCursorAndConnection(cursor, connection)
        return redirect(url_for("order_inventory.inventory"))
    else:
        return redirect(url_for("order_inventory.inventory"))

# Route for managing orders
@order_inventory_bp.route("/manage_orders", methods=['GET', 'POST'])
def manage_orders():
    cursor, connection = getCursor()

    # retrieve all orders with their respective statuses
    cursor.execute("""
		SELECT 
            o.order_id, 
            o.order_time, 
            o.special_requests, 
            o.status, 
            o.pickup_time, 
            CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
            GROUP_CONCAT(
                DISTINCT CONCAT(
                    od.quantity, 'x ', p.name, 
                    IFNULL(CONCAT(' (', pv.variations, ')'), '')
                ) SEPARATOR ', '
            ) AS products,
            (SELECT SUM(amount) FROM order_payment WHERE order_id = o.order_id) AS total_amount,
            op.payment_status,
            c.customer_id
         FROM 
             `orders` o 
         JOIN 
             customer c ON o.customer_id = c.customer_id 
         JOIN 
             order_details od ON o.order_id = od.order_id 
         JOIN 
             product p ON od.product_id = p.product_id 
         LEFT JOIN (
             SELECT 
                 ov.order_detail_id, 
                GROUP_CONCAT(pv.variation_name SEPARATOR ', ') AS variations
            FROM 
                 order_variations ov
             JOIN 
                 product_variations pv ON ov.variation_id = pv.variation_id
             GROUP BY 
                 ov.order_detail_id
         ) pv ON od.order_detail_id = pv.order_detail_id
         LEFT JOIN order_payment op ON o.order_id = op.order_id
         GROUP BY 
             o.order_id, op.payment_status, total_amount
         ORDER BY 
             o.order_time, o.order_id;         
    """)

    orders = cursor.fetchall()

    formatted_orders = []
    ready_orders = []
    completed_orders = []

    for order in orders:
        formatted_order = list(order)
        order_time = order[1].strftime('%d-%m-%Y %H:%M')  # display order time in correct format
        pickup_time = order[4].strftime('%d-%m-%Y %H:%M') # display pickup time in correct format
        formatted_order[1] = order_time
        formatted_order[4] = pickup_time

        if order[3] == 'Pending':
            formatted_orders.append(formatted_order)
        elif order[3] == 'Ready':
            ready_orders.append(formatted_order)
        elif order[3] == 'Collected':
            completed_orders.append(formatted_order)

    return render_template('orders.html', orders=formatted_orders, ready_orders=ready_orders, completed_orders=completed_orders)


# Route for updating order status
@order_inventory_bp.route("/update_order_status", methods=['GET', 'POST'])
def update_order_status():
    cursor, connection = getCursor()
    if request.method == 'POST':
        order_id = request.form.get("order_id")
        status = request.form.get("status")
        order_details = request.form.get("order_details")  
        customer_id = request.form.get("customer_id")
        today = get_nz_now()       # get current date
        
        if status == 'Collected':
            cursor.execute("SELECT * FROM order_payment WHERE order_id = %s", (order_id,))
            orders = cursor.fetchall() # fetch order payment details for collected status

            for order in orders:
                if order[3] != 'Gift Card' and order[4] == 'Pending': # if payment method is pending for collected status, update payment details
                    new_payment_method = random.choice(['Cash', 'Debit Card', 'Credit Card'])
                    payment_status = 'Completed'
                    payment_date = datetime.now()

                    try:
                        cursor.execute("UPDATE order_payment SET payment_method = %s, payment_status = %s, payment_date = %s WHERE order_id = %s", 
                                    (new_payment_method, payment_status, payment_date, order_id))          # update data in order_payment table
                        connection.commit()
                        flash ("Payment updated successfully!", "success")           # success message
                    except Exception as e:
                        print(f"Error updating payment: {e}")
                        flash ("Failed to update the payment. Please try again.", "danger")     # danger message

        try:
            cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (status, order_id))             # update order status
            flash ("Status updated successfully!", "success")           # success message
            if status == 'Ready':
                message = f"Order ID {order_id} is Ready to be collected!"
            else:
                gift_card_info = check_gift_cards_in_order(order_details)
                if gift_card_info:
                    handle_gift_cards(gift_card_info, cursor, connection, customer_id, today)
                message = f"Order ID {order_id} has been Collected! Thank you for shopping with us."
            send_message_to_customer(customer_id, message)             # send message to customer
            connection.commit()
        except Exception as e:
            print(f"Error updating status: {e}")
            flash ("Failed to update the status. Please try again.", "danger")             # danger message
        finally:
            closeCursorAndConnection(cursor, connection)
        return redirect(url_for("order_inventory.manage_orders"))

# Route for adding item to cart
@order_inventory_bp.route("/add_to_cart", methods=['POST'])
def add_to_cart():
    customer_id = session.get('id')                   # get customer in session
    if customer_id is None:
        flash("You must be logged in to shop.", "danger") 
        return jsonify({'status': 'redirect', 'redirect_url': url_for('auth.login')}), 200            # redirect to login if non-logged in customer wants to shop

    try:   
        data = request.json
        product_id = data['product_id']
        quantity = data['quantity']
        variations = data.get('variations', []) 
        
        cursor, connection = getCursor()
        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))        # check if cart already exists for customer
        cart_row = cursor.fetchone()
        if cart_row:
            cart_id = cart_row[0]
        else:
            cursor.execute("INSERT INTO carts (customer_id, creation_time, last_updated) VALUES (%s, NOW(), NOW())", 
                           (customer_id,))     # create new cart
            cart_id = cursor.lastrowid

        cursor.execute("SELECT price FROM product WHERE product_id = %s", (product_id,))                  # fetch product price
        price_row = cursor.fetchone()
        price = price_row[0] if price_row else None  
        
        cursor.execute("INSERT INTO cart_details (cart_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)", 
                       (cart_id, product_id, quantity, price))     # insert item into cart details table

        cursor.execute("SELECT LAST_INSERT_ID()")
        cart_detail_id = cursor.fetchone()[0]

        if variations:
            for variation_id in variations:
                cursor.execute("INSERT INTO cart_variations (cart_detail_id, variation_id) VALUES (%s, %s)", 
                               (cart_detail_id, variation_id))       # insert variation into cart_variations table if there is variation

        connection.commit()
        closeCursorAndConnection(cursor, connection)
        
        return jsonify({'status': 'redirect', 'redirect_url': url_for('order_inventory.shopping_cart')}), 200               # redirect to shopping cart
    except Exception as e:
        print(f"Error adding item to cart: {e}")  
        return jsonify({'status': 'error', 'message': 'Failed to add item to cart.'}), 500             # danger message

# Route for displaying the shopping cart
@order_inventory_bp.route("/shopping_cart")
def shopping_cart():
    try:
        cursor, connection = getCursor()
        customer_id = session.get('id')              # get customer in session
        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
        cart_id_row = cursor.fetchone()

        if cart_id_row:
            cart_id = cart_id_row[0]                  # fetch cart id
            
            # fetch cart details
            cursor.execute("""             
                SELECT 
                    cd.cart_detail_id,
                    p.name AS product_name,
                    p.image AS product_image,
                    GROUP_CONCAT(pv.variation_name SEPARATOR ', ') AS variation_names,
                    SUM(pv.additional_cost) AS total_additional_cost,
                    cd.quantity,
                    cd.price AS item_price,
                    (cd.price + COALESCE(SUM(pv.additional_cost), 0)) AS total_price
                FROM 
                    cart_details cd
                INNER JOIN 
                    product p ON cd.product_id = p.product_id
                LEFT JOIN 
                    cart_variations cv ON cd.cart_detail_id = cv.cart_detail_id
                LEFT JOIN 
                    product_variations pv ON cv.variation_id = pv.variation_id
                WHERE 
                    cd.cart_id = %s
                GROUP BY
                    cd.cart_detail_id, p.name
            """, (cart_id,))
            cart_items = cursor.fetchall()
            
            total_price = 0
            
            for item in cart_items:
                total_price += item[5] * item[7]            # calculate total price

            return render_template('layout.html', cart_items=cart_items, total_price=total_price)
        else:
            return render_template('layout.html', cart_items=[], total_price=0)
    except Exception as e:
        print(f"Error fetching shopping cart: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while fetching your shopping cart. Please try again later.'}), 500               # danger message

# Route for removing an item from the cart   
@order_inventory_bp.route("/remove_item", methods=["POST"])
def remove_item():
    try:
        cursor, connection = getCursor()
        customer_id = session.get('id')               # get customer in session
        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
        cart_id_row = cursor.fetchone()

        if cart_id_row:
            cart_id = cart_id_row[0]                 # fetch cart id
            
        data = request.json
        cart_detail_id = data.get('cart_detail_id')
            
        cursor.execute("DELETE FROM cart_details WHERE cart_detail_id = %s", (cart_detail_id,))             # delete item from cart_details table
        connection.commit()
        
        # fetch updated price of cart
        cursor.execute("""
                SELECT 
                    SUM(pv.additional_cost) AS total_additional_cost,
                    cd.quantity,
                    cd.price AS item_price,
                    (cd.price + COALESCE(SUM(pv.additional_cost), 0)) AS total_price
                FROM 
                    cart_details cd
                INNER JOIN 
                    product p ON cd.product_id = p.product_id
                LEFT JOIN 
                    cart_variations cv ON cd.cart_detail_id = cv.cart_detail_id
                LEFT JOIN 
                    product_variations pv ON cv.variation_id = pv.variation_id
                WHERE 
                    cd.cart_id = %s
                GROUP BY
                    cd.cart_detail_id, p.name;
        """, (cart_id,))
        cart_items = cursor.fetchall()
            
        total_price = 0
            
        for item in cart_items:
            total_price += item[1] * item[3]           # calculate total price
        
        return jsonify({'status': 'success', 'total_price': total_price}), 200           # success message

    except Exception as e:
        print(f"Error removing item: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while removing item from the cart.'}), 500             # danger message

# Route for updating the quantity of an item in the cart
@order_inventory_bp.route("/update_quantity", methods=["POST"])
def update_quantity():
    try:
        customer_id = session.get('id')             # get customer in session
        data = request.json
        cart_detail_id = data.get('cart_detail_id')
        new_quantity = data.get('new_quantity')
            
        cursor, connection = getCursor()
        cursor.execute("UPDATE cart_details SET quantity = %s WHERE cart_detail_id = %s", 
                       (new_quantity, cart_detail_id))            # update item quantity in cart_details table
        connection.commit()
        
        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
        cart_id_row = cursor.fetchone()
        if cart_id_row:
            cart_id = cart_id_row[0]             # fetch cart id
        
        # fetch updated price of cart
        cursor.execute("""
                SELECT 
                    SUM(pv.additional_cost) AS total_additional_cost,
                    cd.quantity,
                    cd.price AS item_price,
                    (cd.price + COALESCE(SUM(pv.additional_cost), 0)) AS total_price
                FROM 
                    cart_details cd
                INNER JOIN 
                    product p ON cd.product_id = p.product_id
                LEFT JOIN 
                    cart_variations cv ON cd.cart_detail_id = cv.cart_detail_id
                LEFT JOIN 
                    product_variations pv ON cv.variation_id = pv.variation_id
                WHERE 
                    cd.cart_id = %s
                GROUP BY
                    cd.cart_detail_id, p.name;
        """, (cart_id,))
        cart_items = cursor.fetchall()
            
        total_price = 0
            
        for item in cart_items:
            total_price += item[1] * item[3]            # calculate total price
        
        return jsonify({'status': 'success', 'total_price': total_price}), 200              # success message
    except Exception as e:
        print(f"Error updating quantity: {e}")
        return jsonify({'status': 'error', 'message': 'An error occurred while updating item quantity.'}), 500          # danger message

# Route for checking out
@order_inventory_bp.route("/checkout", methods=["GET","POST"])
def checkout():
    today = get_nz_now().strftime('%Y-%m-%d')
    customer_id = session.get('id')  # get customer in session
    if customer_id is None:
        flash("You must be logged in to shop.", "danger")
        return jsonify({'status': 'redirect', 'redirect_url': url_for('auth.login')}), 200  # redirect to login if non-logged in customer wants to shop
   
    cursor, connection = getCursor()
    cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
    cart_id_row = cursor.fetchone()
 
    if not cart_id_row:
        flash("No items in cart.", "warning")
        return render_template("checkout.html", cart_items=[], total_price=0, today=today)
 
    cart_id = cart_id_row[0]  # fetch cart id
 
    # fetch cart details
    cursor.execute("""            
        SELECT
            cd.cart_detail_id,
            p.name AS product_name,
            p.image AS product_image,
            GROUP_CONCAT(pv.variation_name SEPARATOR ', ') AS variation_names,
            SUM(pv.additional_cost) AS total_additional_cost,
            cd.quantity,
            cd.price AS item_price,
            (cd.price + COALESCE(SUM(pv.additional_cost), 0)) AS total_price,
            p.product_id,
            COALESCE(MAX(inv.stock_level), 999999) AS stock_level -- 999999 is used to indicate that the product is not in inventory
        FROM
            cart_details cd
        INNER JOIN
            product p ON cd.product_id = p.product_id
        LEFT JOIN
            cart_variations cv ON cd.cart_detail_id = cv.cart_detail_id
        LEFT JOIN
            product_variations pv ON cv.variation_id = pv.variation_id
        LEFT JOIN
            inventory inv ON p.product_id = inv.product_id
        WHERE
            cd.cart_id = %s
        GROUP BY
            cd.cart_detail_id, p.name
    """, (cart_id,))
    cart_items = cursor.fetchall()
    print(cart_items)
    insufficient_stock = any(item[9] < item[5] for item in cart_items) # check if stock level is less than quantity
    if insufficient_stock:
        flash("Some items in your cart are out of stock. Please remove them before checking out.", "danger")
 
    total_price = sum(item[5] * item[7] for item in cart_items)            # calculate total price

    opening_hours = get_opening_hours()
 
    if request.method == "POST":
        try:
            # Retrieve form data for checkout
            special_requests = request.form.get('special_requests', '')
            order_time = get_nz_now()
            pickup_option = request.form.get('pickup_option')
            pickup_date = request.form.get('pickup_date')
            pickup_time = request.form.get('pickup_time')
            promo_id = request.form.get("used_promo_id")
            payment_method = request.form.get('payment_method') if request.form.get('payment_method') else 'card'
            amount = float(request.form.get("final_amount"))
            gift_card_usage = request.form.get("use_gift_card")
            gift_card_id = request.form.get("gift_card_id")
            gift_card_amount = float(request.form.get("gift_card_amount", 0))
 
            gift_card_details = Room.get_gitf_card_by_Id(gift_card_id) if gift_card_id else None # fetch gift card details
 
            if not promo_id or promo_id.lower() == "none":
                promo_id = None
 
            if payment_method == 'card':
                payment_method = random.choice(['Debit Card', 'Credit Card'])
                payment_status = 'Completed'
            else:
                payment_method = 'Pay Later'
                payment_status = 'Pending'
 
            if pickup_option == 'ASAP':
                pickup_time = order_time          
            else:
                pickup_datetime_str = f"{pickup_date} {pickup_time}:00"            
                pickup_time = datetime.strptime(pickup_datetime_str, "%Y-%m-%d %H:%M:%S")            # to be inserted in the correct format in database

            # insert order details
            cursor.execute("""
                INSERT INTO orders (customer_id, order_time, special_requests, status, pickup_time, promo_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (customer_id, order_time, special_requests, 'Pending', pickup_time, promo_id))          # insert data into order table
            order_id = cursor.lastrowid
 
            for item in cart_items:
                # insert order details for each product
                cursor.execute("""
                    INSERT INTO order_details (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item[8], item[5], item[7]))                           # insert data into order_details table
                order_detail_id = cursor.lastrowid                                    # fetch last inserted order detail id
 
                # insert variations for each product
                cursor.execute("""
                    SELECT variation_id FROM cart_variations WHERE cart_detail_id = %s
                """, (item[0],))
                variations = cursor.fetchall()
                for variation in variations:
                    cursor.execute("""
                        INSERT INTO order_variations (order_detail_id, variation_id)
                        VALUES (%s, %s)
                    """, (order_detail_id, variation[0]))                       # insert data into order_variations table
                
                # Check if inventory record exists for the product
                cursor.execute("""
                    SELECT stock_level
                    FROM inventory
                    WHERE product_id = %s
                """, (item[8],))
                stock_result = cursor.fetchone()

                # If the inventory record exists, then update the stock level and check for availability
                if stock_result:
                    stock_level = stock_result[0] - item[5]

                    # Update the stock level
                    cursor.execute(""" 
                        UPDATE inventory SET stock_level = %s
                        WHERE product_id = %s
                    """, (stock_level, item[8]))

                    # If stock level is 0, update product availability
                    if stock_level <= 0:
                        cursor.execute("""
                            UPDATE product 
                            SET is_available = 0 
                            WHERE product_id = %s
                        """, (item[8],))
         
 
            if gift_card_usage and gift_card_amount > 0:
                if amount == 0:
                    cursor.execute("""
                        INSERT INTO order_payment (order_id, amount, payment_method, payment_status, payment_date, gift_card_id, gift_card_amount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (order_id, gift_card_amount, "Gift Card", payment_status, order_time, gift_card_id, gift_card_amount))  # insert data (with gift card) into order_payment table
                else:
                    cursor.execute("""
                        INSERT INTO order_payment (order_id, amount, payment_method, payment_status, payment_date, gift_card_id, gift_card_amount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (order_id, gift_card_amount, "Gift Card", payment_status, order_time, gift_card_id, gift_card_amount))  # insert data (with gift card) into order_payment table
                    cursor.execute("""
                        INSERT INTO order_payment (order_id, amount, payment_method, payment_status, payment_date)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, amount, payment_method, payment_status, order_time)) # insert data (without gift card) into order_payment table
                # update gift card balance and insert transaction
                cursor.execute("""UPDATE gift_cards SET current_balance = %s WHERE gift_card_id = %s""",
                               (gift_card_details.current_balance - Decimal(gift_card_amount), gift_card_id))
                cursor.execute("""INSERT INTO gift_card_transactions (gift_card_id, transaction_type, amount, transaction_date, customer_id) VALUES (%s, %s, %s, %s, %s)""",
                               (gift_card_id, "Redemption", gift_card_amount, today, customer_id))
            else:
                cursor.execute("""
                    INSERT INTO order_payment (order_id, amount, payment_method, payment_status, payment_date)
                    VALUES (%s, %s, %s, %s, %s)
                """, (order_id, amount, payment_method, payment_status, order_time))                 # insert data (without gift card) into order_payment table
 
            # clear the cart
            cursor.execute("DELETE FROM cart_variations WHERE cart_detail_id IN (SELECT cart_detail_id FROM cart_details WHERE cart_id = %s)", (cart_id,))
            cursor.execute("DELETE FROM cart_details WHERE cart_id = %s", (cart_id,))
            cursor.execute("DELETE FROM carts WHERE cart_id = %s", (cart_id,))
            gift_card_amount = gift_card_amount if gift_card_usage else 0
            amount += gift_card_amount
            Room.update_loyalty_points(customer_id, amount, "Earned ", "Order Payment")
 
            connection.commit()
            closeCursorAndConnection(cursor, connection)
            flash("Order has been placed successfully!", "success")               # success message
            return redirect(url_for('order_inventory.order_confirmation', order_id=order_id))
        except Exception as e:
            print(f"Error during checkout: {e}")
            connection.rollback()
            closeCursorAndConnection(cursor, connection)
            flash("Failed to place order. Please try again later.", "danger")          # danger message
            return render_template("checkout.html", cart_items=cart_items, total_price=total_price, today=today, opening_hours=opening_hours, insufficient_stock=insufficient_stock)
    else:
        print(cart_items)
        return render_template("checkout.html", cart_items=cart_items, total_price=total_price, today=today, opening_hours=opening_hours, insufficient_stock=insufficient_stock)

# Route for order confirmation
@order_inventory_bp.route("/order_confirmation/<order_id>", methods=["GET"])
def order_confirmation(order_id):
    customer_id = session.get('id')             # get customer in session
    if customer_id is None:
        flash("You must be logged in to shop.", "danger")          # danger message
        return jsonify({'status': 'redirect', 'redirect_url': url_for('auth.login')}), 200            # redirect to login if customer is not logged in
    
    try:
        cursor, connection = getCursor()
        # fetch order details
        cursor.execute("""
            SELECT 
                o.order_id, 
                o.order_time, 
                o.special_requests, 
                o.pickup_time, 
                GROUP_CONCAT(DISTINCT op.payment_method SEPARATOR ', ') AS payment_methods,
                GROUP_CONCAT(DISTINCT
                    CONCAT(
                        od.quantity, 'x ', p.name,
                        IFNULL(
                            (
                                SELECT CONCAT(' (', GROUP_CONCAT(DISTINCT pv.variation_name SEPARATOR ', '), ')')
                                FROM product_variations pv
                                JOIN order_variations ov ON pv.variation_id = ov.variation_id
                                WHERE ov.order_detail_id = od.order_detail_id
                            ),
                            ''
                        )
                    ) SEPARATOR '; '
                ) AS products,
                (SELECT SUM(amount) FROM order_payment WHERE order_id = o.order_id) AS total_amount
            FROM 
                orders o 
            JOIN 
                order_details od ON o.order_id = od.order_id 
            JOIN 
                product p ON od.product_id = p.product_id 
            JOIN 
                order_payment op ON o.order_id = op.order_id
            WHERE 
                o.order_id = %s AND o.customer_id = %s
            GROUP BY 
                o.order_id;
        """, (order_id, customer_id))
        order = cursor.fetchone()
        print(order)
        
        if not order:
            flash("Order not found.", "danger")
            return redirect(url_for('order_inventory.checkout'))
        
        order_time = order[1].strftime('%d-%m-%Y %H:%M')              # display order time in correct format
        pickup_time = order[3].strftime('%d-%m-%Y %H:%M')             # display pickup time in correct format
        
        formatted_order = list(order)
        formatted_order[1] = order_time
        formatted_order[3] = pickup_time
        amount_excld_GST = (order[6] * Decimal('0.85')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)           # calculate amount excluding GST
        closeCursorAndConnection(cursor, connection)
        return render_template('order_confirmation.html', order=formatted_order, order_id=order_id, amount_excld_GST=amount_excld_GST)
    except Exception as e:
        print(f"Error while fetching order confirmation: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to fetch order confirmation. Please try again later.'}), 500            # danger message

# Route for viewing order history
@order_inventory_bp.route("/order_history", methods=["GET"])
def order_history():
    customer_id = session.get('id')        # get customer in session
    if customer_id is None:
        flash("You must be logged in to view your order history.", "danger")           # danger message
        return jsonify({'status': 'redirect', 'redirect_url': url_for('auth.login')}), 200           # redirect to login if non-logged in customer wants to view order history

    cursor, connection = getCursor()
    # fetch order history
    cursor.execute("""
        SELECT 
            o.order_id,
            o.order_time,
            o.status,
            o.pickup_time,
            o.special_requests,
            GROUP_CONCAT(
                CONCAT(
                    od.quantity, 'x ', p.name,
                    IFNULL(
                        (
                            SELECT CONCAT(' (', GROUP_CONCAT(variation_name SEPARATOR ', '), ')')
                            FROM product_variations pv
                            JOIN order_variations ov ON pv.variation_id = ov.variation_id
                            WHERE ov.order_detail_id = od.order_detail_id
                        ),
                        ''
                    )
                ) ORDER BY od.order_detail_id SEPARATOR '; '
            ) AS products,
            (SELECT SUM(amount) FROM order_payment WHERE order_id = o.order_id) AS total_amount,
            GROUP_CONCAT(od.product_id ORDER BY od.order_detail_id) AS product_ids,
            GROUP_CONCAT(od.order_detail_id ORDER BY od.order_detail_id) AS order_detail_ids,
            COUNT(DISTINCT pr.review_id) > 0 AS order_already_reviewed        
        FROM 
            orders o
        JOIN 
            order_details od ON o.order_id = od.order_id
        JOIN 
            product p ON od.product_id = p.product_id
        LEFT JOIN
            product_reviews pr ON o.order_id = pr.order_id AND pr.product_id = od.product_id AND pr.customer_id = o.customer_id AND pr.order_detail_id = od.order_detail_id
        WHERE 
            o.customer_id = %s
        GROUP BY
            o.order_id, o.order_time
        ORDER BY 
            o.order_time DESC
    """, (customer_id,))
    order_history = cursor.fetchall()         
    closeCursorAndConnection(cursor, connection)
    
    formatted_order_history = []
    for order in order_history:
        formatted_order = list(order)
        formatted_order[1] = order[1].strftime('%d-%m-%Y %H:%M')                # display order time in correct format
        formatted_order[3] = order[3].strftime('%d-%m-%Y %H:%M')                # display pickup time in correct format
        formatted_order_history.append(formatted_order)
    return render_template("order_history.html", order_history=formatted_order_history, customer_id=customer_id)

# Route for reordering
@order_inventory_bp.route("/reorder/<order_id>", methods=["POST"])
def reorder(order_id):
    customer_id = session.get('id')        # get customer in session
    if customer_id is None:
        flash("You must be logged in to reorder.", "danger")           # danger message
        return jsonify({'status': 'redirect', 'redirect_url': url_for('auth.login')}), 200           # redirect to login if non-logged in customer wants to reorder
    
    try:
        cursor, connection = getCursor()
        cursor.execute("SELECT order_id FROM orders WHERE order_id = %s AND customer_id = %s", (order_id, customer_id))        # check if order belongs to customer
        order = cursor.fetchone()
        if not order:
            flash("Order not found.", "danger")                  # danger message
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404            
    
        # fetch order details
        cursor.execute("""
            SELECT 
                od.product_id, 
                od.quantity, 
                od.price, 
                GROUP_CONCAT(ov.variation_id) AS variation_ids 
            FROM 
                order_details od
            LEFT JOIN 
                order_variations ov ON od.order_detail_id = ov.order_detail_id
            WHERE 
                od.order_id = %s
            GROUP BY 
                od.product_id, od.quantity, od.price
        """, (order_id,))
        order_items = cursor.fetchall()

        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))         # check for existing cart
        cart = cursor.fetchone()
        if not cart:
            cursor.execute("INSERT INTO carts (customer_id, creation_time, last_updated) VALUES (%s, NOW(), NOW())", (customer_id,))           # create new cart if no existing cart
            cart_id = cursor.lastrowid
        else:
            cart_id = cart[0]              # fetch cart id

        for item in order_items:
            product_id, quantity, price, variation_ids = item

            cursor.execute("""
                INSERT INTO cart_details (cart_id, product_id, quantity, price) 
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
            """, (cart_id, product_id, quantity, price))              # insert data into cart_details table
            
            cart_detail_id = cursor.lastrowid             # fetch cart detail id

            if variation_ids:
                total_additional_cost = 0
                for variation_id in variation_ids.split(','):
                    cursor.execute("SELECT additional_cost FROM product_variations WHERE variation_id = %s", (variation_id,))
                    additional_cost = cursor.fetchone()[0]
                    total_additional_cost -= additional_cost

                    cursor.execute("""
                        INSERT INTO cart_variations (cart_detail_id, variation_id)
                        VALUES (%s, %s)
                    """, (cart_detail_id, variation_id))  # insert data into cart_variations table

                # Update the price in cart_details to include the additional cost of variations
                cursor.execute("""
                    UPDATE cart_details
                    SET price = price + %s
                    WHERE cart_detail_id = %s
                """, (total_additional_cost, cart_detail_id))

        connection.commit()
        closeCursorAndConnection(cursor, connection)
        return redirect(url_for("order_inventory.checkout"))          
    except Exception as e:
        print(f"Error reordering item: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to reorder item.'}), 500             # danger message

# Route for submitting a review
@order_inventory_bp.route("/submit_review", methods=['POST'])
def submit_review():
    customer_id = session.get('id')        # get customer in session
    if customer_id is None:
        flash("You must be logged in to submit order reviews.", "danger")           # danger message
        return jsonify({'status': 'redirect', 'redirect_url': url_for('auth.login')}), 200           # redirect to login if non-logged in customer wants to reorder
    
    cursor, connection = getCursor()
    
    if request.method == 'POST':
        order_id = request.form.get("order_id")
        product_ids = request.form.getlist("product_ids[]")
        order_detail_ids = request.form.getlist("order_detail_ids[]")

        # check if all products are rated
        for order_detail_id in order_detail_ids:
            rating = request.form.get(f"star_{order_detail_id}")
            if rating is None:
                flash("Please rate all products before submitting your review.", "danger")
                closeCursorAndConnection(cursor, connection)
                return redirect(url_for("order_inventory.order_history"))

        try:
            for product_id, order_detail_id in zip(product_ids, order_detail_ids):
                rating = request.form.get(f"star_{order_detail_id}")
                feedback = request.form.get(f"feedback_{order_detail_id}")

                cursor.execute("INSERT INTO product_reviews (customer_id, product_id, rating, feedback, order_id, order_detail_id) VALUES (%s, %s, %s, %s, %s, %s)",
                               (customer_id, product_id, rating, feedback, order_id, order_detail_id))                # insert data into product_reviews table

                # update product rating
                cursor.execute("""
                    UPDATE product 
                    SET average_rating = (
                        SELECT AVG(rating) 
                        FROM product_reviews 
                        WHERE product_id = %s
                    )
                    WHERE product_id = %s
                """, (product_id, product_id))
                connection.commit()

            flash("Review submitted successfully!", "success")            # success message
        except Exception as e:
            print(f"Error submitting review: {e}")
            flash("Failed to submit review. Please try again.", "danger")         # danger message
        finally:
            closeCursorAndConnection(cursor, connection)

        return redirect(url_for("order_inventory.order_history"))

# Function to check for gift cards in order details
def check_gift_cards_in_order(order_details):
    # define regular expression pattern to match gift card information
    gift_card_pattern = re.compile(r'(\d+)x Gift Card - \$(\d+\.\d{2})')

    # find all gift card information in order details
    gift_cards = gift_card_pattern.findall(order_details)
    if gift_cards:
        gift_card_info = []
        for gift_card in gift_cards:
            quantity = int(gift_card[0])
            amount = float(gift_card[1])
            gift_card_info.append({'quantity': quantity, 'amount': amount})
        return gift_card_info
    else:
        return None

# Function to handle gift cards in an order
def handle_gift_cards(gift_cards, cursor, connection, user_id, today):
    for gift_card in gift_cards:
        quantity = int(gift_card['quantity'])
        amount = float(gift_card['amount']) 
        
        # fetch gift_card_type_id
        cursor.execute("SELECT type_id FROM gift_card_types WHERE amount = %s", (amount,))
        gift_card_type_row = cursor.fetchone()
        if gift_card_type_row:
            gift_card_type_id = gift_card_type_row[0]
        else:
            print(f"No gift card type found for amount: ${amount}")
            continue
        print(f"Gift card type id: {gift_card_type_id}")
        for _ in range(quantity):
            # generate redemption code and password
            redemption_code, password = generate_redemption_code()
            print(f"Redemption code: {redemption_code}, Password: {password}")
            
            # insert gift card
            cursor.execute("""
                INSERT INTO gift_cards (type_id, redemption_code, gift_card_password, current_balance, issue_date, expiry_date) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (gift_card_type_id, redemption_code, password, amount, today, today.replace(year=today.year + 2)))
            gift_card_id = cursor.lastrowid
            print(f"Gift card id: {gift_card_id}")
            # insert gift card transaction
            cursor.execute("""
                INSERT INTO gift_card_transactions (gift_card_id, transaction_type, amount, transaction_date, customer_id) 
                VALUES (%s, %s, %s, %s, %s)
            """, (gift_card_id, 'Top-Up', amount, today, user_id))
            connection.commit()
            
            # send message to customer
            message = f"<br>Your ${amount} gift card code is: <strong>{redemption_code}</strong>. <br>And pin is: <strong>{password}</strong>. <br>Please keep this information safe."
            send_message_to_customer(user_id, message)

# Function to get opening hours for the current day
def get_opening_hours():
    cursor, connection = getCursor()
    today = get_nz_now().strftime('%A')
    
    # Determine the day group based on the current day
    if today in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        day_group = 'Monday-Friday'
    else:
        day_group = 'Saturday-Sunday'

    try:
        query = "SELECT TIME_FORMAT(open_time, '%H:%i'), TIME_FORMAT(close_time, '%H:%i') FROM opening_hours WHERE days = %s"
        cursor.execute(query, (day_group,))
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"Error getting opening hours: {e}")
        return None
    finally:
        closeCursorAndConnection(cursor, connection)