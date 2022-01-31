package hub

import (
	"context"
	"os"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var /* const */ MONGOURI = os.Getenv("MONGOURI")
var Ctx = context.Background()

const SUBSCRIPTIONINTERVAL = 423360000

type SubHubMongo struct {
	MongoClient *mongo.Client
	collection  *mongo.Collection
}

func NewSubHubMongo() *SubHubMongo {
	client, err := mongo.Connect(Ctx, options.Client().ApplyURI(MONGOURI))
	if err != nil {
		panic(err)
	}

	return &SubHubMongo{
		MongoClient: client,
		collection:  client.Database("discordsubhub").Collection("subscriptions"),
	}
}

func expireyFilter(ct int64) bson.M {
	return bson.M{"subscribed": bson.D{{"$lt", ct - SUBSCRIPTIONINTERVAL}}}
}

func (shm *SubHubMongo) ExpiredSubscriptions(ct int64) ([]ExpiredSubscription, error) {
	cursor, err := shm.collection.Find(Ctx, expireyFilter(ct))
	if err != nil {
		return nil, err
	}

	var expired []ExpiredSubscription
	defer cursor.Close(Ctx)
	err = cursor.All(Ctx, &expired)

	return expired, err
}

func (shm *SubHubMongo) RefreshSubscriptions(ct int64) {
	shm.collection.UpdateMany(Ctx, expireyFilter(ct), bson.M{"$set": bson.D{{"$set", bson.D{{"subscribed", ct}}}}})
}

func (shm *SubHubMongo) GetSubscription(id string) (Subscription, error) {
	var sub Subscription
	err = shm.collection.FindOne(Ctx, bson.D{{"_id", id}}).Decode(&sub)
	return sub, err
}

func (shm *SubHubMongo) GetWebhooks(id string) []string {
	s, err := shm.GetSubscription(id)

	if err != nil {
		return []string{}
	}

	return s.Webhooks
}

func (shm *SubHubMongo) Unsubscribe(id, webhook_url string) bool {
	res, err := shm.collection.UpdateOne(Ctx, bson.D{{"_id", id}}, bson.D{{"$pull", bson.D{{"webhooks", webhook_url}}}})
	if err != nil {
		return false
	}

	if res.MatchedCount == 1 && res.ModifiedCount == 0 {
		_, err := shm.collection.DeleteOne(Ctx, bson.D{{"_id", id}, {"webhooks", bson.D{{"$size", 0}}}})
		if err != nil {
			return false
		}

		return true
	}

	if res.ModifiedCount == 1 {
		return shm.Unsubscribe(id, webhook_url)
	}

	return false
}

func (shm *SubHubMongo) Subscribe(id, webhook_url string) bool {
	res, err := shm.collection.UpdateOne(Ctx, bson.D{{"_id", id}}, bson.D{{"$addToSet", bson.D{{"webhooks", webhook_url}}}})
	if err != nil {
		return false
	}

	if res.MatchedCount == 0 {
		_, err := shm.collection.InsertOne(Ctx, bson.D{{"_id", id}, {"subscribed", time.Now().UnixMilli()}, {"webhooks", []string{webhook_url}}})
		if err != nil {
			return false
		}

		return true
	}

	return res.ModifiedCount == 1
}

func (shm *SubHubMongo) Exists(id string) bool {
	var res Subscription
	err = shm.collection.FindOne(Ctx, bson.D{{"_id", id}}).Decode(&res)
	return err != nil
}
