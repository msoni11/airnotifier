import requests
import random
from api import API_PERMISSIONS

HUBURL = "https://moodle.net/local/sitecheck/check.php"


def process_pushnotification_payload(data):
    extra = data.get("extra", {})
    userfrom = extra.get("userfromfullname", None)
    usertoid = extra.get("usertoid", None)
    site = extra.get("site", None)
    timecreated = extra.get("timecreated", None)
    message = extra.get("smallmessage", None)
    notif = extra.get("notification", None)
    title = extra.get("sitefullname", None)
    courseid = extra.get("courseid", None)
    notificationtype = extra.get("notificationtype", None)
    moduleid = extra.get("moduleid", None)

    if not message:
        message = extra.get("fullmessage", None)

    if not title:
        title = "Notification"

    # Set the correct device.
    device = data.get('device', None).lower()
    if device == "android-fcm" or device == "ios-fcm":
        data["device"] = "fcm"
        # fcm only support string in data payload
        if moduleid == False or moduleid is None:
            moduleid = ''
        if courseid == False or courseid is None:
            courseid = ''

    data["gcm"] = {
        "data": {
            "title": title,
            "site": site,
            "userfrom": userfrom,
            "usertoid": usertoid,
            "notif": notif,
            "notId": random.randint(1, 1000000),
            "courseid": courseid,
            "notificationtype": notificationtype,
            "moduleid": moduleid
        }
    }

    data["apns"] = {
        "custom": {
            "title": title,
            "site": site,
            "userfrom": userfrom,
            "usertoid": usertoid,
            "notif": notif,
            "courseid": courseid,
            "notificationtype": notificationtype,
            "moduleid": moduleid
        }
    }

    # Payload for the fcm notifications
    data["fcm"] = {
        "android": {
            "data": {
                "sound": "default",
                "body": message,
                "title": '',
                "site": site,
                "userfrom": userfrom,
                "usertoid": usertoid,
                "courseid": courseid,
                "notificationtype": notificationtype,
                "moduleid": moduleid
            }
        },
        "apns": {
            "payload": {
                "aps": {
                    "sound": "default",
                    "alert": {
                        "body": message,
                        "title": '',
                        "site": site,
                        "userfrom": userfrom,
                        "usertoid": usertoid,
                        "courseid": courseid,
                        "notificationtype": notificationtype,
                        "moduleid": moduleid
                    }
                }
            }
        }
    }

    if "alert" not in data:
        data["alert"] = message

    if not "wns" in extra:
        data["extra"]["wns"] = {
            "type": "toast",
            "template": "ToastText01",
            "text": [data["alert"]],
        }

    if not "fcm" in extra:
        data["extra"]["fcm"] = {"fcm-message": "this is fcm hook"}

    return data


def process_accesskey_payload(data):
    mdlurl = data.get("url", "")
    mdlsiteid = data.get("siteid", "")
    params = {"siteid": mdlsiteid, "url": mdlurl}
    response = requests.get(HUBURL, params=params)
    result = int(response.text)
    if result == 0:
        raise Exception("Site not registered on moodle.net")
    else:
        # This is 1111 in binary means all permissions are granted
        data["permission"] = (
            API_PERMISSIONS["create_token"][0]
            | API_PERMISSIONS["delete_token"][0]
            | API_PERMISSIONS["send_notification"][0]
            | API_PERMISSIONS["send_broadcast"][0]
        )
        return data

def process_token_payload(data):
    return data
