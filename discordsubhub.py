import os
import aiohttp
from aiohttp import web
from hub import Hub


async def web_app():
    hub = Hub()
    app = web.Application()
    routes = web.RouteTableDef()

    @routes.get("/coffee")
    async def wake_up(request):
        return web.Response(text="thankyou :)")

    @routes.get("/pubsubhubbub")
    async def verify_subscription(request):
        print("GET from:", request.url)
        verify_token = request.query.get("hub.verify_token")
        challenge = request.query.get("hub.challenge")
        if (verify_token == hub.verify_token) and challenge:
            return web.Response(body=challenge)

        return web.Response()

    @routes.post("/pubsubhubbub")
    async def subscription_update(request):
        print("POST from:", request.url)
        xml_data = await request.read()

        await hub.dispatch_notification(xml_data)
        return web.Response()

    @routes.post("/subscribe")
    async def subscribe(request):
        print("subscribe event")
        if request.headers is not None:
            webhook_url = request.headers.get("webhook_url")
            channel_url = request.headers.get("channel_url")
            mode = request.headers.get("mode", "subscribe")

            if webhook_url and channel_url:
                success = await hub.pubsubhub(
                    webhook_url=webhook_url, channel_url=channel_url, mode="mode"
                )
                if success:
                    return web.Response(text=f"Successfully {mode.title()}ed")

        return web.Response(
            text="Invalid/Missing 'webhook_url' and/or 'channel_url' header(s)",
            status=400,
        )

    app.add_routes(routes)
    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    web.run_app(web_app(), port=port)
