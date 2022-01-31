package hub

import (
	"net/http"
	"regexp"
)

const YOUTUBECHANNEL = "https://www.youtube.com/channel/"

var r, _ = regexp.Compile(`.*(discord|discordapp)\.com/api/webhooks/(\d+)/([a-zA-Z0-9_-]+)`)

func ChannelExists(id string) bool {
	if len(id) <= 0 {
		return false
	}
	res, err := http.Head(YOUTUBECHANNEL + id)
	return res.StatusCode == 200 && err == nil
}

func WebhookExists(webhook string) bool {
	if len(webhook) <= 0 {
		return false
	}

	if !r.MatchString(webhook) {
		return false
	}

	res, err := http.Head(webhook)
	return res.StatusCode == 200 && err == nil
}
