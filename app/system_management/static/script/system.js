document.addEventListener("DOMContentLoaded", function() {
    var issueDateInput = document.getElementById("issue_date");
    var expiryDateInput = document.getElementById("expiry_date");
    if (issueDateInput && expiryDateInput) {
        issueDateInput.addEventListener("change", function() {
            var issueDate = new Date(issueDateInput.value);
            if (!isNaN(issueDate)) {
                var expiryDate = new Date(issueDate.setFullYear(issueDate.getFullYear() + 2));
                expiryDateInput.value = expiryDate.toISOString().split('T')[0];
            }
        });
    }

    // Initialize balance based on selected type for add gift card modal
    updateBalance();

    // Attach updateBalance function to the type select change event for add gift card modal
    var typeSelect = document.getElementById("type_id");
    if (typeSelect) {
        typeSelect.addEventListener("change", function() {
            updateBalance();
        });
    }

    // Attach updateBalance function to the type select change event for each edit gift card modal
    var editTypeSelects = document.querySelectorAll("[id^=edit_type_id]");
    editTypeSelects.forEach(function(selectElement) {
        var modalIndex = selectElement.id.replace('edit_type_id', '');
        selectElement.addEventListener("change", function() {
            updateBalance(modalIndex);
        });
        // Initialize balance for each edit modal
        updateBalance(modalIndex);
    });

    // Generate redemption code automatically
    var redemptionCodeInput = document.getElementById("redemption_code");
    if (redemptionCodeInput) {
        var maxRedemptionCode = Math.max(...giftcards.map(g => parseInt(g[3].replace('GC', '')))) + 1;
        redemptionCodeInput.value = 'GC' + String(maxRedemptionCode).padStart(3, '0');
    }

    // customer promotions filter
    function filterByStatus() {
        var statusFilter = document.getElementById('statusFilter').value;
        var rows = document.getElementById('activeTableBody').getElementsByTagName('tr');
        var today = new Date().toISOString().split('T')[0];

        for (var i = 0; i < rows.length; i++) {
            var usedDate = rows[i].getElementsByTagName('td')[2].textContent;
            if (statusFilter === 'all') {
                rows[i].style.display = '';
            } else if (statusFilter === 'available' && usedDate === '') {
                rows[i].style.display = '';
            } else if (statusFilter === 'not_available' && usedDate !== '' && usedDate <= today) {
                rows[i].style.display = '';
            } else {
                rows[i].style.display = 'none';
            }
        }
    }
});

// Function to update balance based on selected type
function updateBalance(modalIndex = '') {
    console.log('updateBalance for modal ' + modalIndex);
    var typeSelect = document.getElementById(modalIndex ? "edit_type_id" + modalIndex : "type_id");
    var selectedOption = typeSelect.options[typeSelect.selectedIndex];
    var amount = selectedOption.getAttribute("data-amount");
    var balanceInput = document.getElementById(modalIndex ? "edit_current_balance" + modalIndex : "current_balance");
    balanceInput.value = amount;
}

// Helper function to pad ID numbers
function padId(number, length) {
    return number.toString().padStart(length, '0');
}

// customer promotions filter
function filterByStatus() {
    var statusFilter = document.getElementById('statusFilter').value;
    var rows = document.getElementById('activeTableBody').getElementsByTagName('tr');
    var today = new Date().toISOString().split('T')[0];

    for (var i = 0; i < rows.length; i++) {
        var usedDate = rows[i].getElementsByTagName('td')[2].textContent;
        if (statusFilter === 'all') {
            rows[i].style.display = '';
        } else if (statusFilter === 'available' && usedDate === '') {
            rows[i].style.display = '';
        } else if (statusFilter === 'not_available' && usedDate !== '' && usedDate <= today) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}
