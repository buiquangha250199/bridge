import json
import logging
from datetime import datetime, timedelta
from flask import request, jsonify, render_template, flash, redirect, url_for
from app import app, db
from models import WebhookLog, TelegramMessage
from telegram_service import telegram_service

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main dashboard showing recent webhook activity"""
    try:
        # Get recent webhook logs
        recent_logs = WebhookLog.query.order_by(WebhookLog.timestamp.desc()).limit(10).all()
        
        # Get statistics
        total_webhooks = WebhookLog.query.count()
        successful_sends = WebhookLog.query.filter_by(telegram_status='sent').count()
        failed_sends = WebhookLog.query.filter_by(telegram_status='failed').count()
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_activity = WebhookLog.query.filter(WebhookLog.timestamp >= yesterday).count()
        
        stats = {
            'total_webhooks': total_webhooks,
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'recent_activity': recent_activity,
            'success_rate': round((successful_sends / total_webhooks * 100) if total_webhooks > 0 else 0, 1)
        }
        
        return render_template('index.html', logs=recent_logs, stats=stats, telegram_service=telegram_service)
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        flash(f"Error loading dashboard: {str(e)}", 'danger')
        return render_template('index.html', logs=[], stats={}, telegram_service=telegram_service)

@app.route('/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    """Endpoint to receive TradingView alerts"""
    try:
        # Log the incoming request
        logger.info("Received TradingView webhook")
        
        # Get the JSON data
        if request.is_json:
            alert_data = request.get_json()
        else:
            # Try to parse as form data or plain text
            alert_data = {
                'message': request.get_data(as_text=True),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        logger.info(f"Alert data: {alert_data}")
        
        # Create webhook log entry
        webhook_log = WebhookLog(
            source='tradingview',
            message_content=json.dumps(alert_data),
            telegram_status='pending',
            telegram_channel=telegram_service.channel_id
        )
        db.session.add(webhook_log)
        db.session.commit()
        
        # Format and send message to Telegram
        formatted_message = telegram_service.format_tradingview_message(alert_data)
        result = telegram_service.send_message(formatted_message)
        
        # Update webhook log with result
        if result['success']:
            webhook_log.telegram_status = 'sent'
            
            # Create telegram message record
            telegram_msg = TelegramMessage(
                webhook_log_id=webhook_log.id,
                telegram_message_id=result.get('message_id'),
                sent_at=datetime.utcnow()
            )
            db.session.add(telegram_msg)
            
            logger.info(f"Successfully forwarded alert to Telegram")
        else:
            webhook_log.telegram_status = 'failed'
            webhook_log.error_message = result.get('error', 'Unknown error')
            logger.error(f"Failed to send to Telegram: {result.get('error')}")
        
        db.session.commit()
        
        return jsonify({
            'status': 'success' if result['success'] else 'error',
            'message': 'Alert processed',
            'telegram_sent': result['success'],
            'error': result.get('error') if not result['success'] else None
        }), 200 if result['success'] else 500
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        
        # Try to update webhook log with error
        try:
            if 'webhook_log' in locals():
                webhook_log.telegram_status = 'failed'
                webhook_log.error_message = str(e)
                db.session.commit()
        except:
            pass
            
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'error': str(e)
        }), 500

@app.route('/logs')
def logs():
    """View all webhook logs with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        logs_pagination = WebhookLog.query.order_by(WebhookLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('logs.html', logs=logs_pagination.items, pagination=logs_pagination)
        
    except Exception as e:
        logger.error(f"Error loading logs: {str(e)}")
        flash(f"Error loading logs: {str(e)}", 'danger')
        return render_template('logs.html', logs=[], pagination=None)

@app.route('/test-telegram', methods=['POST'])
def test_telegram():
    """Test endpoint to verify Telegram integration"""
    try:
        test_message = "🧪 Test message from TradingView Webhook Service\n\nIf you receive this, the integration is working correctly!"
        result = telegram_service.send_message(test_message)
        
        if result['success']:
            flash('Test message sent successfully to Telegram!', 'success')
        else:
            flash(f'Failed to send test message: {result.get("error")}', 'danger')
            
    except Exception as e:
        logger.error(f"Error testing Telegram: {str(e)}")
        flash(f'Error testing Telegram: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'telegram_configured': bool(telegram_service.bot_token and telegram_service.channel_id)
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500
