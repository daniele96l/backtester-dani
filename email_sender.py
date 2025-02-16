import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class EmailSender:
    def __init__(self, sender_email: str, app_password: str):
        self.sender_email = sender_email
        self.app_password = app_password

    def send_email_with_pdf(self, receiver_email: str, subject: str, body: str, pdf_content, pdf_filename: str):
        """Sends an email with PDF attachment to the specified receiver."""
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        # Attach the body with the msg instance
        message.attach(MIMEText(body, 'plain'))

        # Attach the PDF
        payload = MIMEBase('application', 'octate-stream', Name=pdf_filename)
        payload.set_payload(pdf_content)

        # Encoding the binary into base64
        encoders.encode_base64(payload)

        # Add header with pdf name
        payload.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
        message.attach(payload)

        # Use gmail with port
        session = smtplib.SMTP('smtp.gmail.com', 587)

        # Enable security
        session.starttls()

        # Login with mail_id and password
        session.login(self.sender_email, self.app_password)

        # Send the email
        text = message.as_string()
        session.sendmail(self.sender_email, receiver_email, text)
        session.quit()

        print('Mail Sent')

if __name__ == "__main__":
    # Test the EmailSender class
    sender_email = "daniele96ligato@gmail.com"
    app_password = EMAIL_PASSWORD# Replace with your app password
    email_sender = EmailSender(sender_email, app_password)

    # Test sending an email
    test_receiver = "daniele96ligato@gmail.com"
    test_subject = "Test Email from Python Class"
    test_body = "Hello, this is a test email sent using the EmailSender class."

    email_sender.send_email_with_pdf(test_receiver, test_subject, test_body, b"PDF content here")