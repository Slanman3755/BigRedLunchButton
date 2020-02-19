import logging
import random
import requests
import yaml

from gpiozero import LED, Button
from pathlib import Path
from pytz import timezone
from time import sleep
from datetime import datetime, time

cycle_time = 0.01  # seconds

tz = timezone('US/Pacific')
valid_window_start = time(11, 0, 0, tzinfo=tz)
valid_window_end = time(14, 0, 0, tzinfo=tz)


def is_in_window(current_time):
    return valid_window_start <= current_time.time() <= valid_window_end


def is_valid_press(current_time, last_time=None):
    in_window = is_in_window(current_time)
    if last_time:
        return current_time.date() != last_time.date() and in_window
    else:
        return in_window


home_path = str(Path.home())
config_file_path = f"{home_path}/.bigredlunchbutton"
log_file_path = f"/var/log/bigredlunchbutton.log"

logging.basicConfig(
    filename=log_file_path,
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


last_posted = None


def post_to_slack(api_url, messages):
    global last_posted

    message = messages[random.randint(0, len(messages) - 1)]
    text = f"@here {message}"
    data = {"text": text, "link_names": 1}

    response = requests.post(api_url, json=data)
    code = response.status_code

    if code == 200:
        last_posted = datetime.now(tz=tz)
        logging.info(f"Posted message to slack: {text}")
    else:
        logging.error(f"Error posting message to slack: {code}\n{response.content}")


def listen(button_pin, led_pin, api_url, messages):
    global last_posted

    button = Button(button_pin, pull_up=False, bounce_time=1)
    led = LED(led_pin)

    logging.info("Initialized GPIO")
    led.blink()

    def button_pressed(current_time):
        logging.info("Button pressed")
        if is_valid_press(current_time, last_posted):
            post_to_slack(api_url, messages)
        else:
            logging.warning(f"Invalid request time, last post: {last_posted}")

    def update_led(current_time):
        if is_in_window(current_time) and last_posted and current_time.date() == last_posted.date():
            led.on()
        else:
            led.off()

    logging.info("Listening...")
    last_button_state = False
    while True:
        button_state = button.is_active
        now = datetime.now(tz=tz)
        if button_state and button_state != last_button_state:
            button_pressed(now)
        update_led(now)
        last_button_state = button_state
        sleep(cycle_time)


def main():
    logging.info("Init")
    with open(config_file_path) as config_file:
        config = yaml.safe_load(config_file)
        config_file.close()

        button_pin = config["button_pin"]
        led_pin = config["led_pin"]
        api_url = config["url"]
        messages_file_path = config["messages_file"]

        logging.info("Loaded config")

        with open(messages_file_path) as messages_file:
            messages = messages_file.readlines()
            messages_file.close()
            logging.info("Loaded messages")

            listen(button_pin, led_pin, api_url, messages)


if __name__ == "__main__":
    main()
