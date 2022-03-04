import ssl
import aiohttp
import structlog
import re
import sys
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from gunncoin.util.constants import NODE_PORT

logger = structlog.getLogger(__name__)


async def get_external_ip():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "http://ipinfo.io", headers={"user-agent": "curl/7.64.1"}
        ) as response:
            response_json = await response.json(content_type=None)
            ip = response_json["ip"]
            logger.info(f"Found external IP: {ip}")
            return ip

def canyouseeme(port=NODE_PORT):
    context = ssl._create_unverified_context() # Ignore SSL: CERTIFICATE_VERIFY_FAILED
    data = urllib.request.urlopen("https://www.canyouseeme.org/", b"ip=1.1.1.1&port=%s" % str(port).encode("ascii"), timeout=20.0, context=context).read().decode("utf8")

    message = re.match(r'.*<p style="padding-left:15px">(.*?)</p>', data, re.DOTALL).group(1)
    message = re.sub(r"<.*?>", "", message.replace("<br>", " ").replace("&nbsp;", " "))  # Strip http tags

    match = re.match(r".*service on (.*?) on", message)
    if match:
        ip = match.group(1)
    else:
        raise Exception("Invalid response: %s" % message)

    if "Success" in message:
        return {"ip": ip, "opened": True}
    elif "Error" in message:
        return {"ip": ip, "opened": False}
    else:
        raise Exception("Invalid response: %s" % message)