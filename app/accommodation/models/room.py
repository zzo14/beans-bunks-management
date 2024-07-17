from flask import flash
from app.utils import getCursor, closeCursorAndConnection
from collections import namedtuple
from datetime import datetime, timedelta
from decimal import Decimal

class Room():
    def get_all_rooms():
        # get all rooms information
        cursor, connection = getCursor()
        query = "SELECT * FROM room"
        cursor.execute(query)
        rows = cursor.fetchall()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        rooms = list(map(lambda row: Row(*row), rows))
        closeCursorAndConnection(cursor, connection)
        return rooms
    
    def get_week_availability(start_date):
        # get the availability of all rooms for the next 7 days
        cursor, connection = getCursor()
        end_date = start_date + timedelta(days=7)
        # get all rooms information
        rooms = Room.get_all_rooms()
        # get all bookings inforamtions since the start date
        cursor.execute("""SELECT booking_id, room_id, check_in_date, check_out_date, number_of_bunks 
                          FROM bookings
                          WHERE (check_in_date < %s AND check_out_date > %s) AND status != 'Cancelled'""", (end_date, start_date))
        rows = cursor.fetchall()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        bookings = list(map(lambda row: Row(*row), rows))

        # create a dictionary to store the availability of each room
        availability = {}
        for room in rooms:
            availability[room.room_id] = {
                'type': room.type,
                'price': room.price_per_night,
                'availability': [room.amount] * 7
            }
        # update the availability of each room
        for booking in bookings:
            room_id = booking.room_id
            check_in_date = max(booking.check_in_date, start_date)
            check_out_date = min(booking.check_out_date, end_date)

            start_idx = (check_in_date - start_date).days
            end_idx = (check_out_date - start_date).days
            
            number_of_bunks = booking.number_of_bunks
            if not booking.number_of_bunks:
                number_of_bunks = 1

            for i in range(start_idx, end_idx):
                availability[room_id]['availability'][i] -= number_of_bunks
        closeCursorAndConnection(cursor, connection)
        return availability
    
    def book_room(customer_id, room_id, check_in_date, check_out_date, number_of_bunks, price):
        # book a room for a customer
        cursor, connection = getCursor()
        try:
            query = """INSERT INTO bookings (customer_id, room_id, number_of_bunks, check_in_date, check_out_date, status, price) VALUES 
                (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (customer_id, room_id, number_of_bunks, check_in_date, check_out_date, "Pending", price))
            connection.commit()
            booking_id = cursor.lastrowid
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.book_room")
            return None
        closeCursorAndConnection(cursor, connection)
        return booking_id
    
    def get_bookings_by_booking_id(booking_id):
        # get booking details by booking id
        cursor, connection = getCursor()
        cursor.execute("""SELECT b.*, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, r.type, r.image, DATEDIFF(check_out_date, check_in_date) AS nights 
                          FROM bookings b 
                          JOIN customer c ON c.customer_id = b.customer_id
                          JOIN room r ON r.room_id = b.room_id
                          WHERE booking_id = %s""", (booking_id,))
        row = cursor.fetchone()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        booking_details = Row(*row)
        closeCursorAndConnection(cursor, connection)
        return booking_details
    
    def get_gitf_card_info():
        # get all active gift cards
        cursor, connection = getCursor()
        cursor.execute("SELECT * FROM gift_cards WHERE expiry_date > CURDATE()")
        rows = cursor.fetchall()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        gift_card = list(map(lambda row: Row(*row), rows))
        closeCursorAndConnection(cursor, connection)
        return gift_card
    
    def get_gitf_card_by_Id(gift_card_id):
        # get gift card details by gift card id
        cursor, connection = getCursor()
        cursor.execute("SELECT * FROM gift_cards WHERE gift_card_id = %s AND expiry_date > CURDATE()", (gift_card_id,))
        row = cursor.fetchone()
        if row:
            Row = namedtuple("Row", [column[0] for column in cursor.description])
            gift_card = Row(*row)
        else:
            gift_card = None
        closeCursorAndConnection(cursor, connection)
        return gift_card
    
    def validate_gift_card(gift_card_code, gift_card_password):
        # validate the gift card by gift card code and password
        cursor, connection = getCursor()
        cursor.execute("SELECT * FROM gift_cards WHERE redemption_code = %s AND gift_card_password = %s AND expiry_date > CURDATE()", (gift_card_code, gift_card_password))
        row = cursor.fetchone()
        if row:
            Row = namedtuple("Row", [column[0] for column in cursor.description])
            gift_card_details = Row(*row)
        else:
            gift_card_details = None
        closeCursorAndConnection(cursor, connection)
        return gift_card_details
    
    def make_booking_payment(booking_id, payment_method, gift_card_usage, gift_card_amount, payment_amount, gift_card_id, customer_id, promo_id=None):
        # make payment for the booking
        payment_amount = Decimal(payment_amount) # convert payment amount to decimal
        gift_card_amount = Decimal(gift_card_amount) # convert gift card amount to decimal
        all_success = True # flag to check if all the payment is successful
        gift_card_details = Room.get_gitf_card_by_Id(gift_card_id) # get gift card details by gift card id

        # use gift card to pay for the booking
        if gift_card_usage and gift_card_amount > 0:
            if payment_amount == 0: # only use gift card to pay for the booking
                if not Room.insert_booking_payment(booking_id, gift_card_amount, "Gift Card", "Completed", gift_card_details.gift_card_id, gift_card_amount):
                    all_success = False
            else: # combine gift card and other payment method to pay for the booking
                # use gift card to pay for the booking
                if not Room.insert_booking_payment(booking_id, gift_card_amount, "Gift Card", "Completed", gift_card_details.gift_card_id, gift_card_amount):
                    all_success = False
                # use other payment method to pay for the remaining amount
                if not Room.insert_booking_payment(booking_id, payment_amount, payment_method, "Completed"):
                    all_success = False
            # update gift card balance
            if not Room.gift_card_payment(gift_card_details, gift_card_amount, customer_id):
                all_success = False
        else:
            # use other payment method to pay for the booking
            if not Room.insert_booking_payment(booking_id, payment_amount, payment_method, "Completed"):
                all_success = False

        if promo_id: # use promo code when making payment
            print("promo_id", promo_id)
            if not Room.insert_promo_trans(promo_id, customer_id):
                all_success = False

        if all_success:
            total_amount = gift_card_amount + payment_amount
            result = Room.update_booking_status(booking_id, "Paid", total_amount) # update booking status
            Room.update_loyalty_points(customer_id, total_amount, "Earned ", "Booking Payment") # update loyalty points
            return result
        else:
            print(f"Error: Failed to complete booking payment for booking_id: {booking_id} at Room.make_booking_payment")
            return False  
    
    def update_booking_status(booking_id, status, total_amount):
        # update booking status
        cursor, connection = getCursor()
        try:
            cursor.execute("UPDATE bookings SET status = %s, price = %s WHERE booking_id = %s", (status, total_amount, booking_id))
            connection.commit()
            if cursor.rowcount > 0:
                return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.update_booking_status")
            return False
        closeCursorAndConnection(cursor, connection)
        return True
    
    def insert_booking_payment(booking_id, amount, payment_method, payment_status, gift_card_id=None, gift_card_amount=None):
        # insert booking payment details
        cursor, connection = getCursor()
        try:
            query = """INSERT INTO `booking_payment` (`booking_id`, `amount`, `payment_method`, `payment_status`, `payment_date`, `gift_card_id`, `gift_card_amount`) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (booking_id, amount, payment_method, payment_status, datetime.now(), gift_card_id, gift_card_amount,))
            connection.commit()
            new_payment_id = cursor.lastrowid
            if new_payment_id:
                return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.insert_booking_payment")
            return False
        finally:
            closeCursorAndConnection(cursor, connection)
    
    def gift_card_payment(gift_card_details, gift_card_amount, customer_id):
        # update gift card balance
        cursor, connection = getCursor()
        gift_card_amount = Decimal(gift_card_amount)
        try:
            # update gift card balance
            query = """UPDATE gift_cards SET current_balance = %s WHERE gift_card_id = %s"""
            cursor.execute(query, (gift_card_details.current_balance - gift_card_amount, gift_card_details.gift_card_id))
            active_rows = cursor.rowcount
            # insert gift card transaction details
            query = """INSERT INTO gift_card_transactions (gift_card_id, transaction_type, amount, transaction_date, customer_id) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (gift_card_details.gift_card_id, "Redemption", gift_card_amount, datetime.now().date(), customer_id))
            new_transaction_id = cursor.lastrowid
            connection.commit()
            if active_rows > 0 and new_transaction_id:
                return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.gift_card_payment")
            return False
        finally:
            closeCursorAndConnection(cursor, connection)

    def get_promo_code_details(promo_code):
        # get promo code details by promo code
        cursor, connection = getCursor()
        cursor.execute("SELECT * FROM promotions WHERE promo_code = %s", (promo_code,))
        row = cursor.fetchone()
        if row:
            Row = namedtuple("Row", [column[0] for column in cursor.description])
            promo_details = Row(*row)
        else:
            promo_details = None
        closeCursorAndConnection(cursor, connection)
        return promo_details
    
    def insert_promo_trans(promo_id, customer_id):
        # insert promo transaction details
        cursor, connection = getCursor()
        try:
            query = """INSERT INTO customer_promos (promo_id, customer_id, used_date) VALUES (%s, %s, %s)"""
            cursor.execute(query, (promo_id, customer_id, datetime.now().date()))
            connection.commit()
            new_transaction_id = cursor.lastrowid
            if new_transaction_id:
                return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.insert_promo_trans")
            return False
        finally:
            closeCursorAndConnection(cursor, connection)
    
    def update_loyalty_points(customer_id, points, transaction_type, description):
        # update loyalty points
        cursor, connection = getCursor()
        try:
            query = """INSERT INTO points_transactions (customer_id, points, transaction_type, description, transaction_date) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (customer_id, points, transaction_type, description, datetime.now().date()))
            new_transaction_id = cursor.lastrowid
            if transaction_type == "Spent":
                query = """UPDATE loyalty_points SET total_spent = total_spent + %s WHERE customer_id = %s"""
            else:
                query = """UPDATE loyalty_points SET total_earned = total_earned + %s WHERE customer_id = %s"""
            cursor.execute(query, (points, customer_id))
            active_rows = cursor.rowcount
            connection.commit()
            if new_transaction_id and active_rows > 0:
                return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.insert_loyalty_points")
            return False
        finally:
            closeCursorAndConnection(cursor, connection)

    def confirm_booking_auto(booking_id):
        # confirm booking automatically
        cursor, connection = getCursor()
        try:
            cursor.execute("UPDATE bookings SET status = 'Confirmed' WHERE booking_id = %s", (booking_id,))
            connection.commit()
            if cursor.rowcount > 0:
                return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.confirm_booking_auto")
            return False
        finally:
            closeCursorAndConnection(cursor, connection)

    def get_bookings_by_customer_id(customer_id):
        # get all bookings by customer id
        cursor, connection = getCursor()
        cursor.execute("""SELECT b.*, r.type, DATEDIFF(check_out_date, check_in_date) AS nights 
                          FROM bookings b 
                          JOIN room r ON r.room_id = b.room_id
                          WHERE customer_id = %s
                          ORDER BY check_in_date, check_out_date""", (customer_id,))
        rows = cursor.fetchall()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        bookings = list(map(lambda row: Row(*row), rows))
        closeCursorAndConnection(cursor, connection)
        return bookings
    
    def cancel_booking(booking_id, customer_id, booking_status):
        # cancel booking
        cursor, connection = getCursor()
        try:
            if booking_status == "Pending":
                cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = %s", (booking_id,))
                connection.commit()
                return True
            else:
                # update booking status to Cancelled
                cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = %s", (booking_id,))
                # make refund for gift card payment
                cursor.execute("SELECT * FROM booking_payment WHERE booking_id = %s", (booking_id,))
                payments = cursor.fetchall()
                total_amount = 0
                for payment in payments: 
                    total_amount += payment[2]
                    payment_method = payment[3]      
                    gift_card_id = payment[6]      
                    gift_card_amount = payment[7]
                    if payment_method == "Gift Card" and gift_card_id: # refund gift card payment
                        cursor.execute("UPDATE gift_cards SET current_balance = current_balance + %s WHERE gift_card_id = %s", (gift_card_amount, gift_card_id))
                        cursor.execute( """INSERT INTO gift_card_transactions (gift_card_id, transaction_type, amount, transaction_date)
                        VALUES (%s, %s, %s, CURDATE())""", (gift_card_id, "Top-Up", gift_card_amount))
                # update payment status to Cancelled
                cursor.execute("UPDATE booking_payment SET payment_status = 'Refunded' WHERE booking_id = %s", (booking_id,))
                Room.update_loyalty_points(customer_id, total_amount, "Spent", "Cancelled Booking Refund")
                connection.commit()
                return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.cancel_booking")
            return False
        finally:
            closeCursorAndConnection(cursor, connection)

    def get_date_conflicts(room_id, new_check_in_date, new_check_out_date, exclude_booking_id=None, number_of_bunks=None):
        # get date conflicts for the booking
        cursor, connection = getCursor()
        try:
            if not exclude_booking_id:
                exclude_booking_id = 0
            query = """
                SELECT booking_id, check_in_date, check_out_date, number_of_bunks
                FROM bookings
                WHERE room_id = %s
                AND booking_id != %s
                AND status != 'Cancelled'
                AND (
                    (check_in_date BETWEEN %s AND %s AND check_in_date != %s)
                    OR (check_out_date BETWEEN %s AND %s AND check_out_date != %s)
                    OR (%s BETWEEN check_in_date AND check_out_date AND %s != check_out_date)
                    OR (%s BETWEEN check_in_date AND check_out_date AND %s != check_in_date))"""
            cursor.execute(query, (
                            room_id, 
                            exclude_booking_id, 
                            new_check_in_date, new_check_out_date, new_check_out_date, 
                            new_check_in_date, new_check_out_date, new_check_in_date,
                            new_check_in_date, new_check_in_date, 
                            new_check_out_date, new_check_out_date))
            conflicts = cursor.fetchall()
            print("conflicts", conflicts)
            if room_id == 1: # Dorm Room
                total_bunks_requested = int(number_of_bunks) if number_of_bunks is not None else 0
                for conflict in conflicts:
                    total_bunks_requested += conflict[3]
                
                if total_bunks_requested > 8:
                    return conflicts
                else:
                    return []
            else:
                return conflicts
        except Exception as e:
            print(f"Error: {e} at Room.get_date_conflicts")
            return []
        finally:
            closeCursorAndConnection(cursor, connection)

    def update_booking_dates(booking_id, new_check_in_date, new_check_out_date):
        # update booking dates
        cursor, connection = getCursor()
        try:
            cursor.execute("""
                UPDATE bookings 
                SET check_in_date = %s, check_out_date = %s 
                WHERE booking_id = %s
            """, (new_check_in_date, new_check_out_date, booking_id))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.update_booking_dates")
            return False
        finally:
           closeCursorAndConnection(cursor, connection)

    def get_all_bookings():
        # get all bookings
        cursor, connection = getCursor()
        cursor.execute("""SELECT b.*, r.type, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
                                 DATEDIFF(check_out_date, check_in_date) AS nights, c.phone, c.email
                          FROM bookings b 
                          JOIN room r ON r.room_id = b.room_id
                          JOIN customer c ON c.customer_id = b.customer_id
                          WHERE b.status != 'BLOCKED' AND c.first_name NOT LIKE '%Admin%' AND c.last_name NOT LIKE '%Admin%'
                          ORDER BY check_in_date, check_out_date,
								CASE b.status
									WHEN 'Pending' THEN 1
									WHEN 'Paid' THEN 2
									WHEN 'Confirmed' THEN 3
									WHEN 'Cancelled' THEN 4
									WHEN 'Completed' THEN 5
									ELSE 6
								 END;""")
        rows = cursor.fetchall()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        bookings = list(map(lambda row: Row(*row), rows))
        closeCursorAndConnection(cursor, connection)
        return bookings
    
    def get_all_active_bookings():
        # get all active bookings
        cursor, connection = getCursor()
        cursor.execute("""SELECT b.*, r.type, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
                                 DATEDIFF(check_out_date, check_in_date) AS nights, c.phone, c.email
                          FROM bookings b 
                          JOIN room r ON r.room_id = b.room_id
                          JOIN customer c ON c.customer_id = b.customer_id
                          WHERE b.status != 'Cancelled'
                          ORDER BY check_in_date, check_out_date,
								CASE b.status
									WHEN 'Pending' THEN 1
									WHEN 'Paid' THEN 2
									WHEN 'Confirmed' THEN 3
									WHEN 'Cancelled' THEN 4
									WHEN 'Completed' THEN 5
									ELSE 6
								 END;""")
        rows = cursor.fetchall()
        Row = namedtuple("Row", [column[0] for column in cursor.description])
        bookings = list(map(lambda row: Row(*row), rows))
        closeCursorAndConnection(cursor, connection)
        return bookings
    
    def set_booking_status(booking_id, booking_status):
        # set booking status
        cursor, connection = getCursor()
        try:
            cursor.execute("UPDATE bookings SET status = %s WHERE booking_id = %s", (booking_status, booking_id))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.set_booking_status")
            return False
        finally:
            closeCursorAndConnection(cursor, connection)

    def block_room(room_id, block_start_date, block_end_date):
        # block a room
        cursor, connection = getCursor()
        try:
            blocker_id = Room.get_admin_id_for_blocking() 
            query = """INSERT INTO bookings (customer_id, room_id, number_of_bunks, check_in_date, check_out_date, status, price) VALUES 
                (%s, %s, %s, %s, %s, %s, %s)""" # insert a special booking record to block the room
            cursor.execute(query, (blocker_id, room_id, 8, block_start_date, block_end_date, "BLOCKED", 0))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.block_room")
            return False
        finally:
            closeCursorAndConnection(cursor, connection)
    
    def get_admin_id_for_blocking():
        # get admin id for blocking
        cursor, connection = getCursor()
        cursor.execute("""SELECT a.id 
                          FROM auth a
                          JOIN customer c ON c.customer_id = a.id
                          WHERE a.username LIKE '%admin%' AND (first_name LIKE '%Admin%' OR last_name LIKE '%Admin%')""")
        row = cursor.fetchone()
        if row:
            return row[0]
        return None
    
    def unblock_room(booking_id):
        # unblock a room
        cursor, connection = getCursor()
        try:
            cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
            connection.commit()
            return True
        except Exception as e:
            connection.rollback()
            print(f"Error: {e} at Room.unblock_room")
            return False
        finally:
            closeCursorAndConnection(cursor, connection)