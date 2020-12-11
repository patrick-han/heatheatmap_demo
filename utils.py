import math

"""
Calculates the distance between 2 points in 3-dimensional space
"""
def distance_3d(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2)

"""
Email Notifications
"""
import smtplib
import ssl
import mail_config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_alert():
    port = 465

    sender = mail_config.sender
    password = mail_config.pw

    receive = mail_config.receive

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Possible Gas Leak"
    msg['From'] = sender
    msg['To'] = receive

    # Create the body of the message
    html = """\
    <html>
      <head></head>
      <body>
        <p>Hi!<br>
           The gas detection sensor you set up has detected a possible leak<br>
           Here is the link to your ARENA: https://arena.andrew.cmu.edu/?scene=patrick_scene<br>
           <br>
           Best,<br>
           - Your ARENA Home Automation System
        </p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))

    context = ssl.create_default_context()
    print("Sending Alert)")
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context = context) as server:
        server.login(sender, password)
        server.sendmail(sender, receive, msg.as_string())
        server.quit()