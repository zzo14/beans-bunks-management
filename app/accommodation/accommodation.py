# This is for the authentication blueprint
# Assigner: Patrick
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import session
from flask import Blueprint
from flask import jsonify
from app.utils import send_message_to_customer, verify_access, validate_form, validate_varchar, validate_text, validate_date, validate_time, validate_decimal
from app.accommodation.models.room import Room
from datetime import datetime
import random
from decimal import Decimal, ROUND_HALF_UP

accommodation_bp = Blueprint("accommodation", __name__, template_folder="templates", static_folder="static", static_url_path="/accommodation/static")

@accommodation_bp.before_request
def before_request():
    endpoint_access = {
        "accommodation.booking_table": (["customer"], "auth.login"),
        "accommodation.book_room": (["customer"], "home.home"),
        "accommodation.booking_payment": (["customer"], "home.home"),
        "accommodation.booking_confirmation": (["customer"], "home.home"),
        "accommodation.cust_booking_management": (["customer"], "home.home"),
        "accommodation.cancel_booking": (["customer", "staff", "manager"], "home.home"),
        "accommodation.edit_booking": (["customer"], "home.home"),
        "accommodation.booking_management": (["staff"], "home.home"),
        "accommodation.set_booking_status": (["staff", "manager"], "home.home"),
        "accommodation.booking_management_calendar": (["manager"], "home.home"),
        "accommodation.block_room": (["manager"], "home.home"),
        "accommodation.unblock_room": (["manager"], "home.home"),
        "accommodation.send_reminder": (["staff", "manager"], "home.home"),
    }
    if request.endpoint in endpoint_access:
        roles, redirect_url = endpoint_access[request.endpoint]
        return verify_access(roles, redirect_url)

@accommodation_bp.route("/booking_table", methods=["GET"])
def booking_table():
    # for customer to booking accommodation
    rooms = Room.get_all_rooms()
    return render_template("booking_table.html", rooms=rooms)

@accommodation_bp.route("/api/room_availability", methods=["GET"])
def room_availability():
    # API endpoint to get room availability
    start_date_str = request.args.get("start_date", datetime.today().strftime("%Y-%m-%d"))
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() # convert to date object
    availability = Room.get_week_availability(start_date)
    return jsonify(availability)

@accommodation_bp.route("/book_room", methods=["POST"])
def book_room():
    # for customer to book a room
    required_fields = ["room_id", "start_date", "end_date", "total_price"] 
    field_validations = {
        "room_id": validate_decimal,
        "start_date": validate_date,
        "end_date": validate_date,
        "total_price": validate_decimal
    }
    if not validate_form(request.form, required_fields, field_validations):
        return redirect(url_for("accommodation.booking_table"))
    customer_id = session.get("id")
    room_id = request.form.get("room_id")
    check_in_date = request.form.get("start_date")
    check_out_date = request.form.get("end_date")
    number_of_bunks = request.form.get("number_of_guests") if request.form.get("number_of_guests") != "" else None
    price = request.form.get("total_price")

    booking_id = Room.book_room(customer_id, room_id, check_in_date, check_out_date, number_of_bunks, price)
    if booking_id:
        return redirect(url_for("accommodation.booking_payment", booking_id=booking_id))
    else:
        flash("Room booking failed", "danger")
        return redirect(url_for("accommodation.booking_table"))

@accommodation_bp.route("/booking_payment/<booking_id>", methods=["GET", "POST"])
def booking_payment(booking_id):
    # for customer to make payment for booking
    customer_id = session.get("id")
    booking_details = Room.get_bookings_by_booking_id(booking_id)
    if request.method == "POST":
        payment_method = random.choice(['debit card', 'credit card'])
        gift_card_usage = request.form.get("use_gift_card")
        gift_card_id = request.form.get("gift_card_id")
        gift_card_amount = float(request.form.get("gift_card_amount", 0))
        payment_amount = request.form.get("total_payment_amount")
        promo_id = request.form.get("used_promo_id")
        if promo_id == "none" or promo_id == "None" or not promo_id:
            promo_id = None
        result = Room.make_booking_payment(booking_id, payment_method, gift_card_usage, gift_card_amount, payment_amount, gift_card_id, customer_id, promo_id)
        if result:
            flash("Payment successful", "success")
            return redirect(url_for("accommodation.booking_confirmation", booking_id=booking_id))
        else:
            flash("Payment failed, Please try again.", "danger")
    return render_template("booking_payment.html", booking_details=booking_details)

@accommodation_bp.route("/api/validate_promo", methods=["POST"])
def validate_promo_code():
    # API endpoint to validate promo code
    data = request.get_json()
    promo_code = data.get("promo_code", "").strip()
    promo_details = Room.get_promo_code_details(promo_code)

    if promo_details and promo_details.discount_rate > 0:
        response = {
            "success": True,
            "promo_id": promo_details.promo_id,
            "discount_rate": promo_details.discount_rate,
            "message": "Promo code applied successfully."
        }
    else:
        response = {
            "success": False,
            "message": "Invalid or expired promo code."
        }
    return jsonify(response)

@accommodation_bp.route("/api/validate_gift_card", methods=["POST"])
def validate_gift_card():
    # API endpoint to validate gift card
    data = request.get_json()
    gift_card_code = data.get("gift_card_code", "").strip()
    gift_card_password = data.get("gift_card_password", "").strip()
    gift_card_details = Room.validate_gift_card(gift_card_code, gift_card_password)

    if gift_card_details and gift_card_details.current_balance > 0:
        response = {
            "success": True,
            "gift_card_id": gift_card_details.gift_card_id,
            "balance": gift_card_details.current_balance,
            "message": "Gift card is valid."
        }
    else:
        response = {
            "success": False,
            "message": "Invalid or expired gift card."
        }
    return jsonify(response)


@accommodation_bp.route("/booking_confirmation/<booking_id>", methods=["GET"])
def booking_confirmation(booking_id):
    # for customer to view booking confirmation
    booking_details = Room.get_bookings_by_booking_id(booking_id)
    Room.confirm_booking_auto(booking_id)
    booking_amount_excluding_GST = (booking_details.price * Decimal(0.85)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)     
    return render_template("booking_confirmation.html", booking_details=booking_details, booking_amount_excluding_GST=booking_amount_excluding_GST)

@accommodation_bp.route("/manage_my_booking", methods=["GET"])
def cust_booking_management():
    # for customer to manage their bookings
    customer_id = session.get("id")
    booking_history = Room.get_bookings_by_customer_id(customer_id)
    return render_template("cust_booking_management.html", booking_history=booking_history)

@accommodation_bp.route("/cancel_booking/<booking_id>", methods=["POST"])
def cancel_booking(booking_id):
    # for cancel booking
    customer_id = request.form.get("customer_id") 
    booking_status = request.form.get("booking_status")
    if not customer_id:
        customer_id = session.get("id")
    role = session.get("role")
    if role == "staff":
        url = "accommodation.booking_management"
    elif role == "customer":
        url = "accommodation.cust_booking_management"
    else:
        url = "accommodation.booking_management_calendar"
    if request.method == "POST":
        result = Room.cancel_booking(booking_id, customer_id, booking_status)
        if result:
            flash(f"Booking cancelled successfully! The deposit has been returned.", "success")
            message = f"Booking ID {booking_id} has been cancelled. The deposit has been returned. We hope to see you again soon!"
            send_message_to_customer(customer_id, message)
        else:
            flash("Failed to cancel booking.", "danger")
    return redirect(url_for(url))

@accommodation_bp.route("/edit_booking/<booking_id>", methods=["POST"])
def edit_booking(booking_id):
    # for edit booking
    booking_details = Room.get_bookings_by_booking_id(booking_id)
    room_id = booking_details.room_id
    original_check_in_date = booking_details.check_in_date
    original_check_out_date = booking_details.check_out_date

    required_fields = ["new_check_in_date", "new_check_out_date"]
    field_validations = {
        "new_check_in_date": validate_date,
        "new_check_out_date": validate_date
    }
    if not validate_form(request.form, required_fields, field_validations):
        return redirect(url_for("accommodation.cust_booking_management"))

    if request.method == "POST":
        check_in_date = request.form.get("new_check_in_date")
        check_out_date = request.form.get("new_check_out_date")
        number_of_bunks = request.form.get("number_of_bunks")

        # Check if the new dates are the same as the original dates
        if check_in_date == str(original_check_in_date) and check_out_date == str(original_check_out_date):
            flash("No changes made, dates remain the same.", "warning")
            return redirect(url_for("accommodation.cust_booking_management"))

        # Check if the new dates overlap with existing bookings for this room
        conflicts = Room.get_date_conflicts(room_id, check_in_date, check_out_date, booking_id, number_of_bunks)

        if conflicts:
            conflict_info = "<br>".join(
                [f"Date: {conflict[1].strftime('%d-%m-%Y')} to {conflict[2].strftime('%d-%m-%Y')}" for conflict in conflicts]
            )
            flash(f"New dates conflict with the following bookings:<br> {conflict_info}", "danger")
            return redirect(url_for("accommodation.cust_booking_management"))

        # Proceed with the booking update
        result = Room.update_booking_dates(booking_id, check_in_date, check_out_date)

        if result:
            flash("Booking updated successfully.", "success")
        else:
            flash("Failed to update booking. Please try again.", "danger")
        return redirect(url_for("accommodation.cust_booking_management"))
    return redirect(url_for("accommodation.cust_booking_management"))

@accommodation_bp.route("/booking_management", methods=["GET"])
def booking_management():
    # for staff to manage bookings
    bookings = Room.get_all_bookings()
    today_date = datetime.now().date()
    return render_template("booking_management.html", bookings=bookings, today_date=today_date)

@accommodation_bp.route("/set_booking_status/<booking_id>", methods=["POST"])
def set_booking_status(booking_id):
    # for staff and manager to set booking status
    booking_status = request.form.get("booking_status")
    url = "accommodation.booking_management" if session.get("role") == "staff" else "accommodation.booking_management_calendar"
    result = Room.set_booking_status(booking_id, booking_status)
    if result:
        flash("Booking status updated successfully", "success")
    else:
        flash("Failed to update booking status", "danger")
    return redirect(url_for(url))

@accommodation_bp.route("/booking_management_calendar", methods=["GET", "POST"])
def booking_management_calendar():
    # for manager to manage bookings in calendar view
    rooms = Room.get_all_rooms()
    bookings = Room.get_all_active_bookings()
    return render_template("booking_management_calendar.html", bookings=bookings, rooms = rooms)

@accommodation_bp.route("/block_room", methods=["POST"])
def block_room():
    # for manager to block room
    # validate form data
    required_fields = ["room_id", "block_start_date", "block_end_date"]
    field_validations = {
        "room_id": validate_decimal,
        "block_start_date": validate_date,
        "block_end_date": validate_date
    }
    if not validate_form(request.form, required_fields, field_validations):
        return redirect(url_for("accommodation.booking_management_calendar"))

    room_id = request.form.get("room_id")
    block_start_date = request.form.get("block_start_date")
    block_end_date = request.form.get("block_end_date")

    # Check if the new dates overlap with existing bookings for this room
    conflicts = Room.get_date_conflicts(room_id, block_start_date, block_end_date)
    if conflicts:
        conflict_info = "<br>".join(
            [f"Date: {conflict[1].strftime('%d-%m-%Y')} to {conflict[2].strftime('%d-%m-%Y')}" for conflict in conflicts]
        ) 
        flash(f"There are bookings on {conflict_info}.<br>Please try again!", "danger")
        return redirect(url_for("accommodation.booking_management_calendar"))

    result = Room.block_room(room_id, block_start_date, block_end_date)
    if result:
        flash("Room blocked successfully", "success")
    else:
        flash("Failed to block room", "danger")
    return redirect(url_for("accommodation.booking_management_calendar"))

@accommodation_bp.route("/unblock_room/<booking_id>", methods=["POST"])
def unblock_room(booking_id):
    # for manager to unblock room
    result = Room.unblock_room(booking_id)
    if result:
        flash("Room unblocked successfully", "success")
    else:
        flash("Failed to unblock room", "danger")
    return redirect(url_for("accommodation.booking_management_calendar"))

@accommodation_bp.route("/send_reminder", methods=["POST"])
def send_reminder():
    # for staff and manager to send reminder to customer for payment
    booking_id = request.form.get("booking_id")
    customer_id = request.form.get("customer_id")
    message = f"This is a reminder for your upcoming booking, <strong>booking ID {booking_id}</strong>. <br>Please ensure that you have made the necessary payment. Thank you!"
    result = send_message_to_customer(customer_id, message)
    if result:
        flash("Reminder sent successfully", "success")
    else:
        flash("Failed to send reminder", "danger")
    url = "accommodation.booking_management" if session.get("role") == "staff" else "accommodation.booking_management_calendar"
    return redirect(url_for(url))