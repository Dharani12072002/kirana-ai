import os
import re

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.agent.agent import KiranaAgent
from app.services.processed_update_service import ProcessedUpdateService

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Keep one agent per Telegram chat.
agents = {}


def get_agent(chat_id: int) -> KiranaAgent:
    """
    Return the agent associated with this Telegram chat.
    """

    if chat_id not in agents:
        agents[chat_id] = KiranaAgent()

    return agents[chat_id]


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handle /start.
    """

    if update.message is None:
        return

    await update.message.reply_text(
        "👋 Welcome to KiranaAI!\n\n"
        "I can help you manage your store through natural language.\n\n"
        "For example:\n"
        "• Add 10 kg rice to stock\n"
        "• Create a bill for Ravi\n"
        "• How much rice is left?\n"
        "• Today's sales?\n"
        "• Check Ravi's khata balance\n"
        "• Send Bill 13 as a PDF\n"
        "• Make a sales analysis deck for today"
    )


async def new_chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Start a fresh AI conversation for this Telegram chat.

    Conversation state is cleared, but store data remains
    in the database.
    """

    if update.effective_chat is None:
        return

    if update.message is None:
        return

    chat_id = update.effective_chat.id

    # Clear only the conversation-level agent state.
    agents[chat_id] = KiranaAgent()

    await update.message.reply_text(
        "🆕 New chat started.\n\n"
        "Your conversation has been cleared. "
        "Your store data remains in the database."
    )

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message is None:
        return

    if update.effective_chat is None:
        return

    # Telegram assigns a unique update_id to every update.
    update_id = update.update_id

    # Idempotency protection.
    #
    # - COMPLETED updates are ignored.
    # - PENDING updates are treated as already being processed.
    # - FAILED updates can be retried.
    # - New updates are marked PENDING.
    idempotency_service = ProcessedUpdateService()

    should_process = idempotency_service.reserve_update(
        update_id
    )

    if not should_process:
        print(
            f"Duplicate or already-processing Telegram update "
            f"ignored: {update_id}"
        )
        return

    chat_id = update.effective_chat.id
    user_message = update.message.text

    if not user_message:
        idempotency_service.mark_failed(update_id)
        return

    agent = get_agent(chat_id)

    try:
        response = agent.run(user_message)

        file_match = re.search(
            r"(generated[/\\](?:invoices|reports)[/\\][^\s*`]+?\.(?:pdf|pptx))",
            response,
            re.IGNORECASE,
        )

        if file_match:
            file_path = file_match.group(1).replace(
                "\\",
                "/",
            )

            if os.path.exists(file_path):
                extension = os.path.splitext(
                    file_path
                )[1].lower()

                if extension == ".pdf":
                    caption = "📄 GST Invoice"
                elif extension == ".pptx":
                    caption = "📊 KiranaAI Sales Analysis"
                else:
                    caption = "📎 Generated document"

                await update.message.reply_document(
                    document=file_path,
                    caption=caption,
                )

                if extension == ".pdf":
                    await update.message.reply_text(
                        "✅ GST invoice generated and sent successfully."
                    )

                elif extension == ".pptx":
                    await update.message.reply_text(
                        "✅ Sales analysis presentation generated and sent successfully."
                    )

                # Mark the update completed only after
                # the Telegram response was successfully sent.
                idempotency_service.mark_completed(
                    update_id
                )

                return

        await update.message.reply_text(response)

        # Normal text response completed successfully.
        idempotency_service.mark_completed(
            update_id
        )

    except Exception as error:
        print(
            "Telegram agent error:",
            error,
        )

        # Allow this Telegram update to be retried
        # after a processing failure.
        idempotency_service.mark_failed(
            update_id
        )

        await update.message.reply_text(
            "❌ Something went wrong while processing your request. "
            "Please try again."
        )

def main():

    if not TELEGRAM_BOT_TOKEN:

        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not configured in .env"
        )

    # -------------------------------------------------------------
    # Create Telegram application
    # -------------------------------------------------------------
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    # -------------------------------------------------------------
    # Command handlers
    # -------------------------------------------------------------
    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        CommandHandler(
            "new",
            new_chat,
        )
    )

    # -------------------------------------------------------------
    # Normal text messages
    # -------------------------------------------------------------
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    print(
        "KiranaAI Telegram bot started."
    )

    # -------------------------------------------------------------
    # Start polling Telegram
    # -------------------------------------------------------------
    application.run_polling()


if __name__ == "__main__":
    main()