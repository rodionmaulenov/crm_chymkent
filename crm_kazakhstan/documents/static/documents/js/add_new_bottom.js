# Create the custom_script.js file and add the following code
document.addEventListener('DOMContentLoaded', function () {
    const saveAndAddAnotherButton = document.querySelector('input[name="_addanother"]');
    if (saveAndAddAnotherButton) {
        saveAndAddAnotherButton.value = 'Your Custom Label';
        saveAndAddAnotherButton.name = '_custom_save';  # Change the name to identify the button in response_change
    }
});