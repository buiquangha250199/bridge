import os
import requests
import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID', '')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_message(self, message: str, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to Telegram channel
        
        Args:
            message: The message to send
            channel_id: Optional channel ID, defaults to configured channel
            
        Returns:
            Dict containing success status and response data
        """
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
            return {
                'success': False,
                'error': 'Bot token not configured'
            }
            
        target_channel = channel_id or self.channel_id
        if not target_channel:
            logger.error("TELEGRAM_CHANNEL_ID environment variable not set and no channel provided")
            return {
                'success': False,
                'error': 'Channel ID not configured'
            }
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': target_channel,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('ok'):
                logger.info(f"Message sent successfully to {target_channel}")
                return {
                    'success': True,
                    'message_id': response_data.get('result', {}).get('message_id'),
                    'response': response_data
                }
            else:
                error_msg = response_data.get('description', 'Unknown error')
                logger.error(f"Failed to send message: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'response': response_data
                }
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return {
                'success': False,
                'error': f'Request failed: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def format_tradingview_message(self, alert_data: Dict[str, Any]) -> str:
        """
        Format TradingView alert data into a readable Telegram message
        
        Args:
            alert_data: The alert data from TradingView
            
        Returns:
            Formatted message string
        """
        try:
            # Extract common TradingView alert fields
            symbol = alert_data.get('ticker', 'Unknown')
            action = alert_data.get('action', 'Alert')
            price = alert_data.get('price', 'N/A')
            time = alert_data.get('time', 'N/A')
            message = alert_data.get('message', '')
            
            # Create formatted message
            formatted_msg = f"🚨 *TradingView Alert*\n\n"
            formatted_msg += f"📈 *Symbol:* {symbol}\n"
            formatted_msg += f"⚡ *Action:* {action}\n"
            formatted_msg += f"💰 *Price:* {price}\n"
            formatted_msg += f"🕐 *Time:* {time}\n"
            
            if message:
                formatted_msg += f"\n📝 *Message:*\n{message}"
            
            return formatted_msg
            
        except Exception as e:
            logger.error(f"Error formatting message: {str(e)}")
            # Fallback to raw JSON if formatting fails
            return f"🚨 *TradingView Alert*\n\n```json\n{json.dumps(alert_data, indent=2)}\n```"

# Global instance
telegram_service = TelegramService()
