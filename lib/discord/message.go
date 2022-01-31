package discord

import (
	"bytes"
	"encoding/json"
	"net/http"
)

type Message struct {
	Content   string  `json:"content"`
	Username  string  `json:"username"`
	AvatarUrl string  `json:"avatar_url"`
	Embeds    []Embed `json:"embeds"`
}

func QuickMessage(content string) *Message {
	return &Message{Content: content}
}

func NewMessage(content string, username string, avatar_url string, embeds []Embed) *Message {
	return &Message{Content: content, Username: username, AvatarUrl: avatar_url, Embeds: embeds}
}

func (m *Message) AsPayload() *bytes.Buffer {
	buffer := new(bytes.Buffer)
	json.NewEncoder(buffer).Encode(m)
	return buffer
}

func (m *Message) Send(webhook_url string) {
	resp, err := http.Post(webhook_url, "application/json", m.AsPayload())
	if err != nil {
		return
	}

	defer resp.Body.Close()
}

func SendPayload(webhook_url *string, payload *bytes.Buffer) int {
	resp, err := http.Post(*webhook_url, "application/json", payload)

	if err != nil {
		return 0
	}

	defer resp.Body.Close()
	return resp.StatusCode
}
