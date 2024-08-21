document.addEventListener('DOMContentLoaded', function () {
    // Add event listener to filter links to update the queryset
    const filterList = document.querySelector('#changelist-filter ul');

    filterList.addEventListener('click', function(event) {
        if (event.target.tagName === 'A') {
            event.preventDefault();  // Prevent default link behavior

            // Remove 'selected' class from currently selected item
            const selectedLi = filterList.querySelector('li.selected');
            if (selectedLi) {
                selectedLi.classList.remove('selected');
            }

            // Get the selected filter value
            const selectedValue = event.target.href.split('=')[1];

            // Add 'selected' class to the clicked item
            event.target.closest('li').classList.add('selected');

            // Add 'active' class to the ul element
            filterList.classList.add('active');

            // Update the URL with the new filter selection
            const newUrl = new URL(window.location);
            newUrl.searchParams.set('time_new_visit', selectedValue);
            history.pushState({}, '', newUrl);

            // Fetch the data for the selected queryset and update the page
            fetch(newUrl)
                .then(response => response.text())
                .then(html => {
                    // Replace the content of the relevant section with the new data
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newContent = doc.querySelector('#result_list');  // or any other specific container
                    document.querySelector('#result_list').innerHTML = newContent.innerHTML;
                });
        }
    });

    // Handle back/forward navigation to maintain the selected state
window.addEventListener('popstate', function() {
    const currentUrlParams = new URLSearchParams(window.location.search);
    const currentFilter = currentUrlParams.get('time_new_visit');

    // Remove 'selected' class from currently selected item
    const selectedLi = filterList.querySelector('li.selected');
    if (selectedLi) {
        selectedLi.classList.remove('selected');
    }

    // Add 'selected' class to the item matching the current filter in the URL
    if (currentFilter) {
        const newSelectedLi = filterList.querySelector(`li a[href="?time_new_visit=${currentFilter}"]`).closest('li');
        if (newSelectedLi) {
            newSelectedLi.classList.add('selected');
        }

        // Add 'active' class to the ul element
        filterList.classList.add('active');

        // Check if the selected filter is not "All" and add the "Clear all filters" link
        if (currentFilter !== '' && currentFilter !== null && currentFilter !== 'All') {
            let clearFilters = document.querySelector('#changelist-filter-clear');
            if (!clearFilters) {
                clearFilters = document.createElement('h3');
                clearFilters.id = 'changelist-filter-clear';
                const clearLink = document.createElement('a');
                clearLink.href = '?';  // Link to clear all filters
                clearLink.textContent = '✖ Clear all filters';
                clearFilters.appendChild(clearLink);

                // Insert before the first h3 (which is the filter label)
                const filterLabel = document.querySelector('#changelist-filter h3');
                filterLabel.parentNode.insertBefore(clearFilters, filterLabel);
            }
        }
    } else {
        // Remove 'active' class if no filter is selected
        filterList.classList.remove('active');

        // Remove the "Clear all filters" link if present
        const clearFilters = document.querySelector('#changelist-filter-clear');
        if (clearFilters) {
            clearFilters.remove();
        }
    }
});


    // Initial check on page load to apply 'selected' and 'active' classes
    const currentUrlParams = new URLSearchParams(window.location.search);
    const currentFilter = currentUrlParams.get('time_new_visit');

    if (currentFilter) {
        const newSelectedLi = filterList.querySelector(`li a[href="?time_new_visit=${currentFilter}"]`).closest('li');
        if (newSelectedLi) {
            newSelectedLi.classList.add('selected');
            filterList.classList.add('active');
        }
    }
});
