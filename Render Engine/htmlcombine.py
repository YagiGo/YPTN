# coding=utf-8

#  Get URL for css
import re
import sys, urlparse, os
import urllib
import requests
import base64
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
            print response.headers['Content-Type'].find('charset')



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
    css = reg.sub(repl, css)
    return css

def generate(index, verbose=False, comment=True, keep_script=True, prettify=False, full_url=True, verify=False, erropage=False):
    orgin_index = index
    html_doc, extra_data = get(index, verbose=verbose, verify=verify, ignore_error=erropage)
    #  return html_doc


if __name__ == '__main__':
    url = "http://www.softlab.cs.tsukuba.ac.jp/index.html.en"

    test_url="https://www.google.com"

    print generate(test_url)