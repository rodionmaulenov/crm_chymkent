document.addEventListener('DOMContentLoaded', function() {
    const imageContainers = document.querySelectorAll('.image-container');

    imageContainers.forEach(container => {
        const image = container.querySelector('.hoverable-image');

        container.addEventListener('click', function() {
            image.classList.toggle('clicked-image');
        });
    });
});
