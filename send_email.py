import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()

def send_linkedin_post_email(post_content: str):
    sender_email = "er.sarthakpande@gmail.com"
    receiver_email = "sarthakpande1008@gmail.com"
    app_password = os.getenv("EMAIL_APP_PASSWORD")

    # Create clickable approval link
    encoded_content = urllib.parse.quote_plus(post_content)
    approval_url = f"http://localhost:5001/approve?content={encoded_content}"  # Change with ngrok later

    html = f"""
    <html>
        <body>
            <p>Here's your AI-generated LinkedIn post:</p>
            <blockquote>{post_content}</blockquote>
            <p>
                <a href="{approval_url}" style="
                    background-color:#0073b1;
                    color:white;
                    padding:10px 20px;
                    text-decoration:none;
                    font-weight:bold;
                    border-radius:5px;">
                    ✅ Approve & Post on LinkedIn
                </a>
            </p>
        </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your AI LinkedIn Post - Approve to Publish"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)

    print("📧 Approval email sent with button!")