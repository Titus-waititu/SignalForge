"""
Telegram Alert Module
Sends notifications via Telegram Bot API
"""

from typing import Dict, Any, List
import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError
from config import config

logger = logging.getLogger(__name__)


class TelegramAlerter:
    """Send alerts via Telegram"""
    
    def __init__(self, token: str = None, chat_id: str = None):
        """
        Initialize Telegram alerter
        
        Args:
            token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
        """
        self.token = token or config.TELEGRAM_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.bot = None
        self.max_retries = 3
        
        if self.token:
            self.bot = Bot(token=self.token)
            logger.info("Telegram alerter initialized")
        else:
            logger.warning("Telegram token not configured, alerts disabled")
    
    async def send_job_alert(self, job: Dict[str, Any]) -> bool:
        """
        Send job alert to Telegram
        
        Args:
            job: Job dictionary
            
        Returns:
            True if sent successfully
        """
        if not self.bot or not self.chat_id:
            logger.warning("Telegram not configured, skipping alert")
            return False
        
        try:
            message = self._format_job_message(job)
            
            for attempt in range(self.max_retries):
                try:
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=message,
                        parse_mode="HTML",
                        disable_web_page_preview=False
                    )
                    logger.info(f"Sent Telegram alert for job {job.get('id')}")
                    return True
                    
                except TelegramError as e:
                    logger.error(f"Telegram error (attempt {attempt + 1}/{self.max_retries}): {e}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    async def send_bulk_alerts(self, jobs: List[Dict[str, Any]]) -> int:
        """
        Send multiple job alerts
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Number of successfully sent alerts
        """
        if not jobs:
            return 0
        
        sent_count = 0
        
        for job in jobs:
            success = await self.send_job_alert(job)
            if success:
                sent_count += 1
            
            # Rate limiting - avoid hitting Telegram limits
            await asyncio.sleep(0.5)
        
        logger.info(f"Sent {sent_count}/{len(jobs)} Telegram alerts")
        return sent_count
    
    def _format_job_message(self, job: Dict[str, Any]) -> str:
        """Format job data as Telegram message"""
        score = job.get("score", 0)
        title = job.get("title", "Unknown")
        company = job.get("company", "Unknown")
        location = job.get("location", "Unknown")
        url = job.get("url", "")
        stack = job.get("stack", "")
        
        # Format stack
        if isinstance(stack, list):
            stack_str = ", ".join(stack)
        elif isinstance(stack, str):
            stack_str = stack.replace(",", ", ")
        else:
            stack_str = "N/A"
        
        # Build message
        message = f"""
🔥 <b>SignalForge Alert</b> (Score: {score})

<b>Position:</b> {title}
<b>Company:</b> {company}
<b>Location:</b> {location}
<b>Stack:</b> {stack_str}

<b>Apply:</b> {url}
"""
        
        return message.strip()
    
    async def send_custom_message(self, text: str) -> bool:
        """
        Send custom message to Telegram
        
        Args:
            text: Message text
            
        Returns:
            True if sent successfully
        """
        if not self.bot or not self.chat_id:
            logger.warning("Telegram not configured")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode="HTML"
            )
            logger.info("Sent custom Telegram message")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send custom message: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Test Telegram connection
        
        Returns:
            True if connection is working
        """
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Telegram bot connected: @{bot_info.username}")
            return True
            
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False


# Synchronous wrapper functions for easier use
def send_job_alert_sync(job: Dict[str, Any]) -> bool:
    """Synchronous wrapper for sending job alert"""
    alerter = TelegramAlerter()
    return asyncio.run(alerter.send_job_alert(job))


def send_bulk_alerts_sync(jobs: List[Dict[str, Any]]) -> int:
    """Synchronous wrapper for sending bulk alerts"""
    alerter = TelegramAlerter()
    return asyncio.run(alerter.send_bulk_alerts(jobs))
