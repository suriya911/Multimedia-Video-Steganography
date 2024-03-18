import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_email(email_to):
    # Setup port number and server name
    smtp_port = 587                 # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server

    # Set up the email lists
    email_from = "blade2strike@gmail.com"
    # Define the password (better to reference externally)
    pswd = "buxacrqhdttxniqm " 

    # name the email subject
    subject2 = "RSA Public key for the Embedded video"

    # Make the body of the email
    body = f"""
        This is Public Key use this to encrypt the secret information for me ......
        """
    # sending the email to the sender 
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to[1]
    msg['Subject'] = subject2

    # Attach the body to both the emails
    msg.attach(MIMEText(body, 'plain'))

    # Define the file to attach for both the emails
    filename = "RSA_public.pem"

    # Open the file in python as a binary
    attackment= open(f"./Keys/{filename}", 'rb')  # r for read and b for binary

    # Define the attachment package for sender 
    
    attachment_package = MIMEBase('application', 'octet-stream')
    attachment_package.set_payload((attackment).read())
    encoders.encode_base64(attachment_package)
    attachment_package.add_header('Content-Disposition', "attachment; filename= " + filename)
    msg.attach(attachment_package)

    # Cast as string
    text = msg.as_string()

    # Connect with the server
    print("Connecting to server...")
    TIE_server = smtplib.SMTP(smtp_server, smtp_port)
    TIE_server.starttls()
    TIE_server.login(email_from, pswd)
    print("Succesfully connected to server")
    print()

    # Send emails to the sender

    print(f"Sending email to: {email_to}...")
    TIE_server.sendmail(email_from, email_to, text)
    print(f"Email sent to: {email_to}")