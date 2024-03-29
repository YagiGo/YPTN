from pymongo import MongoClient
import uuid
from collections import Counter
import operator
from urlparse import urlparse
import time

class DbDataAccess():
    def __init__(self, dbClient, dbName, user_agent, processedDaraDBName):
        """

        :param dbClient: a db instance
        :param dbName: a specified database
        """
        self.dbClient = dbClient
        self.db = self.dbClient[dbName]
        self.collection = self.db["access_sites"]
        self.user_agent = user_agent
        self.dbName = dbName # this db is used to store original data
        self.processedDataDBName = processedDaraDBName

    def go_to_database(self,dbName):
            self.db = self.dbClient[dbName]

    def go_to_collection(self, user_agent):
        try:
            self.collection = self.db[str(uuid.uuid3(namespace=uuid.NAMESPACE_OID, name=user_agent))]
        except:
            # No such collection? Go to the default one
            self.collection = self.db["access_sites"]
    def get_url_and_time(self, assigned_range=10):
        # assigned_range will be used to select the most accessed sites in the db
        # assigned_range will be set to 5 if not assigned
        # and since this is not very accurate, future works will be contributed to improve accuracy by
        # adding other means of benchmarking

        # first go to the db that stores filtered url data
        self.go_to_database(self.dbName)
        self.go_to_collection(self.user_agent)
        benchmark_urls = []
        accessed_url = []
        accessed_time = []
        self.go_to_collection(self.user_agent)
        for post in self.collection.find():
            # print post['time']
            try:
                accessed_url.append(post['url'])
                accessed_time.append(post['time'])
            except:
                print("Abnormal Post!")
                self.collection.delete_one(post)
        url_counter = Counter(accessed_url)
        # print(type(url_counter))
        url_counter = sorted(url_counter.items(), key=operator.itemgetter(1), reverse=True)  # sort the dict in a descending order
        # print(url_counter)
        modified_url = self.url_modify(url_counter)
        print(modified_url)
        url_posts = []
        for item in modified_url:
            # item[0] url
            # item[1] access time
            url_posts.append(self.get_url_post(user_agent=self.user_agent, url = str(item[0]), access_times= int(item[1])))
            # and what the fuck is this?
            # print(item)
            # print(result)
        # when this is done, go back to original db and connection
        self.write_to_db(url_posts)




        for i in range(assigned_range):
            benchmark_urls.append(url_counter[i][0])
            # print(url_counter[i][0]) #url here
        return benchmark_urls

    def get_url_post(self, user_agent, url, access_times):
        return {
            "url":url,
            "user_agent": user_agent,
            # "access_time": access_time, # Emmm, don't add access time at this point
            "access_times": access_times
        }

    def url_modify(self, url_record):
        """
        This function is used to clear redundant urls
        :param url_record: url dict derived from get_url_and_time
        :return: modified url dict
        """
        modified_url = {} # empty dict to store result
        for item in url_record:
            # item is tuple item[0] being url, item[1] being access time
            parsed_result = urlparse(item[0])
            if(parsed_result.path.endswith('.css') or parsed_result.path.endswith('.js') or
               parsed_result.path.endswith('png') or parsed_result.path.endswith('.jpg') or
               parsed_result.path.endswith('.jpeg')):
                continue
            if parsed_result.netloc not in [key for key, value in modified_url.items()]:
                modified_url.update({parsed_result.netloc:int(item[1])})
            else:
                modified_url[parsed_result.netloc] += item[1]

        return sorted(modified_url.items(), key=operator.itemgetter(1), reverse=True)  # sort the dict in a descendin

    def write_to_db(self, posts):
        # First go to the db that stores processed data
        # then go to the collection corresponding to the user based on user-agent
        # next, save the data
        # finally go back to where you began
        self.go_to_database(self.processedDataDBName)
        self.go_to_collection(self.user_agent)
        self.collection.remove()
        self.go_to_collection(self.user_agent) # first remove the original collection and create another one
        self.collection.insert_many(posts)
        self.go_to_database(self.dbName)
        self.go_to_collection(self.user_agent)




if __name__ == "__main__":
    #Now run the program periodically

    test_obj = DbDataAccess(dbClient=MongoClient("localhost", 27017), dbName="test",
                            user_agent = "Mozilla/5.0 (Linux; Android 7.1.1; Nexus 5X Build/N4F26I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.135 Mobile Safari/537.36",
                            processedDaraDBName="processedData")

    # test_obj.get_url_and_time(user_agent="Mozilla/5.0 (Linux; Android 7.1.1; Nexus 5X Build/N4F26I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.135 Mobile Safari/537.36")
    times = 1
    while True and times <= 24:
        print("Start dataprocessing No.{}".format(times))
        test_obj.get_url_and_time()
        time.sleep(3600)
        if times==24:
            times = 0
        times += 1
