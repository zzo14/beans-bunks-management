// for storing the booking details
let currentSelection = {
    roomId: null,
    roomType: "",
    startDate: null,
    endDate: null,
    pricePerNight: 0,
    totalPrice: 0,
    nights: 0,
    numberOfGuests: 1,
}
// for tracking currently selected cells
let selectedCells = []; 
let startDateSelected = false;
let clickCounter = 0;

// initialize the date picker
flatpickr('#startDate', {
    dateFormat: 'Y-m-d',
    minDate: 'today',
    position: "below",
    static: true,
});

function generateDateHeaders(startDate) {
    const dateHeaders = document.getElementById('dateHeaders');
    const daysToAdd = 7;

    while (dateHeaders.children.length > 1) {
        dateHeaders.removeChild(dateHeaders.lastChild);
    }
    for (let i = 0; i < daysToAdd; i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(currentDate.getDate() + i);

        const weekLabel = currentDate.toLocaleDateString('en-NZ', { weekday: 'short'});
        const dayLabel = currentDate.toLocaleDateString('en-NZ', { day: '2-digit'});

        const th = document.createElement('th');
        th.innerHTML = `${weekLabel}<br>${dayLabel}`;
        dateHeaders.appendChild(th);
    }
}

function updateDatePickerDisplay(date) {
    const display = document.getElementById('datePickerDisplay');
    const options = { year: 'numeric', month: 'long' };
    display.innerHTML = `${date.toLocaleDateString('en-NZ', options)} <i class="fa-regular fa-calendar-days"></i>`;
}

function parseStartDate() {
    const dateInput = document.getElementById('startDate').value;
    const currentDate = new Date();
    if (dateInput) {
        return new Date(dateInput);
    }
    return new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
}

function updateBookingSummary() {
    // gets a hidden field element in HTML
    const roomIdInput = document.getElementById('room_id');
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const numberOfGuestsInput = document.getElementById('number_of_guests');
    const totalPriceInput = document.getElementById('total_price');
    // update the hidden field values
    roomIdInput.value = currentSelection.roomId;
    startDateInput.value = currentSelection.startDate;
    endDateInput.value = currentSelection.endDate;
    totalPriceInput.value = currentSelection.totalPrice;
    if (currentSelection.roomType === 'Dorm') {
        numberOfGuestsInput.value = currentSelection.numberOfGuests;
    } else {
        numberOfGuestsInput.value = null;
    }

    // update the booking summary
    const summaryList = document.getElementById("summaryList");
    const clearButton = document.getElementById("clearButton");
    const bookButton = document.getElementById("bookButton");
    const guestDropdownContainer = document.getElementById("guestDropdownContainer");

    if (currentSelection.roomId === null) {
        summaryList.innerHTML = `<li class="list-group-item text-center" id="selectMessage"><strong>Please select a date!</strong></li>`;
        clearButton.classList.add('d-none');
        bookButton.disabled = true;
        guestDropdownContainer.style.display = 'none';
    } else {
        summaryList.innerHTML = `
            <li class="list-group-item"><strong>Room:</strong> ${currentSelection.roomType}</li>
            <li class="list-group-item"><strong>Date:</strong> ${formatDate(currentSelection.startDate)} - ${formatDate(currentSelection.endDate)} (${currentSelection.nights} nights)</li>
            <li class="list-group-item"><strong>Total Amount:</strong> $${currentSelection.totalPrice.toFixed(2)}</li>
        `;
        clearButton.classList.remove('d-none');
        bookButton.disabled = currentSelection.roomId === null;
    }
}

function handleRoomSelection(roomType, roomId, dayIndex, availabilityCount, pricePerNight) {
    const cell = document.querySelector(`#room-${roomId} td[data-day="${dayIndex}"]`);

    // Reset selection if the third click happens on the first selected cell
    if (clickCounter >= 2) {
        clearSelection();
        clickCounter = 0;
        return;
    }

    if (clickCounter === 0 || currentSelection.roomId !== roomId) {
        clearSelection();
        currentSelection.roomId = roomId;
        currentSelection.roomType = roomType;
        currentSelection.pricePerNight = pricePerNight;
        selectedCells = [cell];
        startDateSelected = true;
        cell.classList.add('selected');
        updateDatesAndSelection(roomType, roomId, pricePerNight);
    } else {
        const newSelectedCells = expandSelectedRange(selectedCells[0], cell);
        // Ensure that no "SOLD OUT" cells are selected
        if (newSelectedCells.every(c => !c.classList.contains('sold-out'))) {
            selectedCells = newSelectedCells;
            startDateSelected = false;
            selectedCells.forEach(c => c.classList.add('selected'));
            updateDatesAndSelection(roomType, roomId, pricePerNight);
        } else {
                alert("Selected range includes unavailable days.");
                clearSelection();
                clickCounter = 0;
                return;
        }
    }
    clickCounter += 1;
    // Update `guestDropdown` if the room is a dormitory
    if (roomType === 'Dorm') {
        updateGuestDropdownAcrossSelectedDays(roomType, selectedCells, pricePerNight)
    }
}

function expandSelectedRange(startCell, endCell) {
    const startIndex = parseInt(startCell.dataset.day);
    const endIndex = parseInt(endCell.dataset.day);
    const range = [];
    for (let i = Math.min(startIndex, endIndex); i <= Math.max(startIndex, endIndex); i++) {
        range.push(document.querySelector(`#room-${currentSelection.roomId} td[data-day="${i}"]`));
    }
    return range;
}

function updateDatesAndSelection(roomType, roomId, pricePerNight) {
    const startDayIndex = parseInt(selectedCells[0].dataset.day);
    const endDayIndex = parseInt(selectedCells[selectedCells.length - 1].dataset.day);

    const startDate = new Date(parseStartDate());
    startDate.setDate(startDate.getDate() + startDayIndex);
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + selectedCells.length);

    currentSelection.roomType = roomType;
    currentSelection.roomId = roomId;
    currentSelection.pricePerNight = pricePerNight;
    currentSelection.startDate = startDate.toISOString().split('T')[0];
    currentSelection.endDate = endDate.toISOString().split('T')[0];
    currentSelection.nights = selectedCells.length;
    currentSelection.totalPrice = currentSelection.pricePerNight * currentSelection.nights;

    updateBookingSummary();
}

function updateGuestDropdownAcrossSelectedDays(roomType, selectedCells, pricePerNight) {
    // Find the minimum availability across all selected cells
    const minAvailability = selectedCells.reduce((min, cell) => {
        const availabilityCount = parseInt(cell.textContent) || 0;
        return Math.min(min, availabilityCount);
    }, Infinity);

    // Get the guest dropdown elements
    const guestDropdown = document.getElementById('guestDropdown');
    const guestDropdownContainer = document.getElementById('guestDropdownContainer');
    guestDropdown.innerHTML = '';

    // Populate the guest dropdown with the minimum availability
    for (let i = 1; i <= minAvailability; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = `${i} Guest${i > 1 ? 's' : ''}`;
        guestDropdown.appendChild(option);
    }

    guestDropdownContainer.style.display = 'block';
    guestDropdown.onchange = function () {
        currentSelection.numberOfGuests = parseInt(this.value);
        currentSelection.totalPrice = pricePerNight * currentSelection.nights * currentSelection.numberOfGuests;
        updateBookingSummary();
    };
    guestDropdown.value = currentSelection.numberOfGuests;
}


function clearSelection() {
    document.querySelectorAll('.selected').forEach(cell => cell.classList.remove('selected'));
    // reset current selection and selected cells
    selectedCells = [];
    currentSelection = {
        roomId: null,
        roomType: "",
        startDate: null,
        endDate: null,
        pricePerNight: 0,
        totalPrice: 0,
        nights: 0,
        numberOfGuests: 1,
    };
    startDateSelected = false;
    clickCounter = 0;
    // reset and booking button and clear button
    const clearButton = document.getElementById('clearButton');
    const bookButton = document.getElementById('bookButton');
    clearButton.classList.add('d-none');
    bookButton.disabled = true;
    // reset guest dropdown 
    const guestDropdownContainer = document.getElementById('guestDropdownContainer');
    const guestDropdown = document.getElementById('guestDropdown');
    guestDropdownContainer.style.display = 'none';
    guestDropdown.innerHTML = '';
    // update booking summary
    updateBookingSummary();
}

async function updateRoomAvailability() {
    clearSelection();
    const startDate = parseStartDate();
    generateDateHeaders(startDate);
    updateDatePickerDisplay(startDate);

    const formatedStartDate = startDate.toISOString().split('T')[0];
    const url = `/accommodation/api/room_availability?start_date=${formatedStartDate}`;
    const response = await fetch(url);
    const availability = await response.json();

    const today = new Date();
    today.setHours(0, 0, 0, 0); // Normalize today's date

    const roomIds = Object.keys(availability);
    roomIds.forEach(roomId => {
        const row = document.getElementById(`room-${roomId}`);
        const roomData = availability[roomId];
        const roomType = roomData.type;
        const pricePerNight = parseFloat(roomData.price);
        const roomCells = row.querySelectorAll('td:not(:first-child)');

        roomCells.forEach((cell, dayIndex) => {
            const availabilityCount = roomData.availability[dayIndex];
            const dayOffset = dayIndex; // Adjusted to account for starting day index from 0
            const cellDate = new Date(startDate);
            cellDate.setDate(cellDate.getDate() + dayOffset);

            if (availabilityCount > 0) {
                cell.classList.remove('sold-out');
                cell.setAttribute('data-day', dayIndex);
                if (roomType === 'Dorm') {
                    cell.innerHTML = `${availabilityCount} LEFT`;
                } else {
                    cell.innerHTML = `Available`;
                }
                if (cellDate >= today) {
                    cell.onclick = () => handleRoomSelection(roomType, roomId, dayIndex, availabilityCount, pricePerNight);
                } else {
                    cell.onclick = null;
                }
            } else {
                cell.textContent = 'SOLD OUT';
                cell.classList.add('sold-out');
                cell.onclick = null;
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    var now = new Date() // get today's date
    var formatter = new Intl.DateTimeFormat('en-NZ', {
        timeZone: 'Pacific/Auckland',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }); // format date
    var formattedDate = formatter.format(now).split('/').reverse().join('-'); // format date to yyyy-mm-dd
    document.getElementById('startDate').value = formattedDate;
    updateRoomAvailability();
});

document.getElementById('datePickerDisplay').addEventListener('click', () => {
    document.getElementById('startDate')._flatpickr.open();
});

document.getElementById('prev7').addEventListener('click', () => {
    const currentStartDate = parseStartDate();
    const newStartDate = new Date(currentStartDate);
    newStartDate.setDate(currentStartDate.getDate() - 7);
    document.getElementById('startDate').value = newStartDate.toISOString().split('T')[0];
    updateRoomAvailability();
});

document.getElementById('next7').addEventListener('click', () => {
    const currentStartDate = parseStartDate();
    const newStartDate = new Date(currentStartDate);
    newStartDate.setDate(currentStartDate.getDate() + 7);
    document.getElementById('startDate').value = newStartDate.toISOString().split('T')[0];
    updateRoomAvailability();
});

document.getElementById('startDate').addEventListener('change', updateRoomAvailability);

function formatDate(date) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(date).toLocaleDateString('en-NZ', options);
}