#!/usr/bin/env python
import sys
import httplib
import json
from base64 import b64encode
from hashlib import sha256
from datetime import datetime

if len(sys.argv) < 2:
    print "Usage: python %s <sentence> [recv callsign]" % sys.argv[0]
    sys.exit()

sentence = sys.argv[1]

if not sentence.endswith('\n'):
    sentence += '\n'

sentence = b64encode(sentence)

callsign = sys.argv[2] if len(sys.argv) > 2 else "HABTOOLS"

date = datetime.utcnow().isoformat("T") + "Z"

data = {
    "type": "payload_telemetry",
    "data": {
        "_raw": sentence
        },
    "receivers": {
        callsign: {
            "time_created": date,
            "time_uploaded": date,
            },
        },
}

c = httplib.HTTPConnection("habitat.habhub.org")
c.request(
    "PUT",
    "/habitat/_design/payload_telemetry/_update/add_listener/%s" % sha256(sentence).hexdigest(),
    json.dumps(data),  # BODY
    {"Content-Type": "application/json"}  # HEADERS
    )

response = c.getresponse()

print response.status, response.reason
print response.read()
