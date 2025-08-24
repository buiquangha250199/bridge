from app import db
from datetime import datetime
from sqlalchemy import Text

class WebhookLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    source = db.Column(db.String(50), nullable=False)  # 'tradingview'
    message_content = db.Column(Text, nullable=False)
    telegram_status = db.Column(db.String(20), nullable=False)  # 'sent', 'failed', 'pending'
    error_message = db.Column(Text, nullable=True)
    telegram_channel = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<WebhookLog {self.id}: {self.source} -> {self.telegram_status}>'

class TelegramMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    webhook_log_id = db.Column(db.Integer, db.ForeignKey('webhook_log.id'), nullable=False)
    telegram_message_id = db.Column(db.Integer, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    retry_count = db.Column(db.Integer, default=0)
    
    webhook_log = db.relationship('WebhookLog', backref=db.backref('telegram_messages', lazy=True))
