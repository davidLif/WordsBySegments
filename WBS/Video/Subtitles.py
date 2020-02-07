from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable
from re import sub
import logging


class Subtitles:
    def __init__(self, video_id, subtitles_data):
        self.video_id = video_id
        self.subtitles_data = subtitles_data

    @staticmethod
    def download_subs_from_youtube_video(video_url):
        try:
            subtitles_data = YouTubeTranscriptApi.get_transcript(video_url)
            return Subtitles(video_id=video_url, subtitles_data=subtitles_data)
        except TranscriptsDisabled:
            logging.getLogger().warning(f'skip {video_url} - no subtitles')
            return None
        except VideoUnavailable:
            logging.getLogger().warning(f'skip {video_url} - video is unavailable')
            return None


    def extract_subtitles_words(self):
        for subtitle in self.subtitles_data:
            subtitle['text'] = sub(r'[^a-zA-Z\s]', '', subtitle['text'])
            start = int(subtitle['start'])
            end = int(subtitle['end'])
            for word in subtitle['text'].split(' '):
                yield word, start, end
