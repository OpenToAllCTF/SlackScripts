# SlackScripts


## Purge scripts

Twice a year, OpenToAll performs a "purge" to deactivate inactive users in Slack.
To do this, we invite all members to a `poison` channel. Members have 3 weeks to leave the channel. After 3 weeks, the remaining members in the channel are marked as inactive and their accounts are deactivated.

Being a large team, inviting and deactivating users manually isn't an option. 
The scripts provided here automate the invitation and deactivation process.

### Requirements

Specific tokens are needed in order for these scripts to work : 

- SLACK_TOKEN (available [here](https://api.slack.com/custom-integrations/legacy-tokens))
- SLACK_WEB_TOKEN (available in the HTML source code here : https://[team].slack.com/admin)
