document.addEventListener('DOMContentLoaded', function() {
    var documentTab = document.getElementById('tablink-document');
    var mainDocumentTab = document.getElementById('tablink-main-documents');
    var additionalDocumentTab = document.getElementById('tablink-additional-documents');

    if (documentTab) {
        documentTab.style.display = 'none';
    }

    if (mainDocumentTab) {
        mainDocumentTab.click();
    } else if (additionalDocumentTab) {
        additionalDocumentTab.click();
    }
});
