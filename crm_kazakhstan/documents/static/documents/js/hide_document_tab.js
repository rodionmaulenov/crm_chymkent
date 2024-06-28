document.addEventListener('DOMContentLoaded', function() {
    var documentTab = document.getElementById('tablink-document');
//    var documentTabContent = document.getElementById('tabcontent-document');
    var mainDocumentTab = document.getElementById('tablink-main-documents');

    if (documentTab) {
        documentTab.style.display = 'none';
    }

    if (mainDocumentTab) {
        mainDocumentTab.click();
    }
});
