import re


def verify_mac_address(mac):
    mac = str(mac).replace('\n', '').replace(' ', '')
    pattern = re.compile('^(([a-f0-9]{2}:)|([a-f0-9]{2}-)){5}[a-f0-9]{2}$', re.I)
    result = re.search(pattern, str(mac))
    if result:
        return result.string
    else:
        return None


def verify_isp(isp):
    result = re.match('^[1-3]$', str(isp))
    if result:
        return result.string
    else:
        return None


def verify_campus(campus):
    result = re.match('^[1-3]$', str(campus))
    if result:
        return result.string
    else:
        return None