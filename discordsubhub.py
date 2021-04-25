import os
import aiohttp
import jinja2
import aiohttp_jinja2
from aiohttp import web
from utils.hub import Hub
from utils.ratelimiter import RateLimiter

# from utils.resubber


async def web_app():

    #  resubs
    hub = Hub()
    rate_limit = RateLimiter(rate=5)
    app = web.Application()
    routes = web.RouteTableDef()
    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
    )

    @routes.get("/")
    @aiohttp_jinja2.template("index.html")
    async def index(request: web.Request):
        """displays home page of DiscordSubHub.
        """
        context = {}
        return context

    @routes.post("/form/{mode}")
    @aiohttp_jinja2.template("index.html")
    async def form_action(request: web.Request):
        """attemps to subscribe the inputted webhook_url to the youtube_url.
        """

        # get the mode from the url, subscribe/unsubscribe
        mode = request.match_info["mode"]

        # get the information typed in from the form
        form = await request.post()
        webhook_url, channel_url = form.get("webhook_url"), form.get("channel_url")

        # check to see if the user is not within the rate limit
        is_limited, t = await rate_limit.check_rate(webhook_url)
        text_color = "#ffffff"
        if not is_limited:
            if mode == "test":
                info = await hub.test(webhook_url=webhook_url)
            else:
                # subscribe/unsubscibe the webhook to pubsubhubbub
                info, status = await hub.pubsubhub(
                    webhook_url=webhook_url, channel_url=channel_url, mode=mode
                )
                if status >= 400:
                    text_color = "#f84444"
        else:
            text_color = "#f84444"
            info = f"Slow Down! {t}s"

        # keep the entered info inside the form
        return {
            "info": info,
            "prev_webhook_url": webhook_url,
            "prev_channel_url": channel_url,
            "text_color": text_color,
        }

    @routes.get("/refreshsubs/{token}")
    async def wake_up(request: web.Request):
        """refreshes all expired subscriptions
        """
        token = request.match_info["token"]

        if token == hub.api_token:
            await hub.refresh_subscriptions()

        return web.Response(text="success")

    @routes.get("/coffee")
    async def wake_up(request: web.Request):
        """to keep the heroku app from sleeping.
        """
        return web.Response(text="thanks for the coffee :)")

    @routes.get("/pubsubhubbub")
    async def verify_subscription(request: web.Request):
        """returns the hub.challenge sent with pubsubhubbub's GET
           to verify the subscription.
        """
        print("PubSubHubBub verification")
        verify_token = request.query.get("hub.verify_token")
        challenge = request.query.get("hub.challenge")
        # checks if the verification tokens match as well as for a hub.challenge
        if (verify_token == hub.verify_token) and challenge:
            # return the hub.challenge
            return web.Response(body=challenge)
        return web.Response()

    @routes.post("/pubsubhubbub")
    async def subscription_update(request: web.Request):
        """dispatches the notification to the webhooks subscribed to
           the channel_id specified in the POST from pubsubhubbub.
        """
        print("Channel Upload")
        # get the upload information and dispatch it accordingly
        xml_data = await request.read()
        await hub.dispatch_notification(xml_data)
        return web.Response()

    @routes.post("/subscribe")
    async def subscribe(request: web.Request):
        """handles subscribe/unsubscribe POSTs.
        """
        if request.headers is not None:
            # get all important information from the headers
            token = request.headers.get("token")
            webhook_url = request.headers.get("webhook_url", "")
            channel_url = request.headers.get("channel_url", "")
            mode = request.headers.get("mode", "subscribe")

            # check to see if the user is not within the rate limit
            is_limited, t = await rate_limit.check_rate(
                webhook=webhook_url, token=token == hub.api_token
            )
            if not is_limited:
                # subscribe/unsubscibe the webhook to pubsubhubbub
                info, status = await hub.pubsubhub(
                    webhook_url=webhook_url, channel_url=channel_url, mode=mode
                )
                return web.Response(text=info, status=status)
            else:
                return web.Response(text=f"Slow Down! {t}s", status=429)
        return web.Response(
            text="missing webhook_url and channel_url headers", status=400
        )

    app.add_routes(routes)
    return app
