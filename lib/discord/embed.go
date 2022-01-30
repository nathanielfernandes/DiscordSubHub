package discord

type EmbedField struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

type EmbedAuthor struct {
	Name    string `json:"name"`
	IconUrl string `json:"icon_url"`
	Url     string `json:"url"`
}

type EmbedFooter struct {
	Text string `json:"text"`
}

type Embed struct {
	Title       string       `json:"title"`
	Description string       `json:"description"`
	Color       int64        `json:"color"`
	Fields      []EmbedField `json:"fields"`
	Author      EmbedAuthor  `json:"author"`
	Footer      EmbedFooter  `json:"footer"`
}
