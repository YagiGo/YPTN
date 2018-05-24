from pymongo import MongoClient
"""
An URL post example
{
    "_id" :"the id the db gave",
    "time":"datetime.datetime.utcnow()",
    "url" :"access_url"


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
