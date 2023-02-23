# TikTok automatic Reddit content bot
Automatic content bot - can scrape, render and upload content to TikTok from any subreddit.
# Setup
1. `pip install -r requirements.txt` (you may or may not need to have Chrome installed)
2. Populate all categories in `config.yaml` \
   `tiktok_sessionid`: can be obtained from the cookie header after logging into any TikTok \
   `reddit_clientid`, `reddit_clientsecret`: can be obtained from [here](https://www.reddit.com/prefs/apps/) after creating a new web app \
   `reddit_username`, `reddit_password`: your Reddit username and password 
# Usage
0. To customize the assets: \
   `rsc/background`: .mp4 videos of choice (randomly selected) \
   `rsc/songs`: songs of choice (randomly selected, can be empty) \
1. Run `python3 main.py` to scrape and upload content from the default pool of subreddits \
or \
2. Run `pyhton3 main.py <subreddit> <post_type>` to scrape and upload content from a specific subreddit \
   `<subreddit>`: the subreddit to scrape from \
   `<post_type>`: the type of post to scrape from (can be `story` or `comments`) \
   (`story` posts are posts with only a title and a body - split into cards with moviepy and spacy, \
   `comments` posts are posts with a title and a comment thread - screenshotted with selenium)
