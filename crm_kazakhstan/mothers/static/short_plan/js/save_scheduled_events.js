document.addEventListener('DOMContentLoaded', function () {
    console.log("JavaScript Loaded");
    const updateButton = document.querySelector('#update-checked');

    if (!updateButton) {
        console.error('Update button not found');
        return;
    }

    updateButton.addEventListener('click', function (event) {
        event.preventDefault(); // Prevent the form from submitting

        console.log("Button Clicked");
        const checkboxes = document.querySelectorAll('.is-new-checkbox:checked');
        const motherIds = Array.from(checkboxes).map(cb => cb.getAttribute('data-mother-id'));

        console.log("Mother IDs: ", motherIds);

        if (motherIds.length > 0) {
            const updateUrl = '/admin/mothers/shortplan/update_scheduled_events/';
            console.log("Update URL: ", updateUrl);

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            console.log("CSRF Token: ", csrfToken);

            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ mother_ids: motherIds })
            })
            .then(response => {
                console.log("Response status:", response.status);
                if (response.redirected) {
                    console.log("Redirection detected to", response.url);
                    window.location.href = response.url;
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    console.log("Response Data: ", data);
                    if (data.status === 'success') {
                        console.log("Events updated successfully.");
                        // Remove the updated instances from the DOM
                        motherIds.forEach(id => {
                            const checkbox = document.querySelector(`.is-new-checkbox[data-mother-id="${id}"]`);
                            if (checkbox) {
                                const row = checkbox.closest('tr');
                                if (row) {
                                    row.remove();
                                }
                            }
                        });
                    } else {
                        console.error('Failed to update events:', data.error);
                        alert('Failed to update events: ' + data.error);
                    }
                } else {
                    console.warn("No data received");
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('An error occurred: ' + error.message);
            });
        } else {
            console.warn('No checkboxes selected');
        }
    });
});
