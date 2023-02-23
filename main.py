from datetime import datetime
import random
import sys
from scrape import scrape_post
from upload import upload
from utils import config, clean_temp, log
from image import generate_images
from tts import generate_audio
from video import render_video

def do_order(subreddit, post_type, time = 0):
    post = scrape_post(subreddit, post_type)
    generate_images(post)
    generate_audio(post)
    render_video(post)
    upload(post, time)
    log(post)
    clean_temp()
        
if __name__ == '__main__':
    random.seed(datetime.now())
    if len(sys.argv) == 1:
        do_order(*random.choice(config["default_pool"]))
    else:
        do_order(sys.argv[1], sys.argv[2])