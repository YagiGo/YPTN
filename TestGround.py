import time
timestamp = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())
print("Time now is %s" %timestamp)
print(type(timestamp))