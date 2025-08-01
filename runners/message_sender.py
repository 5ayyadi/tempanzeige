#!/usr/bin/env python3
"""Message sender runner for sending offers to users."""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

from telegram import Bot
from telegram.error import TelegramError

from core.config import config
from core.mongo_client import MongoClientManager
from core.constants import MSG_OFFER_TEMPLATE, TELEGRAM_MAX_MESSAGE_LENGTH
from models.offer import Offer
from models.preferences import UserPreferences

logger = logging.getLogger(__name__)

class MessageSender:
    def __init__(self):
        self.mongo_client = MongoClientManager()
        self.bot = Bot(token=config.BOT_TOKEN)
        
    def _format_offer_message(self, offer: Offer) -> str:
        """Format offer data into message template."""
        # Clean description text (Markdown doesn't need HTML escaping)
        description = offer.description.strip()[:200] + "..." if len(offer.description) > 200 else offer.description.strip()
        
        return MSG_OFFER_TEMPLATE.format(
            description=description,
            address=offer.address,
            date=offer.offer_date,
            link=offer.link or "https://www.kleinanzeigen.de"
        )
    
    def _matches_preference(self, offer: Offer, preference) -> bool:
        """Check if offer matches user preference criteria."""
        # Check location match
        if preference.location.city_id and offer.location.city_id != preference.location.city_id:
            return False
        if preference.location.state_id and offer.location.state_id != preference.location.state_id:
            return False
            
        # Check category match
        if preference.category.category_id and offer.category.category_id != preference.category.category_id:
            return False
        if preference.category.subcategory_id and offer.category.subcategory_id != preference.category.subcategory_id:
            return False
            
        # Check price range
        if preference.price.price_to > 0 and offer.price > preference.price.price_to:
            return False
        if preference.price.price_from > 0 and offer.price < preference.price.price_from:
            return False
            
        # Check time window
        offer_time = datetime.now(timezone.utc) - timedelta(seconds=preference.time_window)
        if offer.created_at < offer_time:
            return False
            
        return True
    
    async def _send_offer_to_user(self, user_id: int, offer: Offer) -> bool:
        """Send a single offer to a user."""
        try:
            message = self._format_offer_message(offer)
            
            # Send photo if available
            if offer.photos:
                try:
                    await self.bot.send_photo(
                        chat_id=user_id,
                        photo=offer.photos[0],
                        caption=offer.title
                    )
                except TelegramError as e:
                    logger.warning(f"Failed to send photo to user {user_id}: {e}")
                    # Continue with text message
            
            # Send message
            if len(message) > TELEGRAM_MAX_MESSAGE_LENGTH:
                message = message[:TELEGRAM_MAX_MESSAGE_LENGTH-3] + "..."
                
            await self.bot.send_message(
                chat_id=user_id,
                text=f"**{offer.title}**\n\n{message}",
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            logger.info(f"Successfully sent offer {offer.id} to user {user_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to send offer {offer.id} to user {user_id}: {e}")
            return False
    
    def _mark_offer_as_sent(self, user_id: int, preference_id: str, offer_id: str):
        """Mark offer as sent for a user's preference."""
        try:
            self.mongo_client.user_preferences_collection.update_one(
                {"user_id": user_id, "preferences._id": preference_id},
                {"$addToSet": {"preferences.$.sent_offers": offer_id}}
            )
        except Exception as e:
            logger.error(f"Failed to mark offer {offer_id} as sent for user {user_id}: {e}")
    
    async def send_offers_to_users(self):
        """Main method to send offers to all users."""
        logger.info("Starting message sender process")
        
        try:
            # Get all users with preferences
            all_user_preferences = self.mongo_client.get_all_user_preferences()
            logger.info(f"Found {len(all_user_preferences)} users with preferences")
            
            total_sent = 0
            total_users_processed = 0
            
            for user_prefs in all_user_preferences:
                user_id = user_prefs.user_id
                logger.info(f"Processing user {user_id} with {len(user_prefs.preferences)} preferences")
                
                user_sent_count = 0
                
                for preference in user_prefs.preferences:
                    try:
                        # Get offers matching this preference
                        filter_criteria = {}
                        
                        # Build filter based on preference
                        if preference.location.city_id:
                            filter_criteria["location.city_id"] = preference.location.city_id
                        elif preference.location.state_id:
                            filter_criteria["location.state_id"] = preference.location.state_id
                            
                        if preference.category.category_id:
                            filter_criteria["category.category_id"] = preference.category.category_id
                        if preference.category.subcategory_id:
                            filter_criteria["category.subcategory_id"] = preference.category.subcategory_id
                        
                        # Time window filter
                        time_threshold = datetime.now(timezone.utc) - timedelta(seconds=preference.time_window)
                        filter_criteria["created_at"] = {"$gte": time_threshold}
                        
                        # Exclude already sent offers
                        sent_offers = getattr(preference, 'sent_offers', [])
                        if sent_offers:
                            filter_criteria["_id"] = {"$nin": sent_offers}
                        
                        # Get matching offers
                        offers = self.mongo_client.get_offers(filter_criteria)
                        logger.info(f"Found {len(offers)} new offers for user {user_id} preference")
                        
                        # Send offers to user
                        for offer in offers:
                            if self._matches_preference(offer, preference):
                                success = await self._send_offer_to_user(user_id, offer)
                                if success:
                                    self._mark_offer_as_sent(user_id, preference._id, offer.id)
                                    user_sent_count += 1
                                    total_sent += 1
                                    
                                    # Small delay to avoid rate limiting
                                    await asyncio.sleep(0.5)
                                    
                    except Exception as e:
                        logger.error(f"Error processing preference for user {user_id}: {e}")
                        continue
                
                logger.info(f"Sent {user_sent_count} offers to user {user_id}")
                total_users_processed += 1
            
            logger.info(f"Message sender completed: processed {total_users_processed} users, sent {total_sent} total offers")
                    
        except Exception as e:
            logger.error(f"Error in send_offers_to_users: {e}")
            raise

def main():
    """Main entry point for the message sender."""
    logging.basicConfig(
        format=config.LOG_FORMAT,
        level=getattr(logging, config.LOG_LEVEL)
    )
    
    logger.info("Starting message sender runner")
    
    sender = MessageSender()
    
    try:
        asyncio.run(sender.send_offers_to_users())
        logger.info("Message sender completed successfully")
    except Exception as e:
        logger.error(f"Message sender failed: {e}")
        raise

if __name__ == "__main__":
    main()
