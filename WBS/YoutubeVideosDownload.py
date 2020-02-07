from pytube import YouTube # It is important to install pytube3 and not pytube
import os
import youtube_dl
import ffmpy
import xml.etree.ElementTree as ElementTree
from html import unescape
import time

FFMPEG_PATH = r"..\Resources\ffmpeg.exe"


def download_youtube_video_and_captions(videourl, path):
    yt = YouTube(videourl)
    yts = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not os.path.exists(path):
        os.makedirs(path)
    yts.download(path)
    caption = yt.captions.get_by_language_code('en')
    if caption:
        with open(r'out\captions.txt', "w") as w:
            w.write(caption.generate_srt_captions())


def get_times_for_words(videos_lst, words_bag):
    pass


def word_bag_for_captions(xml_captions, video_id=0, max_appearences_saved=2):
    words_bag = {}
    root = ElementTree.fromstring(xml_captions)
    for i, child in enumerate(list(root)):
        text = child.text or ""
        caption = unescape(text.replace("\n", " ").replace("  ", " "), )
        caption_words = caption.split(" ")
        duration = float(child.attrib["dur"])
        start = float(child.attrib["start"])
        end = start + duration
        for word in caption_words:
            if word == '':
                continue
            word_curr_data = words_bag.get(word)
            if not word_curr_data:
                words_bag[word] = []
            if len(word_curr_data) < max_appearences_saved:
                words_bag[word].append((video_id, start, end))
        return words_bag


def download_youtube_cut(videourl, dirPath, start, end):
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(videourl, download=False, process=False)
        video_id = info['id']
        video_duration_seconds = info['duration']
        formats_info = info['formats']
        audios_only_info = []
        videos_only_info = []
        both_info = []
        for format_info in formats_info:
            if format_info['acodec'] == 'none' and not format_info['vcodec'] == 'none':
                videos_only_info.append(format_info)
                # print("video")
            elif not format_info['acodec'] == 'none' and format_info['vcodec'] == 'none':
                audios_only_info.append(format_info)
                # print("audio")
            elif not format_info['acodec'] == 'none' and not format_info['vcodec'] == 'none':
                both_info.append(format_info)
            else:
                print("format with no video nor audio")
        # "-ss {0} -to {1} -i \"{2}\" -ss {0} -to {1} -i \"{3}\" -map 0:a -map 1:v \"{4}\""
        path = dirPath + "\\{0}_{1}_{2}.mkv".format(video_id, start.replace(":", ";"), end.replace(":", ";"))
        ff_options = ['-y', '-v', 'quiet', '-hide_banner', '-loglevel panic']
        youtube_input = None
        # both the audio list and video list goes from worst to best. (according to the youtube_dl inner code)
        if len(audios_only_info) > 0 and len(videos_only_info) > 0:
            # This is the first option because same stream for both is considered part legacy
            youtube_input = {
                audios_only_info[-1]['url']: '-ss {0} -to {1}'.format(start, end)
                , videos_only_info[-1]['url']: '-ss {0} -to {1}'.format(start, end)}
        elif len(both_info) > 0:
            youtube_input = {both_info[-1]['url']: '-ss {0} -to {1}'.format(start, end)}
        else:
            raise TypeError("Couldn't find an audio and video streams for the youtube video " + video_id)
        file_output = {path: '-map 0:a -map 1:v'}
        ffmpy.FFmpeg(executable=FFMPEG_PATH, global_options=ff_options, inputs=youtube_input, outputs=file_output)\
            .run()
        return path


start = time.time()
download_youtube_cut('https://www.youtube.com/watch?v=pt9PlFcdvQE', r'..\out'
                     , '00:30', '00:50')
end = time.time()
print("20 seconds")
print(end - start)
