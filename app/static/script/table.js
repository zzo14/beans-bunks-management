document.addEventListener("DOMContentLoaded", function(){
    var activeTableBody = document.getElementById("activeTableBody");
    if (activeTableBody){
        originalRows = Array.from(activeTableBody.getElementsByTagName("tr"));
        allRows = originalRows.slice(); 
        updateTableDisplay();
    }
});

//gloable variables
var allRows = []
var originalRows = []
var currentPage = 0;
var pageSize = 10;

//function to sort the table based on the column
function sortTable(n) {
    var switching, i, t, shouldSwitch, dir, switchcount = 0;
    switching = true;
    table = document.getElementById("activeTable");
    // Set the sorting direction to ascending:
    dir = "asc";
    // Resst the sorting icon
    var allSortIcons = table.getElementsByClassName("sort-icon");
    for (t = 0; t < allSortIcons.length; t++) {
        allSortIcons[t].className = "fa-solid fa-sort sort-icon";
    }
    // Make a loop that will continue until no switching has been done:
    while (switching) {
        switching = false;
        for (i = 0; i < (allRows.length -1); i++) {
            shouldSwitch = false;
            var x = allRows[i].getElementsByTagName("td")[n]
            var y = allRows[i + 1].getElementsByTagName("td")[n]
            // Check if the cell contain number or string
            var xValue = handleInput(x.innerHTML || x.textContent);
            var yValue = handleInput(y.innerHTML || y.textContent);
            if (dir == "asc") {
                if (xValue > yValue){
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (xValue < yValue){
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            allRows.splice(i, 0, allRows.splice(i+1, 1)[0]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
    // update the sorting icon
    var sortIcon = table.rows[0].getElementsByTagName("th")[n].getElementsByClassName("sort-icon")[0];
    if (dir == "asc") {
        sortIcon.className = "fa-solid fa-sort-up sort-icon";
    } else {
        sortIcon.className = "fa-solid fa-sort-down sort-icon";
    }
    // update the allRows array after sorting
    updateTableDisplay();
}

function searchFilterTable() {
    var input = document.getElementById("filterInput");
    var filter = input.value.toUpperCase();
    allRows = originalRows.filter(row => {
        var isVisable = Array.from(row.getElementsByTagName("td")).some(td => td.innerHTML.toUpperCase().includes(filter)); // check if any cell in the row contains the filter
        return isVisable;
    })

    currentPage = 0;
    updateTableDisplay();
}

function updateTableDisplay() {
    var filteredRows = filterRows(allRows);
    var paginatedRows = paginateRows(filteredRows);
    renderTable(paginatedRows);
    updatePagination(filteredRows.length);
}

function filterRows(rows) {
    var headers = document.getElementById("activeTable").rows[0].cells;
    var typeIndex = -1;
    var staffFilter = document.getElementById("staffFilter"); // for staff status
    var customerFilter = document.getElementById("customerFilter"); // for customer status
    var bookingStatusFilter = document.getElementById("bookingStatusFilter"); // for booking status
    var productFilter = document.getElementById("productFilter");
    var productFilterValue = productFilter ? productFilter.value : "all";

    

    return rows.filter(row => {
        // check if the staff status filter exists and if so, apply it
        if (staffFilter) {
            var staffStatusFilter = staffFilter.value;
            var staffStatusCell = row.cells[7];
            var staffStatus = staffStatusCell.textContent.trim();
            if (staffStatusFilter === "active" && staffStatus !== "Active") {
                return false
            } else if (staffStatusFilter === "inactive" && staffStatus !== "Inactive") {
                return false
            }
        }

        // check if the customer status filter exists and if so, apply it
        if (customerFilter) {
            var customerFilterValue = customerFilter.value;
            var customerStatusCell = row.cells[8];
            var customerStatus = customerStatusCell.textContent.trim();

            if (customerFilterValue === "active" && customerStatus !== "Active") {
                return false
            } else if (customerFilterValue === "inactive" && customerStatus !== "Inactive") {
                return false
            }
        }

        // check if the booking_status filter exists and if so, apply it
        if (bookingStatusFilter) {
            var bookingStatusFilterValue = bookingStatusFilter.value;
            var bookingStatusCell = row.cells[4];
            var bookingStatus = bookingStatusCell.textContent.trim();
            // Define active and history statuses
            var activeStatuses = ["Pending", "Paid", "Confirmed"];
            var historyStatuses = ["Cancelled", "Completed"];
            if (bookingStatusFilterValue === "active" && !activeStatuses.includes(bookingStatus)) {
                return false
            } else if (bookingStatusFilterValue === "inactive" && !historyStatuses.includes(bookingStatus)) {
                return false
            }
        }

        // check if the product filter exists and if so, apply it
        if (productFilter) {
            var productCell = row.cells[5]; // assuming product status is in the 6th column
            var productStatus = productCell.textContent.trim().toLowerCase();
            if (productFilterValue === "available" && productStatus !== "available") {
                return false;
            } else if (productFilterValue === "not_available" && productStatus !== "not available") {
                return false;
            }
        }


        return true;
    });
}

// function to paginate the table
function paginateRows(rows) {
    var start = currentPage * pageSize;
    var end = start + pageSize;
    return rows.slice(start, end);
}

// function to render the table
function renderTable(rows) {
    var tableBody = document.getElementById("activeTableBody");
    tableBody.innerHTML = "";

    var anyRowsVisable = rows.some(row => row.style.display !== "none")

    if (rows.length === 0 || !anyRowsVisable) {
        var noDataTr = document.createElement("tr");
        var noDataTd = document.createElement("td");
        var columnCount = document.getElementById("activeTable").rows[0].cells.length;
        noDataTd.colSpan = columnCount;
        noDataTd.textContent = "No data available after filter.";
        noDataTd.classList.add("text-center");
        noDataTr.appendChild(noDataTd);
        tableBody.appendChild(noDataTr);
    } else {
        rows.forEach(row => tableBody.appendChild(row));
    }
}

// function to update the pagination
function updatePagination(totalRows) {
    var totalPages = Math.ceil(totalRows/pageSize);
    var pagination = document.getElementById("pagination");

    // remove old page number links
    var firstButton = pagination.children[0];
    var lastButton = pagination.children[pagination.children.length - 1];
    pagination.innerHTML = "";
    pagination.appendChild(firstButton);


    for (let i=0; i<totalPages; i++) {
        var li = document.createElement("li");
        li.className = "page-item" + (i === currentPage ? " active" : "");
        var button = document.createElement("button");
        button.className = "page-link";
        button.textContent = i + 1;
        button.onclick = (function(page) {
            return function() {
                currentPage = page;
                updateTableDisplay();
            };
        })(i);
        li.appendChild(button);
        pagination.appendChild(li);
    }
    // add last button
    pagination.appendChild(lastButton);
}

function goToFirstPage() {
    currentPage = 0;
    updateTableDisplay();
}

function goToLastPage() {
    currentPage = Math.ceil(allRows.length/pageSize) - 1;
    updateTableDisplay();
}

var pageSizeSelect = document.getElementById("pageSizeSelect")
if (pageSizeSelect) {
    pageSizeSelect.addEventListener("change", function(){
        pageSize = parseInt(this.value);
        currentPage = 0;
        updateTableDisplay();
    })
}

var typeFilter = document.getElementById("typeFilter");
var staffFilter = document.getElementById("staffFilter");
var customerFilter = document.getElementById("customerFilter");
var bookingStatusFilter = document.getElementById("bookingStatusFilter");
var productFilter = document.getElementById("productFilter");


[typeFilter, staffFilter, customerFilter, bookingStatusFilter, productFilter].forEach(filter => {
    if (filter) {
        filter.addEventListener("change", function() {
            currentPage = 0;
            updateTableDisplay();
        });
    }
});


//Helper function to handle input for sorting
function handleInput(inputText) {
    // remove dollar sign
    var cleanedText = inputText.replace(/[$,]/g, '');

    // try to extract number from the text
    var matches = cleanedText.match(/(\d+)/);
    if (matches) {
        var numberPart = parseFloat(matches[0]);
        if (!isNaN(numberPart) && cleanedText.match(/^\d+$/)) {
            return numberPart;
        }
    }

    // check if the input is a time range like 09:00 - 10:00
    if (inputText.includes(' - ') && inputText.match(/^\d{2}:\d{2} - \d{2}:\d{2}$/)) {
        var timePatrs = inputText.split(' - ');
        var startTimeParts = timePatrs[0].split(':');
        var startHour = parseInt(startTimeParts[0], 10);
        var startMinute = parseInt(startTimeParts[1], 10);
        return new Date(1970, 0, 1, startHour, startMinute);
    } 
    
    // check if the input is a date like 01-01-2024 09:00 - 10:00 
    var parts = inputText.split(' ');
    if (parts[0].match(/^\d{2}-\d{2}-\d{4}$/)) {
        var dateParts = parts[0].split('-')
        var year = parseInt(dateParts[2], 10);
        var month = parseInt(dateParts[1], 10) - 1;
        var day = parseInt(dateParts[0], 10);
        if (parts.length > 1 && parts[1].match(/^\d{2}:\d{2}$/)) {
            // time part exists
            var timePatrs = parts[1].split(':');
            var hour = parseInt(timePatrs[0], 10);
            var minute = parseInt(timePatrs[1], 10);
            return new Date(year, month, day, hour, minute);
        } else {
            return new Date(year, month, day);
        }
    }

    // for handling cases like 'xx minutes' 
    if (numberPart && isNaN(parseFloat(inputText))) {
        return numberPart;
    }

    // return ther input as lower case
    return inputText.toLowerCase();
}

// Toggle password visibility
function toggle_password_visibility(password_id) {
    var passwordInput = document.getElementById(password_id);
    var isVisibility = passwordInput.type === 'text';
    passwordInput.type = isVisibility ? 'password' : 'text';
    var toggle_icon = passwordInput.nextElementSibling.querySelector('i');
    toggle_icon.className = isVisibility ? 'fa-regular fa-eye' : 'fa-regular fa-eye-slash';

    // Update aria-label or title for screen readers
    var actionText = isVisibility ? 'Show Password' : 'Hide Password';
    passwordInput.nextElementSibling.setAttribute('aria-label', actionText);
    passwordInput.nextElementSibling.setAttribute('title', actionText);
};

// change password input border color based on password complexity and enable/disable submit button
function validate_password(password_id, tooltip_id) {
    var passwordInput = document.getElementById(password_id);
    var tooltip = document.getElementById(tooltip_id)
    var submitButton = passwordInput.form.querySelector('button[type=submit]')
    var pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z\d]).{8,}$/;

    if (passwordInput.value === '') {
        passwordInput.style.borderColor = '';
        tooltip.style.display = 'none';
        submitButton.disabled = false;
    }
    else if (pattern.test(passwordInput.value)) {
        passwordInput.style.borderColor = 'green';
        tooltip.style.display = 'none';
        submitButton.disabled = false;
    } else {
        passwordInput.style.borderColor = 'red';
        tooltip.style.display = 'block';
        submitButton.disabled = true;
    }
}

// set max datepicker date to today
function max_date_today() {
    var today = new Date() // get today's date
    var max_date = today.toISOString().split('T')[0]; // format date
    document.getElementById('date_of_birth').max = max_date;
}