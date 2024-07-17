// Make non-persistent flash messages disappear after 10 seconds
function handle_alerts() {
  var alerts = document.querySelectorAll('.alert');
  alerts.forEach(function (alert) {
      // Check for the presence of the 'persistent-alert' class
      if (!alert.classList.contains('persistent-alert')) {
          setTimeout(function () {
              alert.style.opacity = '0';
              setTimeout(function () {
                  alert.remove();
              }, 600);
          }, 10000); // Adjust the time as necessary
      }
  });
}

// Run the function once the DOM content is fully loaded
document.addEventListener("DOMContentLoaded", function () {
  handle_alerts();
});
//homepage about scroll down
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('aboutUsLink').addEventListener('click', function(event) {
        event.preventDefault();
        document.getElementById('aboutUs').scrollIntoView({ behavior: 'smooth' });
    });
});

