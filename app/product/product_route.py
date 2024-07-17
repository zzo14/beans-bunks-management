# This is for the product blueprint
# Assigner: Ren
from flask import Flask, flash, render_template, redirect, url_for, session, Blueprint
from app.utils import getCursor, closeCursorAndConnection
from .models.Poduct import Product, ProductCategory, Room, ProductVariation

product_bp = Blueprint("product", __name__, template_folder="templates", static_folder="static", static_url_path="/product/static")

@product_bp.route("/products", defaults={'category': None})
@product_bp.route("/products/<category>")
def products(category):
    """Display products based on category. If no category is specified, display all products."""
    if category:
        category_obj = ProductCategory.get_category_by_name(category)  # Get category object by name
        if category_obj:
            products = Product.get_products_by_category(category_obj.category_id) # Fetch products for the specified category
            category_id = category_obj.category_id
        else:
            products = []
            flash("Category not found", "warning")
            category_id = None
    else:
        products = Product.get_all_products() # Fetch all products if no category is specified
        category_id = 1

    categories = ProductCategory.get_all_categories() # Get all product categories
    # Set availability status for each product
    for product in products:
        if product.is_available == 0:
            product.availability = "Unavailable"
        else:
            product.availability = "Available"
    return render_template("products.html", category_id=category_id, products=products, categories=categories)

@product_bp.route("/menu")
def menu():
    """
    Display the menu with all products and their details.
    """
    products, categories, reviews_data = handle_product()
    return render_template("menu.html", products=products, categories=categories, reviews_data=reviews_data)

@product_bp.route("/shop")
def shop():
    """
    Display the shop page with all products and their details.
    """
    products, categories, reviews_data = handle_product()
    return render_template("shop.html", products=products, categories=categories, reviews_data=reviews_data)

@product_bp.route("/rooms")
def rooms():
    """
    Display the rooms page with all available rooms.
    """
    rooms = Room.get_all_rooms()
    return render_template("rooms.html", rooms=rooms)


def handle_product():
    """
    Fetch all products and categories, and update product details with availability, ratings, and variations.
    Returns:
        products (list): List of Product objects with updated details.
        categories (list): List of ProductCategory objects.
    """
    products = Product.get_all_products()
    categories = ProductCategory.get_all_categories()
    reviews_data = Product.get_products_reviews()

    for product in products:
        # Set availability status for each product
        if product.is_available == 0:
            product.availability = "Unavailable"
        else:
            product.availability = "Available"

        # Get detailed product information
        product_details = Product.get_product_details(product.product_id)
        if product_details:
            product.average_rating = product_details.average_rating
            product.total_ratings = product_details.total_ratings 
        else:
            product.average_rating = 0
            product.total_ratings = 0   
        # Get variations for the product
        product.variations = ProductVariation.get_variations_by_product_id(product.product_id)
    return products, categories, reviews_data