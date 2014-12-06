#!/usr/bin/env python
import aprs
import sys
import urllib
import json
import time
import re


if len(sys.argv) < 3:
    print "Usage: python %s <password> <aprs_packet_log_file>" % sys.argv[0]
    sys.exit()

info = {
    "tEQNS": [[0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0], [0, 1, 0]],
    "tPARM": ["Ch1", "Ch2", "Ch3", "Ch4", "Ch4", "01", "O2", "O3", "O4", "I1", "I2", "I3", "I4"],
    "tUNIT": ["", "", "", "", "", "01", "O2", "O3", "O4", "I1", "I2", "I3", "I4"]
}

password = sys.argv[1]

with open(sys.argv[2]) as f:
    packets = f.readlines()

    count = 1
    for line in packets:
        print "Uploading position #%d..." % count,
        count += 1

        timestr, data = line.split(": ", 1)
        timestr = re.sub(r"[^0-9]", "", timestr)

        data = aprs.parse(data)

        if data['format'] not in ['compressed', 'uncompressed', 'mic-e']:
            continue

        post_data = {
            "vehicle":  data['from'],
            "callsign": "APRS_LOG",
            "time":     timestr,
            "lat":      data['latitude'],
            "lon":      data['longitude'],
            "alt":      int(data['altitude']),
            "pass":     password
        }

        tdata = {}

        if 'comment' in data and data['comment'] != "":
            tdata.update({"comment": data['comment']})

        if 'telemetry' in data:
            idx = 0
            for val in data['telemetry']['vals']:
                chname = "%s" % info['tPARM'][idx]
                chname += " (%s)" % info['tUNIT'][idx] if info['tUNIT'][idx] != "" else ""

                a, b, c = info['tEQNS'][idx]
                val = (a * val**2) + b*val + c

                tdata.update({chname: str(val)})
                idx += 1

        if len(tdata) > 0:
            post_data['data'] = json.dumps(tdata)

        data = urllib.urlencode(post_data)
        urllib.urlopen("http://spacenear.us/tracker/track.php?{data}".format(data=data))

        print " ok."

        time.sleep(0.05)
