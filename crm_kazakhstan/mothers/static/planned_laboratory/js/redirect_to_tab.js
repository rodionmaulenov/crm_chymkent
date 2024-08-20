document.addEventListener('DOMContentLoaded', function() {
    // The ID of the tab you want to automatically open
    var targetTab = '#laboratorys';

    // Check if the hash is already present in the URL
    if (window.location.hash !== targetTab) {
        // Append the target tab hash to the URL and reload the page
        window.location.hash = targetTab;
    }
});
