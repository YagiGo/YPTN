# from JSMinimizing.CCJS import manification, evaluate
from JSMinimizing.getSrc import *
import pagemodifier
import time
if __name__ == '__main__':
    '''
    testJS = [
        'https://images-fe.ssl-images-amazon.com/images/G/01/AUIClients/ClientSideMetricsAUIJavascript-8c1980e96f6cf47481b4002e1807fbe4b06c90da._V2_.js',
        'https://g.alicdn.com/kg/??combobox/6.2.7/index-min.js,search-suggest/6.3.1/mods/local-query-min.js,search-suggest/6.3.1/mods/menu-min.js,search-suggest/6.3.1/tpl/cloud-min.js,search-suggest/6.3.1/mods/bts-min.js,uploader/6.2.13/index-min.js,uploader/6.2.13/plugins/auth/auth-min.js,uploader/6.2.13/plugins/filedrop/filedrop-min.js,search-suggest/6.3.1/mods/stat-min.js,uploader/6.2.13/theme-min.js',
        'https://s.yimg.jp/images/top/sp2/js/8.0.17/fp_base_bd_ga_8.0.17.js',
        'https://s1.hdslb.com/bfs/static/jinkela/home/home.a847a847.js',
        'http://127.0.0.1:8887/jsfile.js'
    ]
    # JS File Source: Amazon Japan, Taobao, Yahoo Japan, Youtube, Bilibili
    for url in testJS:
        # print(url)
        # print(type((manification(url, 'SIMPLE_OPTIMIZATIONS', 'statistics'))))
        start_time = time.time()
        print(
            evaluate(
                manification(
                    url,
                    'SIMPLE_OPTIMIZATIONS',
                    'statistics')))
        end_time = time.time()
        print('time cost:' + str(int(end_time - start_time)))
    '''
    # Test Sites: Alexa Top 50 Sites
    test_sites = [
        'https://www.google.com',
        'https://www.youtube.com',
        'https://www.facebook.com',
        'https://www.baidu.com',
        'https://www.wikipedia.org',
        'https://www.yahoo.com',
        'https://www.reddit.com',
        'https://www.qq.com',
        'https://www.taobao.com',
        'https://www.amazon.com',
        'https://www.tmall.com',
        'https://www.twitter.com',
        'https://www.sohu.com',
        'https://www.live.com',
        'https://www.vk.com',
        'https://www.instagram.com',
        'https://www.sina.com.cn',
        'https://www.360.cn',
        'https://www.jd.com',
        'https://www.linkedin.com',
        'https://www.weibo.com',
        'https://www.yahoo.co.jp',
        'https://www.yandex.ru',
        'https://www.netflix.com',
        'https://www.t.co',
        'https://www.hao123.com',
        'https://www.imgur.com',
        'https://www.wordpress.com',
        'https://www.msn.com',
        'https://www.aliexpress.com',
        'https://www.bing.com',
        'https://www.tumblr.com',
        'https://www.microsoft.com',
        'https://www.stackoverflow.com',
        'https://www.twitch.tv',
        'https://www.amazon.co.jp',
        'https://www.soso.com',
        'https://www.apple.com',
        'https://www.naver.com',
        'https://www.imdb.com',
        'https://www.tianya.cn',
        'https://www.office.com',
        'https://www.github.com',
        'https://www.pinterest.com',
        'https://www.paypal.com',
        'https://www.adobe.com',
        'https://www.wikia.com',
        'https://www.cnzz.com',
        'https://www.rakuten.co.jp',
        'http://www.soundcloud.com',
        'http://www.bilibili.com'
    ]
    header = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'accept-language',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    # header is something needed to be modified if deployed
    i = 1
    custom_site = ['https://www.taobao.com','https://www.facebook.com',
                   'https://www.youtube.com','https://www.weibo.com','https://www.twitter.com',
                   'https://www.imdb.com','https://www.bilibili.com','https://www.niconicovideo.jp']
    failed_site = ['https://www.amazon.co.jp']
    for site in failed_site:
        mod_files = SiteSrcFiles(site, header)
        start_time = time.time()
        print("Processing No.{}".format(i))
        mod_files = SiteSrcFiles(site, header)
        mod_files.getjsmodified()
        end_time = time.time()
        print("Time Cost for No.{}:{}".format(i, end_time - start_time))
        i += 1
