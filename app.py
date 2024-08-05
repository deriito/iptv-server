from flask import Flask, render_template, request, redirect, url_for
import requests
import io
import re

app = Flask(__name__)

STREAM_FILE_URLS = {
    'CN (ipv6)': 'https://live.fanmingming.com/tv/m3u/ipv6.m3u',
    'JP': 'https://raw.githubusercontent.com/luongz/iptv-jp/main/jp.m3u',
    'Global': 'https://raw.githubusercontent.com/YueChan/Live/main/Global.m3u',
    'Radio': 'https://raw.githubusercontent.com/fanmingming/live/main/radio/m3u/fm.m3u'
}

def fetch_and_parse_streams(url):
    response = requests.get(url)
    response.raise_for_status()
    file_content = io.StringIO(response.text)

    streams = []
    for line in file_content:
        line = line.strip()
        if line.startswith("#EXTINF"):
            parts = line.split(' ', 1)
            if len(parts) > 1:
                attributes = parts[1].split(',')
                if len(attributes) == 2:
                    match = re.search(r'tvg-logo="([^"]+)"', attributes[0])
                    logo_url = match.group(1) if match else None
                    tv_name = attributes[1].strip()
                    next_line = next(file_content).strip()
                    if next_line.startswith("http"):
                        streams.append({
                            'name': tv_name,
                            'url': next_line,
                            'logo': logo_url
                        })
    return streams

@app.route('/')
def index():
    return render_template('index.html', stream_urls=STREAM_FILE_URLS)

@app.route('/playlists/<url_name>')
def playlists(url_name):
    if url_name in STREAM_FILE_URLS:
        url = STREAM_FILE_URLS[url_name]
        streams = fetch_and_parse_streams(url)
        return render_template('playlist.html', streams=streams, url_name=url_name)
    else:
        return "URL not found", 404
    
@app.route('/player')
def player():
    stream_url = request.args.get('stream_url')
    return render_template('player.html', stream_url=stream_url)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
