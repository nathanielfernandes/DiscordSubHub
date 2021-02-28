import os
import datetime
import pymongo
import motor.motor_asyncio


class Mongo_Youtube:
    def __init__(self):
        MONGOURI = os.environ.get("MONGOURI")
        self.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(MONGOURI))
        self.database = self.mongo["discordsubhub"]
        self.collection = self.database["youtube"]

    async def get_webhooks(self, channel_id):
        channel = await self.collection.find_one({"_id": channel_id})
        if channel is not None:
            return channel["webhooks"]

    async def get_channel(self, channel_id):
        return await self.collection.find_one({"_id": channel_id})

    async def exists(self, channel_id):
        channel = await self.get_channel(channel_id)
        return channel is not None

    async def delete_channel(self, channel_id):
        if not await self.get_channel(channel_id):
            return

        await self.collection.delete_one({"_id": channel_id})

    async def upsert_channel(self, channel_id):
        try:
            await self.collection.insert_one({"_id": channel_id, "webhooks": []})
        except pymongo.errors.DuplicateKeyError:
            return

    async def num_webhooks(self, channel_id):
        channel = await self.get_channel(channel_id)
        if channel is not None:
            return len(channel["webhooks"])
        else:
            return 0

    async def delete_webhook(self, channel_id, webhook):
        webhooks = await self.get_webhooks(channel_id)
        if webhooks is not None:
            if webhook in webhooks:
                webhooks.remove(webhook)
                await self.collection.update_one(
                    {"_id": channel_id}, {"$set": {"webhooks": webhooks}}
                )

    async def upsert_webhook(self, channel_id, webhook):
        webhooks = await self.get_webhooks(channel_id)
        if webhooks is not None:
            if webhook not in webhooks:
                webhooks.append(webhook)
                await self.collection.update_one(
                    {"_id": channel_id}, {"$set": {"webhooks": webhooks}}
                )

    async def webhook_exists(self, channel_id, webhook):
        webhooks = await self.get_webhooks(channel_id)
        if webhooks is not None:
            return webhook in webhooks
