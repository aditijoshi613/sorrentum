"""
- Open Telegram and navigate to the group for which you want to get the ID.

- Add the Telegram bot that you created as an admin to the groups.

- Once the bot is added to the group, send any message in the group.

to run outside a Docker container:
```
> python get_telegram_groupid.py
```

Show the Group ID and the last message in each groups.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")


def _get_group_info():
    response = requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates")
    data = response.json()
    group_messages = {}
    for update in data["result"]:
        if "message" in update and "chat" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            message = update["message"]
            # Get the last message.
            if "text" in message:
                group_messages[chat_id] = message["text"]
    for group_id, last_message in group_messages.items():
        print(f"Group ID: {group_id}, Last Message: {last_message}")


def _main():
    _get_group_info()


if __name__ == "__main__":
    _main()