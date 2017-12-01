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
        print(Fore.GREEN + "Host is " + htmlfileName)
        open("Cache/{}{}.html".format(htmlfileName, time.time()), "wb").write(htmlfile)
        # TODO Using the Minification System

    if flow.response.headers.get("content-type", "").startswith("text/javascript"):
        jsfile = flow.response.content
        jsfileName = flow.request.headers.get("Host", "")
        if not jsfileName:
            jsfileName = flow.request.headers.get(":authority", "")
        print(Fore.WHITE + Back.BLACK + "JavaScript Files Intercepted!")
        print(Fore.GREEN + "Host is" + jsfileName)
        open("Cache/{}{}.js".format(jsfileName, time.time()), "wb").write(jsfile)
        # TODO Using the Minification System

    """
    Do Something with the images captured
    Jpeg and png format, need to do something about it
    Compression and monitoring
    """
    img_format = flow.response.headers.get("content-type", "")
    if img_format.startswith("image"):
        # TODO The code is too messy and redundant, use @ to rewrite!
        imgname = flow.request.headers.get("Host", "")
        if not imgname:
            imgname = flow.request.headers.get(":authority", "")

        if img_format == "image/jpeg":
            # TODO Do something about the jpeg, for now, just save it as cache
            img_save(imgname, flow, img_format="jpeg")
            img_rotate(flow, img_format="JPEG", content_type="image/jpeg")

        elif img_format == "image/png":
            # TODO Do Something about the png, for now just save it as cache
            img_save(imgname, flow, img_format="png")
            img_rotate(flow, img_format="PNG", content_type="image/png")
        elif img_format == "image/jpg":
            img_save(imgname, flow, img_format="jpg")
            img_rotate(flow, img_format="JPG", content_type="image/jpg")

        elif img_format == "image/gif":
            img_save(imgname,flow, img_format="gif")
            img_rotate(flow, img_format="GIF", content_type="image/gif")

    # TODO Monitoring the User, include but not limited to screen resolution, conncetion speed
def img_save(img_name, flow, img_format):
    try:
        img = Image.open(io.BytesIO(flow.response.content))
        img.save("Cache/" + img_name +"{}.{}".format(time.time(), img_format),
                 img_format)

        print(Fore.WHITE + Back.BLACK + "Image Packet Intercepted, format:%s" %img_format)
        print(Fore.WHITE + Back.BLACK + "Host is" + img_name)
    except Exception as e:
        print(Fore.BLUE + Back.WHITE + e)
def img_rotate(flow, img_format, content_type):
    s = io.BytesIO(flow.response.content)
    img = Image.open(s).rotate(180)
    s2 = io.BytesIO()
    img.save(s2, img_format)
    flow.response.content = s2.getvalue()
    flow.response.headers["content-type"] = content_type