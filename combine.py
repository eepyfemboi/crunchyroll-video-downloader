import os
import json
import shutil
import subprocess

def decrypt_fragment(input_file, output_file, key):
    with open(key, 'w') as f:
        f.write(key)
    try:
        fragment_number = int(input_file.split('fragment-')[1].split('-')[0]) + 1
    except:
        fragment_number = 1
    key1 = f'{fragment_number}:{key}'
    subprocess.run(['mp4decrypt', f'--key', key1, input_file, output_file])

def combine_fragments(base_dir):
    with open('decryption_keys.json', 'r') as f:
        decryption_keys = json.load(f)

    fragment_files = [f for f in os.listdir(base_dir) if f.startswith('fragment-') and f.endswith('.m4s')]

    audio_fragments = sorted([f for f in fragment_files if '-a1-' in f], key=lambda x: (int(x.split('-')[1]),))
    video_fragments = sorted([f for f in fragment_files if '-v1-' in f], key=lambda x: (int(x.split('-')[1]),))
    
    audio_fragments = [f for f in fragment_files if 'a1' in f]
    video_fragments = [f for f in fragment_files if 'v1' in f]

    def group_fragments(fragments):
        grouped = {}
        for fragment in fragments:
            f_id = fragment.split('-')[2]
            if f_id not in grouped:
                grouped[f_id] = []
            grouped[f_id].append(fragment)
        return grouped

    audio_groups = group_fragments(audio_fragments)
    video_groups = group_fragments(video_fragments)

    def combine(group, base_init_file, output_file, key):
        decrypted_files = []
        for fragment in group:
            decrypted_fragment = f"decrypted-{fragment}"
            decrypt_fragment(os.path.join(base_dir, fragment), os.path.join(base_dir, decrypted_fragment), key)
            decrypted_files.append(decrypted_fragment)

        with open('filelist.txt', 'w') as f:
            f.write(f"file '{base_init_file}'\n")
            for fragment in decrypted_files:
                f.write(f"file '{os.path.join(base_dir, fragment)}'\n")

        subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'filelist.txt', '-c', 'copy', output_file])
        #os.remove('filelist.txt') #add this back later ig

        #for fragment in decrypted_files:
            #os.remove(os.path.join(base_dir, fragment))

    for f_id, group in audio_groups.items():
        #try:
        init_audio_file = next(f for f in os.listdir(base_dir) if f.startswith(f'init-{f_id}-') and '-a1-' in f)
        output_audio_file = os.path.join(base_dir, f'compiled-{init_audio_file}')
        #output_audio_file = "F:/supportbot/test_cr_downloader/videos/" + f'compiled-{init_audio_file}'
        #print(output_audio_file)
        shutil.copy(os.path.join(base_dir, init_audio_file), output_audio_file)
        key_id = f'{f_id.replace('f', '')}-init-{f_id}-a1-x3.mp4'  # Update with logic to get the correct key ID
        key = decryption_keys.get(key_id)
        print(key)
        print(key_id)
        if key:
            decrypt_fragment(output_audio_file, output_audio_file, key)
            combine(group, output_audio_file, output_audio_file, key)
        #except:
        #    pass

    for f_id, group in video_groups.items():
        #try:
        init_video_file = next(f for f in os.listdir(base_dir) if f.startswith(f'init-{f_id}-') and '-v1-' in f)
        output_video_file = os.path.join(base_dir, f'compiled-{init_video_file}')
        shutil.copy(os.path.join(base_dir, init_video_file), output_video_file)
        key_id = f'{f_id.replace('f', '')}-init-{f_id}-v1-x3.mp4'
        key = decryption_keys.get(key_id)
        print(key)
        print(key_id)
        if key:
            decrypt_fragment(output_video_file, output_video_file, key)
            combine(group, output_video_file, output_video_file, key)
        #except:
        #    pass

combine_fragments('videos')
