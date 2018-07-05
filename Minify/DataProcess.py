from pymongo import MongoClient
import uuid
from collections import Counter
import operator

class DbDataAccess():
    def __init__(self, dbClient, dbName):
        """

        :param dbClient: a db instance
        :param dbName: a specified database
        """
        self.db = dbClient[dbName]
        self.collection = self.db["access_sites"]

    def go_to_collection(self, user_agent):
        try:
            self.collection = self.db[str(uuid.uuid3(namespace=uuid.NAMESPACE_OID, name=user_agent))]
        except:
            # No such collection? Go to the default one
            self.collection = self.db["access_sites"]
    def get_url_and_time(self, user_agent, assigned_range=5):
        # assigned_range will be set to 5 if not assigned
        benchmark_urls = []
        accessed_url = []
        accessed_time = []
        self.go_to_collection(user_agent)
        for post in self.collection.find():
            accessed_url.append(post['url'])
            accessed_time.append(post['time'])
        url_counter = Counter(accessed_url)
        print(type(url_counter))
        url_counter = sorted(url_counter.items(), key=operator.itemgetter(1), reverse=True)  # sort the dict in a descending order
        # print(url_counter)
        """
        for key, value in url_counter.items():
            print(value, key)
        """
        for i in range(assigned_range):
            benchmark_urls.append(url_counter[i][0])
            # print(url_counter[i][0]) #url here
        return benchmark_urls
if __name__ == "__main__":
    test_obj = DbDataAccess(dbClient=MongoClient("localhost", 27017), dbName="test")

    # test_obj.get_url_and_time(user_agent="Mozilla/5.0 (Linux; Android 7.1.1; Nexus 5X Build/N4F26I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.135 Mobile Safari/537.36")
    test_obj.get_url_and_time(user_agent="Mozilla/5.0 (Linux; Android 7.1.1; Nexus 5X Build/N4F26I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.135 Mobile Safari/537.36")

