import xml.etree.ElementTree as ET
import re
from copy import copy
import json

rg = lambda x: re.sub(r"\s*{.*}\s*", "", x)


def sift_xml(d: dict):
    e = d.get("feed").get("entry")
    sifted = {
        "videoId": e.get("videoId").get("_text"),
        "channelId": e.get("channelId").get("_text"),
        # "videltitle": e.get("title").get("_text"),
        "link": e.get("link").get("href"),
        "author": e.get("author").get("name").get("_text"),
    }
    return sifted


def parse_xml(r, root=True):
    if root:
        r = ET.fromstring(r.decode("utf-8"))
        return sift_xml({rg(r.tag): parse_xml(r, False)})
    d = copy(r.attrib)
    if r.text:
        d["_text"] = r.text
    for x in r.findall("./*"):
        if rg(x.tag) not in d:
            d[rg(x.tag)] = parse_xml(x, False)
    return d


def parse_channel_url(url: str):
    return url.strip("https://www.youtube.com/channel/")


def pubsubhub_data(channel_id: str, verify_token: str, mode: str = "subscribe"):
    data = {
        "hub.callback": "https://discordsubhub.herokuapp.com/pubsubhubbub",
        "hub.topic": f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}",
        "hub.verify": "async",
        "hub.mode": mode,
        "hub.verify_token": verify_token,
    }

    return data


def webhook_body(creator: str, video_link: str):
    return {
        "content": f"[New Upload From]({video_link}) **{creator}**",
        "embeds": None,
        "username": "DiscordSubHub",
        "avatar_url": "https://cdn.discordapp.com/attachments/741384050387714162/815695936436043816/discordsubhub2.png",
    }
