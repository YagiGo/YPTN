import requests
from Proxy.IPProxy import *
def manification(js_code, compilation_level, output_info):
    # TODO Using Proxies to Reduce Server Decline Rate
    data = dict(input = js_code)
    succeed_flag = 0  # Check if compiling succeed
    while(succeed_flag == 0):
        try:
            #  proxy = getIPProxies()
            #  print(proxy)
            conn = requests.post('https://javascript-minifier.com/raw', data=data)
            succeed_flag = 1
        except Exception as e:
            print(str(e))
    # Do not change header
    # result = ast.literal_eval(conn.text)  # Using ast lib to convert str to dict
    '''
    if "serverErrors" in result:
        err_flag = 1
        err_msg = result["serverErrors"][0]
        return err_flag, err_msg
    else:
        err_flag = 0
        return err_flag, result["compiledCode"]
    '''
    return conn.text