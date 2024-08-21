document.addEventListener('DOMContentLoaded', function () {
    const updateButton = document.querySelector('#update-checked');

    if (!updateButton) {
        return;
    }

    updateButton.addEventListener('click', function (event) {
        event.preventDefault(); // Prevent the form from submitting

        const checkboxes = document.querySelectorAll('.is-new-checkbox:checked');
        const motherIds = Array.from(checkboxes).map(cb => cb.getAttribute('data-mother-id'));

        if (motherIds.length > 0) {
            const updateUrl = '/admin/mothers/plannedlaboratory/update_is_completed/';
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ mother_ids: motherIds })
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data && data.status === 'success') {
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
                    // After removing rows, check if the table is now empty and redirect if necessary
                    const remainingCheckboxes = document.querySelectorAll('.is-new-checkbox');
                    if (remainingCheckboxes.length === 0) {
                        window.location.href = '/admin/mothers/plannedlaboratory/';
                    }
                }
            });
        }
    });
});
