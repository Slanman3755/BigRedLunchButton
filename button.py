import random
import requests
import RPi.GPIO as gpio
import time
import yaml

from pathlib import Path


gpio.setmode(gpio.BCM)
button_pin = 17
led_pin = 27
gpio.setup(button_pin, gpio.IN)
gpio.setup(led_pin, gpio.OUT)


config_file_path = str(Path.home()) + "/.bigredlunchbutton"
messages_file_path = "messages.txt"


def post_to_slack(config, messages):
    api_url = config["url"]
    message = messages[random.randint(0, len(messages) - 1)]
    text = "@here " + message
    data = {"text": text, "link_names": 1}

    response = requests.post(api_url, json=data)
    code = response.status_code

    if code == 200:
        print(f"Posted message to slack: {text}")
    else:
        print(f"Error posting message to slack: {code}\n{response.content}")
        exit(1)


def listen(config, messages):
    prev_state = 0
    while True:
        button_state = gpio.input(button_pin)
        gpio.output(led_pin, button_state)

        if button_state and button_state != prev_state:
            post_to_slack(config, messages)

        prev_state = button_state


def main():
    with open(config_file_path) as config_file:
        config = yaml.full_load(config_file)
        with open(messages_file_path) as messages_file:
            messages = messages_file.readlines()
            listen(config, messages)


if __name__ == "__main__":
    main()
