import os
import time
import textwrap
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import create_bot, config, sanitize_text
from PIL import Image, ImageDraw, ImageFont

tfont = ImageFont.truetype("rsc/fonts/Roboto-Bold.ttf", 27)  # for title
font = ImageFont.truetype("rsc/fonts/Roboto-Regular.ttf", 20)  # for text
bgcolor = (0, 0, 0)
fcolor = (255, 255, 255)
padding = 5
cardsize = (500, 176)
width = lambda f,x: f.getlength(x)
height = lambda f,x: f.getbbox(x)[3] - font.getbbox(x)[1]

def generate_screenshots(post):
    bot = create_bot(headless=True)
    try:
        # Screenshotting title
        bot.get(post["url"])
        page = WebDriverWait(bot, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Post')))
        page.screenshot('temp/post.png')
        
        # Screenshotting comments
        for i, comment in enumerate(post["comments"]):
            bot.get(comment["url"])
            page = WebDriverWait(bot, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Comment')))
            page.screenshot(f'temp/{i}.png')
        
    except Exception as e:
        print(e)
        exit(1)
        
        
def draw_multiple_line_text(image, text, font, wrap=50):
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=wrap)
    
    y = (image_height / 2) - (
        ((height(font,text) + (len(lines) * padding) / len(lines)) * len(lines)) 
        / 2
    )
    for line in lines:
        draw.text(((image_width - width(font,line)) / 2, y), line, font=font, fill=fcolor)
        y += height(font,line) + padding


def generate_cards(post):
    
    # Generate title card
    image = Image.new("RGBA", cardsize, bgcolor)
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    if len(post["title"]) > 40:
        draw_multiple_line_text(image, post["title"], tfont, wrap=30)
    else:
        draw.text(
            ((image_width - width(tfont,post["title"])) / 2, 
             (image_height - height(tfont,post["title"])) / 2),
            font=tfont,
            text=post["title"]) 
    image.save(f"temp/post.png")
    
    # Generate cards for story
    for id, text in enumerate(post["text"]):
        image = Image.new("RGBA", cardsize, bgcolor)
        draw = ImageDraw.Draw(image)
        if len(text) > 50:
            draw_multiple_line_text(image, text, font)
        else:
            draw.text(
                ((image.size[0] - width(font,text)) / 2, 
                 (image.size[1] - height(font,text)) / 2),
                font=font,
                text=text,
            ) 
        image.save(f"temp/{id}.png")


def generate_images(post):
    if post["post_type"]=="comments":
        generate_screenshots(post)
        print("Screenshots generated")
    else:
        generate_cards(post) 
        print("Cards generated")
        
if __name__ == "__main__":
    import scrape
    generate_images(scrape.scrape_post("nosleep", "story"))
