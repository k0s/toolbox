// focus the search element
$(document).ready(function() {
    if (!location.hash.length) {
        $('#search-text').focus();
    }
});
