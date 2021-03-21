import os
import aiohttp
from utils.mongo import *
from utils.parsing import *
from utils.capped_list import CappedList
from copy import copy


class Hub:
    """Handles the process of subscribing and unsubscribing webhooks to
       the database as well as pubsubhubhub.
    """

    def __init__(self):
        # connect to MongoDB
        self.db = Mongo_Youtube()
        self.pubsubhub_url = "https://pubsubhubbub.appspot.com/subscribe"

        # start an aiohttp clientsession
        self.sesion = aiohttp.ClientSession()

        # gets special tokens
        self.verify_token = os.environ.get("VERIFYTOKEN")
        self.api_token = os.environ.get("APITOKEN")

        self.recent_updates = CappedList(max_length=100)

    # -- Pointer Methods --
    async def GET(
        self,
        url: str,
        headers: dict = None,
        params: dict = None,
        data: dict = None,
        content: bool = False,
    ):
        """points to self.request, the request parameter always being "GET".
        """
        return await self.request(
            request="GET",
            url=url,
            headers=headers,
            params=params,
            data=data,
            content=content,
        )

    async def POST(
        self,
        url: str,
        headers: dict = None,
        params: dict = None,
        data: dict = None,
        json: dict = None,
    ):
        """points to self.request, the request parameter always being "POST".
        """
        return await self.request(
            request="POST",
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json,
        )

    # UNUSED
    # async def sub(self, webhook_url: str, channel_url: str):
    #     return await self.pubsubhub(webhook_url, channel_url, mode="subscribe")

    # async def unsub(self, webhook_url: str, channel_url: str):
    #     return await self.pubsubhub(webhook_url, channel_url, mode="unsubscribe")

    # -- Actual Methods --
    async def request(
        self,
        request: str,
        url: str,
        headers: dict = None,
        params: dict = None,
        data: dict = None,
        json: dict = None,
        content: bool = False,
    ):
        """performs asynchronous GET/POST requests and returns the response object.
        """
        if request == "GET":
            async with self.sesion.get(
                url=url, headers=headers, params=params, data=data
            ) as response:
                if content:
                    text = await response.text()
                    return response, text
                return response
        elif request == "POST":
            async with self.sesion.post(
                url=url, headers=headers, params=params, data=data, json=json
            ) as response:
                return response

    async def remove_webhook(self, channel_id: str, webhook_url: str):
        """removes a webhook from the database. Aditionally checks whether there are
           other webhooks that are still subscribed to that channel, if not it removes
           the channel from the database as well as unsubscribes discordsubhub from the
           channel.
        """
        # removes the webhook from the database
        await self.db.delete_webhook(channel_id, webhook_url)
        # check the remaining number of webhooks in the channel
        num_hooks = await self.db.num_webhooks(channel_id)
        if num_hooks == 0:
            # unsubscibe DiscordSubHub from the channel as well as delete the channel from
            # the data base
            data = pubsubhub_data(
                channel_id=channel_id,
                verify_token=self.verify_token,
                mode="unsubscribe",
            )
            await self.db.delete_channel(channel_id)
            await self.POST(self.pubsubhub_url, data=data)

    async def test(self, webhook_url: str):
        if webhook_url.startswith("https://discord.com/api/webhooks/"):
            response = await self.POST(
                url=webhook_url,
                headers={"Content-Type": "application/json"},
                json=webhook_body(
                    creator="DiscordSubHub Test",
                    video_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                ),
            )
            status = response.status
            if status == 204:
                return "Sent A Test Message"
            else:
                return "Invalid Webhook Url"
        else:
            return "Unsupported Webhook Url"

    async def pubsubhub(
        self, webhook_url: str, channel_url: str, mode: str = "subscribe"
    ) -> (str, int):
        """validates webhook_url and channel_url and subscribes/unsubscribes the webhook
           to the database and subscribes/unsubscribes DiscordSubHub to the channel.
        """
        # check to see if the urls follow the correct format
        if webhook_url.startswith(
            "https://discord.com/api/webhooks/"
        ) or webhook_url.startswith("https://discordapp.com/api/webhooks/"):
            if channel_url.startswith("https://www.youtube.com/"):
                if channel_url.startswith(
                    "https://www.youtube.com/user/"
                ) or channel_url.startswith("https://www.youtube.com/c/"):

                    channel, soup = await self.GET(channel_url, content=True)
                    channel_id = find_id(soup)
                    if channel_id is None:
                        return "Could Not Verify Webhook Url", 400

                    channel_url = f"https://www.youtube.com/channel/{channel_id}"
                else:
                    channel = await self.GET(channel_url)
                # makes a get request to check the validity of the urls based on their response statuses
                hook = await self.GET(webhook_url)

                hook = hook.status
                channel = channel.status
                if channel == 200:
                    if hook == 200:
                        # get the channel id from the url
                        channel_id = parse_channel_url(channel_url)
                        # check the database to see if the webhook aldready exists
                        webhook_exists = await self.db.webhook_exists(
                            channel_id, webhook_url
                        )

                        # get the data to POST into the correct form
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
                                return "Sucessfully Subscribed!", 201
                            else:
                                return "Aldready Subscribed", 200
                        else:
                            if webhook_exists:
                                await self.remove_webhook(channel_id, webhook_url)
                                return "Sucessfully Unsubscribed!", 201
                            else:
                                return "Aldready Unsubscribed", 200
                    else:
                        return "Could Not Verify Webhook Url", 400
                else:
                    return "Could Not Verify Channel Url", 400
            else:
                return "Unsupported Channel Url", 400
        else:
            return "Unsupported Webhook Url", 400

    async def dispatch_notification(self, xml_data):
        """Sends out the notification to all the webhooks subscribed to a channel via POSTs.
           If the webhook does not return a 204 representing that the message was sent, it
           will be automatically unsubscribed from the channel.
        """
        # parse the xml data into a useable dict
        data = parse_xml(xml_data)
        video_link = data.get("link")
        new = self.recent_updates.log(video_link.strip())
        print(video_link)
        print(new)
        if new:
            channel_id = data.get("channelId")
            creator = data.get("author")
            body = webhook_body(creator=creator, video_link=video_link)
            webhooks = await self.db.get_webhooks(channel_id)
            if webhooks is not None:
                for url in webhooks:
                    response = await self.POST(
                        url=url,
                        headers={"Content-Type": "application/json"},
                        json=body,
                    )
                    status = response.status
                    if status != 204:
                        await self.remove_webhook(channel_id, url)


# OLD:
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

