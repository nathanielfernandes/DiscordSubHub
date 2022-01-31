package main

import (
	"discordsubhub/lib/hub"
	"fmt"
	"log"
	"net/http"
)

func main() {
	h := hub.NewHub()
	defer h.Shm.MongoClient.Disconnect(hub.Ctx)

	http.HandleFunc("/pubsubhub", h.PubsubhubHandler)
	http.HandleFunc("/subscribe", h.Subscribe)
	http.HandleFunc("/unsubscribe", h.Unsubscribe)

	fmt.Printf("DiscordSubHub\nListening on port 8080\n")
	if err := http.ListenAndServe("127.0.0.1:8080", nil); err != nil {
		log.Fatal(err)
	}
}
