package hub

import (
	"discordsubhub/lib/feed"
	"fmt"
	"net/http"
)

func (h *Hub) Subscribe(w http.ResponseWriter, r *http.Request) {
	if h.Rlm.IsRatelimited(r.RemoteAddr) {
		http.Error(w, "ratelimited", http.StatusTooManyRequests)
		return
	}

	channel := r.URL.Query().Get("channel")
	webhook := r.URL.Query().Get("webhook")

	if !ChannelExists(channel) {
		http.Error(w, "invalid channel id", http.StatusNotAcceptable)
		return
	}

	if !WebhookExists(webhook) {
		http.Error(w, "invalid webhook", http.StatusNotAcceptable)
		return
	}

	if !h.Shm.Subscribe(channel, webhook) {
		http.Error(w, "aldready subscribed", http.StatusConflict)
		return
	}

	if !h.Shm.Exists(channel) {
		defer h.PubSubManage(channel, "subscribe")
	}

	fmt.Fprintf(w, "Sucessfully Subscribed!")
}

func (h *Hub) Unsubscribe(w http.ResponseWriter, r *http.Request) {
	if h.Rlm.IsRatelimited(r.RemoteAddr) {
		http.Error(w, "ratelimited", http.StatusTooManyRequests)
		return
	}

	channel := r.URL.Query().Get("channel")
	webhook := r.URL.Query().Get("webhook")

	if !ChannelExists(channel) {
		http.Error(w, "invalid channel id", http.StatusNotAcceptable)
		return
	}

	if !WebhookExists(webhook) {
		http.Error(w, "invalid webhook", http.StatusNotAcceptable)
		return
	}

	if !h.Shm.Unsubscribe(channel, webhook) {
		http.Error(w, "aldready unsubscribed", http.StatusConflict)
		return
	}

	if !h.Shm.Exists(channel) {
		defer h.PubSubManage(channel, "unsubscribe")
	}

	fmt.Fprintf(w, "Sucessfully Unubscribed!")
}

func PubsubChallenge(w *http.ResponseWriter, r *http.Request) {
	vt := r.URL.Query().Get("hub.verify_token")
	challenge := r.URL.Query().Get("hub.challenge")

	if vt == VERIFYTOKEN {
		fmt.Fprintf(*w, challenge)
		return
	}

	http.Error(*w, "invalid verify token", http.StatusUnauthorized)
}

func (h *Hub) PostNotification(w *http.ResponseWriter, r *http.Request) {
	f, err := feed.Parse(&r.Body)
	if err != nil {
		http.Error(*w, "Invalid Xml", http.StatusBadRequest)
		return
	}

	// _, ok := h.Uploaded[f.Entry.VideoId]
	if !h.Uploaded[f.Entry.VideoId] {
		h.Uploaded[f.Entry.VideoId] = true
		h.DispatchNotifications(&f)
	}

	fmt.Fprintf(*w, "sent")
}

func (h *Hub) PubsubhubHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("PubSub\n")

	switch r.Method {
	case "GET":
		PubsubChallenge(&w, r)
	case "POST":
		h.PostNotification(&w, r)
	default:
		http.Error(w, "Method is not supported.", http.StatusNotFound)
	}
}
