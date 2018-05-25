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

if __name__ == "__main__":
    dbInstance = DatabaseObject(MongoClient("localhost", 27017), dbName="test", dbCollection="access_sites")
    url_post_example = {
        "time" : datetime.datetime.utcnow(),
        "url" : "www.example.com",
        "user-agent" : "Mozilla/5.0 (Linux; Android 7.1.1; Nexus 5X Build/N4F26I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.135 Mobile Safari/537.36"
    }
    dbInstance.insert_url(url_post_example)
    dbInstance.display_url(url="www.example.com")

