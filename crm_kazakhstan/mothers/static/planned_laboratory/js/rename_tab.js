document.addEventListener('DOMContentLoaded', function() {
    // Select the tab button by its ID
    var laboratoryTab = document.getElementById('tablink-laboratory');

    // Check if the element exists
    if (laboratoryTab) {
        // Change the text content of the tab
        laboratoryTab.textContent = 'Main Data';
    }
});
