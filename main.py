import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiohttp import ClientTimeout
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from feed_orchestration import FeedOrchestration
from requests_readers import RequestReaderFactory
from ai_clients import AIClientFactory
from transformers import TransformerFactory
from exceptions.parser_exceptions import MindFeedAIException
from config import CONFIG
from logger.logger import setup_logging

logger = logging.getLogger(__name__)


def _build_app():
    try:
        session = AiohttpSession(timeout=ClientTimeout(total=60))
        bot = Bot(token=CONFIG.token, session=session)
        reader = RequestReaderFactory.get_reader(reader_type=CONFIG.request_reader, yaml_path=CONFIG.yaml_path)
        ai_client = AIClientFactory.get_ai_client(client_type=CONFIG.ai_client)
        transformer = TransformerFactory.get_transformer(transformer_type=CONFIG.transformer)
        orchestrator = FeedOrchestration(
            article_count=CONFIG.article_count,
            request_reader=reader,
            ai_client=ai_client,
            transformer=transformer,
        )
        return bot, orchestrator
    except Exception:
        logger.exception('Failed to initialise application components.')
        sys.exit(1)


bot, orchestrator = _build_app()
dp = Dispatcher()
chat_id = CONFIG.chat_id


async def send_scheduled_message():
    logger.info('Scheduled digest run started.')
    try:
        article_str = await orchestrator.build_digest()
    except MindFeedAIException:
        logger.exception('Digest build failed — skipping this scheduled run.')
        return
    except Exception:
        logger.exception('Unexpected error during digest build — skipping this scheduled run.')
        return

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=article_str,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        logger.info('Telegram message sent successfully to chat_id=%s.', chat_id)
    except TelegramAPIError:
        logger.exception('Failed to send Telegram message.')


async def main():
    setup_logging()
    logger.info('Application starting.')

    scheduler = AsyncIOScheduler()
    schedule = CONFIG.schedule
    if schedule.mode == 'daily':
        trigger_kwargs = {'hour': schedule.hour, 'minute': schedule.minute}
    elif schedule.mode == 'weekly':
        trigger_kwargs = {'day_of_week': schedule.day_of_week, 'hour': schedule.hour, 'minute': schedule.minute}
    else:  # multi_weekly
        trigger_kwargs = {'day_of_week': ','.join(map(str, schedule.days_of_week)), 'hour': schedule.hour, 'minute': schedule.minute}

    scheduler.add_job(send_scheduled_message, trigger='cron', **trigger_kwargs)
    scheduler.start()
    logger.info('Scheduler configured: mode=%s, hour=%s, minute=%s.', schedule.mode, schedule.hour, schedule.minute)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
