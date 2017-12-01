
import datetime
import logging
"""
This file is for logging crucial and critical information
"""


def create_log_file():
    """

    :param log_created_flag: bool if True, the log file has been created, no need to create anymore
    should be set to False at First
    :return:  log_created_flag and fh
    """
    try:
        timetag = datetime.datetime.now().strftime("%b_%d_%y %H_%M_%S")
        fh = logging.FileHandler("%s.log" % timetag)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        print("log file created!")
        log_created_flag = True
        return fh
    except Exception:
        return None


class Log:
    """
    An abstract class for logging, should be inherited by all minify class,
    including but not limited to HTML/JS/CSS
    """

    def __init__(self, functionname, level, log_file):
        self.logger = logging.getLogger(functionname)
        self.logger.addHandler(log_file)
        self.logger.setLevel(level)

    def log_info(self, info):
        self.logger.info(info)
        """

        :param info: logging info
        :return: None
        """

    def log_warning(self, warning):
        self.logger.warning(warning)
        """

        :param warning: logging warning
        :return: None
        """

    def log_error(self, error):
        """

        :param error: logging error
        :return: None
        """
        self.logger.error(error)

    def log_critical(self, critical):
        """

        :param critical: logging critical error
        :return: None
        """
        self.logger.critical(critical)
