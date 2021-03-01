import os
import aiohttp

import jinja2
import aiohttp_jinja2
from aiohttp import web
from utils.hub import Hub
from utils.ratelimiter import RateLimiter


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
        context = {"name": ":)"}
        return context

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
            limited = await limit.check_rate(
                ip=request.remote, token=token == hub.api_token
            )
            if limited:
                webhook_url = request.headers.get("webhook_url")
                channel_url = request.headers.get("channel_url")
                mode = request.headers.get("mode", "subscribe")

                if webhook_url and channel_url:
                    success = await hub.pubsubhub(
                        webhook_url=webhook_url, channel_url=channel_url, mode=mode
                    )
                    if success:
                        return web.Response(text=f"Successfully {mode.title()}ed")
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    web.run_app(web_app(), port=port)
