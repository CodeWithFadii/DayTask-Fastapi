import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import EmailStr


def send_otp_email(receiver_email: EmailStr) -> str:
    sender_email = "furiousboy79@gmail.com"
    sender_password = "hfxh jlwz yapz aejk"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Generate OTP
    otp = "".join(random.choices(string.digits, k=4))

    subject = "Your DayTask OTP Code"

    html_body = f"""
    <html>
    <head>
        <style>
            .container {{
                font-family: Arial, sans-serif;
                padding: 20px;
                max-width: 500px;
                margin: auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }}
            .header {{
                text-align: center;
                padding-bottom: 20px;
            }}
            .otp {{
                font-size: 32px;
                font-weight: bold;
                color: #4CAF50;
                text-align: center;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #888;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>DayTask Verification</h2>
                <p>Use the OTP below to verify your email address</p>
            </div>
            <div class="otp">{otp}</div>
            <p style="text-align: center;">This OTP will expire in 10 minutes. Do not share it with anyone.</p>
            <div class="footer">
                &copy; 2025 DayTask. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

    # MIME setup
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"OTP sent to {receiver_email}")
        return otp

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise Exception("Failed to send email")

    finally:
        server.quit()  # type: ignore
