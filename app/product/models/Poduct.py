from app.utils import getCursor, closeCursorAndConnection
from collections import namedtuple

# Class for product categories
class ProductCategory:
    def __init__(self, category_id, name):
        self.category_id = category_id
        self.name = name

    @staticmethod
    def get_all_categories():
        """Retrieve all product categories from the database."""
        categories = []
        cursor, connection = getCursor()
        cursor.execute("SELECT * FROM product_category")
        result = cursor.fetchall()
        for row in result:
            category = ProductCategory(row[0], row[1])
            categories.append(category)
        closeCursorAndConnection(cursor, connection)
        return categories

    @staticmethod
    def get_category_by_name(name):
        """Retrieve a specific product category by name."""
        cursor, connection = getCursor()
        cursor.execute("SELECT * FROM product_category WHERE name = %s", (name,))
        result = cursor.fetchone()
        closeCursorAndConnection(cursor, connection)
        if result:
            return ProductCategory(result[0], result[1])
        return None

# Class for products
class Product:
    def __init__(self, product_id, name, description, price, category_id, image, is_available, is_inventory, average_rating=0, total_ratings=0):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price
        self.category_id = category_id
        self.image = image
        self.is_available = is_available
        self.is_inventory = is_inventory
        self.average_rating = average_rating
        self.total_ratings = total_ratings

    @staticmethod
    def get_all_products():
        """Retrieve all products from the database."""
        products = []
        cursor, connection = getCursor()
        cursor.execute("SELECT * FROM product")
        result = cursor.fetchall()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        for row in result:
            product = Product(*row)
            products.append(product)
        closeCursorAndConnection(cursor, connection)
        return products

    @staticmethod
    def get_products_by_category(category_id):
        """Retrieve all available inventory products in a specific category."""
        products = []
        cursor, connection = getCursor()
        cursor.execute("SELECT * FROM product WHERE category_id = %s AND is_available = 1 AND is_inventory = 1", (category_id,))
        result = cursor.fetchall()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        for row in result:
            product = Product(*row)
            products.append(product)
        closeCursorAndConnection(cursor, connection)
        return products
    
    @staticmethod
    def get_products_reviews():
        """Retrieve all available inventory products in a specific category."""
        cursor, connection = getCursor()
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
        closeCursorAndConnection(cursor, connection)
        return reviews_data

    @staticmethod
    def get_product_details(product_id):
        """Retrieve detailed information about a specific product, including average rating and total ratings."""
        cursor, connection = getCursor()
        cursor.execute("""
            SELECT p.product_id, p.name, p.description, p.price, p.category_id, p.image, p.is_available, p.is_inventory,
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
            WHERE p.product_id = %s
        """, (product_id,))
        result = cursor.fetchone()
        closeCursorAndConnection(cursor, connection)
        if result:
            return Product(*result)
        return None

# Class for rooms
class Room:
    def __init__(self, room_id, type, capacity, description, price_per_night, image, amount):
        self.room_id = room_id
        self.type = type
        self.capacity = capacity
        self.description = description
        self.price_per_night = price_per_night
        self.image = image
        self.amount = amount

    @staticmethod
    def get_all_rooms():
        """Retrieve all rooms from the database."""
        rooms = []
        cursor, connection = getCursor()
        cursor.execute("SELECT * FROM room")
        result = cursor.fetchall()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        for row in result:
            room = Room(*Row(*row))
            rooms.append(room)
        closeCursorAndConnection(cursor, connection)
        return rooms

# Class for product variations
class ProductVariation:
    def __init__(self, variation_id, product_id, variation_name, additional_cost):
        self.variation_id = variation_id
        self.product_id = product_id
        self.variation_name = variation_name
        self.additional_cost = additional_cost
    
    @staticmethod
    def get_variations_by_product_id(product_id):
        """Retrieve all variations for a specific product."""
        variations = []
        cursor, connection = getCursor()
        cursor.execute("SELECT * FROM product_variations WHERE product_id = %s", (product_id,))
        result = cursor.fetchall()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        for row in result:
            variation = ProductVariation(*Row(*row))
            variations.append(variation)
        closeCursorAndConnection(cursor, connection)
        return variations
