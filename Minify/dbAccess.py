import uuid
import datetime
from pymongo import MongoClient
"""
An URL post example
{
    "_id" :"the id the db gave",
    "time":"datetime.datetime.utcnow()",
    "url" :"access_url"
    "user-agent" : "user-agent here, fetching from request header"


"""
class DatabaseObject():
    def __init__(self, dbClient, dbName, dbCollection):
        """

        :param dbClient: a db instance
        :param dbName: a specified database
        """
        self.db = dbClient[dbName]
        try:
            self.collection = self.db[dbCollection]
        except:
            # No such collection? create one
            self.collection = self.db.createCollection(dbCollection)

    def insert_url(self,url_post):
        """
        :param url_post: a formatted post containing url
        :return: Nothing
        """
        self.collection.insert_one(url_post)

    def get_url(self, url):
        return self.collection.find({"url":url})

    def delete_url(self, url):
        self.collection.remove({"url":url})

    def display_url(self, url):
        print(self.collection.find({"url":url}))

    def get_user(self, user_agent):
        return self.collection.find({"uuid":uuid.uuid3(namespace=uuid.NAMESPACE_OID, name=user_agent)})

    def insert_user(self, user_post):
        print(user_post)
        if self.collection.find({"uuid":uuid.uuid3(namespace=uuid.NAMESPACE_OID, name = user_post["user-agent"])}) is None:
            self.collection.insert_one(user_post)
        else:
            print("User Already Exist!")

    def change_collection(self, collectionName):
        try:
            self.collection = self.db[collectionName]
        except:
            self.collection = self.db.createCollection()


if __name__ == "__main__":
    dbInstance = DatabaseObject(MongoClient("localhost", 27017), dbName="test", dbCollection="access_sites")
    url_post_example = {
        "time" : datetime.datetime.utcnow(),
        "url" : "www.example.com",
        "user-agent" : "Mozilla/5.0 (Linux; Android 7.1.1; Nexus 5X Build/N4F26I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.135 Mobile Safari/537.36"
    }
    dbInstance.insert_url(url_post_example)
    dbInstance.display_url(url="www.example.com")

