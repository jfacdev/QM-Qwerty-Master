
import urllib.request
import urllib.parse
import json
import os

music_dir = "music"
if not os.path.exists(music_dir):
    os.makedirs(music_dir)

# File titles on Wikimedia Commons
files = [
    ("Holst_Mars.ogg", "File:Holst-_mars.ogg"),
    ("Beethoven_Sym5.ogg", "File:Ludwig_van_Beethoven_-_Symphonie_5_c-moll_-_1._Allegro_con_brio.ogg"),
    ("Mozart_Nachtmusik.ogg", "File:Mozart_-_Eine_kleine_Nachtmusik_-_1._Allegro.ogg")
]

opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'DvorakMaster/1.0 (https://github.com/example/DvorakMaster; juan@example.com)')]
urllib.request.install_opener(opener)

def get_real_url(file_title):
    base_api = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }
    query_string = urllib.parse.urlencode(params)
    api_url = f"{base_api}?{query_string}"
    
    try:
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read().decode())
            pages = data["query"]["pages"]
            for page_id in pages:
                if "imageinfo" in pages[page_id]:
                    return pages[page_id]["imageinfo"][0]["url"]
    except Exception as e:
        print(f"Error getting URL for {file_title}: {e}")
    return None

for filename, file_title in files:
    print(f"Resolving URL for {file_title}...")
    real_url = get_real_url(file_title)
    if real_url:
        print(f"Downloading {real_url} to {filename}...")
        try:
            urllib.request.urlretrieve(real_url, os.path.join(music_dir, filename))
            print(f"Successfully downloaded {filename}")
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
    else:
        print(f"Could not find URL for {file_title}")
