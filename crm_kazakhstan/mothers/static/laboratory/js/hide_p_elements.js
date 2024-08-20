document.addEventListener('DOMContentLoaded', function() {
    // Generalized function to hide <p> tags within the 'original' class of elements whose IDs start with a given prefix
    const hideDescriptions = (prefix) => {
        document.querySelectorAll(`[id^="${prefix}"] .original p`).forEach(p => {
            p.style.display = 'none';
        });
    };

    // Initial hide for both document sets
    hideDescriptions('laboratories');

});