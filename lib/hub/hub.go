package hub

import (
	"discordsubhub/lib/discord"
	"discordsubhub/lib/feed"
	"fmt"
)

const WEBHOOKURL = ""
const USERNAME = "DiscordSubHub"
const AVATARURL = "https://cdn.discordapp.com/attachments/741384050387714162/837936214903881748/7dc993c70d4adba215b87cafdc59d82d.png"

// test
func DispatchNotification(data *feed.Feed) {
	msg := fmt.Sprintf("**%s** just uploaded a new video, [**check it out!**](%s)", data.Entry.Author.Name, data.Entry.Link.Href)
	go discord.NewMessage(msg, USERNAME, AVATARURL, nil).Send(WEBHOOKURL)
}
