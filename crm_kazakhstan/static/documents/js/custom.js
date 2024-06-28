document.addEventListener('DOMContentLoaded', function() {
    Dropzone.autoDiscover = false;
    var dropzones = document.querySelectorAll('.dropzone');
    dropzones.forEach(function(dropzoneElement) {
        var myDropzone = new Dropzone(dropzoneElement, {
            url: dropzoneElement.getAttribute('data-url'),
            maxFiles: 1,
            acceptedFiles: "image/*"
        });
    });
});
