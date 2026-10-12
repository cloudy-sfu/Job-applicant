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

// Initially filled values
const linkdapi_key = document.getElementById('linkdapi_key');
$.ajax({
    type: 'GET',
    url: `http://127.0.0.1:${flask_port}/init_vars`,
    timeout: 10000,
    success: (response) => {
        linkdapi_key.setAttribute('value', response.linkdapi_key);
    },
    error: () => show_message('danger', 'Fail to initialize the ' +
        'extension.')
});

// Forms
$('#linkdapi-form').submit(function (event) {
    event.preventDefault();
    const form = $(this);
    $.ajax({
        type: 'POST',
        url: `http://127.0.0.1:${flask_port}/set_linkdapi_key`,
        timeout: 10000,
        data: form.serialize(), // Serialize the form data
        success: (response) => {
            if (response.error_code === 0) {
                show_message('success', 'Renidly API key updated.');
            } else {
                show_message('danger', response.error);
            }
        },
        error: () => show_message('danger', 'Fail to set Renidly API key.')
    });
})

$('#linkedin-form').submit(function (event) {
    event.preventDefault();
    const form = $(this);
    $.ajax({
        type: 'POST',
        url: `http://127.0.0.1:${flask_port}/add_linkedin_profile`,
        timeout: 10000,
        data: form.serialize(), // Serialize the form data
        success: (response) => {
            if (response.error_code === 0) {
                show_message('success', 'Added profile.');
            }
            else {
                show_message('danger', response.error);
            }
        },
        error: () => show_message('danger', 'Fail to add LinkedIn profile.')
    });
});
