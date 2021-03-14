#!/usr/bin/env python3

import time
import sys

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests

# Taken here : https://api.slack.com/custom-integrations/legacy-tokens
SLACK_TOKEN  = "xoxb-..."

# Available in the HTML source code of https://[team].slack.com/admin
WEB_SLACK_TOKEN = "xoxs-..."

# Channel containing the members we want to deactivate
DEST_CHANNEL = "FILL ME IN"

# Team Slack domain
SLACK_DOMAIN = "opentoallctf.slack.com"

# Users we won't ban even if they are in the channel
safe_user_names = {
        "7feilee",
        "Kroz",
        "Diis",
        "r00k",
        "Ariana",
        "Lord_Idiot",
        "UnblvR",
        "an0n",
        "drtychai",
        "enio",
        "eriner",
        "fevral",
        "grazfather",
        "idr0p",
        "kileak",
        "mementomori",
        "rh0gue",
        "sae",
        "sferrini",
        "uafio",
        "vakzz",
        "viva",
        "waywardsun",
}

def channel_id_by_name(client, name):
    """Fetch channel ID for a given channel name."""
    limit = 1000
    cursor = None
    while True:
        resp = client.conversations_list(types="public_channel", limit=limit, cursor=cursor)
        channels = resp["channels"]

        for channel in channels:
            if channel["name"] == name:
                return channel["id"]

        cursor = resp["response_metadata"]["next_cursor"]
        if not cursor:
            break

    return None


def get_all_users(client):
    """Fetch all users in the team. Includes deleted/deactivated users."""
    resp = client.users_list()
    return resp["members"]


def get_all_users_in_channel(client, channel_id):
    limit = 1000
    cursor = None
    members = []
    while True:
        resp = sc.conversations_members(channel=channel_id, limit=1000, cursor=cursor)
        cursor = resp["response_metadata"]["next_cursor"]
        members += resp["members"]
        if not cursor:
            break

    return members

sc = WebClient(SLACK_TOKEN)

channel_id = channel_id_by_name(sc, DEST_CHANNEL)

if not channel_id:
    print("[!] No channel ID found for channel '{}'.".format(DEST_CHANNEL))
    sys.exit(1)

print("[*] Found channel {} ({}).".format(DEST_CHANNEL, channel_id))

# Get all members
members = get_all_users(sc)
members = {member["id"]: member for member in members}
print("[*] Found {} total members.".format(len(members)))

# Get members in channel
members_in_channel = get_all_users_in_channel(sc, channel_id)
print("[*] Found {} members in {}".format(len(members_in_channel), DEST_CHANNEL))

# Get member ids of the safe list
safe_member_ids = {m_id for m_id, member in members.items() if member["name"] in safe_user_names}
print("[*] Found {} blessed users".format(len(safe_member_ids)))

# Filter out bots and deactivated users.
doomed_members = []

doomed_members = [m_id for m_id in members_in_channel if
        not members[m_id]["deleted"] and not members[m_id]["is_bot"]
        and not m_id in safe_member_ids]

print("[*] Found {} doomed members".format(len(doomed_members)))

# Deactivate members.
# Member deactivation through the slack API is only available for premium teams.
# We can bypass this restriction by using a different API endpoint.
# The code below simulates an admin manually deactivating users through the
# ... web interface.
print("[*] Deactivating {} members.".format(len(doomed_members)))
deactivate_url = "https://{}/api/users.admin.setInactive".format(SLACK_DOMAIN)
for member_id in doomed_members:

    username = members[member_id]["profile"]["display_name"]
    data = {"user": member_id, "token": WEB_SLACK_TOKEN}
    headers = {"Content-Type" : "application/x-www-form-urlencoded"}
    response = requests.post(deactivate_url, data=data, headers=headers)

    print("[*] Banning {} ({})".format(username, member_id))
    print(response.text)
    if response.json().get("error") == "ratelimited":
        time.sleep(1)

    # Avoid Slack's rate limiting
    time.sleep(0.5)
