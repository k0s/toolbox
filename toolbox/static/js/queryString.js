function parseQueryString() {
    var args = {};
    var searchString = document.location.search.slice(1);
    if (!searchString.length) {
        // no query string to speak of
        return null;
    }
    if (searchString[searchString.length -1] == '&') {
        // remove trailing '&'
        searchString = searchString.substr(0, searchString.length-1);
    }

    // split by '&'
    var params = document.location.search.slice(1).split("&");
    
    for (p in params) {
        var l = params[p].split("=").map(function(x) {
            try {
                return decodeURIComponent(x); 
            } catch(e) {
                return x;
            }
            });
        if (l.length != 2) {
            continue;
        }
        if (!args[l[0]]) {
            args[l[0]] = [];
        }
        args[l[0]].push(l[1]);
    }
    return args;
}