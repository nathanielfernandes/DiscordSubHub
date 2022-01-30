package discord

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
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

func (m *Message) asPayload() *bytes.Buffer {
	buffer := new(bytes.Buffer)
	json.NewEncoder(buffer).Encode(m)
	return buffer
}

func (m *Message) Send(webhook_url string) {
	resp, err := http.Post(webhook_url, "application/json", m.asPayload())

	if err != nil {
		log.Fatal(err)
	}

	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)

	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(string(body))
}
