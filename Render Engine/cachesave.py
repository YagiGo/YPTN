# start simple by adding html file into db
#  from htmlcombine import mergeHTML
from pymongo import MongoClient
import datetime, time
from htmlcombine import generate
def savetoAndReadfromDB(conn, url, threshold):
    """

    :param conn: db connection
    :param url: web page url
    :param htmlsrc: processed html file
    :param threshold: expiration threshold
    :return: html source code
    """
    db = conn.webcache

    # use hash to represent url because mongodb can not handle . in key
    webcache = db.webcache_test1
    existcache = webcache.find_one({"url" : str(hash(url))})
    if not existcache:
        try:
            htmlsrc = generate(url)
            cachefile = {
                "url": str(hash(url)), "src": htmlsrc, "date": str(datetime.datetime.utcnow()),
                "recent_access_time": 0,
            }
            cachefile_id = webcache.insert_one(cachefile).inserted_id
        except  Exception as err:
            err_handle = {
                "Error": "ERROR %s"%str(err), "data": datetime.datetime.utcnow()
            }
            cachefile_id = webcache.insert_one(err_handle).inserted_id
    elif isexpired(existcache, threshold):
        try:
            #  update src file and datetime
            htmlsrc = generate(url)
            existcache['src'] = htmlsrc
            existcache['date'] = datetime.datetime.utcnow()
        except Exception as err:
            err_handle = {
                "Error": "ERROR %s"%str(err), "data": datetime.datetime.utcnow()
            }
            cachefile_id = webcache.insert_one(err_handle).inserted_id
    return webcache.find_one({"url" : str(hash(url))})['src']

def isexpired(cache, threshold):
    current_time = str(datetime.datetime.utcnow()).split('.')[0]
    current_timestamp = time.mktime(current_time)
    cache_time = cache['date'].split('.')[0]
    cache_timestamp = time.mktime(cache_time)
    live_time = int(current_timestamp) - int(cache_timestamp)
    if live_time > threshold:
        return True
    else:
        return False
if __name__ == "__main__":
    test_urls = [
        "https://www.baidu.com",
        "https://www.gooogle.com",
        "https://www.yahoo.co.jp",
        "https://www.imdb.com",
        "https://www.yahoo.com",
        "https://www.twitter.com",
        "https://www.microsoft.com",
        "http://www.softlab.cs.tsukuba.ac.jp/members.html"
    ]
    HOST = "localhost"
    PORT = 27017
    conn = MongoClient(host=HOST, port=PORT)
    for url in test_urls:
        htmlsrc = "This is supposed to be html src of %s" %url
        savetodb(conn, url, htmlsrc)