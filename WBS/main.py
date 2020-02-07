import logging
import argparse

from WBS.DataStructs import ProfileData
from WBS.FrontEnd.UserOuput import create_song
from WBS.Video.YoutubeVideo import YoutubeVideo
from WBS.FrontEnd.UserInputParser import *


def update_data(data_file_path, user_videos_input_file_path):
    data = ProfileData.load(data_file_path)
    for video_url in get_videos_from_user_file(user_videos_input_file_path):
        if not data.contains(video_url):
            try:
                data.add(YoutubeVideo(video_url))
                log.info(f'add {video_url} to data')
            except Exception as e:
                log.error(e)
    data.save(data_file_path)


def find_word(word, data_file_path):
    results = ProfileData.load(data_file_path).find(word)
    youtube_links = []
    for result in results:
        youtube_links.append(f'https://youtu.be/{result.video_id}?t={result.time}\n')
    with open(f'find_word/{word}.txt', 'w') as file:
        file.writelines(youtube_links)


def main(param):
    if param.video:
        data_file_path = f'data/{0}.data'.format(param.video.replace('.txt', ''))
        user_videos_input_file_path = f'videos/{param.video}.txt'

        update_data(data_file_path, user_videos_input_file_path)

        if param.word and not param.song:
            find_word(param.word, data_file_path)

        if param.song and not param.word:
            song_file_path = f'songs/{param.song}.txt'
            html_output_path = f'songs_words/{param.song}-{param.video}.html'

            create_song(song_file_path, data_file_path, html_output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--video')
    parser.add_argument('-w', '--word')
    parser.add_argument('-s', '--song')
    args = parser.parse_args()

    logging.basicConfig(format='[%(asctime)s] %(levelname)-s | %(message)s',
                        datefmt='%d-%b-%Y %H:%M:%S', level=logging.ERROR)
    log = logging.getLogger()

    main(args)