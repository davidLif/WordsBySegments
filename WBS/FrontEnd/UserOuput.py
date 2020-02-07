from WBS.DataStructs import ProfileData
from re import sub


def create_html(song):
    html = '<html><body>'
    for word in song:
        html += word + ' '
    html += '</body></html>'
    return html


def create_song(songs_file_path, data_file_path, html_output_path):
    song = []
    with open(songs_file_path, 'r') as song_file:
        lines = song_file.readlines()
    data = ProfileData.load(data_file_path)
    for line in lines:
        line = sub(r'[^a-zA-Z\s]', '', line)
        line = line.strip()
        if line:
            for word in line.split(' '):
                result = data.find(word)
                if not result:
                    song.append(word)
                else:
                    e = next(iter(result))
                    song.append(f'<a href="https://youtu.be/{e.video_id}?t={e.time}">{word}</a>')
        song.append('<br>')
    with open(html_output_path, 'w') as file:
        file.write(create_html(song))