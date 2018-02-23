import os
from selenium import webdriver
Firefox_path = 'C:\geckodriver-v0.19.1-win64\geckodriver.exe'
PhantomJs_path = 'C:\phantomjs\phantomjs.exe'
import unittest
from selenium import webdriver
def getScreenShoot(url):
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless")  # No Browser Showed
    driver = webdriver.Firefox(executable_path=Firefox_path, firefox_options=firefox_options)
    driver.get(url)
    driver.save_screenshot('test_screenshoot.png')
    driver.quit()
def getHtmlSource(url):
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless")  # No Browser Showed
    driver = webdriver.Firefox(executable_path=Firefox_path, firefox_options=firefox_options)
    driver.get(url)
    html = driver.page_source
    return html
def getWholePagewithWget(url, dir):
    """

    :param url: destination
    :param dir: directory to save the page
    :return:
    """
    wget = "wget -p -k -P {} {}".format(dir, url)
    os.system(wget)
'''
class TestOne(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.PhantomJS(executable_path=PhantomJs_path)
        self.driver.set_window_size(1120, 550)

    def test_url(self):
        self.driver.get("http://duckduckgo.com/")
        self.driver.find_element_by_id(
            'search_form_input_homepage').send_keys("realpython")
        self.driver.find_element_by_id("search_button_homepage").click()
        self.assertIn(
            "https://duckduckgo.com/?q=realpython", self.driver.current_url
        )

    def tearDown(self):
        self.driver.quit()
'''
if __name__ == '__main__':
    url = "https://www.youtube.com"
    lab_url = "http://www.softlab.cs.tsukuba.ac.jp/research.html"
    #  getScreenShoot(url)
    #  print (getHtmlSource(url))
    dir = "./TestFiles"
    getWholePagewithWget(url, dir)


