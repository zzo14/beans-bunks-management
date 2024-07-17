# This is for the news and message blueprint
# Assigner: Elaine, Ren
from flask import Flask, flash
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import Blueprint
from flask import request
from datetime import datetime
from app.utils import getCursor, closeCursorAndConnection, verify_access, validate_form, validate_varchar, validate_text, validate_date, validate_time, validate_decimal
from .models.Message import create_message, create_inquiry, get_filtered_sorted_inquiries, get_all_messages, update_inquiry_status, get_inquiries_for_customer, get_messages_for_customer, get_inquiries_with_customer_names, update_message_status, update_inquiry_status


news_message_bp = Blueprint("news_message", __name__, template_folder="templates", static_folder="static", static_url_path="/news_message/static")

# Route for handling customer inquiries
@news_message_bp.route('/customer', methods=['GET', 'POST'])
def customer_inquiries():
    if 'loggedin' not in session or session.get('role') not in ['customer', 'staff', 'manager']:
        flash('You need to be logged in to view messages.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        form = request.form
        inquiry_text = form.get('message_text')

        if not inquiry_text:
            flash('Message content is required.', 'danger')
        else:
            customer_id = session.get('id')
            create_inquiry(customer_id, inquiry_text)
            flash('Inquiry sent successfully!', 'success')

    inquiries = get_inquiries_for_customer(session.get('id'))
    messages = get_messages_for_customer(session.get('id'))
    return render_template('customer_inquiries.html', inquiries=inquiries, messages=messages)

# Route for marking a message as read
@news_message_bp.route('/mark_message_as_read', methods=['POST'])
def mark_message_as_read():
    if 'loggedin' not in session or session.get('role') not in ['customer', 'staff', 'manager']:
        flash('You need to be logged in to perform this action.', 'danger')
        return redirect(url_for('auth.login'))

    message_id = request.form.get('message_id')
    if message_id:
        update_message_status(message_id, 'received')
        flash('New message has been read.', 'success')
    
    return redirect(url_for('news_message.customer_inquiries'))

# Route for handling staff messages
@news_message_bp.route('/staff', methods=['GET', 'POST'])
def staff_messages():
    if 'loggedin' not in session or session.get('role') not in ['staff', 'manager']:
        flash('You need to be logged in as staff or manager to view inquiries.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        form = request.form
        inquiry_id = form.get('inquiry_id')
        response_text = form.get('response_text')
        customer_id = form.get('customer_id')

        if not response_text:
            flash('Response content is required.', 'danger')
        else:
            staff_id = session.get('id')
            create_message(staff_id, customer_id, inquiry_id, response_text)
            update_inquiry_status(inquiry_id, 'responded')
            flash('Response sent and inquiry status updated to responded.', 'success')

    inquiries = get_inquiries_with_customer_names()

    # Sort inquiries by status (unread > pending > responded), then by timestamp
    inquiries = sorted(inquiries, key=lambda i: (['responded', 'pending', 'unread'].index(i['status']), i['timestamp']), reverse=True)

    messages = get_all_messages()
    return render_template('staff_messages.html', inquiries=inquiries, messages=messages)

# Route for marking an inquiry as read
@news_message_bp.route('/mark_inquiry_as_read', methods=['POST'])
def mark_inquiry_as_read():
    if 'loggedin' not in session or session.get('role') not in ['staff', 'manager']:
        flash('You need to be logged in as staff or manager to perform this action.', 'danger')
        return redirect(url_for('auth.login'))

    inquiry_id = request.form.get('inquiry_id')
    if inquiry_id:
        update_inquiry_status(inquiry_id, 'pending')
        flash('New inquiry has been read.', 'success')
    
    return redirect(url_for('news_message.staff_messages'))

# Route for displaying news
@news_message_bp.route("/news")
def news():
    dbconn, connection = getCursor()
    query = """
    SELECT news_id, title, content, publish_time 
    FROM news 
    ORDER BY publish_time DESC 
    LIMIT 5
    """
    dbconn.execute(query)
    news_list = dbconn.fetchall()
    closeCursorAndConnection(dbconn, connection)
    
    # Transform data to match template needs and include categories
    transformed_news = [
        {
            'id': news[0],
            'title': news[1],
            'content': news[2],
            'publish_time': news[3].strftime("%d-%m-%y"),  # Format publish time
            'summary': news[2][:100] + '...' if len(news[2]) > 100 else news[2]  # Truncate summary if too long
        }
    for i, news in enumerate(news_list)]

    return render_template("news.html", news_list=transformed_news)

# Route for adding news
@news_message_bp.route("/add_news", methods=["POST"])
def add_news():
    required_fields = ['title', 'content']
    field_validations = {
        'title': validate_text,
        'content': validate_text
    }
    if not validate_form(request.form, required_fields, field_validations):
        return redirect(url_for('news_message.news'))
    if request.method == "POST":
        db_cursor, db_connection = getCursor()
        title = request.form.get('title')
        content = request.form.get('content')
        manager_id = session.get('id')  # Assuming manager's user_id is stored in session
        
        if not manager_id:
            flash('You must be logged in to add news.', 'danger')
            return redirect(url_for('news_message.news'))

        try:
            query = """
            INSERT INTO news (title, content, publish_time, manager_id)
            VALUES (%s, %s, %s, %s)
            """
            db_cursor.execute(query, (title, content, datetime.now(), manager_id))
            db_connection.commit()
            flash('News item added successfully.', 'success')
        except Exception as e:
            db_connection.rollback()
            print(f"Error: {e} at news_message.add_news")
            flash(f'An error occurred while adding the news item: {e}', 'danger')
        finally:
            db_cursor.close()
            db_connection.close()
        return redirect(url_for('news_message.news'))

# Route for updating news
@news_message_bp.route("/update_news", methods=["POST"])
def update_news():
    # This route processes the form submission for updating a news item.
    required_fields = ['title', 'content']
    field_validations = {
        'title': validate_text,
        'content': validate_text
    }
    if not validate_form(request.form, required_fields, field_validations):
        return redirect(url_for('news_message.news'))

    db_cursor, db_connection = getCursor()
    news_id = request.form.get('news_id')
    title = request.form.get('title')
    content = request.form.get('content')
    manager_id = session.get('id')  # Assuming manager's user_id is stored in session

    if not manager_id:
        flash('You must be logged in to update news.', 'danger')
        return redirect(url_for('news_message.news'))
    try:
        query = """UPDATE news SET title = %s, content = %s WHERE news_id = %s"""
        db_cursor.execute(query, (title, content, news_id))
        db_connection.commit()
        if db_cursor.rowcount > 0:
            flash('News updated successfully.', 'success')
        else:
            flash('No update for news.', 'warning')
    except Exception as e:
        db_connection.rollback()
        print(f"Error: {e} at news_message.update_news")
        flash('An error occurred while updating the news item. Please try again.', 'danger')
    finally:
        db_cursor.close()
        db_connection.close()
    return redirect(url_for('news_message.news'))

# Route for deleting news
@news_message_bp.route("/delete_news", methods=["POST"])
def delete_news():
    # This route processes the form submission for deleting a news item.
    db_cursor, db_connection = getCursor()
    news_id = request.form.get('news_id')
    manager_id = session.get('id')  # Assuming manager's user_id is stored in session

    if not manager_id:
        flash('You must be logged in to delete news.', 'danger')
        return redirect(url_for('news_message.news'))
    try:
        query = """DELETE FROM news WHERE news_id = %s"""
        db_cursor.execute(query, (news_id,))
        db_connection.commit()
        if db_cursor.rowcount > 0:
            flash('News deleted successfully.', 'success')
        else:
            flash('Deletion failed, please try again.', 'danger')
    except Exception as e:
        db_connection.rollback()
        print(f"Error: {e} at news_message.delete_news")
        flash('An error occurred while deleting the news item. Please try again.', 'danger')
    finally:
        db_cursor.close()
        db_connection.close()
    return redirect(url_for('news_message.news'))

