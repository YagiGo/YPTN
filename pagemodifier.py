"""
This script rotates all images passing through the proxy by 180 degrees.
"""
import io

# from PIL import Image
from PIL import Image
from mitmproxy import http
import time
from colorama import init, Fore, Back


"""
def response(flow: http.HTTPFlow) -> None:
    if flow.response.headers.get("content-type", "").startswith("image"):
        s = io.BytesIO(flow.response.content)
        img = Image.open(s).rotate(180)
        s2 = io.BytesIO()
        img.save(s2, "png")
        flow.response.content = s2.getvalue()
        flow.response.headers["content-type"] = "image/png"
"""


def response(flow: http.HTTPFlow) -> None:
    # TODO wanna find out the host and create cache accordingly
    # print(flow.request.headers)
    # print(flow.response.headers)
    """
    Find the html and js files for minification purpose
    """
    init() # Color Print from colorama
    if flow.response.headers.get("content-type", "").startswith("text/html"):
        htmlfile = flow.response.content
        htmlfileName = flow.request.headers.get("Host", "")
        if not htmlfileName:
            htmlfileName = flow.request.headers.get(":authority", "")
        print(flow.request.headers.get("user-agent", ""))
        print(Fore.WHITE + Back.BLACK + "HTML Files Intercepted!")
        print(Fore.GREEN + "htmlfilename is " + htmlfileName)
        open("Cache/{}{}.html".format(htmlfileName, time.time()), "wb").write(htmlfile)
        # TODO Using the Minification System

    if flow.response.headers.get("content-type", "").startswith("text/javascript"):
        jsfile = flow.response.content
        jsfileName = flow.request.headers.get("Host", "")
        if not jsfileName:
            jsfileName = flow.request.headers.get(":authority", "")
        print(Fore.WHITE + Back.BLACK + "JavaScript Files Intercepted!")
        print(Fore.GREEN + "jsfilename is" + jsfileName)
        open("Cache/{}{}.js".format(jsfileName, time.time()), "wb").write(jsfile)
        # TODO Using the Minification System

    """
    Do Something with the images captured
    Jpeg and png format, need to do something about it
    Compression and monitoring
    """
    img_format = flow.response.headers.get("content-type", "")
    if ima_format.startswith("image"):
        # TODO The code is too messy and redundant, use @ to rewrite!
        imgname = flow.request.headers.get("Host", "")
        if not imgname:
            imgname = flow.request.headers.get(":authority", "")
        if img_format == "image/jpeg":
            # TODO Do something about the jpeg, for now, just save it as cache
            print(Fore.WHITE + Back.BLACK + "Image Packet Intercepted, format:jpeg")
            #
            s = io.BytesIO(flow.response.content)
            img = Image.open(io.BytesIO(flow.response.content))
            # s2 = io.BytesIO()
            img.save("Cache/{}{}.jpeg".format(imgname, time.time()), "JPEG")
            # open("{}.png".format(time.time()), "wb").write(s2)
            # flow.response.content = s2.getvalue()
            # Convert JPEG to PNG, NOT necessary
            # flow.response.content = s2.getvalue()
            # flow.response.headers["content-type"] = "img/jpeg"

        elif img_format == "image/png":
            # TODO Do Something about the png, for now just save it as cache
            # s = io.BytesIO(flow.response.content)
            img = Image.open(io.BytesIO(flow.response.content))  # A test without actual use
            img.save("Cache/{}{}.png".format(imgname,time.time()), "PNG")
            # open("{}.png".format(time.time()), "wb").write(s2)
            # flow.response.content = s2.getvalue()
            # Convert JPEG to PNG, NOT necessary
            # flow.response.content = s2.getvalue()
            # flow.response.headers["content-type"] = "img/png"
            print(Fore.WHITE + Back.BLACK + "Image Packet Intercepted, format:png")
        elif img_format == "image/jpg":
            img = Image.open
    # TODO Monitoring the User, include but not limited to screen resolution, conncetion speed