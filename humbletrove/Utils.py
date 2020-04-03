from tqdm import tqdm
import unicodedata, hashlib, re
import requests

def slugify(value, allow_unicode=False):
    value = str(value)

    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')

    value = re.sub(r'[^\w\s-]', '', value.lower()).strip()
    return re.sub(r'[-\s]+', '-', value)

def create_hash(filename, method):
    hash_obj = getattr(hashlib, method)()
    
    with open(filename, 'rb') as f:
        while True:
            data = f.read(65536)

            if not data:
                break

            hash_obj.update(data)

    return hash_obj.hexdigest()

def download_file(url, filename):
    req = requests.get(url, stream=True)
    total_size = int(req.headers.get('content-length', 0))

    with tqdm(total=total_size, unit='iB', unit_scale=True) as bar:
        with open(filename, 'wb') as f:
            for data in req.iter_content(16384):
                bar.update(len(data))
                f.write(data)