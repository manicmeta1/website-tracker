import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any

class EmailNotifier:
    def __init__(self):
        self.email_recipient = None
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = "your-email@gmail.com"  # Configure with actual email
        self.smtp_password = "your-password"  # Configure with actual password
        
    def set_email(self, email: str):
        """Set email recipient"""
        self.email_recipient = email
        
    def send_notification(self, changes: List[Dict[str, Any]]):
        """Send email notification about changes"""
        if not self.email_recipient:
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.email_recipient
            msg['Subject'] = "Website Changes Detected - edicanaturals.com"
            
            # Create email body
            body = "The following changes were detected:\n\n"
            for change in changes:
                body += f"Type: {change['type']}\n"
                body += f"Location: {change['location']}\n"
                body += f"Before: {change['before']}\n"
                body += f"After: {change['after']}\n"
                body += "-" * 50 + "\n"
                
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
        except Exception as e:
            raise Exception(f"Failed to send email notification: {str(e)}")
