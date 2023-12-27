function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function toggleDarkMode() {
    const body = document.body;
    const mainContainer = document.querySelector('.container');
    const nestedContainer = document.querySelector('body > div > div');
    const modeIcon = document.getElementById('modeIcon');

    const isDarkTheme = body.classList.contains('dark-theme');

    body.classList.toggle('dark-theme', !isDarkTheme);
    mainContainer.classList.toggle('dark-theme', !isDarkTheme);

    if (nestedContainer) {
        nestedContainer.classList.toggle('dark-theme', !isDarkTheme);
    }

    modeIcon.src = isDarkTheme ? "/static/sun.png" : "/static/moon.png";
    setCookie('theme', isDarkTheme ? 'light' : 'dark', 365);
}

function applySavedTheme() {
    const savedTheme = getCookie('theme');
    const modeIcon = document.getElementById('modeIcon');

    if (!savedTheme) {
        setCookie('theme', 'dark', 365);
        toggleDarkMode();
    } else {
        if (savedTheme === 'dark') {
            toggleDarkMode();
        } else {
            modeIcon.src = "/static/sun.png";
        }
    }
}


function showMessage(message, isError) {
    const icon = isError ? 'error' : 'success';

    Swal.fire({
        icon: icon,
        title: isError ? 'Error' : 'Success',
        text: message,
        confirmButtonColor: '#007bff',
    });
}

function showMessageAndReset(data) {
    showMessage(data.message, data.error);
    messageBox.innerText = data.message;
    grecaptcha.reset();
}

function showTermsModal() {
    const termsCheckbox = document.getElementById('termsCheckbox');

    Swal.fire({
        title: 'Terms and Conditions',
        html: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ...',
        icon: 'info',
        confirmButtonText: 'I agree',
        showCancelButton: true,
        cancelButtonText: 'Cancel',
        allowOutsideClick: false,
    }).then((result) => {
        termsCheckbox.checked = result.isConfirmed;
    });
}

function validateTermsCheckbox() {
    const termsCheckbox = document.getElementById('termsCheckbox');

    if (!termsCheckbox.checked) {
        showMessage("Please agree to the terms and conditions.", true);
        return false;
    }

    return true;
}

function submitForm(event) {
    const serverId = document.getElementById('serverId').value;
    const recaptchaResponse = grecaptcha.getResponse();
    event.preventDefault();

    if (!validateTermsCheckbox()) {
        return;
    }

    if (!recaptchaResponse || recaptchaResponse.length === 0) {
        showMessage("Please complete the reCAPTCHA challenge.", true);
        return;
    }

    fetch('/whitelist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `server_id=${serverId}&g-recaptcha-response=${recaptchaResponse}`,
    })
    .then(response => response.json())
    .then(data => showMessageAndReset(data))
    .catch(error => {
        console.error('Error:', error);
        showMessage('An error occurred while processing the request.', true);
    });
}

function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}


document.addEventListener('DOMContentLoaded', function () {
    applySavedTheme();
    const submitButton = document.getElementById('submitButton');
    var serverIdParam = getUrlParameter('id');
    if (serverIdParam) {
        var serverIdInput = document.getElementById('serverId');
        serverIdInput.value = serverIdParam;
    
        serverIdInput.readOnly = true;
    }
    
    submitButton.addEventListener('click', function (event) {
        submitForm(event);
    });
});
