#!usr/bin/python3.6
import requests
import ast
import time
import os
import csv
from Proxy.IPProxy import getIPProxies
import traceback

def manification(js_code, compilation_level, output_info):
    # TODO Using Proxies to Reduce Server Decline Rate
    params = {
        'js_code': js_code,
        'compilation_level': compilation_level,
        'output_format': 'json',
        'output_info': output_info
    }
    '''
    code_url: location of the JS script
    compilation_level: WHITESPACE_ONLY, SIMPLE_OPTIMIZATIONS, ADVANCED_OPTIMIZATIONS
    output_info:compiled_code, warnings,errors, statistics
    '''
    # Using POST method to process js file
    succeed_flag = 0  # Check if compiling succeed
    headers = {"Content=type": "application/x-www-form-urlencode"}
    while(succeed_flag == 0):
        try:
            proxy = getIPProxies()
            print(proxy)
            conn = requests.post('https://closure-compiler.appspot.com/compile', proxies=proxy, data=params, headers=headers)
            succeed_flag = 1
        except Exception as e:
            print(str(e))
    # Do not change header
    result = ast.literal_eval(conn.text)  # Using ast lib to convert str to dict
    if "serverErrors" in result:
        err_flag = 1
        err_msg = result["serverErrors"][0]
        return err_flag, err_msg
    else:
        err_flag = 0
        return err_flag, result["compiledCode"]


def evaluate(result, url, test_result):
    eval_result = ast.literal_eval(result)  # Using ast lib to convert str to dict
    try:

        compressed = int(eval_result['statistics']['originalSize']) - int(eval_result['statistics']['compressedSize'])
        if compressed < 0:
            test_result.append((url, 'Compression not Effective!', '', ''))
        else:
            test_result.append((url, result['statistics']['originalSize'], result['statistics']['compressedSize'], compressed))

    except Exception as err:
        test_result.append((url, 'Failed with err' + str(err), '', '', ''))


if __name__ == '__main__':
    testJS = "var aPageStart = (new Date()).getTime();"
    err_check, result = manification(testJS, compilation_level="SIMPLE_OPTIMIZATIONS", output_info="compiled_code")
    if(err_check):
        print("Compile Failed with ERROR CODE:" + str(result["code"]) + " " + result["error"])
    else:
        print(result)
