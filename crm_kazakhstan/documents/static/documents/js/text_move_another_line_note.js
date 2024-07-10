//document.addEventListener('DOMContentLoaded', function() {
//    const noteFields = document.querySelectorAll('.field-note p');
//
//    noteFields.forEach(field => {
//        const words = field.innerText.split(' ');
//        let formattedText = '';
//        let lineLength = 0;
//
//        words.forEach(word => {
//            if (lineLength + word.length + 1 > 60) {
//                formattedText += '\n' + word + ' ';
//                lineLength = word.length + 1;
//            } else {
//                formattedText += word + ' ';
//                lineLength += word.length + 1;
//            }
//        });
//
//        field.innerText = formattedText.trim();
//    });
//});
document.addEventListener('DOMContentLoaded', function() {
    const noteFields = document.querySelectorAll('.field-note p');

    noteFields.forEach(field => {
        const text = field.innerText;
        const words = text.split(' ');
        let formattedText = '';
        let lineLength = 0;
        const maxLineLength = 80;

        words.forEach(word => {
            if (word.length > maxLineLength) {
                // If the word itself is longer than maxLineLength, split it
                for (let i = 0; i < word.length; i += maxLineLength) {
                    formattedText += word.slice(i, i + maxLineLength) + '\n';
                }
                lineLength = 0; // Reset line length after breaking a long word
            } else if (lineLength + word.length + 1 > maxLineLength) {
                formattedText += '\n' + word + ' ';
                lineLength = word.length + 1;
            } else {
                formattedText += word + ' ';
                lineLength += word.length + 1;
            }
        });

        field.innerText = formattedText.trim();
    });
});

