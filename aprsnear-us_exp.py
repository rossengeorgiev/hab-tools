#!/usr/bin/env python

import sys
import os
import urllib
import time
import datetime
import json
import yaml
import logging
import re

class APRSServerFail(Exception):
    pass

class NoPositionData(Exception):
    pass

class DuplicateData(Exception):
    pass

class APRS(object):
    def __init__(self, config):
        self.callsign = config["callsign"]
        self.spacenearus_callsign = config["spacenearus"]\
                                        .get("callsign", self.callsign)
        self.sleep = config["sleep"]
        self.aprs_url = config["aprs"]["url"]
        self.aprs_tele_url = config["aprs"]["tele_url"]
        self.aprs_apikey = config["aprs"]["apikey"]
        self.spacenearus_url = config["spacenearus"]["url"]
        self.spacenearus_password = config["spacenearus"]["password"]
        self.prev_timestamp = 0
        self.prev_tele_timestamp = 0

    def get_telemtry(self):
        logging.debug("Polling Telemtry")
        url = self.aprs_tele_url.format(callsign=self.callsign)
        response = urllib.urlopen(url).read()

        # find the name of the fields
        fields =  re.findall(r"700px;'>{0} +(.*?)   ".format(self.callsign), response)

        if len(fields) == 0:
            logging.debug("No telemetry available")
            return {}

        logging.debug("Fields: {0}".format(fields))

        # find the latest data
        tmp = re.sub(r" ([a-z]+): ",r' "\1": ', re.findall(r"_d \= \[.*", response)[0]).split(';')

        if len(tmp) == 0:
            logging.debug("No data for fields???")
            return {}

        data = {}
        idx = 0

        last_ts = self.prev_tele_timestamp

        for line in tmp:
            if line[:5] == "_d = ":
                ts,dpoint = json.loads(line[5:])[0]['data'][-1]

                last_ts = ts

                data[fields[idx]] = dpoint;
                idx += 1

        if last_ts == self.prev_tele_timestamp:
            logging.debug("Ignoring duplicate telemetry")
            return {}

        self.prev_tele_timestamp = last_ts

        logging.debug("Telemetry: {0}".format(data))
        return data

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

        """
        time - the time when the target first reported this (current) position (the time of arrival at current coordinates)
        lasttime - the time when the target last reported this (current) position
        """
        timestamp = int(data["time"])
        #timestamp = int(data["lasttime"])

        # duplicate data is discarded and not posted to spacenear.us
        if self.prev_timestamp >= timestamp:
            raise DuplicateData

        self.prev_timestamp = timestamp

        d = datetime.datetime.utcfromtimestamp(timestamp)
        time_str = d.strftime("%H%M%S")

        post_data = {
            "vehicle":  self.spacenearus_callsign,
            "callsign": "APRS",
            "time":     time_str,
            "lat":      data['lat'],
            "lon":      data['lng'],
            "alt":      data.get('altitude', 0),
            "pass":     self.spacenearus_password
        }

        # get_telemtry is a very unstable routine
        # if anything goes wrong, we panic and poke the author
        try:
            data = self.get_telemtry()
        except Exception, e:
            logging.exception(e)
            data = {}

        if 'comment' in data:
            data["comment"] = data['comment']

        if len(data) > 0:
            post_data["data"] = json.dumps(data)

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
            except DuplicateData:
                logging.debug("Got duplicate position data. Discarding...");
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
