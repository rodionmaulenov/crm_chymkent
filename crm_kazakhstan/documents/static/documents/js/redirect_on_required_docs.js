document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const documentsParam = urlParams.get('documents');

    if (documentsParam === 'required') {
        const mainTab = document.querySelector('#tab-required-documents');
        const mainTabLink = document.querySelector('#tablink-required-documents');

        // Remove other tabs and links
        document.querySelectorAll('[id^="tab-"]:not(#tab-required-documents), [id^="tablink-"]:not(#tablink-required-documents)')
            .forEach(element => element.remove());

        // Display only the Main Documents tab
        if (mainTab && mainTabLink) {
            mainTabLink.classList.add('active');
            mainTab.style.display = 'block';
        }

        // Redirect to the Main Documents tab content
        window.location.hash = '#required-documents';
    }
});
