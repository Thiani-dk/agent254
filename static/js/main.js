// static/js/main.js

function copyToClipboard(element, textToCopy) {
    navigator.clipboard.writeText(textToCopy).then(() => {
        // Use innerHTML to preserve icons inside the button
        const originalHTML = element.innerHTML;
        element.innerHTML = 'Copied!';
        element.disabled = true;
        setTimeout(() => {
            element.innerHTML = originalHTML;
            element.disabled = false;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        alert('Failed to copy text.');
    });
}

document.addEventListener("DOMContentLoaded", () => {
    // --- FEATURE: COPY ALL LOGIC ---
    // Find the "Copy All" button by its ID
    const copyAllButton = document.getElementById("copyAllBtn");
    if (copyAllButton) {
        // Add a click event listener
        copyAllButton.addEventListener("click", () => {
            // Get the message details from the button's data attributes
            const link = copyAllButton.dataset.link;
            const messageId = copyAllButton.dataset.messageId;
            const otp = copyAllButton.dataset.otp;

            // Create a user-friendly, formatted string for the clipboard
            const formattedText = `Hello! Here are the details for the secure message:\n\n` +
                                  `1. Retrieval Link:\n${link}\n\n` +
                                  `2. Message ID:\n${messageId}\n\n` +
                                  `3. One-Time Password (OTP):\n${otp}`;

            // Use the existing copyToClipboard function to copy the text and give user feedback
            copyToClipboard(copyAllButton, formattedText);
        });
    }
    // --- END OF COPY ALL FEATURE ---


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
            const otpValue = otpInput.value.trim().toUpperCase();
            otpInput.value = otpValue; // Force uppercase for consistency
            if (!/^[0-9A-F]{6}$/.test(otpValue)) {
                otpInput.setCustomValidity("OTP must be exactly 6 hexadecimal characters (0-9, A-F).");
            } else {
                otpInput.setCustomValidity("");
            }
        });
    }
});