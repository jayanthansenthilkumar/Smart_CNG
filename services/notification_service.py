"""
Notification Service for Price Alerts and Updates
Supports Email, SMS, and Push Notifications
"""
import os
import logging
from datetime import datetime
from typing import List, Dict
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    """Handles sending notifications to users"""
    
    def __init__(self):
        self.email_enabled = bool(os.getenv('SMTP_SERVER'))
        self.sms_enabled = bool(os.getenv('TWILIO_ACCOUNT_SID'))
        self.push_enabled = bool(os.getenv('FIREBASE_API_KEY'))
    
    def send_price_alert(self, user, fuel_type, new_price, station=None):
        """
        Send price drop alert to user
        
        Args:
            user: User object
            fuel_type: Type of fuel (cng, petrol, diesel)
            new_price: New price value
            station: Optional Station object
        """
        try:
            station_name = station.name if station else "your area"
            
            subject = f"🔔 {fuel_type.upper()} Price Drop Alert!"
            message = f"""
            Great news! The price of {fuel_type.upper()} has dropped.
            
            New Price: ₹{new_price:.2f}
            Location: {station_name}
            
            Visit Smart CNG to find the best deals near you!
            """
            
            # Get user's preferred notification method
            if hasattr(user, 'preferences') and user.preferences:
                method = user.preferences.notification_method
            else:
                method = 'email'
            
            if method == 'email':
                self.send_email(user.email, subject, message)
            elif method == 'sms':
                self.send_sms(user.phone, message)
            elif method == 'push':
                self.send_push_notification(user.id, subject, message)
            
            logger.info(f"Price alert sent to user {user.id} via {method}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending price alert: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str):
        """Send email notification"""
        if not self.email_enabled:
            logger.warning("Email not configured. Skipping email notification.")
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_sms(self, phone: str, message: str):
        """Send SMS notification using Twilio"""
        if not self.sms_enabled:
            logger.warning("SMS not configured. Skipping SMS notification.")
            return False
        
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_phone = os.getenv('TWILIO_PHONE_NUMBER')
            
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(
                body=message,
                from_=from_phone,
                to=phone
            )
            
            logger.info(f"SMS sent to {phone}: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    def send_push_notification(self, user_id: int, title: str, body: str):
        """Send push notification using Firebase Cloud Messaging"""
        if not self.push_enabled:
            logger.warning("Push notifications not configured.")
            return False
        
        try:
            # TODO: Implement Firebase Cloud Messaging
            # This requires storing FCM tokens for each user
            logger.info(f"Push notification would be sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
    
    def send_booking_confirmation(self, user, booking):
        """Send booking confirmation to user"""
        try:
            station = booking.station
            
            subject = f"✅ CNG Booking Confirmed - Queue #{booking.queue_number}"
            message = f"""
            Your CNG booking has been confirmed!
            
            Station: {station.name}
            Address: {station.address}
            Queue Number: #{booking.queue_number}
            Estimated Arrival: {booking.estimated_arrival.strftime('%I:%M %p')}
            
            Please arrive on time to maintain your queue position.
            """
            
            self.send_email(user.email, subject, message)
            
            if user.phone:
                sms_message = f"CNG Booking Confirmed! Queue #{booking.queue_number} at {station.name}. Arrive by {booking.estimated_arrival.strftime('%I:%M %p')}"
                self.send_sms(user.phone, sms_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending booking confirmation: {e}")
            return False
    
    def send_new_station_alert(self, users: List, station):
        """Notify users about new station opening nearby"""
        try:
            subject = f"🆕 New CNG Station Opened: {station.name}"
            message = f"""
            A new CNG station has opened near you!
            
            Station: {station.name}
            Location: {station.address}
            Operator: {station.operator}
            
            Check it out on Smart CNG app!
            """
            
            for user in users:
                self.send_email(user.email, subject, message)
            
            logger.info(f"New station alerts sent to {len(users)} users")
            return True
            
        except Exception as e:
            logger.error(f"Error sending new station alerts: {e}")
            return False


# Singleton instance
notification_service = NotificationService()
