//gloable variables
var tables = {};

// function to initialize the table
function initializeTable(tableId) {
    var tableBody = document.getElementById(tableId + "Body");
    if (tableBody) {
        if (!tables[tableId]) {
            // only initialize the table once
            tables[tableId] = {
                originalRows: Array.from(tableBody.getElementsByTagName("tr")),
                allRows: Array.from(tableBody.getElementsByTagName("tr")),
                currentPage: 0,
                pageSize: 10
            };
        }
        updateTableDisplay(tableId);
    } else {
        console.error("Table body not found for:", tableId);
    }
}

//function to sort the table based on the column
function sortTable(tableId, n) {
    initializeTable(tableId);
    var data = tables[tableId];
    var switching = true;
    var dir = "asc";
    var switchcount = 0;
    var table = document.getElementById(tableId);
    var shouldSwitch;
    var length = data.allRows.length;

    // Resst the sorting icon
    var allSortIcons = table.getElementsByClassName("sort-icon");
    for (t = 0; t < allSortIcons.length; t++) {
        allSortIcons[t].className = "fa-solid fa-sort sort-icon";
    }
    // Make a loop that will continue until no switching has been done:
    while (switching) {
        switching = false;
        for (var i = 0; i < (length -1); i++) {
            shouldSwitch = false;
            var x = data.allRows[i].getElementsByTagName("td")[n];
            var y = data.allRows[i + 1].getElementsByTagName("td")[n];
            // Check if the cell contain number or string
            var xValue = handleInput(x.innerHTML || x.textContent);
            var yValue = handleInput(y.innerHTML || y.textContent);
            // Skip "No Review" cells
            if (xValue.type === 'text' && xValue.value === 'no review') continue;
            if (yValue.type === 'text' && yValue.value === 'no review') continue;
            
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
            data.allRows.splice(i, 0, data.allRows.splice(i+1, 1)[0]);
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
    sortIcon.className = dir === "asc" ? "fa-solid fa-sort-up sort-icon" : "fa-solid fa-sort-down sort-icon";
    // update the allRows array after sorting
    updateTableDisplay(tableId);
}

// function to search and filter the table
function searchFilterTable(tableId, inputId) {
    var input = document.getElementById(inputId);
    var filter = input.value.toUpperCase();
    var data = tables[tableId];

    data.allRows = data.originalRows.filter(row => {
        return Array.from(row.getElementsByTagName("td")).some(td => td.textContent.toUpperCase().includes(filter));
    });

    data.currentPage = 0;
    updateTableDisplay(tableId);
}

function updateTableDisplay(tableId) {
    var data = tables[tableId];
    var filteredRows = filterRows(data.allRows);
    var paginatedRows = paginateRows(data.allRows, data.currentPage, data.pageSize);
    renderTable(paginatedRows, tableId + "Body");
    updatePagination(filteredRows.length, data.currentPage, data.pageSize, tableId);
}

function filterRows(rows) {
    return rows;
}

// function to paginate the table
function paginateRows(rows, currentPage, pageSize) {
    var start = currentPage * pageSize;
    var end = start + pageSize;
    return rows.slice(start, end);
}

// function to render the table
function renderTable(rows, tableBodyId) {
    var tableBody = document.getElementById(tableBodyId);
    tableBody.innerHTML = "";

    if (rows.length === 0) {
        var noDataTr = document.createElement("tr");
        var noDataTd = document.createElement("td");
        // get the column count of the table
        var columnCount = document.getElementById(tableBodyId).parentNode.rows[0].cells.length;
        noDataTd.colSpan = columnCount;
        noDataTd.textContent = "No data available after filter.";
        noDataTd.classList.add("text-center");
        noDataTr.appendChild(noDataTd);
        tableBody.appendChild(noDataTr);
    } else {
        rows.forEach(row => {
            tableBody.appendChild(row);
        });
    }
}

// function to update the pagination
function updatePagination(totalRows, currentPage, pageSize, tableId) {
    var totalPages = Math.ceil(totalRows / pageSize);
    var pagination = document.getElementById(tableId + "Pagination");

    // remove old page number links
    var firstButton = pagination.children[0];
    var lastButton = pagination.children[pagination.children.length - 1];
    pagination.innerHTML = "";
    pagination.appendChild(firstButton);

    for (let i = 0; i < totalPages; i++) {
        var li = document.createElement("li");
        li.className = "page-item" + (i === currentPage ? " active" : "");
        var button = document.createElement("button");
        button.className = "page-link";
        button.textContent = i + 1;
        button.addEventListener("click", function() {
            tables[tableId].currentPage = i;
            updateTableDisplay(tableId);
        });
        li.appendChild(button);
        pagination.appendChild(li);
    }
    // add last button
    pagination.appendChild(lastButton);
}

function goToFirstPage(tableId) {
    var data = tables[tableId];
    data.currentPage = 0;
    updateTableDisplay(tableId);
}

function goToLastPage(tableId) {
    var data = tables[tableId];
    data.currentPage = Math.ceil(data.allRows.length/data.pageSize) - 1;
    updateTableDisplay(tableId);
}

function changePageSize(selectElement, tableId) {
    var data = tables[tableId];
    pageSize = parseInt(selectElement.value);
    data.pageSize = pageSize;
    data.currentPage = 0;
    updateTableDisplay(tableId);
}

//Helper function to handle input for sorting
function handleInput(inputText) {
    // remove dollar sign
    var cleanedText = inputText.replace(/[$,]/g, '');

    // try to extract number from the text
    var matches = cleanedText.match(/(\d+)/);
    if (matches) {
        var numberPart = parseFloat(matches[0]);
        if (!isNaN(numberPart)) {
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