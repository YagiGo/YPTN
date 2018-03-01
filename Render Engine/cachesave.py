# start simple by adding html file into db
#  from htmlcombine import mergeHTML
from pymongo import MongoClient
import datetime
def savetodb(conn, url, htmlsrc):
    db = conn.webcache
    cachefile = {
        "url" : str(hash(url)), "src" : htmlsrc, "date" : datetime.datetime.utcnow()
    }
    # use hash to represent url because mongodb can not handle . in key
    webcache = db.webcache
    try:
        cachefile_id = webcache.insert_one(cachefile).inserted_id
    except  Exception as err:
        err_handle = {
            "Error": "ERROR %s"%str(err), "data": datetime.datetime.utcnow()
        }
        cachefile_id = webcache.insert_one(err_handle).inserted_id

if __name__ == "__main__":
    test_urls = [
        "https://www.baidu.com",
        "https://www.gooogle.com",
        "https://www.yahoo.co.jp",
        "https://www.imdb.com",
        "https://www.yahoo.com",
        "https://www.twitter.com",
        "https://www.microsoft.com",
        "http://http://www.softlab.cs.tsukuba.ac.jp/members.html"
    ]
    HOST = "localhost"
    PORT = 27017
    conn = MongoClient(host=HOST, port=PORT)
    for url in test_urls:
        htmlsrc = "This is supposed to be html src of %s" %url
        savetodb(conn, url, htmlsrc)