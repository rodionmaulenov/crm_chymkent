document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const documentsParam = urlParams.get('add_or_change');

    if (documentsParam === 'change')  {
        const mainTab = document.querySelector('#tab-scheduled-events');
        const mainTabLink = document.querySelector('#tablink-scheduled-events');

        // Remove other tabs and links
        document.querySelectorAll('[id^="tab-"]:not(#tab-scheduled-events), [id^="tablink-"]:not(#tablink-scheduled-events)')
            .forEach(element => element.remove());

        // Display only the Main Documents tab
        if (mainTab && mainTabLink) {
            mainTabLink.classList.add('active');
            mainTab.style.display = 'block';
        }

        // Redirect to the Main Documents tab content
        window.location.hash = '#scheduled-events';
    }
});
