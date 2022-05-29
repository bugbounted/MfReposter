import asyncio
import logging

import constants
from models.channel import Channel
import utils.asyncio
import jobs

from pyrogram import Client
from configurator import PyrogramConfig, DatabaseConfig, load_config
from tortoise import Tortoise


async def initialize_database(config: DatabaseConfig):
    """
    Initializes database
    """
    await Tortoise.init(
        db_url=config.database_url,
        modules={
            "models": [
                "models"
            ],
        }
    )

    await Tortoise.generate_schemas()


async def client_builder(config: PyrogramConfig) -> Client:
    """
    Returns an initialized client
    :param PyrogramConfig config: A configuration-object
    :rtype: Client
    :return: Initialized client
    """

    client = Client(
        name="pyrogram",
        api_hash=config.api_hash,
        api_id=config.api_id,
    )

    await client.start()

    return client


async def main():
    """Heart of project"""

    config = load_config(constants.CONFIG_FILENAME)
    # client = await client_builder(config.pyrogram)

    await initialize_database(config.database)

    ch = await Channel.get_or_create(
        identifier=1,
        defaults={
            "last_post_id": 0,
        }
    )

    tasks = [
        utils.asyncio.schedule(jobs.handle_updates, config.scheduler.update_interval, client, config.channels)
    ]

    # await asyncio.wait(tasks)
    print("OK")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
