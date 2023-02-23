import datetime
import time
from moviepy.editor import *
import random,os
from utils import config

resolution = (1080,1920)

def random_start_end(video_len, clip_len):
    x = random.randint(100, int(video_len - clip_len))
    return (x, x + video_len)

def render_video(post):
    # Create clip 'flow'
    flow = ['post']
    for i in range(50):
        if os.path.exists(f'temp/{i}.mp3'):
            flow.append(str(i))

    # Load all the clips
    image_clips = []
    sound_clips = []
    duration = 0
    for part in flow:
        sound_clips.append(
            AudioFileClip(f"temp/{part}.mp3"))
        image_clips.append(
            ImageClip(f"temp/{part}.png",duration=sound_clips[-1].duration)
            .fx(vfx.resize,width=resolution[0]*0.9)
            .set_opacity(0.85)
            .crossfadein(0.2)
            .crossfadeout(0.2)
            )
        duration += sound_clips[-1].duration

    # Combine all the clips into one
    image_clips = concatenate_videoclips(image_clips).set_position(("center",300))
    sound_clips = concatenate_audioclips(sound_clips)

    # 3 minute limit
    # if sound_clips.duration > 60*2.9:
    #     return False

    #Loading background
    background_clip = "rsc/backgrounds/" + random.choice(os.listdir("rsc/backgrounds"))
    background = VideoFileClip(background_clip).fx(vfx.resize, height=resolution[1]).set_position(("center","center"))
    background = background.subclip(
        *random_start_end(background.duration, image_clips.duration)
        )
    
    #Load music
    if len(os.listdir("rsc/songs")):
        song = AudioFileClip("rsc/songs/" + random.choice(os.listdir("rsc/songs")))
        song = afx.audio_loop(song, duration=sound_clips.duration)
        song = song.set_start(0)
        song = song.volumex(0.2)
        sound_clips = sound_clips.set_start(0)
        composite_audio = CompositeAudioClip([song, sound_clips])
        composite_audio = composite_audio.set_duration(sound_clips.duration)
    else:
        composite_audio = sound_clips
    
    
    composite = CompositeVideoClip([background,image_clips],resolution)
    composite.audio = composite_audio
    composite.duration = composite_audio.duration
    
    #Speed up
    composite = composite.speedx(factor=config["speed"])

    # Render
    composite.write_videofile(f'output/{post["id"]}.mp4',threads=4,fps=30)
    return True
