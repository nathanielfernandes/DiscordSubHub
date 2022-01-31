package feed

import (
	"encoding/xml"
	"io"
)

type Feed struct {
	XMLName xml.Name `xml:"feed"`
	Title   string   `xml:"title"`
	Updated string   `xml:"updated"`
	Entry   Entry    `xml:"entry"`
}

type Entry struct {
	XMLName   xml.Name `xml:"entry"`
	Id        string   `xml:"id"`
	VideoId   string   `xml:"videoId"`
	ChannelId string   `xml:"channelId"`
	Title     string   `xml:"title"`
	Link      Link     `xml:"link"`
	Author    Author   `xml:"author"`
	Published string   `xml:"published"`
	Updated   string   `xml:"updated"`
}

type Link struct {
	XMLName xml.Name `xml:"link"`
	Href    string   `xml:"href,attr"`
}

type Author struct {
	XMLName xml.Name `xml:"author"`
	Name    string   `xml:"name"`
	Uri     string   `xml:"uri"`
}

func Parse(feedXml *io.ReadCloser) (Feed, error) {
	var f Feed
	err := xml.NewDecoder(*feedXml).Decode(&f)
	return f, err
}
