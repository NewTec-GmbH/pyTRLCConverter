document.addEventListener("DOMContentLoaded", function() {
    // Search for all elements with the class .wy-nav-content
    var elements = document.querySelectorAll('.wy-nav-content');
    elements.forEach(function(el) {
        // delete specific the limit defined in max-width 
        el.style.maxWidth = 'none';
       
    });
});