<p align="center"> 
<img href="https://discordsubhub.herokuapp.com/" src="https://cdn.discordapp.com/attachments/741384050387714162/815695936436043816/discordsubhub2.png" alt="DiscordSubHub" width=150>
</p>

<h1 align="center">
  <a href="https://discordsubhub.herokuapp.com/">DiscordSubHub</a>
</h1>

<h3 align="center">A User-Friendly Feed API Designed For Discord Webhooks.</h3>
<br>

`Go rewrite` readme comming soon.

<!-- <p align="center">
    <a href="https://https://github.com/nathanielfernandes/DiscordSubHub">
    <img src="https://img.shields.io/github/last-commit/nathanielfernandes/DiscordSubHub.svg?style=for-the-badge&logo=github&logoColor=white"
         alt="GitHub last commit">
    <a href="https://github.com/nathanielfernandes/DiscordSubHub">
    <img src="https://img.shields.io/github/issues/nathanielfernandes/DiscordSubHub.svg?style=for-the-badge&logo=github&logoColor=white"
         alt="GitHub issues">
    <a href="https://github.com/nathanielfernandes/piston/pulls">
    <img src="https://img.shields.io/github/issues-pr-raw/nathanielfernandes/DiscordSubHub.svg?style=for-the-badge&logo=github&logoColor=white"
         alt="GitHub pull requests">
</p>

---

<h4 align="center">
  <a href="#About">About</a> •
  <a href="#Public-API">Public API</a> •
  <a href="#Usage">Usage</a> •
  <a href="#License">License</a>
</h4>

---

<br>

# About

DiscordSubHub is a Feed API designed for subscribing Discord Webhooks to a YouTube channel. For example, when you subscribe your discord-webhook to a youtube channel, DiscordSubHub will subscribe to the channel itself through a pubsubhub. From DiscordSubHub will relay any notifcations from the creator directly to your discord-webhook.

It is currently in use by my Discord Bot [Hamood](https://nathanielfernandes.github.io/HamoodBot/), allowing users to automatically subscribe to creators through a simple command.

<br>

# Public API

- Requires no installation and you can use it immediately.
- Reference [Usage](#Usage) to learn about the request formats.

<br>

If you are subscribing manually, use this URL: [DiscordSubHub](https://discordsubhub.herokuapp.com/)

When using the public DiscordSubHub API, use the URL:

#### POST

```
https://discordsubhub.herokuapp.com/subscribe
```

> Important Note: The DiscordSubHub API is rate limited to 1 requests every 5 seconds. If you have a need for more requests than that
> and it's for a good cause, please reach out to me (nathan#3724) on Discord
> so we can discuss potentially getting you an unlimited key.

<br>

# Usage

## Manual Method

<p>You can subscibe/unsubscribe your webhooks directly from <a href="https://discordsubhub.herokuapp.com/">discordsubhub.herokuapp.com</a><p>
<img href="https://discordsubhub.herokuapp.com/" src="https://cdn.discordapp.com/attachments/741384050387714162/817242533595447316/unknown.png" alt="DiscordSubHub" width=600>
<p>Uploads will be sent to your discord-webhook and will appear in chat like this:<p>
<img href="https://discordsubhub.herokuapp.com/" src="https://cdn.discordapp.com/attachments/741384050387714162/817242911493849118/unknown.png" alt="DiscordSubHub" width=400>

## API Method

#### Subscribe Endpoint

`POST /subscribe`
This endpoint requests a subscription/unsubscription of your webhook to a YouTube channel.

- `webhook_url` (**required**) The url of your Discord-Webhook.
- `channel_url` (**required**) The url of your Content Creator.
- `mode` (**required**) The action you want DiscordSubHub to take ('subscribe' or 'unsubscribe').

#### Required `Headers`

```python
{
    "webhook_url": webhook_url,
    "channel_url": channel_url,
    "mode":"subscribe"
}
```

The response upon a successful subscription/unsubscription will be `200 Ok`

```
Successfully Subscribed/Unsubscribed!
```

The response upon a subscription/unsubscription that aldready exists will be `200 OK`

```
Aldready Subscribed/Unsubscribed
```

The response upon an unsuccessful subscription will be `400 Bad Request`

```
Invalid/Missing 'webhook_url' and/or 'channel_url' header(s)
```

The response when hit by the rate limit will be `429 Too Many Requests`

```
Slow Down! (5s)
```

<br>

# License

DiscordSubHub is licensed under the MIT license. -->
