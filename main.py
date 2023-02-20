import asyncio,tts,os,video,requests
import imp
from scrape import scrape, scrape_post
from upload import upload
from utils import config, clean_temp, load_orders, log
from image import generate_images
from tts import generate_audio
from video import render_video

def main():
    for order in load_orders('orders.txt'):
        (subreddit, post_type, time) = order
        post = scrape_post(subreddit, post_type)
        generate_images(post)
        generate_audio(post)
        render_video(post)
        upload(post, time)
        log(post)
        clean_temp()

if __name__ == '__main__':
    main()