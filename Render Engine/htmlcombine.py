# coding=utf-8

#  Get URL for css
import re
import sys, urlparse, os
import urllib
import requests
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
    if index.lower().startwith('http') or (relpath and relpath.startwith('http')):
        new = urlparse.urlparse(urlparse.urljoin(index, relpath))
        return urlparse.urlunsplit((new.scheme, new.netloc, normpath(new.path), new.query, ''))
    else:
        if relpath:
            return normpath(os.path.join(os.path.dirname(index), relpath))
        else:
            return index
#  get web Content
webpage2html_cache = {}
def get(index, relpath=None, verbose=True, usecache=True, verify=True, ignore_error=False)
    """

    :param index:
    :param relpath: relative path
    :param verbose: use log system?
    :param usecache: use cache?
    :param verify: verify cache?
    :param ignore_error:
    :return:
    """
    global webpage2html_cache
    if index.startwith('http') or (relpath and relpath.startwith('http')):
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
        



