<p align="center"> 
<img src="https://cdn.discordapp.com/attachments/741384050387714162/815695936436043816/discordsubhub2.png" alt="DiscordSubHub" width=150>
</p>
<!-- <img src="https://cdn.discordapp.com/attachments/741384050387714162/815695936436043816/discordsubhub2.png" alt="DiscordSubHub" class="center"> -->
<h1 align="center">
  DiscordSubHub
</h1>

<h3 align="center">A user-friendly Feed API designed for Discord Webhooks.</h3>
<br>

<p align="center">
    <a href="https://https://github.com/nathanielfernandes/DiscordSubHub">
    <img src="https://img.shields.io/github/last-commit/nathanielfernandes/DiscordSubHub.svg?style=for-the-badge&logo=github&logoColor=white"
         alt="GitHub last commit">
    <a href="https://github.com/engineer-man/DiscordSubHub">
    <img src="https://img.shields.io/github/issues/nathanielfernandes/DiscordSubHub.svg?style=for-the-badge&logo=github&logoColor=white"
         alt="GitHub issues">
    <a href="https://github.com/engineer-man/piston/pulls">
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
DiscordSubHub is a Feed API designed for subscribing Discord Webhooks to noitifications from a content creator. For example, when you subscribe your discord-webhook, along with the youtube channel of the creator you want notifications from, DiscordSubHub will subscribe to the creator itself through a pubsubhub and from then relay any notifcations from the creator directly to your discord-webhook.

It is currently in use by my Discord Bot [Hamood](https://nathanielfernandes.github.io/HamoodBot/), allowing users to automatically subscribe to creators through a simple command.

<br>

# Public API
- Requires no installation and you can use it immediately.
- Reference [Usage](#Usage) to learn about the request formats.

<br>

When using the public DiscordSubHub API, use the URL:
#### POST
```
https://discordsubhub.herokuapp.com/subscribe
```
> Important Note: The DiscordSubHub API is rate limited to 1 requests every 5 seconds. If you have a need for more requests than that
and it's for a good cause, please reach out to me (nathan#3724) on Discord
so we can discuss potentially getting you an unlimited key.

<br>

# Usage
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
The response upon a successful subscription will be `200 OK`
```
Successfully Subscribed
```
The response upon an unsuccessful subscription will be `400 Bad Request`
```
Invalid/Missing 'webhook_url' and/or 'channel_url' header(s)
```
The response when hit by the rate limit will be `429 Too Many Requests`
```
slow down!
```

<br>

# License
DiscordSubHub is licensed under the MIT license.