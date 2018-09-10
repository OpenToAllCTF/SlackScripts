#!/usr/bin/env python3

from slackclient import SlackClient

# Slack API Token
SLACK_TOKEN  = ""

# Channel to invite users too
DEST_CHANNEL = "general"

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

members = get_all_users(sc)
print("[*] Found {} members.".format(len(members)))

# Invite to channel in groups of 30
# Slack limits channel invitations to 30 members per API call.
print("[*] Inviting users.")
member_ids = [member['id'] for member in members]
groups = [member_ids[n:n+30] for n in range(0, len(member_ids), 30)]

for group in groups:
    sc.api_call("conversations.invite", channel=channel_id, users=','.join(group))
