document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded and parsed");
    var dropzones = document.querySelectorAll('.dropzone');

    dropzones.forEach(function(dropzone) {
        console.log("Found dropzone:", dropzone);
        var dropzoneId = dropzone.id.split('-').slice(1).join('-'); // Adjust ID parsing
        var input = document.getElementById('id_' + dropzoneId);
        var preview = document.getElementById('preview-' + dropzoneId);

        if (!input) {
            console.error("Input element not found for dropzone:", dropzone.id);
            return;
        }
        if (!preview) {
            console.error("Preview element not found for dropzone:", dropzone.id);
            return;
        }

        // Click event to open file dialog
        dropzone.addEventListener('click', function () {
            console.log("Dropzone clicked:", dropzone.id);
            input.click();
        });

        // Drag over event
        dropzone.addEventListener('dragover', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
            console.log("Drag over dropzone:", dropzone.id);
        });

        // Drag leave event
        dropzone.addEventListener('dragleave', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
            console.log("Drag leave dropzone:", dropzone.id);
        });

        // Drop event
        dropzone.addEventListener('drop', function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
            console.log("Files dropped on dropzone:", dropzone.id);
            var files = e.dataTransfer.files;
            handleFiles(files, input, preview);
        });

        // File input change event
        input.addEventListener('change', function (e) {
            console.log("File input changed:", input.id);
            var files = e.target.files;
            handleFiles(files, input, preview);
        });
    });

    function handleFiles(files, input, preview) {
        preview.innerHTML = '';  // Clear previous previews
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            previewFile(file, preview);
        }
        input.files = files;
    }

    function previewFile(file, preview) {
        var fileName = document.createElement('div');
        fileName.textContent = file.name;
        preview.appendChild(fileName);
        console.log("File name added to preview:", file.name);
    }
});
