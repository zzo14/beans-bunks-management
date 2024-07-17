from flask_login import UserMixin
from flask import flash
from app.utils import getCursor, closeCursorAndConnection
from app import login_manager

class UserAuth(UserMixin): # UserMixin is a class from flask_login that provides default implementations for the methods that Flask-Login expects user objects to have.
    def __init__(self, id, username, first_name, last_name, role, isActive):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.isActive = isActive
    
    def get_id(self):
        return str(self.id)
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_role(self):
        return self.role
    
@login_manager.user_loader # This decorator is used to tell Flask-Login how to get a user object from the user ID stored in the session.
def load_user(user_id):
    # This function is used to load a user object from the user ID stored in the session.
    cursor, connection = getCursor()
    auth_query = "SELECT id, username, role, is_active FROM auth WHERE id = %s"
    cursor.execute(auth_query, (user_id,))
    auth_data = cursor.fetchone()

    if not auth_data:
        closeCursorAndConnection(cursor, connection)
        return None

    user_id, username, role, is_active = auth_data
    if role == 'customer':
        detail_query = "SELECT first_name, last_name FROM customer WHERE customer_id = %s"
    elif role == 'staff':
        detail_query = "SELECT first_name, last_name FROM staff WHERE staff_id = %s"
    elif role == 'manager':
        detail_query = "SELECT first_name, last_name FROM manager WHERE manager_id = %s"
    else:
        closeCursorAndConnection(cursor, connection)
        return None

    cursor.execute(detail_query, (user_id,))
    detail_data = cursor.fetchone()
    closeCursorAndConnection(cursor, connection)

    if detail_data:
        first_name, last_name = detail_data
        user = UserAuth(user_id, username, first_name, last_name, role, is_active)
        return user
    return None
