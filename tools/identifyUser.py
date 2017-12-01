from ua_parser import user_agent_parser
import pprint
class IdentifyDevice(object):
    def __init__(self, flow):
        self.flow = flow

    def get_user_agent(self):
        return self.flow.request.headers["User-Agent"]

    def parse_ua(self):
        return user_agent_parser.Parse(self.get_user_agent())
    @staticmethod
    def return_os(ua):
        return ua["os"]["family"]

    @staticmethod
    def return_browser(ua):
        return ua["user_agent"]["family"]

    @staticmethod
    def return_device(ua):
        return  ua["device"]["family"]

    def get_os(self):
        return self.return_os(self.parse_ua(self.get_user_agent()))

    def get_browser(self):
        return self.return_os(self.parse_ua(self.get_user_agent()))

    def get_device(self):
        return self.return_device(self.parse_ua(self.get_user_agent()))


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    ua_string = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    parsed_string = user_agent_parser.Parse(ua_string)
    pp.pprint(parsed_string["os"]["family"])