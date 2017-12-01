from tools import log
import logging
import time
import sys
log_created_flag = False
log_file = log.create_log_file()
testlog = log.Log(functionname=sys.argv[0], level=logging.INFO, log_file=log_file)
testlog2 = log.Log(functionname=sys.argv[0], level=logging.INFO, log_file=log_file)
print(sys.argv)
while True:
    if(input("input:") == "1"):
        testlog.log_info("Nothing to see here")
        testlog2.log_info("Nothing to see here either")
    if (input("input:") == "2"):
        testlog3 = log.Log(functionname=sys.argv[0], level=logging.INFO, log_file=log_file)
        testlog3.log_warning("log3: Hello, something wrong here")
        testlog.log_warning("I think something is wrong here...")
        testlog2.log_warning("I think something is wrong here too...")
    if (input("input:") == "3"):
        testlog.log_error("yeah...something wrong here...")
        testlog2.log_error("yeah...something wrong here too...")
    if (input("input:") == "4"):
        testlog.log_critical("Shit is going down!")
        testlog2.log_critical("Shit is going down too!")
    if (input("input:") == "0"):
        break