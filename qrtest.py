import io
import json
import qrcode

qr = qrcode.QRCode()
qr.add_data(json.dumps({"ip": "10.0.0.1", "port": 123}))
f = io.StringIO()
qr.print_ascii(out=f)
f.seek(0)
print(f.read())

"""

The QR Code will be displayed to be scanned by the gunncoin app
Using tcp connection (try LAN or port forwarding), configure miner settings

{
    "public_address": "some address",
    "save_config": true,
}

"""