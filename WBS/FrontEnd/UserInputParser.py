

def get_videos_from_user_file(file_path):
    videos = set()
    with open(file_path) as file:
        for url in file.readlines():
            url = url.strip()
            if url:
                videos.add(url[32:])
    return videos
