from pytube import YouTube # It is important to install pytube3 and not pytube
import youtube_dl
import ffmpy
import math

SEGMENT_END_ERROR = "The segment end time is larger than the video duration ({0} seconds)"
DOWNLOADED_SEGMENT_NAME = "\\{0}_{1}_{2}.mkv"


class YoutubeVideo:
    def __init__(self, url, ffmpeg_path=r"..\Resources\ffmpeg.exe"):
        self.url = url
        self.ffmpeg_path = ffmpeg_path

    def download_captions(self, output_file_path=None, language='en', caps_format_str=True):
        yt = YouTube(self.url)
        caption_obj = yt.captions.get_by_language_code(language)

        if caps_format_str:
            captions_data = caption_obj.generate_srt_captions()
        else:
            captions_data = caption_obj.xml_captions

        if output_file_path:
            with open(output_file_path, "w") as w:
                w.write(captions_data)
            return output_file_path
        else:
            return  captions_data

    def download_segment(self, output_dir, start, end, max_video_format='720p', min_video_format='480p'):
        video_stream_meta = self._get_video_stream_metadata()

        if self._str_time_to_seconds(end) > video_stream_meta['duration_seconds']:
            raise ValueError(SEGMENT_END_ERROR.format(video_stream_meta['duration_seconds']))

        video_id = video_stream_meta['id']
        audio_streams_info = video_stream_meta['audio_streams_info']
        video_streams_info = video_stream_meta['video_streams_info']
        combined_streams_info = video_stream_meta['combined_streams_info']

        self._filter_video_stream_by_format(
            max_video_format, min_video_format, video_streams_info)
        self._filter_video_stream_by_format(
            max_video_format, min_video_format, combined_streams_info)

        path = self._download_streams_by_ffmpeg(audio_streams_info, combined_streams_info, end, output_dir, start,
                                                video_id, video_streams_info)
        return path

    def _download_streams_by_ffmpeg(self, audio_streams_info, combined_streams_info, end, output_dir, start, video_id,
                                    video_streams_info):
        # "-ss {0} -to {1} -i \"{2}\" -ss {0} -to {1} -i \"{3}\" -map 0:a -map 1:v \"{4}\""
        # both the audio list and video list goes from worst to best. (according to the youtube_dl inner code)
        if len(audio_streams_info) > 0 and len(video_streams_info) > 0:
            # This is the first option because same stream for both is considered part legacy
            youtube_input = {
                audio_streams_info[-1]['url']: '-ss {0} -to {1}'.format(start, end)
                , video_streams_info[-1]['url']: '-ss {0} -to {1}'.format(start, end)}
        elif len(combined_streams_info) > 0:
            youtube_input = {combined_streams_info[-1]['url']: '-ss {0} -to {1}'.format(start, end)}
        else:
            raise TypeError("Couldn't find an audio and video streams for the youtube video "
                            + self.url + "With the required format")
        path = output_dir + DOWNLOADED_SEGMENT_NAME.format(video_id, start.replace(":", ";"), end.replace(":", ";"))
        ff_options = ['-y', '-v', 'quiet', '-hide_banner', '-loglevel panic']
        file_output = {path: '-map 0:a -map 1:v'}
        ffmpy.FFmpeg(
            executable=self.ffmpeg_path, global_options=ff_options, inputs=youtube_input, outputs=file_output).run()
        return path

    def _get_video_stream_metadata(self):
        ydl_opts = {'verbose': False, 'quiet': True}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
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
        return_dict = {
            "audio_streams_info": audios_only_info,
            "combined_streams_info": both_info,
            "duration_seconds": video_duration_seconds,
            "id": video_id,
            "video_streams_info": videos_only_info}
        return return_dict

    @staticmethod
    def _str_time_to_seconds(str_time):
        time_arr = str_time.split(":")
        if len(time_arr) < 1 or time_arr > 3:
            raise TypeError(
                "The string {0} isn't in one of the following formats: ss , mm:ss, hh:mm:ss".format(str_time))

        time_in_seconds = 0
        for i in range(3):
            if len(time_arr) < i:
                return time_in_seconds
            else:
                time_in_seconds = int(time_arr[i]) * math.pow(60, i)

    @staticmethod
    def _filter_video_stream_by_format(max_video_format, min_video_format, video_streams_info):
        max_video_format_num = int(max_video_format[:-1])
        min_video_format_num = int(min_video_format[:-1])

        for i in range(len(video_streams_info)):
            curr_stream_format_num = int(video_streams_info[i]['format_note'][:-1])
            if curr_stream_format_num < min_video_format_num or curr_stream_format_num > max_video_format_num:
                del video_streams_info[i]
