#!/usr/bin/env python3

import time
import sys

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Slack API Token
SLACK_TOKEN  = "xoxb-..."

# Channel to invite users too
DEST_CHANNEL = "FILL ME IN"

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

sc = WebClient(SLACK_TOKEN)

channel_id = channel_id_by_name(sc, DEST_CHANNEL)

if not channel_id:
    print("[!] No channel ID found for channel '{}'.".format(DEST_CHANNEL))
    sys.exit(1)

print("[*] Found channel {} ({}).".format(DEST_CHANNEL, channel_id))

members = get_all_users(sc)
print("[*] Found {} members.".format(len(members)))

# Join the channel, so we can invite to it
sc.conversations_join(channel=channel_id)

# Invite to channel in groups of 30
# Slack limits channel invitations to 30 members per API call.
print("[*] Inviting users.")
member_ids = [member["id"] for member in members]
groups = [member_ids[n:n+30] for n in range(0, len(member_ids), 30)]

for group in groups:
    try:
        sc.conversations_invite(channel=channel_id, users=",".join(group))
    except SlackApiError as e:
        # Technically we can have up to 30 errors, and some might be bad
        # e.response.data["errors"] to check them individually
        if "ratelimited" in str(e):
            time.sleep(1)
        elif "cant_invite_self" in str(e):
            continue
        elif "already_in_channel" in str(e):
            continue
        # TODO: Should we bail otherwise?
        continue
