import os
import aiohttp
from aiohttp import web
from hub import Hub
from ratelimiter import RateLimiter


async def web_app():
    hub = Hub()
    limit = RateLimiter(rate=5)
    app = web.Application()
    routes = web.RouteTableDef()

    @routes.get("/coffee")
    async def wake_up(request):
        return web.Response(text="thankyou :)")

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
            text="Invalid/Missing 'webhook_url' and/or 'channel_url' header(s)",
            status=400,
        )

    app.add_routes(routes)
    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    web.run_app(web_app(), port=port)
