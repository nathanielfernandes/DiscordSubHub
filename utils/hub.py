import os
import aiohttp
from utils.mongo import *
from utils.parsing import *
from copy import copy


class Hub:
    def __init__(self):
        self.db = Mongo_Youtube()
        self.pubsubhub_url = "https://pubsubhubbub.appspot.com/subscribe"
        self.sesion = aiohttp.ClientSession()
        self.verify_token = os.environ.get("VERIFYTOKEN")
        self.api_token = os.environ.get("APITOKEN")

    # -- Pointer Methods --
    async def GET(
        self, url: str, headers: dict = None, params: dict = None, data: dict = None,
    ):
        return await self.request(
            request="GET", url=url, headers=headers, params=params, data=data
        )

    async def POST(
        self,
        url: str,
        headers: dict = None,
        params: dict = None,
        data: dict = None,
        json: dict = None,
    ):
        return await self.request(
            request="POST",
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json,
        )

    async def sub(self, webhook_url: str, channel_url: str):
        return await self.pubsubhub(webhook_url, channel_url, mode="subscribe")

    async def unsub(self, webhook_url: str, channel_url: str):
        return await self.pubsubhub(webhook_url, channel_url, mode="unsubscribe")

    # -- Actual Methods --
    async def request(
        self,
        request: str,
        url: str,
        headers: dict = None,
        params: dict = None,
        data: dict = None,
        json: dict = None,
    ):
        if request == "GET":
            async with self.sesion.get(
                url=url, headers=headers, params=params, data=data
            ) as response:
                return response
        elif request == "POST":
            async with self.sesion.post(
                url=url, headers=headers, params=params, data=data, json=json
            ) as response:
                return response

    async def remove_webhook(self, channel_id: str, webhook_url: str):
        await self.db.delete_webhook(channel_id, webhook_url)
        num_hooks = await self.db.num_webhooks(channel_id)
        if num_hooks == 0:
            data = pubsubhub_data(
                channel_id=channel_id,
                verify_token=self.verify_token,
                mode="unsubscribe",
            )
            await self.db.delete_channel(channel_id)
            await self.POST(self.pubsubhub_url, data=data)

    async def pubsubhub(
        self, webhook_url: str, channel_url: str, mode: str = "subscribe"
    ):
        if channel_url.startswith("https://www.youtube.com/channel/UC"):
            if webhook_url.startswith("https://discord.com/api/webhooks/"):
                hook = await self.GET(webhook_url)
                channel = await self.GET(channel_url)
                hook = hook.status
                channel = channel.status
                if channel == 200:
                    if hook == 200:
                        channel_id = parse_channel_url(channel_url)
                        webhook_exists = await self.db.webhook_exists(
                            channel_id, webhook_url
                        )
                        data = pubsubhub_data(
                            channel_id=channel_id,
                            verify_token=self.verify_token,
                            mode=mode,
                        )
                        if mode == "subscribe":
                            if not webhook_exists:
                                await self.POST(self.pubsubhub_url, data=data)
                                await self.db.upsert_channel(channel_id)
                                await self.db.upsert_webhook(channel_id, webhook_url)
                                return True, "Sucessfully Subscribed!"
                            else:
                                return True, "Aldready Subscribed"
                        else:
                            if webhook_exists:
                                await self.remove_webhook(channel_id, webhook_url)
                                return True, "Sucessfully Unsubscribed!"
                            else:
                                return True, "Aldready Unsubscribed"
                    else:
                        return False, "Invalid Webhook Url"
                else:
                    return False, "Invalid Channel Url"
            else:
                return False, "Invalid Webhook Url"
        else:
            return False, "Invalid Channel Url"

    async def dispatch_notification(self, xml_data):
        data = parse_xml(xml_data)
        channel_id = data.get("channelId")
        video_link = data.get("link")
        creator = data.get("author")
        body = webhook_body(creator=creator, video_link=video_link)
        webhooks = await self.db.get_webhooks(channel_id)
        if webhooks is not None:
            for url in webhooks:
                response = await self.POST(
                    url=url, headers={"Content-Type": "application/json"}, json=body,
                )
                status = response.status
                if status != 204:
                    await self.remove_webhook(channel_id, url)


# if channel_url.startswith(
#     "https://www.youtube.com/channel/"
# ) and webhook_url.startswith("https://discord.com/api/webhooks/"):

#     hook = await self.GET(webhook_url)
#     channel = await self.GET(channel_url)
#     hook = hook.status
#     channel = channel.status

#     if (hook == 200) and (channel == 200):
#         channel_id = parse_channel_url(channel_url)
#         exists = await self.db.exists(channel_id)
#         data = pubsubhub_data(
#             channel_id=channel_id, verify_token=self.verify_token, mode=mode,
#         )
#         if mode == "subscribe":
#             if not exists:
#                 await self.POST(self.pubsubhub_url, data=data)

#             await self.db.upsert_channel(channel_id)
#             await self.db.upsert_webhook(channel_id, webhook_url)
#         else:
#             await self.remove_webhook(channel_id, webhook_url)

#         return True
# else:
#     return False

