package hub

import (
	"bytes"
	"discordsubhub/lib/discord"
	"discordsubhub/lib/feed"

	rl "github.com/nathanielfernandes/rl"

	"fmt"
	"net/http"
	"net/url"
	"os"

	"github.com/joho/godotenv"
)

var err = godotenv.Load()
var /* const */ WEBHOOKURL = os.Getenv("TEST_WEBHOOK")
var /* const */ VERIFYTOKEN = os.Getenv("VERIFYTOKEN")
var /* const */ CALLBACK = os.Getenv("CALLBACK")

const USERNAME = "DiscordSubHub"
const AVATARURL = "https://cdn.discordapp.com/attachments/741384050387714162/837936214903881748/7dc993c70d4adba215b87cafdc59d82d.png"
const PUBSUBHUBBUB = "https://pubsubhubbub.appspot.com/subscribe"
const BASETOPIC = "https://www.youtube.com/xml/feeds/videos.xml?channel_id="

type Hub struct {
	Shm      *SubHubMongo
	Uploaded map[string]bool
	Rlm      *rl.RatelimitManager
}

func NewHub() Hub {
	return Hub{Shm: NewSubHubMongo(), Uploaded: make(map[string]bool), Rlm: rl.NewRatelimitManager(1, 5000)}
}

func (h *Hub) pushNotification(id, webhook_url *string, payload *bytes.Buffer) {
	s := discord.SendPayload(webhook_url, payload)

	if s == 404 {
		h.Shm.Unsubscribe(*id, *webhook_url)
	}
}

func (h *Hub) DispatchNotifications(f *feed.Feed) {
	m := fmt.Sprintf("**%s** just uploaded a new video, [**check it out!**](%s)", f.Entry.Author.Name, f.Entry.Link.Href)
	payload := discord.NewMessage(m, USERNAME, AVATARURL, nil).AsPayload()

	s, err := h.Shm.GetSubscription(f.Entry.ChannelId)
	if err != nil {
		h.PubSubManage(f.Entry.ChannelId, "unsubscribe")
		return
	}

	for _, webhook := range s.Webhooks {
		go h.pushNotification(&f.Entry.ChannelId, &webhook, payload)
	}

}

func (h *Hub) PubSubManage(channelId, m string) {
	params := "?hub.callback=" + url.QueryEscape(CALLBACK) + "&hub.topic=" + url.QueryEscape(BASETOPIC+channelId) + "&hub.verify=async&hub.mode=" + m + "&hub.verify_token=" + VERIFYTOKEN
	resp, err := http.Post(PUBSUBHUBBUB+params, "application/x-www-form-urlencoded", nil)

	if err != nil {
		return
	}

	defer resp.Body.Close()
}
