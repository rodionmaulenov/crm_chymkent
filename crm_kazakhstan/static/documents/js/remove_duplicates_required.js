document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('#requireddocument_set-group'); // Ensure the correct selector here

    // Function to update all dropdowns based on selected values
    const updateTitleDropdowns = () => {
        const selectedTitles = new Set();
        const selects = container.querySelectorAll('.field-title select');

        // Collect all non-empty selected values
        selects.forEach(select => {
            if (select.value) selectedTitles.add(select.value);
        });

        // Adjust options visibility based on selections
        selects.forEach(select => {
            const currentSelection = select.value;
            Array.from(select.options).forEach(option => {
                option.disabled = selectedTitles.has(option.value) && option.value !== currentSelection;
            });
        });
    };

    // Attach or re-attach event listeners to all current dropdowns
    const setupDropdownListeners = () => {
        const selects = container.querySelectorAll('.field-title select');
        selects.forEach(select => {
            select.removeEventListener('change', updateTitleDropdowns);
            select.addEventListener('change', updateTitleDropdowns);
        });
    };

    // Mutation observer to re-apply logic when inlines are added or removed
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            if (mutation.type === 'childList') {
                if (mutation.addedNodes.length || mutation.removedNodes.length) {
                    setupDropdownListeners();
                    updateTitleDropdowns();  // Re-calculate dropdowns whenever a change occurs
                }
            }
        });
    });

    // Observe changes in the container for any DOM updates
    observer.observe(container, { childList: true, subtree: true });

    // Initial setup
    setupDropdownListeners();
    updateTitleDropdowns();
});
