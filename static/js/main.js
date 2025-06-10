// static/js/main.js

// Copy a given string to the clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => alert("Copied to clipboard!"))
        .catch(err => alert("Failed to copy: " + err));
}

// Form validation helpers
document.addEventListener("DOMContentLoaded", () => {
    // Validate recipient email on compose page
    const emailInput = document.getElementById("recipient_email");
    if (emailInput) {
        emailInput.addEventListener("input", () => {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!re.test(emailInput.value.trim())) {
                emailInput.setCustomValidity("Enter a valid email address.");
            } else {
                emailInput.setCustomValidity("");
            }
        });
    }

    // Validate OTP field on retrieve page
     const otpInput = document.getElementById("otp");
    if (otpInput) {
        otpInput.addEventListener("input", () => {
            // Allow exactly 6 hexadecimal characters (0–9, A–F)
            if (!/^[0-9A-Fa-f]{6}$/.test(otpInput.value.trim())) {
                otpInput.setCustomValidity("OTP must be exactly 6 hexadecimal characters (0–9, A–F).");
            } else {
                otpInput.setCustomValidity("");
            }
        });
}
});
