# coding=utf-8

#  Get URL for css
# encoding=utf8
import re
import sys, urlparse, os
import urllib
import requests
import base64
from bs4 import BeautifulSoup
import datetime, time
from multiprocessing import Pool
#  from cachesave import savetoAndReadfromDB
from pymongo import MongoClient
re_css_url = re.compile('(url\(.*?\))') #  get css url

#  colored logging, at present, stderr is used, may shift to log file system
try:
    from termcolor import colored
except:
    def colored(text, color=None, on_color=None, attrs=None):
        return text
def log(s, color=None, on_color=None, attrs=None, new_line=True):
    if not color:
        #  使用 print >> std, str 把输出字符串定义到stderr
        #  new_line: 是否换行
        print >> sys.stderr, str(s)
    else:
        print >> sys.stderr, colored(str(s), color, on_color, attrs)

    if new_line:
        print >> sys.stderr.write("\n")
    sys.stderr.flush()
#  convert all relpath to abspath
"""
    将urlstring解析成6个部分，它从urlstring中取得URL，并返回元组 (scheme, netloc, path, parameters, query, fragment)，
    但是实际上是基于namedtuple，是tuple的子类。它支持通过名字属性或者索引访问的部分URL，每个组件是一串字符，也有可能是空的。
    组件不能被解析为更小的部分，%后面的也不会被解析，分割符号并不是解析结果的一部分，除非用斜线转义，注意，返回的这个元组非常有用，
    例如可以用来确定网络协议(HTTP、FTP等等 )、服务器地址、文件路径，等等。

    >>> import urlparse
    >>> parsed_tuple = urlparse.urlparse("http://www.google.com/search?hl=en&q=urlparse&btnG=Google+Search")
    >>> print parsed_tuple
    ParseResult(scheme='http',
    netloc='www.google.com',
    path='/search',
    params='',
    query='hl=en&q=urlparse&btnG=Google+Search',
    fragment='')
"""
def absurl(index, relpath=None, normpath=None):
    if normpath is None:
        normpath = lambda x:x
    #  Process for relpath
    if index.lower().startswith('http') or (relpath and relpath.startswith('http')):
        new = urlparse.urlparse(urlparse.urljoin(index, relpath))
        return urlparse.urlunsplit((new.scheme, new.netloc, normpath(new.path), new.query, ''))
    else:
        if relpath:
            return normpath(os.path.join(os.path.dirname(index), relpath))
        else:
            return index
#  get web Content
webpage2html_cache = {}
def get(index, relpath=None, verbose=True, usecache=True, verify=True, ignore_error=False):
    """

    :param index:
    :param relpath: relative path
    :param verbose: use log system?
    :param usecache: use cache?
    :param verify: verify cache?
    :param ignore_error:
    :return: content(str), extra_data(dict, url, content-type e.t.c)
    """
    global webpage2html_cache
    if index.startswith('http') or (relpath and relpath.startswith('http')):
        fullpath = absurl(index, relpath)
        if not fullpath:
            if verbose: log('[WARN] invalid path, %s %s' %(index, relpath), 'yellow')
            return '', None
        # urllib2 only accepts valid url, the following code is taken from urllib
        # http://svn.python.org/view/python/trunk/Lib/urllib.py?r1=71780&r2=71779&pathrev=71780
        #  按照标准， URL 只允许一部分 ASCII 字符（数字字母和部分符号），其他的字符（如汉字）是不符合 URL 标准的。
        #  所以 URL 中使用其他字符就需要进行 URL 编码
        fullpath = urllib.quote(fullpath, safe="%/:=&?~#+!$,;'@()*[]")
        if usecache:
            if fullpath in webpage2html_cache:
                if verbose: log('[CACHE-HIT] -%s' %fullpath)
                return webpage2html_cache[fullpath], None
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)'
        }
        try:
            response = requests.get(fullpath, headers=headers, verify=verify)
            #  Some web page not encoded with UTF-8, which could cause problem
            # TODO need an RE here to find out the encoding


            if verbose: log('[GET] %d -%s' %(response.status_code, response.url))
            if not ignore_error and response.status_code >= 400 or response.status_code < 200:
                content = ''
            else:
                content = response.content
            if usecache:
                #  Save as Cache
                webpage2html_cache[response.url] = response.content
            return content, {'url':response.url, 'content-type':response.headers.get('content-type')}
        except Exception as ex:
            if verbose: log('[WARN] Opps - %s %s' %(fullpath, ex), 'yellow')
            return '', None

    elif os.path.exists(index):
        if relpath:
            relpath = relpath.split('#')[0].split('?')[0]
            if os.path.exists(relpath):
                fullpath = relpath
            else:
                #  Normalize a pathname by collapsing redundant separators and up-level references
                #  so that A//B, A/B/, A/./B and A/foo/../B all become A/B.
                fullpath = os.path.normpath(os.path.join(os.path.dirname(index), relpath))
            try:
                ret = open(fullpath, 'rb').read()
                if verbose: log('[LOCAL] found - %s' %fullpath)
                return ret, None
            except IOError as err:
                #  Head up: IOError
                if verbose: log('[WARN] file not found - %s %s'%(index, str(err)), 'yellow')
                return '', None
        else:
            try:
                ret = open(index, 'rb').read()
                if verbose: log('[LOCAL] found - %s' %index)
                return ret, None
            except IOError as err:
                #  Head up: IOError
                if verbose: log('[WARN] file not found - %s %s'%(index, str(err)), 'yellow')
                return '', None
    else:
        if verbose: log('[ERROR] invalid index - %s' %index, 'red')
        return '', None

#  use data URI scheme to inclde data in-line in web pages see  http://en.wikipedia.org/wiki/Data_URI_scheme
#  related introduction(Chinese Version) https://www.jianshu.com/p/ea49397fcd13
#  Basic format of Data URI
"""
data:[<mime type>][;charset=<charset>][;<encoding>],<encoded data>
1.  data ：协议名称；
2.  [<mime type>] ：可选项，数据类型（image/png、text/plain等）
3.  [;charset=<charset>] ：可选项，源文本的字符集编码方式
4.  [;<encoding>] ：数据编码方式（默认US-ASCII，BASE64两种）
5.  ,<encoded data> ：编码后的数据
"""
def data_to_base64(index, src, verbose=True):
    sp = urlparse.urlparse(src).path.lower()
    if src.strip().startswith('data:'):
        return src
    if sp.endswith('.png'):
        fmt = 'image/png'
    elif sp.endswith('.gif'):
        fmt = 'image/gif'
    elif sp.endswith('.ico'):
        fmt = 'image/x-icon'
    elif sp.endswith('.jpg') or sp.endswith('.jpeg'):
        fmt = 'image/jpg'
    elif sp.endswith('.svg'):
        fmt = 'image/svg+xml'
    elif sp.endswith('.ttf'):
        fmt = 'application/x-font-ttf'
    elif sp.endswith('.otf'):
        fmt = 'application/x-font-opentype'
    elif sp.endswith('.woff'):
        fmt = 'application/font-woff'
    elif sp.endswith('.woff2'):
        fmt = 'application/font-woff2'
    elif sp.endswith('.eot'):
        fmt = 'application/vnd.ms-fontobject'
    elif sp.endswith('.sfnt'):
        fmt = 'application/font-sfnt'
    elif sp.endswith('.css') or sp.endswith('.less'):
        fmt = 'text/css'
    elif sp.endswith('.js'):
        fmt = 'application/javascript'
    else:
        # what if it's not a valid font type? may not matter
        fmt = 'image/png'
    data, extra_data = get(index, src, verbose)
    if extra_data and extra_data.get('content-type'):
        fmt = extra_data.get('content-type').replace(' ', '')
    if data:
        return('data:%s;base64,'%fmt) + base64.b64encode(data)
    else:
        return absurl(index, src)


#  Handle CSS
css_encoding_re = re.compile(r'''@charset\s+["']([-_a-zA-Z0-9]+)["']\;''', re.I)

def handle_css_content(index, css, verbose=True):
    if not css:
        return css
    if not isinstance(css, unicode):
        #  if css file is not unicode encoded, try to convert it into unicode
        mo = css_encoding_re.search(css)
        if mo:
            try:
                css = css.decode(mo.group(1))
            except:
                log('[WARN] failed to convert css to encoding %s'%mo.group(1), 'yellow')
    reg = re.compile(r'url\s*\((.+?)\)')

    def repl(matchobj):
        src = matchobj.group(1).strip('\'"')
        return 'url(' + data_to_base64(index, src, verbose=verbose) + ')'
        return 'url(' + data_to_base64(index, src, verbose=verbose) + ')'
    css = reg.sub(repl, css)
    return css
def generate(index, verbose=True, comment=True, keep_script=True, prettify=False, full_url=True, verify=False, erropage=False):
    orgin_index = index
    html_doc, extra_data = get(index, verbose=verbose, verify=verify, ignore_error=erropage)
    if extra_data and extra_data.get('url'):
        index = extra_data['url']
    soup = BeautifulSoup(html_doc, 'lxml')
    soup_title = soup.title.string if soup.title else ''
    for link in soup('link'):
        """
        <link href="/index.html" rel="index"/>
        <link href="/css/import.css" media="screen, tv, projection" rel="stylesheet" type="text/css"/>
        """
        #  print link
        if link.get('href'):
            if 'mask-icon' in (link.get('rel') or []) or 'icon' in(link.get('rel') or []) or 'apple-touch-icon' in (link.get('rel') or []) or 'apple-touch-icon-precomposed' in (link.get('rel') or []):
                #  Convert icon into URI form with base64
                link['data-href'] = link['href']
                link['href'] = data_to_base64(index, link['href'], verbose=verbose)
                #  print link['href']
            #  now the css part needs to be handled encoding with base64
            elif link.get('type') == 'text/css' or link['href'].lower().endswith('.css') or 'stylesheet' in (link.get('rel') or []):
                new_type = 'text/css' if not link.get('type') else link['type']
                css = soup.new_tag('style', type=new_type)
                #  print link['href']
                css['data-href'] = link['href']
                #  print link
                """
                <link href="/yts/cssbin/player-vflUq7Z-t/www-player.css" name="player/www-player" rel="stylesheet"/>
                attrs:href, name, rel
                """
                for attr in link.attrs:
                    if attr in ['href']: continue  #  ignore href
                    css[attr] = link[attr]
                css_data, _ = get(index, relpath=link['href'], verbose=verbose)
                new_css_content = handle_css_content(absurl(index, link['href']), css_data, verbose=verbose)
                if False:
                    link['href'] = 'data:text/css;base64,' + base64.b64encode(new_css_content)
                else:
                    css.string = new_css_content
                    link.replace_with(css)
            elif full_url:
                link['data-href'] = link['href']
                link['href'] = absurl(index, link['href'])
    #  Embed js script with base64 encoding
    #  TODO in the future, try to execute js files on the server and transmit result to the client
    for js in soup('script'):
        if not keep_script:
            js.replace_with('')
            continue
        if not js.get('src'): continue
        new_type = 'text/javascript' if not js.has_attr('type') or not js['type'] else js['type']
        code = soup.new_tag('script', type=new_type)
        code['data-src'] = js['src']
        try:
            js_str, _ = get(index, relpath=js['src'], verbose=verbose)
            if js_str.find('</script>') > -1:
                code['src'] = 'data:text/javascript;base64,' + base64.b64encode(js_str)
            #  the CDATA part
            elif js_str.find(']]>') < 0:
                code.string = '<!--//--><![CDATA[//><!--\n' + js_str + '\n//--><!]]>'
            else:
                code.string = js_str.encode('utf-8')
            """
            被<![CDATA[]]>这个标记所包含的内容将表示为纯文本，比如<![CDATA[<]]>表示文本内容“<”。 
            此标记用于xml文档中，我们先来看看使用转义符的情况。
            我们知道，在xml中，”<”、”>”、”&”等字符是不能直接存入的，否则xml语法检查时会报错，
            如果想在xml中使用这些符号，必须将其转义为实体，如”&lt;”、”&gt;”、”&amp;”，这样才能保存进xml文档。 
            在使用程序读取的时候，解析器会自动将这些实体转换回”<”、”>”、”&”。
            举个例子： 
            <age> age < 30 </age> 
            上面这种写法会报错，应该这样写： 
            <age> age &lt; 30 </age> 
             """
        except:
            if verbose: log(repr(js_str))
            raise
        js.replace_with(code)
    #  encode img with base64 and URI scheme
    # try use multiprocessing
    """
    def check_alt(attr):
        if img.has_attr(attr) and img[attr].startswith('this.src='):
            if verbose: log('[WARN] %s found in img tag and unhandled, which may be broken' % attr, 'yellow')
    def process_img(img):
        if img.get('src'):
            img['data-src'] = img['src']
            img['src'] = data_to_base64(index, img['src'], verbose=verbose)
            # `img` elements may have `srcset` attributes with multiple sets of images.
            # To get a lighter document it will be cleared, and used only the standard `src` attribute
            # Maybe add a flag to enable the base64 conversion of each `srcset`?
            # For now a simple warning is displayed informing that image has multiple sources
            # that are stripped.
            # TODO handle srcset
            if img.get('srcset'):
                img['data-srcset'] = img['srcset']
                del img['srcset']
                if verbose: log(
                    '[WARN] srcset found in img tag. Attribute will be cleared. File src = %s' % img['data-src'], 'yellow')

        # For any other situation that can not be handled at this stage, just warn the user

        # fail to load

        #  <img src="image.gif" onerror="alert('The image could not be loaded.')" />
        check_alt('onerror')
        # onmouseover and onmouseout
        check_alt('onmouseover')
        check_alt('onmouseout')
    """
    # Multiprocessing here
    # functions are only picklable if they are defined at the top-level of a module.
    """
    for img in soup('img'):
        if not img.get('src'): continue
        img['data-src'] = img['src']
        img['src'] = data_to_base64(index, img['src'], verbose=verbose)
        # `img` elements may have `srcset` attributes with multiple sets of images.
        # To get a lighter document it will be cleared, and used only the standard `src` attribute
        # Maybe add a flag to enable the base64 conversion of each `srcset`?
        # For now a simple warning is displayed informing that image has multiple sources
        # that are stripped.
        # TODO handle srcset
        if img.get('srcset'):
            img['data-srcset'] = img['srcset']
            del img['srcset']
            if verbose: log('[WARN] srcset found in img tag. Attribute will be cleared. File src = %s' %img['data-src'], 'yellow')
        #  For any other situation that can not be handled at this stage, just warn the user
        def check_alt(attr):
            if img.has_attr(attr) and img[attr].startswith('this.src='):
                if verbose: log('[WARN] %s found in img tag and unhandled, which may be broken'%attr, 'yellow')
        # fail to load

        #  <img src="image.gif" onerror="alert('The image could not be loaded.')" />
        check_alt('onerror')
        # onmouseover and onmouseout
        check_alt('onmouseover')
        check_alt('onmouseout')
    """
    for tag in soup(True):

        if full_url and tag.name == 'a' and tag.has_attr('href') and not tag['href'].startswith('#'):
            #  Hyperlink
            tag['data-href'] = tag['href']
            tag['href'] = absurl(index, tag['href'])
        if tag.has_attr('style'):
            #  print tag
            # style sheet
            if tag['style']:
                tag['style'] = handle_css_content(index, tag['style'], verbose=verbose)
                #  print tag['style']
            elif tag.name == 'link' and tag.has_attr('type') and tag['type'] == 'text/css':
                if tag.string:
                    tag.string = handle_css_content(index, tag.string, verbose=verbose)
            elif tag.name == 'style':
                if tag.string:
                    tag.string = handle_css_content(index, tag.string, verbose=verbose)
    # Insert some comment
    if comment:
        for html in soup('html'):
            html.insert(0, BeautifulSoup(
                '<!-- \n single html Orginal:https://github.com/zTrix/webpage2html\n Modified by https://github.com/YagiGo\n title: %s\n url: %s\n date: %s\n-->' % (
                soup_title, index, datetime.datetime.now().ctime()
            ), 'lxml'))
            break
    if prettify:
        return soup.prettify(formatter='html')
    else:
        return str(soup)
#  DB CACHE

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

    def isexpired(cache, threshold):
        current_time = time.strptime(str(datetime.datetime.utcnow()).split('.')[0], "%Y-%m-%d %H:%M:%S")
        current_timestamp = int(time.mktime(current_time))
        cache_time = time.strptime(cache['date'].split('.')[0], "%Y-%m-%d %H:%M:%S")
        cache_timestamp = int(time.mktime(cache_time))
        live_time = current_timestamp - cache_timestamp
        #  print "live time" + str(live_time)
        if live_time > threshold:
            return True
        else:
            return False
    if not existcache:
        try:
            htmlsrc = generate(url)
            cachefile = {
                "url": str(hash(url)), "src": htmlsrc, "date": str(datetime.datetime.utcnow()),
                "recent_access_time": 1
            }
            cachefile_id = webcache.insert_one(cachefile).inserted_id
        except  Exception as err:
            err_handle = {
                "url": str(hash(url)),
                "Error": "ERROR %s"%str(err), "date": str(datetime.datetime.utcnow())
            }
            cachefile_id = webcache.insert_one(err_handle).inserted_id
    elif isexpired(existcache, threshold):
        try:
            #  update src file and datetime
            htmlsrc = generate(url)
            #  print "expired!"
            #  existcache['src'] = htmlsrc
            #  print existcache['date']
            #  existcache['date'] = str(datetime.datetime.utcnow())
            #  修改记录 db.Account.update({"UserName":"libing"},{"$set":{"Email":"libing@126.com","Password":"123"}})

            webcache.update_one({'url':str(hash(url))}, {"$set" : {"src":htmlsrc, "date":str(datetime.datetime.utcnow())}})
        except Exception as err:
            err_handle = {
                "url": str(hash(url)),
                "Error": "ERROR %s"%str(err), "date": str(datetime.datetime.utcnow())
            }
            cachefile_id = webcache.insert_one(err_handle).inserted_id
    # return HTML page if there is nothing wrong else return an Error page
    try:
        return webcache.find_one({"url" : str(hash(url))})['src']
    except Exception as err:
        return "Opps, it appears that something went wrong" + str(err)
#  TODO Create a database for image encoding to avoid redundancy.

def isexpired(cache, threshold):
    current_time = time.strptime(str(datetime.datetime.utcnow()).split('.')[0], "%Y-%m-%d %H:%M:%S")
    current_timestamp = int(time.mktime(current_time))
    cache_time = time.strptime(cache['date'].split('.')[0], "%Y-%m-%d %H:%M:%S")
    cache_timestamp = int(time.mktime(cache_time))
    live_time = current_timestamp - cache_timestamp
    #  print "live time" + str(live_time)
    if live_time > threshold:
        return True
    else:
        return False




def mergeHTML(conn, url, output):
    """

    :param url: access url
    :param output: processed html src
    :param conn: database connection
    :return: NONE
    """

    """
    if url in page_cache:
        rs = page_cache[url]
    else:
        rs = generate(url, output)
        page_cache[url] = rs
    with open(output, 'wb') as f:
        f.write(rs)
    """
    reload(sys)
    sys.setdefaultencoding('utf8') #  This is the pain in the ass for python in windows, set sys to utf8 to avoid ascii bs!
    # rs = generate(url)
    with open(output, "wb") as f:
        f.write(savetoAndReadfromDB(conn, url, threshold=600))
    #  print page_cache
    #  print savetoAndReadfromDB(conn, url, threshold=600)


    #  TODO Emmmm...  There may be other things that need to be done
    #  return html_doc
    #  return soup_title


if __name__ == '__main__':
    #  CACHE DB CONFIG HERE
    HOST = "localhost"
    PORT = 27017
    test_url1 = "https://realpython.com/blog/python/introduction-to-mongodb-and-python/"

    test_url2 = "https://www.taobao.com/"
    test_url3 = "https://developer.mozilla.org/zh-CN/docs/Web/API/GlobalEventHandlers/onerror"
    test_url4 = "http://www.amazarashi.com/top/"
    test_urls = [
            "https://www.baidu.com",
            "https://www.gooogle.com",
            "https://www.yahoo.co.jp",
            "https://www.imdb.com",
            "https://www.yahoo.com",
            "https://www.twitter.com",
            "https://www.microsoft.com",
            "http://www.softlab.cs.tsukuba.ac.jp/members.html",
            "https://github.com/YagiGo"
        ]
    test_urls2 = [
        "https://www.yahoo.co.jp",
        "https://news.yahoo.co.jp/pickup/6273847",
        "https://news.yahoo.co.jp/pickup/6273853"
        "https://headlines.yahoo.co.jp/hl?a=20180301-00138618-nksports-fight"

    ]
    conn = MongoClient(HOST, PORT)
    output = "test.html"
    first_start_time = time.time()
    for url in test_urls:
        start_time = time.time()
        mergeHTML(conn, url, output)
    #  print test_return
        end_time = time.time()
        print ("url: %s" %url + "\ntime cost: %s"%(str(end_time - start_time)))


    # mergeHTML(conn, img_url, output)
    final_end_time = time.time()
    print ("total time cost: %s" % (str(final_end_time - first_start_time)))
#  TODO 使用数据库（推荐MongoDB）缓存转换好的HTML文件，按照LRU算法对缓存文件进行更新，在用户访问某网站时直接调用缓存
#  TODO 但是对很多实时性要求高的网站不能使用这个方法(SNS)
#  TODO 对这类网站加上标签，然后直接访问，不经过HTML转换
#  TODO 加标签的方法，emmmm 机器学习走一波