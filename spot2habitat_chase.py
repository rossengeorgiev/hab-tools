#!/usr/bin/env python

import sys
import urllib2
import json
import logging
import time
from datetime import datetime

class SPOTError(Exception):
    pass

class HabitatError(Exception):
    pass

class SPOT(object):
    def __init__(self, config):
        self.callsign = config["callsign"]
        self.callsign_init = False
        self.feed_id = config["feed_id"]
        self.password = config["password"]
        self.url_spot_feed = "https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/%s/latest.json"
        self.url_habitat_uuids = "http://habitat.habhub.org/_uuids?count=%d"
        self.url_habitat_db = "http://habitat.habhub.org/habitat/"
        self.uuids = []
        self.sleep = 60
        self.prev_msg_id = ""

    def fetch_latest_spot_message(self):
        try:
            resp = urllib2.urlopen(self.url_spot_feed % self.feed_id).read()
            msg = json.loads(resp)
            logging.debug("Received latest message:\n%s" % json.dumps(msg, indent=2))
        except urllib2.HTTPError, e:
            raise SPOTError(" while feetching feed. (%s" % e)
        except ValueError:
            raise SPOTError(" Unable to parse feed's JSON");

        if 'errors' in msg['response']:
            logging.debug(resp)
            xref = msg['response']['errors']['error']
            raise SPOTError("%s (%s)" % (xref['description'], xref['code']))

        return msg

    def ISOStringNow(self):
        return "%sZ" % datetime.utcnow().isoformat()

    def getVersion(self):
        v = sys.version_info
        return "Python %d.%d.%d %s" % (v.major, v.minor, v.micro, v.releaselevel)

    def postData(self, doc):
        # do we have at least one uuid, if not go get more
        if len(self.uuids) < 1:
            self.fetch_uuids()

        # add uuid and uploade time
        doc['_id'] = self.uuids.pop()
        doc['time_uploaded'] = self.ISOStringNow()

        data = json.dumps(doc)
        headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Referer': self.url_habitat_db,
                }

        logging.debug("Posting doc to habitat\n%s" % json.dumps(doc, indent=2))

        req = urllib2.Request(self.url_habitat_db, data, headers)
        return urllib2.urlopen(req).read()

    def fetch_uuids(self):
        while True:
            try:
                resp = urllib2.urlopen(self.url_habitat_uuids % 10).read()
                data = json.loads(resp)
            except urllib2.HTTPError, e:
                logging.error(e);
                logging.info("Unable to fetch uuids. Retrying in 10 seconds...");
                time.sleep(10)
                continue

            logging.debug("Received a set of uuids.\n %s" % json.dumps(data, indent=2))
            self.uuids.extend(data['uuids'])
            break;


    def init_callsign(self):
        doc = {
                'type': 'listener_information',
                'time_created' : self.ISOStringNow(),
                'data': { 'callsign': self.callsign }
                }

        while True:
            try:
                resp = self.postData(doc)
                logging.info("Callsign initialized.")
                break;
            except urllib2.HTTPError, e:
                logging.error(e);
                logging.info("Unable initialize callsign. Retrying in 10 seconds...");
                time.sleep(10)
                continue

    def run(self):
        while True:
            try:
                # grab the latest spot message
                msg = self.fetch_latest_spot_message()

                # initialize call sign (one time only)
                if not self.callsign_init:
                    self.init_callsign()
                    self.callsign_init = True

                # discard the message if its a duplicate
                xref = msg['response']['feedMessageResponse']['messages']['message']

                if xref['id'] == self.prev_msg_id:
                    logging.debug("No new position.")
                    time.sleep(self.sleep)
                    continue

                # remember msg id
                self.prev_msg_id = xref['id']

                # make position doc
                doc = {
                        'type': 'listener_telemetry',
                        'time_created': self.ISOStringNow(),
                        'data': {
                            'callsign': self.callsign,
                            'chase': True,
                            'latitude': xref['latitude'],
                            'longitude': xref['longitude'],
                            'altitude': 0,
                            'speed': 0,
                            'client': {
                                'name': 'spot2habitat.py (hab-tools)',
                                'version': '1.0',
                                'agent': self.getVersion()
                            }
                        }
                    }

                # post position to habitat
                self.postData(doc)
                logging.info("Uploaded latest position (%f, %f)." % (xref['latitude'], xref['longitude']))

                # wait
                time.sleep(self.sleep)
            except KeyboardInterrupt:
                logging.debug("Exiting...")
                sys.exit(0)
            except SPOTError, e:
                logging.error(e);
                logging.info("Retrying in 10 seconds...")
                time.sleep(10);
            except:
                logging.exception("Exception; continuing")
                time.sleep(self.sleep)


def main():
    if len(sys.argv) < 3:
        print "You have not specified enough parameters."
        print "The feed password is optional\n"
        print "Usage: %s <callsign> <feed_id> [password]" % sys.argv[0]
        sys.exit(1)

    logging.basicConfig(level=getattr(logging, "INFO"),
                        format="[%(asctime)s] %(levelname)s: %(message)s")
    config = {}
    config['callsign'] = sys.argv[1]
    config['feed_id'] = sys.argv[2]
    config['password'] = sys.argv[3] if len(sys.argv) > 3 else ""


    logging.debug("Config loaded.\n%s" % json.dumps(config, indent=2))

    SPOT(config).run()

if __name__ == "__main__":
    main()
