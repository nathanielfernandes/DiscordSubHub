package main

import (
	"discordsubhub/lib/feed"
	"discordsubhub/lib/hub"
	"fmt"
	"log"
	"net/http"
	"os"
)

var /* const */ VERIFYTOKEN = os.Getenv("VERIFYTOKEN")

func baseHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Message Sent\n")
}

func pubsubChallenge(w *http.ResponseWriter, r *http.Request) {
	vt := r.URL.Query().Get("hub.verify_token")
	challenge := r.URL.Query().Get("hub.challenge")

	if vt == VERIFYTOKEN {
		fmt.Fprintf(*w, challenge)
		return
	}

	http.Error(*w, "invalid verify token", http.StatusUnauthorized)
}

func postNotification(w *http.ResponseWriter, r *http.Request) {
	data, err := feed.Parse(&r.Body)
	if err != nil {
		http.Error(*w, "Invalid Xml", http.StatusBadRequest)
		return
	}

	hub.DispatchNotification(&data)
	fmt.Fprintf(*w, "Message Sent\n")
}

func pubsubhubHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("PubSub\n")

	switch r.Method {
	case "GET":
		pubsubChallenge(&w, r)
	case "POST":
		postNotification(&w, r)
	default:
		http.Error(w, "Method is not supported.", http.StatusNotFound)
	}
}

func main() {
	http.HandleFunc("/", baseHandler)
	http.HandleFunc("/pubsubhub", pubsubhubHandler)

	fmt.Printf("Listening on port 8080\n")
	if err := http.ListenAndServe("127.0.0.1:8080", nil); err != nil {
		log.Fatal(err)
	}
}
