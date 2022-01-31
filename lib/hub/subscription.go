package hub

// type Subscription struct {
// 	ChannelID  string   `bson:"_id,omitempty"`
// 	Subscribed int64    `bson:"subscribed,omitempty"`
// 	Webhooks   []string `bson:"webhooks,omitempty"`
// }

type Subscription struct {
	ChannelID  string   `bson:"_id,omitempty"`
	Subscribed int64    `bson:"subscribed,omitempty"`
	Webhooks   []string `bson:"webhooks,omitempty"`
}
type ExpiredSubscription struct {
	ChannelID string `bson:"_id,omitempty"`
}
