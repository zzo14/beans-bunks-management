from app.utils import getCursor, closeCursorAndConnection
from collections import namedtuple

# Define namedtuples for Message and Inquiry to structure data
Message = namedtuple('Message', ['message_id', 'sender_id', 'customer_id', 'inquiry_id', 'message_text', 'timestamp', 'status'])
Inquiry = namedtuple('Inquiry', ['inquiry_id', 'customer_id', 'inquiry_text', 'timestamp', 'status'])

# Function to create a message in the database
def create_message(sender_id, customer_id, inquiry_id, message_text):
    dbconn, connection = getCursor()
    try:
        sql = "INSERT INTO messages (sender_id, customer_id, inquiry_id, message_text) VALUES (%s, %s, %s, %s)"
        dbconn.execute(sql, (sender_id, customer_id, inquiry_id, message_text))
        connection.commit()
    finally:
        closeCursorAndConnection(dbconn, connection)

# Function to fetch all messages for a specific customer
def get_messages_for_customer(customer_id):
    dbconn, connection = getCursor()
    try:
        sql = "SELECT message_id, sender_id, customer_id, inquiry_id, message_text, timestamp, status FROM messages WHERE customer_id = %s"
        dbconn.execute(sql, (customer_id,))
        result = dbconn.fetchall()
        messages = [Message(*row) for row in result]
        return messages
    finally:
        closeCursorAndConnection(dbconn, connection)

# Function to fetch all messages
def get_all_messages():
    dbconn, connection = getCursor()
    try:
        sql = "SELECT message_id, sender_id, customer_id, inquiry_id, message_text, timestamp, status FROM messages"
        dbconn.execute(sql)
        result = dbconn.fetchall()
        messages = [Message(*row) for row in result]
        return messages
    finally:
        closeCursorAndConnection(dbconn, connection)

# Function to fetch all inquiries with non-empty inquiry text
def get_inquiries():
    dbconn, connection = getCursor()
    try:
        sql = "SELECT inquiry_id, customer_id, inquiry_text, timestamp, status FROM inquiries WHERE inquiry_text != ''"
        dbconn.execute(sql)
        result = dbconn.fetchall()
        inquiries = [Inquiry(*row) for row in result]
        return inquiries
    finally:
        closeCursorAndConnection(dbconn, connection)

# Function to create an inquiry in the database
def create_inquiry(customer_id, inquiry_text):
    dbconn, connection = getCursor()
    try:
        sql = "INSERT INTO inquiries (customer_id, inquiry_text) VALUES (%s, %s)"
        dbconn.execute(sql, (customer_id, inquiry_text))
        connection.commit()
    finally:
        closeCursorAndConnection(dbconn, connection)

# Function to update the status of an inquiry
def update_inquiry_status(inquiry_id, status):
    dbconn, connection = getCursor()
    try:
        sql = "UPDATE inquiries SET status = %s WHERE inquiry_id = %s"
        dbconn.execute(sql, (status, inquiry_id))
        connection.commit()
    finally:
        closeCursorAndConnection(dbconn, connection)

# Function to fetch all inquiries for a specific customer
def get_inquiries_for_customer(customer_id):
    dbconn, connection = getCursor()
    try:
        sql = "SELECT inquiry_id, customer_id, inquiry_text, timestamp, status FROM inquiries WHERE customer_id = %s"
        dbconn.execute(sql, (customer_id,))
        result = dbconn.fetchall()
        inquiries = [Inquiry(*row) for row in result]
        return inquiries
    finally:
        closeCursorAndConnection(dbconn, connection)

# Function to fetch all inquiries along with customer names
def get_inquiries_with_customer_names():
    dbconn, connection = getCursor()
    try:
        sql = """
            SELECT i.inquiry_id, i.customer_id, c.first_name, c.last_name, i.inquiry_text, i.timestamp, i.status
            FROM inquiries i
            JOIN customer c ON i.customer_id = c.customer_id
            WHERE i.inquiry_text != ''
            ORDER BY i.timestamp DESC
        """
        dbconn.execute(sql)
        result = dbconn.fetchall()
        inquiries = [{
            'inquiry_id': row[0],
            'customer_id': row[1],
            'customer_name': f"{row[2]} {row[3]}",
            'inquiry_text': row[4],
            'timestamp': row[5],
            'status': row[6]
        } for row in result]
        return inquiries
    except Exception as e:
        print(f"Error fetching inquiries with customer names: {e}")
        return []
    finally:
        closeCursorAndConnection(dbconn, connection)

# Function to update the status of a message
def update_message_status(message_id, status):
    dbconn, connection = getCursor()
    try:
        sql = "UPDATE messages SET status = %s WHERE message_id = %s"
        dbconn.execute(sql, (status, message_id))
        connection.commit()
    except Exception as e:
        print(f"Error updating message status: {e}")
    finally:
        closeCursorAndConnection(dbconn, connection)

# Function to update the status of an inquiry
def update_inquiry_status(inquiry_id, status):
    cursor, conn = getCursor()
    try:
        cursor.execute("UPDATE inquiries SET status = %s WHERE inquiry_id = %s", (status, inquiry_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating inquiry status: {e}")
    finally:
        closeCursorAndConnection(cursor, conn)

# Function to fetch inquiries with filters and sorting
def get_filtered_sorted_inquiries(customer_name, inquiry_text, timestamp):
    dbconn, connection = getCursor()
    try:
        sql = """
            SELECT i.inquiry_id, i.customer_id, c.first_name, c.last_name, i.inquiry_text, i.timestamp, i.status
            FROM inquiries i
            JOIN customer c ON i.customer_id = c.customer_id
            WHERE (%s = '' OR c.first_name LIKE %s OR c.last_name LIKE %s)
            AND (%s = '' OR i.inquiry_text LIKE %s)
            AND (%s = '' OR i.timestamp >= %s)
            ORDER BY
                CASE
                    WHEN i.status = 'unread' THEN 1
                    WHEN i.status = 'pending' THEN 2
                    WHEN i.status = 'responded' THEN 3
                    ELSE 4
                END,
                i.timestamp DESC
        """
        dbconn.execute(sql, (
            customer_name, f'%{customer_name}%', f'%{customer_name}%',
            inquiry_text, f'%{inquiry_text}%',
            timestamp, timestamp
        ))
        result = dbconn.fetchall()
        inquiries = [{
            'inquiry_id': row[0],
            'customer_id': row[1],
            'customer_name': f"{row[2]} {row[3]}",
            'inquiry_text': row[4],
            'timestamp': row[5],
            'status': row[6]
        } for row in result]
        return inquiries
    except Exception as e:
        print(f"Error fetching inquiries with filters: {e}")
        return []
    finally:
        closeCursorAndConnection(dbconn, connection)
