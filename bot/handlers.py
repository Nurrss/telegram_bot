"""Message handlers for the bot."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n\n"
        f"I'm a simple echo bot. Send me any message and I'll echo it back to you!\n\n"
        f"Commands:\n"
        f"/start - Show this welcome message\n"
        f"/help - Show help information"
    )
    logger.info(f"User {user.id} ({user.username}) started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    await update.message.reply_text(
        "📖 Help Information\n\n"
        "This is an echo bot. Whatever message you send, I'll send it right back!\n\n"
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )


async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    user = update.effective_user
    message_text = update.message.text

    logger.info(f"Echoing message from user {user.id} ({user.username}): {message_text}")

    # Echo the message back
    await update.message.reply_text(message_text)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")
