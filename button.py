import random
import requests


messages_file_path = "messages.txt"
api_url = "https://hooks.slack.com/services/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"


def post_to_slack():
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


def on_press():
    post_to_slack()


if __name__ == "__main__":
    print("Now listening...")
    # listener.join()
    post_to_slack()
