# documentation for tiktok api: https://github.com/oscie57/tiktok-voice/wiki
import base64
import random
import time
from typing import Optional, Final
from utils import config

import requests

disney_voices: Final[tuple] = (
    "en_us_ghostface",  # Ghost Face
    "en_us_chewbacca",  # Chewbacca
    "en_us_c3po",  # C3PO
    "en_us_stitch",  # Stitch
    "en_us_stormtrooper",  # Stormtrooper
    "en_us_rocket",  # Rocket
    "en_female_madam_leota",  # Madame Leota
    "en_male_ghosthost",  # Ghost Host
    "en_male_pirate",  # pirate
)

eng_voices: Final[tuple] = (
    "en_au_001",  # English AU - Female
    "en_au_002",  # English AU - Male
    "en_uk_001",  # English UK - Male 1
    "en_uk_003",  # English UK - Male 2
    "en_us_001",  # English US - Female (Int. 1)
    "en_us_002",  # English US - Female (Int. 2)
    "en_us_006",  # English US - Male 1
    "en_us_007",  # English US - Male 2
    "en_us_009",  # English US - Male 3
    "en_us_010",  # English US - Male 4
    "en_male_narration",  # Narrator
    "en_male_funny",  # Funny
    "en_female_emotional",  # Peaceful
    "en_male_cody",  # Serious
)

non_eng_voices: Final[tuple] = (
    # Western European voices
    "fr_001",  # French - Male 1
    "fr_002",  # French - Male 2
    "de_001",  # German - Female
    "de_002",  # German - Male
    "es_002",  # Spanish - Male
    "it_male_m18"  # Italian - Male
    # South american voices
    "es_mx_002",  # Spanish MX - Male
    "br_001",  # Portuguese BR - Female 1
    "br_003",  # Portuguese BR - Female 2
    "br_004",  # Portuguese BR - Female 3
    "br_005",  # Portuguese BR - Male
    # asian voices
    "id_001",  # Indonesian - Female
    "jp_001",  # Japanese - Female 1
    "jp_003",  # Japanese - Female 2
    "jp_005",  # Japanese - Female 3
    "jp_006",  # Japanese - Male
    "kr_002",  # Korean - Male 1
    "kr_003",  # Korean - Female
    "kr_004",  # Korean - Male 2
)

vocals: Final[tuple] = (
    "en_female_f08_salut_damour",  # Alto
    "en_male_m03_lobby",  # Tenor
    "en_male_m03_sunshine_soon",  # Sunshine Soon
    "en_female_f08_warmy_breeze",  # Warmy Breeze
    "en_female_ht_f08_glorious",  # Glorious
    "en_male_sing_funny_it_goes_up",  # It Goes Up
    "en_male_m2_xhxs_m03_silly",  # Chipmunk
    "en_female_ht_f08_wonderful_world",  # Dramatic
)

headers = {
            "User-Agent": "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; "
            "Build/NRD90M;tt-ok/3.12.13.1)",
            "Cookie": f"sessionid=" + config["tiktok_sessionid"] +";",
        }

URI_BASE = "https://api16-normal-c-useast1a.tiktokv.com/media/api/text/speech/invoke/"

_session = requests.Session()
# set the headers to the session, so we don't have to do it for every request
_session.headers = headers

def get_voice(text, voice = None) -> dict:
    """If voice is not passed, the API will try to use the most fitting voice"""
    # sanitize text
    text = text.replace("+", "plus").replace("&", "and").replace("r/", "")

    # prepare url request
    params = {"req_text": text, "speaker_map_type": 0, "aid": 1233}

    if voice is not None:
        params["text_speaker"] = voice

    # send request
    try:
        response = _session.post(URI_BASE, params=params)
    except ConnectionError:
        time.sleep(random.randrange(1, 7))
        response = _session.post(URI_BASE, params=params)

    return response.json()

class TikTokTTSException(Exception):
    def __init__(self, code: int, message: str):
        self._code = code
        self._message = message

    def __str__(self) -> str:
        if self._code == 1:
            return f"Code: {self._code}, reason: probably the aid value isn't correct, message: {self._message}"

        if self._code == 2:
            return f"Code: {self._code}, reason: the text is too long, message: {self._message}"

        if self._code == 4:
            return f"Code: {self._code}, reason: the speaker doesn't exist, message: {self._message}"

        return f"Code: {self._message}, reason: unknown, message: {self._message}"
    

def generate(text, name_for_path):
    voice = random.choice(config["tiktok_voices"].split(","))

    # get the audio from the TikTok API
    data = get_voice(voice=voice, text=text)

    # check if there was an error in the request
    status_code = data["status_code"]
    if status_code != 0:
        raise TikTokTTSException(status_code, data["message"])

    # decode data from base64 to binary
    try:
        raw_voices = data["data"]["v_str"]
    except:
        print("The TikTok TTS returned an invalid response. Please try again later, and report this bug.")
        raise TikTokTTSException(0, "Invalid response")
    decoded_voices = base64.b64decode(raw_voices)

    # write voices to specified filepath
    with open(f"temp/{name_for_path}.mp3", "wb") as out:
        out.write(decoded_voices)
        
        
def generate_audio(post):
    title = post["title"]
    generate(title, "post")
    if post["post_type"] == "comments":
        for i, comment in enumerate(post["comments"]):
            generate(comment["text"], i)
    else:
        for i, sentence in enumerate(post["text"]):
            generate(sentence, i)
    print("Audio generated")


if __name__ == "__main__":
    from scrape import scrape_post
    from image import generate_images
    post = scrape_post("nosleep", "story")
    generate_images(post)
    generate_audio(post)