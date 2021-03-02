import os
import aiohttp
import jinja2
import aiohttp_jinja2
from aiohttp import web
from utils.hub import Hub
from utils.ratelimiter import RateLimiter

import datetime


async def web_app():
    hub = Hub()
    limit = RateLimiter(rate=5)
    app = web.Application()
    routes = web.RouteTableDef()
    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
    )

    @routes.get("/")
    @aiohttp_jinja2.template("index.html")
    async def index(request):
        context = {}
        return context

    @routes.post("/form/{mode}")
    @aiohttp_jinja2.template("index.html")
    async def form_action(request):
        mode = request.match_info["mode"]
        form = await request.post()
        webhook_url, channel_url = form.get("webhook_url"), form.get("channel_url")
        limited = await limit.check_rate(webhook_url)

        if limited:
            success, info = await hub.pubsubhub(
                webhook_url=webhook_url, channel_url=channel_url, mode=mode
            )
        else:
            info = "Slow Down! (5s)"

        return {
            "info": info,
            "prev_webhook_url": webhook_url,
            "prev_channel_url": channel_url,
        }

    @routes.get("/coffee")
    async def wake_up(request):
        return web.Response(text="thanks for the coffee :)")

    @routes.get("/pubsubhubbub")
    async def verify_subscription(request):
        print("PubSubHubBub verification")
        verify_token = request.query.get("hub.verify_token")
        challenge = request.query.get("hub.challenge")
        if (verify_token == hub.verify_token) and challenge:
            return web.Response(body=challenge)
        return web.Response()

    @routes.post("/pubsubhubbub")
    async def subscription_update(request):
        print("Channel Upload")
        xml_data = await request.read()
        await hub.dispatch_notification(xml_data)
        return web.Response()

    @routes.post("/subscribe")
    async def subscribe(request):
        if request.headers is not None:
            token = request.headers.get("token")
            webhook_url = request.headers.get("webhook_url")
            channel_url = request.headers.get("channel_url")
            mode = request.headers.get("mode", "subscribe")

            if webhook_url and channel_url:
                limited = await limit.check_rate(
                    webhook=webhook_url, token=token == hub.api_token
                )

                if limited:
                    success, info = await hub.pubsubhub(
                        webhook_url=webhook_url, channel_url=channel_url, mode=mode
                    )
                    if success:
                        return web.Response(text=f"Successfully {mode.title()}d")
                else:
                    return web.Response(text="slowdown!", status=429)

            return web.Response(
                text="Invalid 'webhook_url' and/or 'channel_url' header(s)", status=400,
            )
        else:
            return web.Response(
                text="Missing 'webhook_url' and/or 'channel_url' header(s)", status=400,
            )

    app.add_routes(routes)
    return app
