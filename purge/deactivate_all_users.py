#!/usr/bin/env python3

from slackclient import SlackClient
import requests
import time

# Taken here : https://api.slack.com/custom-integrations/legacy-tokens
SLACK_TOKEN = ""

# Available in the HTML source code of https://[team].slack.com/admin
WEB_SLACK_TOKEN = ""

# Channel containing the members we want to deactivate
DEST_CHANNEL = "general"

# Team Slack domain
SLACK_DOMAIN = "opentoallctf.slack.com"

def channel_id_by_name(client, name):
    """ Fetch channel ID for a given channel name. """

    output = client.api_call("channels.list")
    channels = output['channels']

    channel_id = ''
    for channel in channels:
        if channel['name'] == name:
            return channel['id']

    return None

def get_all_users(client):
    """ Fetch all users in the team. Includes deleted/deactivated users. """

    output = client.api_call("users.list")
    return output['members']

sc = SlackClient(SLACK_TOKEN)

channel_id = channel_id_by_name(sc, DEST_CHANNEL)

if not channel_id:
    print("[!] No channel ID found for channel '{}'.".format(DEST_CHANNEL))

print("[*] Found channel {} ({}).".format(DEST_CHANNEL, channel_id))

# Get all members
members = get_all_users(sc)
members = dict([(member['id'], member) for member in members])

# Get members in channel
output = sc.api_call("channels.info", channel=channel_id)
members_in_channel = output['channel']['members']

# Filter out bots and deactivated users.
members_to_deactivate = []
for member_id in members_in_channel:
    is_deactivated = members[member_id]['deleted']
    is_bot = members[member_id]['is_bot']

    if not is_deactivated and not is_bot:
        members_to_deactivate.append(member_id)

# Deactivate members.
# Member deactivation through the slack API is only available for premium teams.
# We can bypass this restriction by using a different API endpoint.
# The code below simulates an admin manually deactivating users through the
# ... web interface.
print("[*] Deactivating {} members.".format(len(members_to_deactivate)))
deactivate_url = "https://{}/api/users.admin.setInactive".format(SLACK_DOMAIN)
for member_id in members_to_deactivate:

    username = members[member_id]['profile']['display_name']
    data = { "user" : member_id, "token": WEB_SLACK_TOKEN }
    headers = { "Content-Type" : "application/x-www-form-urlencoded" }
    response = requests.post(deactivate_url, data=data, headers=headers)

    print("[*] Kicking {} : {}".format(repr(username), member_id))
    print(response.text)

    # Prevent Slack's rate limiting
    time.sleep(1)
