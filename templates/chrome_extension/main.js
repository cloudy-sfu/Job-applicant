import {flask_port} from "./flask_port.js";

// Error message banner
const errorAlert = document.getElementById('error-alert');
const errorMessage = document.getElementById('error-message');
const closeButton = document.getElementById('error-close');
function show_message(level, message) {
    const themes = [
        'theme-primary',
        'theme-accent',
        'theme-success',
        'theme-danger',
        'theme-warning',
        'theme-info',
        'theme-inverse',
        'theme-secondary'
    ];
    errorAlert.classList.remove(...themes);
    if (themes.includes(`theme-${level}`)) {
        errorAlert.classList.add(`theme-${level}`);
    } else {
        console.warn("func show_message: Argument \"level\" must be in: " +
            "primary, accent, success, danger, warning, info, inverse, secondary.");
    }
    errorMessage.textContent = message;
    errorAlert.classList.remove('d-none');
}
function clear_message() {
    errorAlert.classList.add('d-none');
}
closeButton.addEventListener('click', clear_message);
// Error message banner END

function set_linkdapi_key (linkdapi_key) {
    const field = document.getElementById('linkdapi_key');
    field.setAttribute('value', linkdapi_key);
}

$.ajax({
    type: 'GET',
    url: `http://127.0.0.1:${flask_port}/get_linkdapi_key`,
    timeout: 10000,
    success: (response) => set_linkdapi_key(response),
    error: () => show_message('danger', 'Fail to get Linkdapi key.')
})

$('#linkdapi-form').submit(function (event) {
    event.preventDefault();
    const form = $(this);
    $.ajax({
        type: 'POST',
        url: `http://127.0.0.1:${flask_port}/set_linkdapi_key`,
        timeout: 10000,
        data: form.serialize(), // Serialize the form data
        success: (response) => {
            show_message('success', 'Linkdapi key updated.');
            set_linkdapi_key(response.responseText);
        },
        error: () => show_message('danger', 'Fail to set Linkdapi key.')
    });
})