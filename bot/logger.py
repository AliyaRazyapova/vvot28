import json


class Logger:
    def log(self, level, message, data=None):
        log_message = {"level": level, "message": message}
        if data:
            log_message["data"] = data
        print(json.dumps(log_message))

    def debug(self, message, data=None):
        self.log("DEBUG", message, data)

    def error(self, message, data=None):
        self.log("ERROR", message, data)


logger = Logger()
