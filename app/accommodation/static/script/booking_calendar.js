var calendar;
let debouceTimeout;

function serachFilterCalendar() {
    clearTimeout(debouceTimeout);
    debouceTimeout = setTimeout(function() {
        var input = document.getElementById("filterInput");
        var filter = input.value.toUpperCase();
        var filteredData = calendarData.filter(function(c) {
            return c.title.toUpperCase().includes(filter)
        });
        initCalendar(filteredData);
    }, 300);
}


// Initialize the timetable with classes
function initCalendar(bookings) {
    var calendarEl = document.getElementById('calendar');
    if (!calendar) {
        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            fixedWeekCount: false,
            displayEventTime: false,
            headerToolbar: {
                left: 'prev next today',
                center: 'title',
                right: 'dayGridMonth timeGridWeek timeGridDay'
            }, 
            eventTimeFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true,
            },
            events: bookings,
            eventClassNames: function(info) {
                var classes = ['fc-event'];
                if (info.event.extendedProps.status === 'Confirmed' && new Date(info.event.start) < new Date()) {
                    classes.push('past-confirmed');
                } else if (info.event.extendedProps.status === 'Pending') {
                    classes.push('pending');
                } else if (info.event.extendedProps.status === 'BLOCKED') {
                    classes.push('blocked');
                }
                return classes;
            },
            eventClick: function(info) {
                var event = info.event;
                var title = event.title;
                var start = event.start;
                var end = event.end;
                var customer_id = event.extendedProps.customer_id;
                var customer = event.extendedProps.customer;
                var customer_email = event.extendedProps.customer_email;
                var customer_phone = event.extendedProps.customer_phone;
                var room_id = event.extendedProps.room_id;
                var room = event.extendedProps.room;
                var nights = event.extendedProps.nights;
                var number_of_bunks = event.extendedProps.number_of_bunks;
                var status = event.extendedProps.status;
                var price = event.extendedProps.price;
                var modal_footer = document.getElementById('modal-footer');
                var unblock_modal_footer = document.getElementById('unblock-modal-footer');
                var unblock_text = document.getElementById('unblock-text');
                modal_footer.innerHTML = '';
                var cancel_url = `/accommodation/cancel_booking/${event.id}`;
                var set_status_url = `/accommodation/set_booking_status/${event.id}`;
                var unblock_url = `/accommodation/unblock_room/${event.id}`;
                var send_reminder_url = `/accommodation/send_reminder`;
                

                if (status == 'BLOCKED') {
                    unblock_text.innerHTML = `Are you sure you want to unblock ${room} room on ${combineDateTime(start, end)}?`;
                    unblock_modal_footer.innerHTML = `
                    <form method="POST" action="${unblock_url}">
                        <button type="submit" class="btn btn-danger">Unblock</button>
                    </form>`;
                    unblock_modal_footer.innerHTML += '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>'
                }else if (status == 'Pending' && new Date(start) > new Date()) {
                    modal_footer.innerHTML += `
                    <form method="POST" action="${send_reminder_url}">
                        <!-- Hidden input to pass the booking-->
                        <input type="hidden" name="booking_id" value="${event.id}">
                        <input type="hidden" name="customer_id" value="${customer_id}">
                        <!-- Editable fields -->
                        <button type="submit" class="btn btn-warning">Send Reminder</button>
                    </form>
                    `;
                    modal_footer.innerHTML += `
                    <form method="POST" action="${cancel_url}">
                        <!-- Hidden input to pass the booking-->
                        <input type="hidden" name="booking_status" value="${status}">
                        <!-- Editable fields -->
                        <button type="submit" class="btn btn-color-1">Cancel Booking</button>
                    </form>`
                    modal_footer.innerHTML += '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>'
                } else if (status == 'Confirmed' && new Date(start) < new Date()) {
                    modal_footer.innerHTML += `
                    <form method="POST" action="${set_status_url}">
                        <input type="hidden" name="booking_status" value="Completed">
                        <button type="submit" class="btn btn-color-1">Set Completed</button>
                    </form>
                    <form method="POST" action="${set_status_url}">
                        <input type="hidden" name="booking_status" value="Cancelled">
                        <button type="submit" class="btn btn-warning">Set No Show</button>
                    </form>`;
                } else if (new Date(event.start) > new Date()) {
                    modal_footer.innerHTML += `
                    <form method="POST" action="${cancel_url}">
                        <!-- Hidden input to pass the booking-->
                        <input type="hidden" name="booking_status" value="${status}">
                        <!-- Editable fields -->
                        <button type="submit" class="btn btn-color-1">Cancel Booking</button>
                    </form>`;
                    modal_footer.innerHTML += '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>'
                }

                // fill the modal with the event details
                document.getElementById('booking-title').innerHTML = title;
                document.getElementById('booking_id').innerHTML = `<strong>Booking ID:</strong> ${event.id}`;
                document.getElementById('room').innerHTML = `<strong>Room:</strong> ${room}`;
                document.getElementById('date').innerHTML = `<strong>Date:</strong> ${combineDateTime(start, end)} (${nightsFormat(nights)})`;
                document.getElementById('price').innerHTML = `<strong>Price:</strong> $${price}`;
                document.getElementById('status').innerHTML = `<strong>Status:</strong> ${status}`;
                document.getElementById('customer').innerHTML = `<strong>Guest:</strong> ${customer}`;
                document.getElementById('customer_email').innerHTML = `<strong>Email:</strong> ${customer_email}`;
                document.getElementById('customer_phone').innerHTML = `<strong>Phone:</strong> ${customer_phone}`;
                if (number_of_bunks) {
                    document.getElementById('number_of_bunks').innerHTML = `<strong>Bunks:</strong> ${number_of_bunks}`;
                }
                // show the modal
                if (status == 'BLOCKED') {
                    var unblock_modal = new bootstrap.Modal(document.getElementById('unblockRoomModal'));
                    unblock_modal.show();
                } else {
                    var modal = new bootstrap.Modal(document.getElementById('bookingDetailModal'));
                    modal.show();
                }
            }
        });
    }
    calendar.removeAllEvents();
    bookings.forEach(event => calendar.addEvent(event))
    calendar.render();
}


// Helper function to convert time to normal time format
function formatDateTime(time) {
    const formatter = new Intl.DateTimeFormat('en-NZ', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: '2-digit',
    });
    return formatter.format(time);
}

// Helper function to combine date and time
function combineDateTime(start, end){
    var formatStart = formatDateTime(start)
    var formatEnd = formatDateTime(end)
    return `${formatStart} - ${formatEnd}`

}

function nightsFormat(night) {
    if (night > 1) {
        return `${night} nights`
    } else {
        return `${night} night`
    }
}

// set max datepicker date to today
function min_date_today() {
    var now = new Date() // get today's date
    var formatter = new Intl.DateTimeFormat('en-NZ', {
        timeZone: 'Pacific/Auckland',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }); // format date
    var formattedDate = formatter.format(now).split('/').reverse().join('-'); // format date to yyyy-mm-dd
    document.getElementById('block_end_date').min = formattedDate;
    document.getElementById('block_start_date').min = formattedDate;
}

function updateEndDate() {
    var start_date = document.getElementById('block_start_date').value;
    if (!start_date) {
        var now = new Date() // get today's date
        var formatter = new Intl.DateTimeFormat('en-NZ', {
            timeZone: 'Pacific/Auckland',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }); // format date
        var start_date = formatter.format(now).split('/').reverse().join('-'); // format date to yyyy-mm-dd
    }
    document.getElementById('block_end_date').min = start_date;
}

document.getElementById('block_start_date').addEventListener('change', updateEndDate);