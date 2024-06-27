from mitmproxy import http
import os
import json
import urllib.parse

video_dir = "videos"
keys_file = "decryption.json"

if not os.path.exists(video_dir):
    os.makedirs(video_dir)

decryption_keys = {}

def save_keys():
    with open(keys_file, 'w') as f:
        json.dump(decryption_keys, f)

def response(flow: http.HTTPFlow) -> None:
    if "video/mp4" in flow.response.headers.get("Content-Type", ""):
        if 'init-' in flow.request.url:
            filename = 'init-' + flow.request.url.split('init-')[1].split('.mp4')[0] + '.mp4'
            with open(os.path.join(video_dir, filename), 'wb') as f:
                f.write(flow.response.content)
        elif 'fragment-' in flow.request.url:
            fragment = flow.request.url.split('fragment-')[1].split('.m4s')[0]
            video_path = os.path.join(video_dir, f'fragment-{fragment}.m4s')
            with open(video_path, "wb") as f:
                f.write(flow.response.content)

        if '*~hmac=' in flow.request.url:
            parsed_url = urllib.parse.urlparse(flow.request.url)
            f_id = flow.request.url.split('-f')[1].split('-')[0]
            key_id = f'{f_id}-{parsed_url.path.split("/")[-1]}'
            hmac_key = flow.request.url.split('*~hmac=')[1]
            decryption_keys[key_id] = hmac_key
            save_keys()
