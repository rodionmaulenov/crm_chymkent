// Configuration for filters
const filterConfigs = {
    timeToVisit: {
        correctOrder: ['new_visit', 'visit', 'not_visit'], // Defines the order of filter items
        url: '/admin/mothers/plannedlaboratory/get_filter_choices/', // URL to fetch filter choices
        filterHeadingText: 'By time to visit', // Text to match the filter heading in the DOM
        paramName: 'time_new_visit' // Query parameter name to use in the URL
    },
    usersObjects: {
        correctOrder: [], // No specific order defined for this filter
        url: '/admin/mothers/plannedlaboratory/get_users_objects_choices/', // URL to fetch filter choices
        filterHeadingText: 'By users objects', // Text to match the filter heading in the DOM
        paramName: 'username' // Query parameter name to use in the URL
    }
};

document.addEventListener("DOMContentLoaded", function () {

    function FetchFilterChoices(url) {
        return fetch(url).then(response => response.json());
    }

      function fetchFilteredData(params) {
        console.log(params)
        return fetch(`/admin/mothers/plannedlaboratory/?${params}`)
            .then(response => response.text())  // Fetch the HTML content as text
            .then(html => {
                updatePageContent(html); // Update the page content with the fetched data
            });
    }

    // Update filter`s lists
    function UpdateFilterList(data, config) {
        // Step 1: Identify filter heading by it`s text
        const filterHeading = Array.from(document.querySelectorAll("#changelist-filter h3"))
            .find(h3 => h3.textContent.trim() === config.filterHeadingText)

        if (data) {
            if (filterHeading) {
                // Step 2: Clear the list items in the corresponding <ul>
                const filterSection = filterHeading.nextElementSibling
                if (filterSection && filterSection.tagName === 'UL') {
                    filterSection.innerHTML = ''; // clear the current list items

                    // Step 3: Create a document fragment to hold the new list items
                    const fragment = document.createDocumentFragment()

                    // If correctOrder is empty, use data.choices directly, otherwise, use correctOrder
                    const itemsToDisplay = config.correctOrder.length > 0 ? config.correctOrder : data.choices.map(choice => choice.value);
                    // Step 4: Loop through the correctOrder and create list items
                    itemsToDisplay.forEach(value => {
                        let displayText = (data.choices.find(choice => choice.value === value) || {}).display;
                        if (displayText) {
                            const li = document.createElement('li')
                            const a = document.createElement('a')
                            a.href = `?${config.paramName}=${value}`
                            a.textContent = displayText
                            li.appendChild(a)
                            fragment.appendChild(li) // add list item to the fragment

                            // Step 6: Add event listener to handle the selected class and URL update
                            li.addEventListener('click', function (event) {
                                event.preventDefault();

                                // Remove the selected class from any currently selected item in this list
                                const currentSelected = filterSection.querySelector('li.selected');
                                if (currentSelected) {
                                    currentSelected.classList.remove('selected');
                                }

                                // Toggle selected class on the clicked item
                                li.classList.toggle('selected');

                                // Add 'active' class to the parent ul if any item is selected
                                if (li.classList.contains('selected')) {
                                    filterSection.classList.add('active');
                                    filterHeading.classList.add('active')
                                } else {
                                    filterSection.classList.remove('active');
                                    filterHeading.classList.remove('active')
                                }

                                // Update the URL with combined query params
                                updateUrlWithSelectedFilters();

                                // Check if 'clear all filters' link needs to be added or removed
                                toggleClearFiltersLink();

                                // Fetch the filtered data after updating the URL
                                const params = new URLSearchParams(window.location.search).toString();
                                fetchFilteredData(params); // Update with filtered data
                            });

                            // Check if this filter should be active based on the current URL when reloading
                            const currentUrlParams = new URLSearchParams(window.location.search);
                            if (currentUrlParams.get(config.paramName) === value) {
                                li.classList.add('selected');
                                filterSection.classList.add('active');
                                filterHeading.classList.add('active');
                            }
                        }
                    });

                    // Step 5: Append the fragment to the <ul>
                    filterSection.appendChild(fragment);
                }

            } else {
                console.log(`No filter heading found for: ${config.filterHeadingText}`);
            }
        }

    } // #UpdateFilterList end

    // Function to update the page content dynamically
    function updatePageContent(html) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newContent = doc.querySelector("#changelist-form")
        const currentContent = document.querySelector("#changelist-form")
        currentContent.innerHTML = newContent.innerHTML
    }

    // Function to update the URL with all selected filters
    function updateUrlWithSelectedFilters() {
        const url = new URL(window.location);
        const selectedFilters = document.querySelectorAll("#changelist-filter ul li.selected a");

        // Clear all existing query parameters related to filters
        Object.keys(filterConfigs).forEach(key => {
            const paramName = filterConfigs[key].paramName;
            url.searchParams.delete(paramName);
        });

        // Add query parameters for all selected filters
        selectedFilters.forEach(link => {
            const param = new URL(link.href).searchParams;
            param.forEach((value, key) => {
                url.searchParams.set(key, value);
            });
        });
        // Update the URL without reloading the page
        history.pushState({}, '', url);

    }

    // Function to toggle the "Clear all filters" link
    function toggleClearFiltersLink() {
        const selectedFilters = document.querySelectorAll("#changelist-filter ul li.selected");
        const clearFilters = document.querySelector("#changelist-filter-clear");
        if (selectedFilters) {
            if (!clearFilters) {
                // Add "Clear all filters" link if it doesn't exist
                const clearFiltersElement = document.createElement('h3');
                clearFiltersElement.id = "changelist-filter-clear";
                const clearLink = document.createElement('a');
                clearLink.href = '?';
                clearLink.textContent = '✖ Clear all filters';
                clearFiltersElement.appendChild(clearLink)

                // Insert it after the changelist-filter div
                const changelistFilter = document.querySelector("#changelist-filter h2");
                if (changelistFilter) {
                    changelistFilter.insertAdjacentElement("afterend", clearFiltersElement)
                }
            }
        } else {
            // Remove "Clear all filters" link if no filters are select
            if (clearFilters) {
                clearFilters.remove()
            }
        }

    } // End toggleClearFiltersLink

    // //Fetch data for all filters at one moment and update DOM at once
    // Promise.all(
    //     Object.keys(filterConfigs).map(key => {
    //         const config = filterConfigs[key];
    //         return FetchFilterChoices(config.url).then(data => ({key, data}));
    //     })
    // ).then(results => {
    //     results.forEach(({key, data}) => {
    //         const config = filterConfigs[key];
    //         UpdateFilterList(data, config);
    //     });
    // });

    function checkAndUpdateFilters() {
        Object.keys(filterConfigs).forEach(key => {
            const config = filterConfigs[key];
            FetchFilterChoices(config.url).then(data => {
                const filterHeading = Array.from(document.querySelectorAll("#changelist-filter h3"))
                    .find(h3 => h3.textContent.trim() === config.filterHeadingText);

                if (!filterHeading) {
                    UpdateFilterList(data, config);
                } else {
                    const filterSection = filterHeading.nextElementSibling;
                    const currentOptions = Array.from(filterSection.querySelectorAll("li a")).map(a => a.href);
                    const newOptions = data.choices.map(choice => `?${config.paramName}=${choice.value}`);
                    const hasNewOptions = newOptions.some(option => !currentOptions.includes(option));

                    if (hasNewOptions) {
                        UpdateFilterList(data, config);
                    }
                }
            });
        });
    }

    // Initialize filters
    checkAndUpdateFilters();

    // Set interval to periodically check for new filters or options
    setInterval(checkAndUpdateFilters, 2000);

}); // #Dom End