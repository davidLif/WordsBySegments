from pickle import dump, load
from . import Trie


class ProfileData:
    def __init__(self):
        self._profile_videos_word_pool = Trie()
        self._related_video_ids = set()

    def _contains(self, video_id):
        return video_id in self._related_video_ids

    def add_video(self, video_obj):
        if self._contains(video_obj.url):
            return
        self._related_video_ids.add(video_obj.url)
        self._add_video_subtitles_2_word_pool(video_obj)

    def _add_video_subtitles_2_word_pool(self, video_obj):
        video_id = video_obj.id
        for word, start, end in video_obj.substitels.extract_subtitles_words():
            self._profile_videos_word_pool.add(word, (video_id, start))

    def find(self, word):
        return self._profile_videos_word_pool.find(word)

    def save(self, file_path):
        with open(file_path, 'wb') as file:
            dump(self, file)

    @staticmethod
    def load(file_path):
        try:
            with open(file_path, 'rb') as file:
                return load(file)
        except FileNotFoundError:
            return ProfileData()
