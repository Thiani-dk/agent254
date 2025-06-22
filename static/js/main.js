// static/js/main.js

function copyToClipboard(element, textToCopy) {
    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = element.innerText;
        element.innerText = 'Copied!';
        element.disabled = true;
        setTimeout(() => {
            element.innerText = originalText;
            element.disabled = false;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        alert('Failed to copy text.');
    });
}

document.addEventListener("DOMContentLoaded", () => {
    // Validate recipient email on compose page
    const emailInput = document.getElementById("recipient_email");
    if (emailInput) {
        emailInput.addEventListener("input", () => {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!re.test(emailInput.value.trim())) {
                emailInput.setCustomValidity("Please enter a valid email address.");
            } else {
                emailInput.setCustomValidity("");
            }
        });
    }

    // Validate OTP field on retrieve page
    const otpInput = document.getElementById("otp");
    if (otpInput) {
        otpInput.addEventListener("input", () => {
            const otpValue = otpInput.value.trim();
            otpInput.value = otpValue.toUpperCase(); // Force uppercase for consistency
            if (!/^[0-9A-F]{6}$/.test(otpValue)) {
                otpInput.setCustomValidity("OTP must be exactly 6 hexadecimal characters (0-9, A-F).");
            } else {
                otpInput.setCustomValidity("");
            }
        });
    }
});