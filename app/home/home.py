# This is for the home blueprint
# Assigner: Mavis
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import Blueprint
from flask import request
from app.utils import getCursor, closeCursorAndConnection

home_bp = Blueprint("home", __name__, template_folder="templates", static_folder="static", static_url_path="/home/static")

@home_bp.before_request
def before_request():
    if "loggedin" in session and request.endpoint in ["home.home"]:
        if session.get("role") == "staff":
            return redirect(url_for("user_management.staff_dashboard"))
        elif session.get("role") == "manager":
            return redirect(url_for("user_management.manager_dashboard"))

@home_bp.route("/")
def home():
    cursor, connection = getCursor()

    # Get the products list
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()
    
    # Get the categories list
    cursor.execute("SELECT * FROM product_category")
    categories = cursor.fetchall()

    # Filter products for Merchandise and Others categories
    merchandise_products = [product for product in products if product[4] == 5]
    others_products = [product for product in products if product[4] == 6]

    # Get the rooms list
    cursor.execute("SELECT * FROM room")
    rooms = cursor.fetchall()

    # Get the latest 2 news
    query = """
    SELECT news_id, title, content, publish_time 
    FROM news 
    ORDER BY publish_time DESC 
    LIMIT 2
    """
    cursor.execute(query)
    news_list = cursor.fetchall()

    # Transform data to match template needs and include categories
    transformed_news = [
        {
            'id': news[0],
            'title': news[1],
            'content': news[2],
            'publish_time': news[3].strftime("%d-%m-%y"),
            'summary': news[2][:100] + '...' if len(news[2]) > 100 else news[2]
        }
        for news in news_list
    ]
    closeCursorAndConnection(cursor, connection)
    return render_template("home_page.html", news_list=transformed_news, products=products, categories=categories, merchandise_products=merchandise_products, others_products=others_products, rooms=rooms)
