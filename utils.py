import json
import yaml
import undetected_chromedriver as uc
import re
import os

# Load and validate config
config = yaml.safe_load(open('config.yaml').read())

def create_bot(headless=False):
    options = uc.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument('disable-infobars')
    if headless:
        options.headless = True

    bot = uc.Chrome(options=options)

    bot.set_page_load_timeout(25)
    bot.set_window_size(1920, 1080)
    return bot

def load_orders(path):
    orders = []
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            orders.append(line.split())
    return orders

def sanitize_text(text):
    # remove any urls from the text
    regex_urls = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
    result = re.sub(regex_urls, " ", text)

    # remove `^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
    regex_expr = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-%—“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
    result = re.sub(regex_expr, " ", result)
    result = result.replace("+", "plus").replace("&", "and")
 
    # remove extra whitespace
    return " ".join(result.split())

def log(post):
    if not os.path.exists('rsc/log.json'):
        with open('rsc/log.json', 'w+') as f:
            f.write('[]')

    with open('rsc/log.json', 'r') as f:
        data = json.load(f)

    data[post["id"]] = post["url"]

    with open('rsc/log.json', 'w') as f:
        json.dump(data, f)

def clean_temp():
    for file in os.listdir('temp'):
        os.remove(f'temp/{file}')