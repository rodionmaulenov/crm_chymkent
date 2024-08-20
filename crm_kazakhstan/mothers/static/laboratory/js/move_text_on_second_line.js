document.addEventListener('DOMContentLoaded', function() {

    // Select all field-description <td> elements
    var descriptionFieldContainers = document.querySelectorAll('.field-description');

    if (descriptionFieldContainers.length > 0) {
        console.log("Description field containers found:", descriptionFieldContainers);

        // Loop through each field-description container
        descriptionFieldContainers.forEach(function(descriptionFieldContainer) {
            // Find the paragraph inside the container
            var paragraph = descriptionFieldContainer.querySelector('p');
            if (paragraph) {
                var content = paragraph.innerHTML;
                var maxChars = 65;  // Set the number of characters before wrapping
                var wrappedContent = '';

                var words = content.split(' ');  // Split content into words
                var currentLine = '';

                words.forEach(function(word) {
                    if ((currentLine + word).length > maxChars) {
                        // If adding the word exceeds the maxChars limit, insert a line break
                        wrappedContent += currentLine.trim() + '<br>';
                        currentLine = word + ' ';  // Start a new line with the current word
                    } else {
                        // Add the word to the current line
                        currentLine += word + ' ';
                    }
                });

                // Add any remaining words to the wrapped content
                wrappedContent += currentLine.trim();

                // Update the paragraph content with the wrapped text
                paragraph.innerHTML = wrappedContent.trim();
            }
        });
    }
});
