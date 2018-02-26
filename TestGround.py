import time
import sys
import os
'''
timestamp = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
print("Time now is %s" %timestamp)
print(type(timestamp))
def testif(inout):
    data = inout if not inout else 0
    print(data)
testif()
'''
'''
import json
test = {"statistics":{"originalSize":13537,"originalGzipSize":5712,"compressedSize":13544,"compressedGzipSize":5719,"compileTime":16}}
print(type(test))
print(test['statistics']['originalSize'])
'''

'''
import requests
from bs4 import BeautifulSoup
header = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'accept-language',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}
# header is something needed to be modified if deployed
try:
    response = requests.get('http://www.baidu.com', header)
    if(response.status_code!= 200):
        print('Error Occured with return code ' + str(response.status_code))
    else:
        sortedHTML = BeautifulSoup(response.text, "html.parser")
        # print(sortedHTML)
        scriptfile = sortedHTML.find_all('script')
        # print(scriptfile)
        file = open(os.path.abspath('JSMinimizing') + '\\jsfile.js', 'w', encoding='utf-8')
        for script in scriptfile:
            file.write(script.text)
        file.close()
except Exception as e:
    print('ERROR:' + str(e))
'''
'''
# HASH TEST
import hashlib
print(hashlib.sha224(b"https://www.a.com").hexdigest()
      )
print(hashlib.sha224(b"https://www.b.com").hexdigest()
      )
print(hashlib.sha224(b"https://www.c.com").hexdigest()
      )
'''
'''
# Replace Test
from bs4 import BeautifulSoup
newText = 'HELLO'
soup = BeautifulSoup('<script type="text/javascript">var aPageStart = (new Date()).getTime();</script><script>var aPageStart = (new Date()).getTime();</script>', 'html.parser')
for script in soup.findAll('script', {'type': ''}):
    mod_script = soup.new_tag('script')
    mod_script.string = "HELLO"
    script.replace_with(mod_script)

print(soup)
'''
'''
import logging
import time
logger = logging.getLogger("TestGround")
hdlr = logging.FileHandler("{}.log".format(time.time()))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
logger.error("Huston, We have a problem")
logger.cr
'''
'''
def test():
    res = "1"
    ret = "0"
    return res if res != "1" else ret
print(test())
'''
import re
m = re.search('(?<=-)\w+', 'spam-egg')
print m.group(0)