$(document).ready(function() {
    $("tbody tr").each(function() {
        var hiddenData = $(this).find("span.hidden-data");
        if (hiddenData.length > 0) {
            var hasRelatedDocuments = hiddenData.data("related-docs");
            var nameField = $(this).find("th.field-custom_name");

            if (hasRelatedDocuments === "True") {
                var link = nameField.find("a").attr("href");
                nameField.html('<a href="' + link + '">' + nameField.text() + '</a>');
            } else {
                nameField.html(nameField.text());
            }
        } else {
        }
    });
});
