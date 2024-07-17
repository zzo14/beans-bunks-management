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