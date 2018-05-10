import io
import os
import time
from PIL import Image

from tools import log


class Minifyflow(log.Log):
    """
    Use a flow to represent a work flow of intercepting and process intercepted file(HTML/JS/CSS)
    A queue(or list or dict) should be initialized to store file NOT REALLY
    This class should be inherited by all minify class, including but not limited to HTML/JS/CSS
    """

    def __init__(self, functionname, level, log_file):
        super(Minifyflow, self).__init__(functionname, level, log_file)  # A proper way to init parent class, python2
        # notice python3 super(ParentClass, self).__inin__(*kwag **warg)

    @ staticmethod
    def get_host(headers):
        return headers.get("Host", "") if not None else headers.get(":authority", "")

    @staticmethod
    def get_user_agent(headers):
        return headers.get("user-agent", "")

    @staticmethod
    def file_type(headers):
        return headers.get("content-type", "")

    def is_js(self, headers):
        return self.file_type(headers).startswith("text/javascript")

    def is_html(self, headers):
        return self.file_type(headers).startswith("text/html")

    def is_jpeg(self, headers):
        return self.file_type(headers).startswith("image/jpeg")

    def is_png(self, headers):
        return self.file_type(headers).startswith("image/png")

    def is_jpg(self, headers):
        return self.file_type(headers).startswith("image/jpg")

    #  A simple function for storing files as cache, might get removed in the future
    #  WARNING: This is very Cruel and should not be used for more than just test purpose
    def cache_file(self, filename, filecontent, filetype):
        #  print(filename, filetype)
        with open(self.create_dir("Cache") + "\{}{}.{}".format(filename, time.time(), filetype), "wb") as f:
            f.write(filecontent)

    #  A simple function for storing image as cache, might get removed in the future
    #  WARNING: This is very Cruel and should not be used for more than just test purpose
    def cache_image(self, img_name, image, img_format):
        #  print(img_name, img_format)
        with Image.open(io.BytesIO(image)) as img:
            img.save(self.create_dir("Cache") + "\{}{}.{}".format(img_name, time.time(), img_format))

    def process_js(self, flow):
        try:
            if self.is_js(flow.response.headers):
                jsfile = flow.response.content
                msg = self.get_host(flow.request.headers)
                self.log_info("Host: " + msg + " sent a JavaScript file")
                try:
                    self.cache_file(self.get_host(flow.request.headers), jsfile, filetype="js")
                    self.log_info("JS file from " + msg + " has been cached")
                except Exception as e:
                    self.log_error("Something went wrong while caching " + msg + " error: " + str(e))
                    print(str(e))

        except Exception as e:
            print(e)
            self.log_error("Something went wrong while attempting to processing JS file. Error: " + str(e))

    def process_html(self, flow):
        try:
            if self.is_html(flow.response.headers):
                htmlfile = flow.response.content
                msg = self.get_host(flow.request.headers)
                self.log_info("Host: " + msg + " sent a HTML file")
                try:
                    self.cache_file(msg, htmlfile, filetype="html")
                    self.log_info("HTML File from: " + msg + "has been cached")
                except Exception as e:
                    self.log_error("Something went wrong while caching " + msg + " error: " + str(e))
                    print(str(e))
        except Exception as e:
            self.log_error("Something went wrong while attempting to process HTML file. Error: " + str(e))
            print(str(e))

    def process_image(self, flow, img_format):
        try:
            img = flow.response.content
            msg = self.get_host(flow.request.headers)
            self.log_info("Host: " + msg + " sent an image")
            try:
                self.cache_image(msg, img, img_format=img_format)
                self.log_info("Image from " + msg + " has been cached")
            except Exception as e:
                self.log_error("Something went wrong while caching." + msg + " Error: " + str(e))
                print(str(e))

        except Exception as e:
            self.log_error("Something went wrong while attempting to process Image file. Error: " + str(e))
            print(str(e))

    def process_all_img(self, flow):
        if self.is_jpg(flow.response.headers):
            self.process_image(img_format="jpg", flow=flow)
        elif self.is_jpeg(flow.response.headers):
            self.process_image(img_format="jpeg", flow=flow)
        elif self.is_png(flow.response.headers):
            self.process_image(img_format="png", flow=flow)
        flow.response.headers["Edge_Server"] = "ENTIM_Proxy"
    #  A Good Way to get root path
    @staticmethod
    def root_path():
        return os.path.abspath(os.sep)

    @staticmethod
    def create_dir(foldername):
        if not os.path.isdir(foldername):
            os.mkdir(foldername)
        return os.path.abspath(foldername)

    def get_userID(self, flow):
        #  Find out the User ID(IP, Device, UUID)
        return flow.request.headers["User-Agent"]

#  log_file = create_log_file()

#  addons = [Minifyflow(functionname=sys.argv[0], level=logging.INFO, log_file=log_file)]