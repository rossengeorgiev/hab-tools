hab-tools
=========

A bunch of scripts for high altitude ballooning

```
aprsnear-us.py
  submits latest position of a callsign to spacenear.us (password and apikey required)

spot2habitat_chase.py
  fetches SPOT position from feed and uploads it as chasecar in habitat

tinyburstmodel.py
  calculates burst altitude based on balloon diameter and fill volume

aprsfi_raw_to_txt.py <url>
  takes a url to a aprs.fi raw page and echos valid lines

  Example:
  ----------------
  ./aprsfi_raw_to_txt.py http://aprs.fi/?c=raw&call=KF5PGW-9&limit=1000&view=normal

aprsfi_raw_to_snus.py <logfile.txt>
  parses and uploads a copy pasted raw log taken from aprs.fi

  Use 'aprsfi_raw_to_txt.py'

  Example logfile.txt from http://aprs.fi/?c=raw&call=aeth28-3
  ----------------
  2014-11-22 16:03:52 GMT: AETH28-1>APSTM1,qAR,F0EXC-10:!/6eF;PL'zO;<YG3HB1#R0B/A=061760|$&HS"U9t!)!&!^|
  2014-11-22 16:04:07 GMT: AETH28-1>APSTM1,qAS,HB9FM-10:!/6eGFPL)8OA=YG3HB1#a0B/A=061840|$'Hi"O9q!(!&"C|
  2014-11-22 16:05:52 GMT: AETH28-1>APSTM1,qAR,HB9BA-2:!/6eLePL3.O;>YG3HB1$o0B/A=061723 KF5KMP |$(EP"S9X!)!&!^|
  2014-11-22 16:08:07 GMT: AETH28-1>APSTM1,qAR,HB9BA-2:!/6eScPL?AO>=YG3HB1&@0B/A=061731|$+CX"E9B!(!&"C|


send_tlm_to_habitat.py <sentence> [recv callsign]
    uploads a single sentence to habitat

```
