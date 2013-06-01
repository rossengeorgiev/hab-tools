#!/usr/bin/env python

import sys
import os
import urllib
import time
import datetime
import json
import yaml
import logging

class APRSServerFail(Exception):
    pass

class NoPositionData(Exception):
    pass

class APRS(object):
    def __init__(self, config):
        self.callsign = config["callsign"]
        self.spacenearus_callsign = config["spacenearus"]\
                                        .get("callsign", self.callsign)
        self.sleep = config["sleep"]
        self.aprs_url = config["aprs"]["url"]
        self.aprs_apikey = config["aprs"]["apikey"]
        self.spacenearus_url = config["spacenearus"]["url"]
        self.spacenearus_password = config["spacenearus"]["password"]

    def get_aprs(self):
        logging.debug("Polling APRS")
        url = self.aprs_url.format(callsign=self.callsign,
                                   apikey=self.aprs_apikey)
        response = urllib.urlopen(url).read()
        logging.debug("APRS Response: {0}".format(response))
        response = json.loads(response)

        if response['result'] == "fail":
            raise APRSServerFail

        if response['found'] < 1:
            raise NoPositionData

        data = response['entries'][-1]

        d = datetime.datetime.utcfromtimestamp(int(data["time"]))
        time_str = d.strftime("%H%M%S")

        post_data = {
            "vehicle":  self.spacenearus_callsign,
            "time":     time_str,
            "lat":      data['lat'],
            "lon":      data['lng'],
            "alt":      data.get('altitude', 0),
            "pass":     self.spacenearus_password
        }

        if 'comment' in data:
            post_data["data"] = json.dumps({"comment": data['comment']})

        logging.info("Got: {0}".format(post_data))

        return post_data

    def post_spacenearus(self, data):
        data = urllib.urlencode(data)
        logging.debug("Posting {0}".format(data))
        u = urllib.urlopen(self.spacenearus_url.format(data=data))
        response = u.read()
        logging.info("Submitted")
        logging.debug("spacenearus responded: {0!r}".format(response))

    def run(self):
        while True:
            try:
                self.post_spacenearus(self.get_aprs())
            except KeyboardInterrupt:
                logging.debug("Exiting...")
            except:
                logging.exception("Exception; continuing")

            time.sleep(self.sleep)


DEFAULT_CONFIG = os.path.join(os.path.dirname(__file__),
                              "aprsnear-us-config.yml")

def load_config(filename=DEFAULT_CONFIG):
    with open(filename) as f:
        return yaml.safe_load(f)

def main():
    if len(sys.argv) >= 2:
        config = load_config(sys.argv[1])
    else:
        config = load_config()

    log_level = config["logging_level"].upper()
    logging.basicConfig(level=getattr(logging, log_level),
                        format="[%(asctime)s] %(levelname)s: %(message)s")

    APRS(config).run()

if __name__ == "__main__":
    main()
