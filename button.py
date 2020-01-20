import logging
import random
import requests
import yaml

from gpiozero import LED, Button
from pathlib import Path
from signal import pause


home_path = str(Path.home())
config_file_path = f"{home_path}/.bigredlunchbutton"
log_file_path = f"{home_path}/bigredlunchbutton.log"

logging.basicConfig(
    filename=log_file_path,
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def post_to_slack(api_url, messages):
    message = messages[random.randint(0, len(messages) - 1)]
    text = "@here " + message
    data = {"text": text, "link_names": 1}

    response = requests.post(api_url, json=data)
    code = response.status_code

    if code == 200:
        logging.info(f"Posted message to slack: {text}")
    else:
        logging.error(f"Error posting message to slack: {code}\n{response.content}")


def listen(button_pin, led_pin, api_url, messages):
    button = Button(button_pin, pull_up=False)
    led = LED(led_pin)
    logging.info("Initialized GPIO")

    def button_pressed():
        logging.info("Button pressed")
        led.on()
        post_to_slack(api_url, messages)

    def button_released():
        logging.info("Button released")
        led.off()

    button.when_pressed = button_pressed
    button.when_released = button_released

    logging.info("Listening...")

    pause()


def main():
    logging.info("Init")
    with open(config_file_path) as config_file:
        config = yaml.full_load(config_file)
        config_file.close()

        button_pin = config["button_pin"]
        led_pin = config["led_pin"]
        api_url = config["url"]
        working_dir = config["working_dir"]
        messages_file_path = f"{working_dir}/messages.txt"

        logging.info("Loaded config")

        with open(messages_file_path) as messages_file:
            messages = messages_file.readlines()
            messages_file.close()
            logging.info("Loaded messages")

            listen(button_pin, led_pin, api_url, messages)


if __name__ == "__main__":
    main()
