from __future__ import unicode_literals

import json
from flask import Flask, render_template, request, send_from_directory, current_app
from flask_bootstrap import Bootstrap
import requests
from werkzeug.utils import redirect
from youtube_dl import YoutubeDL
import os

os.environ["FLASK_APP"] = "hello.py"
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'haha'
app.config['UPLOAD_FOLDER'] = './uploads'
bootstrap = Bootstrap(app)
audio_downloader = YoutubeDL(
    {
        'format': 'bestaudio/best',
        'outtmpl': './uploads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }
)

appMessage = ''


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", appMessage=appMessage)


@app.route('/youtube-downloader', methods=['POST', 'GET'])
def youtube_downloader():
    videos = []
    try:
        if request.method == "POST" and request.form.get('video_search_value') is not None:
            videos = get_videos(request.form.get('video_search_value'))

    except Exception as e:
        return render_template("error.html", message=e)

    return render_template("youtube-downloader.html", videos=videos, appMessage=appMessage)


@app.route('/download', methods=['POST'])
def download():
    try:
        if request.method == "POST" and request.form.get('download_video_id') is not None:
            videoId = request.form.get('download_video_id')
            filename = request.form.get('download_video_title') + '.mp3'

            audio_downloader.extract_info('https://youtu.be/' + videoId)

            return redirect('/uploads/' + filename)

    except:
        return render_template(
            "error.html",
            message='unable download'
        )

    return render_template("index.html", appMessage=appMessage)


@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download_audio(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename)


def get_videos(video_search_value):
    apiKey = ''

    with open('config.json') as outfile:
        apiKey = json.load(outfile)['ytbApiKey']

    videos = []
    url = 'https://www.googleapis.com/youtube/v3/search' \
          '?part=snippet' \
          '&q=' + video_search_value + \
          '&key=' + apiKey + \
          '&maxResults=10' \
          '&type=video' \
          '&order=viewCount'
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

    try:
        r = requests.get(url, headers=headers)
        videos = json.loads(r.text)
        videos = videos['items']
    except:
        videos = []
        pass

    if len(videos) == 0:
        raise Exception('Missing or invalid Google Api Key')

    return videos


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
