var select_button = document.getElementById('possible-spinner')

function replace_with_spinner() {
    select_button.innerHTML = "<div class=\"spinner-border spinner-border-sm text-dark\" role=\"status\">\
                                   <span class=\"visually-hidden\">Loading...</span>\
                               </div>"
}
