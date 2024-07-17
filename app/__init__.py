from flask import Flask
from flask_login import LoginManager
from flask import session
from flask import g
from datetime import timedelta
import os
from app.utils import getCursor, closeCursorAndConnection, nz_time_filter, format_timedelta

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.jinja_env.filters['nz_time'] = nz_time_filter

    # this is where you import the blueprints
    from app.home import home
    from app.auth import auth
    from app.accommodation import accommodation
    from app.news_message import news_message
    from app.order_inventory import order_inventory
    from app.product import product_route
    from app.system_management import system_management
    from app.user_managememt import user_management


    app.secret_key = "key"
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    app.permanent_session_lifetime = timedelta(hours=24)
    UPLOAD_FOLDER = os.path.join(app.root_path, "static/image")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # this is where you register the blueprints
    app.register_blueprint(home.home_bp)
    app.register_blueprint(auth.auth_bp, url_prefix="/auth")
    app.register_blueprint(accommodation.accommodation_bp, url_prefix="/accommodation")
    app.register_blueprint(news_message.news_message_bp, url_prefix="/news_message")
    app.register_blueprint(order_inventory.order_inventory_bp, url_prefix="/order_inventory")
    app.register_blueprint(product_route.product_bp, url_prefix="/product")
    app.register_blueprint(system_management.system_management_bp, url_prefix="/system_management")
    app.register_blueprint(user_management.user_management_bp, url_prefix="/user_management")

    # Add context processor
    @app.context_processor
    def check_unread_inquiries():
        if 'loggedin' in session:
            user_id = session.get('id')
            unread_inquiries = has_unread_inquiries()
            unread_messages = has_unread_messages(user_id)
        else:
            unread_inquiries = False
            unread_messages = False
        hours = opening_hours()
        return dict(has_unread_inquiries=unread_inquiries, has_unread_message=unread_messages, hours=hours)
        
    return app

def has_unread_inquiries():
    cursor, connection = getCursor()
    try:
        unread_inquiries_query = "SELECT COUNT(*) FROM inquiries WHERE status = 'unread'"
        cursor.execute(unread_inquiries_query)
        unread_count = cursor.fetchone()[0]
        return unread_count > 0
    except Exception as e:
        print(f"Error checking unread inquiries: {e}")
        return False
    finally:
        closeCursorAndConnection(cursor, connection)

def has_unread_messages(user_id):
    cursor, connection = getCursor()
    try:
        unread_messages_query = "SELECT COUNT(*) FROM messages WHERE customer_id = %s AND status = 'unread'"
        cursor.execute(unread_messages_query, (user_id,))
        unread_count = cursor.fetchone()[0]
        return unread_count > 0
    except Exception as e:
        print(f"Error checking unread messages: {e}")
        return False
    finally:
        closeCursorAndConnection(cursor, connection)

def opening_hours():
        cursor, connection = getCursor()
        try:
            cursor.execute("""SELECT id, days, TIME_FORMAT(open_time, '%H:%i'), TIME_FORMAT(close_time, '%H:%i') 
                            FROM opening_hours ORDER BY id""")
            opening_hours = cursor.fetchall()
            return opening_hours
        except Exception as e:
            print(f"Error getting opening hours: {e}")
            return None
        finally:
            closeCursorAndConnection(cursor, connection)