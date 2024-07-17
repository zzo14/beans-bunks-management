document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-bs-toggle='modal']").forEach(function (button) {
        var targetModal = button.getAttribute("data-bs-target");
        button.onclick = function () {
            var modalIndex = targetModal.replace("#editBookingModal", "");

            // Attempt to access elements by ID
            var checkInInput = document.getElementById(`new_check_in_date_${modalIndex}`);
            var bookingDateDisplay = document.getElementById(`new_booking_date_${modalIndex}`);
            var originalNightsInput = document.getElementById(`original_nights_${modalIndex}`);
            
            // Verify that elements exist
            if (!checkInInput || !bookingDateDisplay || !originalNightsInput) {
                console.error("Missing modal elements for index:", modalIndex);
                return;
            }

            var originalNights = parseInt(originalNightsInput.value);

            // Set onchange event listener
            checkInInput.onchange = function () {
                var checkInDate = new Date(checkInInput.value);

                // Validate the input
                if (isNaN(checkInDate.getTime())) {
                    bookingDateDisplay.innerHTML = "<strong>Error:</strong> Invalid check-in date.";
                    return;
                }

                // Calculate the new check-out date
                var checkOutDate = new Date(checkInDate);
                checkOutDate.setDate(checkOutDate.getDate() + originalNights);

                // Format the dates
                var formattedCheckIn = formatNZDate(checkInDate);
                var formattedCheckOut = formatNZDate(checkOutDate);
                document.getElementById(`new_check_out_date_${modalIndex}`).value = formatDate(checkOutDate);

                // Update the display paragraph
                bookingDateDisplay.innerHTML = `<strong>New Booking Dates: Check-In: ${formattedCheckIn}, Check-Out: ${formattedCheckOut}</strong>`;
            };
        };
    });
});
function formatNZDate(date) {
    let day = String(date.getDate()).padStart(2, '0');
    let month = String(date.getMonth() + 1).padStart(2, '0');
    let year = date.getFullYear();
    return `${day}-${month}-${year}`;
}
function formatDate(date) {
    let day = String(date.getDate()).padStart(2, '0');
    let month = String(date.getMonth() + 1).padStart(2, '0');
    let year = date.getFullYear();
    return `${year}-${month}-${day}`;
}
// set max datepicker date to today
function min_date_today(element_id) {
    var now = new Date() // get today's date
    var formatter = new Intl.DateTimeFormat('en-NZ', {
        timeZone: 'Pacific/Auckland',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }); // format date
    var formattedDate = formatter.format(now).split('/').reverse().join('-'); // format date to yyyy-mm-dd
    document.getElementById(element_id).min = formattedDate;
}