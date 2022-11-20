import phpserialize
from phpserialize import unserialize, phpobject
import json

file_open

def unserializePWA(binary_data):
    # unserialize array
    output = phpserialize.unserialize(binary_data, decode_strings=True)
    print('json:', json.dumps(output, indent=2))

    return output

flowObject = unserializePWA(b'a:6:{s:12:"stepFunction";s:15:"updateCollected";s:6:"silent";s:1:"1";s:4:"hook";s:1:"1";s:4:"auth";s:3:"app";s:14:"collectedAppId";s:8:"27247425";s:6:"values";a:1:{i:0;a:4:{s:7:"fieldId";s:9:"236417227";s:4:"type";s:3:"app";s:8:"function";s:4:"calc";s:5:"value";s:88:"[*item_value_pfref:27247425:related-full-apps*].&#34;,&#34;.[*item_value_podio_item_id*]";}}}')