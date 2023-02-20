from genericpath import exists
import json
import random
import time,utils,string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import config, sanitize_text
 
 
def scrape(post_url):
    bot = utils.create_bot(headless=True)
    data = {}
    #data={}
    #post: post_text
    #generating screenshot
    #1: text of first comment
    #generate screenshot
    #2: text of second comment
    # generate screenshot
    #...
    
    try:
        # Load cookies to prevent cookie overlay & other issues
        bot.get('https://www.reddit.com')
        for cookie in config['reddit_cookies'].split('; '):
            cookie_data = cookie.split('=')
            bot.add_cookie({'name':cookie_data[0],'value':cookie_data[1],'domain':'reddit.com'})
        bot.get(post_url)

        # Fetching the post itself, text & screenshot
        post = WebDriverWait(bot, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Post')))
        post_text = post.find_element(By.CSS_SELECTOR, 'h1').text
        data['post'] = post_text
        post.screenshot('output/post.png')

        # Let comments load
        bot.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Fetching comments & top level comment determinator
        comments = bot.find_elements(By.CSS_SELECTOR, 'div[id^=t1_][tabindex]')
        allowed_style = comments[0].get_attribute("style")
        
        # Filter for top only comments
        NUMBER_OF_COMMENTS = 5
        comments = [comment for comment in comments if comment.get_attribute("style") == allowed_style][:NUMBER_OF_COMMENTS]

        print('💬 Scraping comments...',end="",flush=True)
        # Save time & resources by only fetching X content
        for i in range(len(comments)):
            try:
                print('.',end="",flush=True)
                # Filter out locked comments (AutoMod) 
                try:
                    comments[i].find_element(By.CSS_SELECTOR, 'icon.icon-lock_fill')
                    continue
                except:
                    pass

                # Scrolling to the comment ensures that the profile picture loads
                # Credits: https://stackoverflow.com/a/57630350
                desired_y = (comments[i].size['height'] / 2) + comments[i].location['y']
                window_h = bot.execute_script('return window.innerHeight')
                window_y = bot.execute_script('return window.pageYOffset')
                current_y = (window_h / 2) + window_y
                scroll_y_by = desired_y - current_y

                bot.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)
                time.sleep(0.2)

                # Getting comment into string
                text = "\n".join([element.text for element in comments[i].find_elements(By.CSS_SELECTOR, '.RichTextJSON-root')])

                # Screenshot & save text
                comments[i].screenshot(f'output/{i}.png')
                data[str(i)] = ''.join(filter(lambda c: c in string.printable, text))
            except Exception as e:
                if config['debug']:
                    raise e
                pass

        if bot.session_id:
            bot.quit()
        return data
    except Exception as e:
        if bot.session_id:
            bot.quit()
        if config['debug']:
            raise e
        return False
    
    
import re
from prawcore.exceptions import ResponseException
from utils import sanitize_text
import praw
from praw.models import MoreComments
from prawcore.exceptions import ResponseException
import spacy

def is_post_valid(post, post_type):
    if not exists("rsc/log.json"):
        with open("rsc/log.json", "w+") as f:
            json.dump([], f)
    with open(
        "rsc/log.json", "r", encoding="utf-8"
    ) as done_vids_raw:
        done_videos = json.load(done_vids_raw)
    
    
    if str(post) in done_videos.keys() or \
        post.over_18 or \
        post.stickied or \
        (post_type== "comments" and post.num_comments < 30) or \
        (post_type == "story" and post.selftext == "") or \
        (post_type == "story" and post.selftext in ["[removed]", "[deleted]"]) or \
        (post_type == "story" and len(post.selftext) >6000):
        print("Invalid post: " + str(post))
        return False
        
    return True

def is_comment_valid(comment):
    if isinstance(comment, MoreComments) or \
        comment.body in ["[removed]", "[deleted]"] or \
        comment.stickied or \
        len(comment.body) > 300 or \
        len(comment.body) < 3 or \
        comment.author is None:
            return False
    
    return True
                


def scrape_post(sub, post_type):
    # returns data={}, where data is an object of the form:
    # post_type: 'story' or 'comments'
    # sub: subreddit name
    # id: id of the post
    # url: url of the post
    # title: post title
    # text: sentences of the post in a list
    # ^ empty if post_type isn't 'story'
    # comments: list of objects of the form {
        #id
        #url
        #text
    #}
    # ^ empty if post_type isn't 'comments'
    
    data = {}
    data["post_type"] = post_type
    data["sub"] = sub
    
    # Creating reddit instance
    try:
        reddit = praw.Reddit(
            client_id=config["reddit_clientid"],
            client_secret=config["reddit_clientsecret"],
            user_agent="Accessing Reddit threads",
            username=config["reddit_username"],
            passkey=config["reddit_password"],
            check_for_async=False,
        )
    except ResponseException as e:
        if e.response.status_code == 401:
            print("Invalid credentials - please check them in config")
            exit(1)
    except:
        print("Something went wrong...")
        exit(1)

    
    # Getting random post
    subreddit = reddit.subreddit(sub)
    tolerance=0
    while True:
        post = random.choice(list(subreddit.hot(limit=10+tolerance)))
        if is_post_valid(post, post_type):
            break
        tolerance+=2

    # Getting its properties
    post_url = f"https://reddit.com{post.permalink}"
    print(f"Video will be: {post.title}")
    print(f"Post url is : {post_url}")
    data["id"] = post.id
    data["url"] = post_url
    data["title"] = sanitize_text(post.title)
    data["text"] = []
    data["comments"] = []
    
    if post_type == "story":
        # If story, the text gets split into sentences with spacy and saved into the [post_text]
        text = re.sub("\n", "", post.selftext)
        text = sanitize_text(text)
        try:
            nlp = spacy.load('en_core_web_sm')
        except OSError:
            print("The spacy model can't load. You need to install it with \npython -m spacy download en")
            exit(1)
        doc = nlp(text)
        data["text"] = [sent.text for sent in doc.sents if sent.text not in ["x200B", "", " "]]
        
    elif post_type == "comments":
        # If comments, the comments get saved into the [comments] list and the [post_text] is empty
        needed = config["no_of_comments"]
        for comment in post.comments:
            if is_comment_valid(comment):
                needed-=1
                comment.body = sanitize_text(comment.body)
                data["comments"].append(
                    {
                        "text": comment.body,
                        "url": f"https://reddit.com{comment.permalink}",
                        "id": comment.id,
                    }
                )
            if needed == 0:
                break
                
    else:
        print("Invalid post type")
        exit(1)
        
    return data

if __name__ == "__main__":
    post = scrape_post("askreddit", "comments")
    print(post)
