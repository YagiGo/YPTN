# coding=utf-8

#  Get URL for css
import re
import sys, urlparse, os
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



