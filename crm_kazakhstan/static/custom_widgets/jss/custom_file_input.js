document.addEventListener('DOMContentLoaded', function () {
    var dropzones = document.querySelectorAll('.dropzone');

    dropzones.forEach(function(dropzone) {
        var input = dropzone.previousElementSibling;
        var preview = dropzone.nextElementSibling;

        dropzone.addEventListener('dragover', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
            var files = e.dataTransfer.files;
            handleFiles(files, input, preview);
        });

        input.addEventListener('change', function (e) {
            var files = e.target.files;
            handleFiles(files, input, preview);
        });
    });

    function handleFiles(files, input, preview) {
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            previewFile(file, preview);
        }
        input.files = files;
    }

    function previewFile(file, preview) {
        var reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = function () {
            var img = document.createElement('img');
            img.src = reader.result;
            preview.appendChild(img);
        }
    }
});
