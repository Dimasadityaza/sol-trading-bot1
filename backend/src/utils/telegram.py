import asyncio
import httpx
from typing import Optional
from datetime import datetime

class TelegramBot:
    """Send notifications via Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": text,
                        "parse_mode": parse_mode
                    },
                    timeout=10.0
                )
                
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False
    
    async def notify_new_token(self, token_data: dict):
        """Notify about new token detected"""
        text = f"""
🎯 <b>New Token Detected!</b>

Token: {token_data.get('symbol', 'Unknown')}
Address: <code>{token_data.get('address', 'N/A')}</code>
Liquidity: {token_data.get('liquidity', 0)} SOL
Safety Score: {token_data.get('safety_score', 0)}/100

Platform: {token_data.get('platform', 'Unknown')}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(text)
    
    async def notify_trade_executed(self, trade_data: dict):
        """Notify about executed trade"""
        trade_type = trade_data.get('type', 'buy').upper()
        emoji = "🟢" if trade_type == "BUY" else "🔴"
        
        text = f"""
{emoji} <b>Trade Executed: {trade_type}</b>

Token: <code>{trade_data.get('token_address', 'N/A')}</code>
Amount: {trade_data.get('amount', 0)} SOL
Strategy: {trade_data.get('strategy', 'manual')}

Signature: <code>{trade_data.get('signature', 'N/A')}</code>
Explorer: {trade_data.get('explorer_url', 'N/A')}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(text)
    
    async def notify_profit_target(self, profit_data: dict):
        """Notify when profit target hit"""
        text = f"""
💰 <b>Profit Target Hit!</b>

Token: <code>{profit_data.get('token_address', 'N/A')}</code>
Profit: +{profit_data.get('profit', 0)} SOL ({profit_data.get('profit_percent', 0)}%)

Entry: {profit_data.get('entry_price', 0)}
Exit: {profit_data.get('exit_price', 0)}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(text)
    
    async def notify_stop_loss(self, loss_data: dict):
        """Notify when stop loss triggered"""
        text = f"""
⚠️ <b>Stop Loss Triggered</b>

Token: <code>{loss_data.get('token_address', 'N/A')}</code>
Loss: {loss_data.get('loss', 0)} SOL ({loss_data.get('loss_percent', 0)}%)

Entry: {loss_data.get('entry_price', 0)}
Exit: {loss_data.get('exit_price', 0)}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(text)
    
    async def notify_error(self, error_msg: str):
        """Notify about errors"""
        text = f"""
❌ <b>Error Occurred</b>

{error_msg}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await self.send_message(text)
    
    async def send_daily_summary(self, stats: dict):
        """Send daily trading summary"""
        pnl = stats.get('total_pnl', 0)
        pnl_emoji = "💰" if pnl >= 0 else "📉"
        
        text = f"""
{pnl_emoji} <b>Daily Summary</b>

Total PnL: {pnl} SOL
Win Rate: {stats.get('win_rate', 0)}%

Trades: {stats.get('total_trades', 0)}
├─ Wins: {stats.get('wins', 0)}
└─ Losses: {stats.get('losses', 0)}

Best Trade: +{stats.get('best_trade', 0)} SOL
Worst Trade: {stats.get('worst_trade', 0)} SOL

Date: {datetime.now().strftime('%Y-%m-%d')}
"""
        await self.send_message(text)

# Singleton instance
_telegram_bot: Optional[TelegramBot] = None

def get_telegram_bot(bot_token: str = None, chat_id: str = None) -> Optional[TelegramBot]:
    """Get or create Telegram bot instance"""
    global _telegram_bot
    
    if bot_token and chat_id:
        _telegram_bot = TelegramBot(bot_token, chat_id)
    
    return _telegram_bot

async def send_notification(notification_type: str, data: dict):
    """Send notification if Telegram is configured"""
    bot = get_telegram_bot()
    
    if not bot:
        return False
    
    try:
        if notification_type == "new_token":
            await bot.notify_new_token(data)
        elif notification_type == "trade":
            await bot.notify_trade_executed(data)
        elif notification_type == "profit_target":
            await bot.notify_profit_target(data)
        elif notification_type == "stop_loss":
            await bot.notify_stop_loss(data)
        elif notification_type == "error":
            await bot.notify_error(data.get("message", "Unknown error"))
        elif notification_type == "daily_summary":
            await bot.send_daily_summary(data)
        
        return True
    except Exception as e:
        print(f"Notification failed: {e}")
        return False
