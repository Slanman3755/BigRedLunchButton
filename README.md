# Big Red Lunch Button
Posts Venice lunch notfications to the System1 slack

Add custom lunch messages by appending new lines to the messages.txt file

## Installation
- Have a Raspberry Pi connected to an led and a switch in a pull down configuration
- Clone repository
- Install required python packages `pip install -r requirements.txt`
- Copy `config.yaml` to `~/.bigredlunchbutton`
- Fill out values in yaml config (slack webhooks api url, path to messages.txt, gpio pins)
- Run script `python button.py`
