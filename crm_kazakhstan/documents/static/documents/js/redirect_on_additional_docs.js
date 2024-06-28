document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const documentsParam = urlParams.get('documents');

    if (documentsParam === 'additional') {
        const mainTab = document.querySelector('#tab-additional-documents');
        const mainTabLink = document.querySelector('#tablink-main-documents');

        // Remove other tabs and links
        document.querySelectorAll('[id^="tab-"]:not(#tab-additional-documents), [id^="tablink-"]:not(#tablink-additional-documents)')
            .forEach(element => element.remove());

        // Display only the Main Documents tab
        if (mainTab && mainTabLink) {
            mainTabLink.classList.add('active');
            mainTab.style.display = 'block';
        }

        // Redirect to the Main Documents tab content
        window.location.hash = '#additional-documents';
    }
});
