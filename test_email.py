import smtplib
from email.mime.text import MIMEText

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "hasheabduljabbar@gmail.com"
MAIL_PASSWORD = "loodjuwiqepmjylb"

def test_email():
    try:
        msg = MIMEText("This is a test email from Agent254.")
        msg['From'] = MAIL_USERNAME
        msg['To'] = "<recipient-email>"
        msg['Subject'] = "Test Email"

        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, "<recipient-email>", msg.as_string())
        server.quit()

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

test_email()