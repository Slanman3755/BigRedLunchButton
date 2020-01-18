import random
import requests
import yaml
from pathlib import Path


config_file_path = str(Path.home()) + "/.bigredlunchbutton"
messages_file_path = "messages.txt"


def post_to_slack():
    with open(config_file_path) as config_file:
        config = yaml.full_load(config_file)
        api_url = config["url"]

        with open(messages_file_path) as messages_file:
            messages = messages_file.readlines()
            message = messages[random.randint(0, len(messages) - 1)]

            text = "@here " + message
            data = {"text": text, "link_names": 1}
            response = requests.post(api_url, json=data)
            code = response.status_code

            if code == 200:
                print("Success")
            else:
                print(f"Failure {code}\n{response.content}")
                exit(1)


def on_press():
    post_to_slack()


if __name__ == "__main__":
    # listener.join()
    post_to_slack()
