from . import Utils
import argparse, sys, os
import requests

class HumbleTrove(object):

    def __init__(self, base_dir, cookie, platforms, full_verify):
        self.base_dir = base_dir
        self.platforms = platforms
        self.full_verify = full_verify
        self.headers = {'User-Agent': 'Mozilla/5.0', 'cookie': '_simpleauth_sess=' + cookie}

        self.products = None
        self.verified_products = []

    def get_filename(self, platform_name, platform_info, human_name):
        filename = platform_info['url']['web']
        return os.path.join(self.base_dir, platform_name, Utils.slugify(human_name) + os.path.splitext(filename)[1])

    def get_all_products(self):
        if self.products is not None:
            return self.products

        index = 0
        self.products = []

        print('Fetching Humble Trove product information...')

        while True:
            chunk = requests.get('https://humblebundle.com/api/v1/trove/chunk?property=popularity&direction=desc&index={0}'.format(index)).json()

            if not chunk:
                break

            self.products.extend(chunk)
            index += 1

        return self.products

    def redeem_download(self, product_name, download_name):
        data = {'download': download_name, 'download_page': 'false', 'product': product_name}
        req = requests.post('https://www.humblebundle.com/humbler/redeemdownload', headers=self.headers, data=data)

        try:
            return eval(req.text)['success']
        except:
            raise Exception('Invalid response: {0}'.format(req.text))

    def get_download_link(self, download_name, filename):
        data = {'machine_name': download_name, 'filename': filename}
        req = requests.post('https://www.humblebundle.com/api/v1/user/download/sign', headers=self.headers, data=data)

        try:
            return req.json()['signed_url']
        except:
            raise Exception('Invalid response: {0}'.format(req.text))

    def download_product(self, product):
        product_name = product['machine_name']
        human_name = product['human-name']

        for platform_name, platform_info in product['downloads'].items():
            if platform_name not in self.platforms:
                continue

            download_path = self.get_filename(platform_name, platform_info, human_name)

            if os.path.exists(download_path):
                continue

            platform_dir = os.path.dirname(download_path)

            if not os.path.exists(platform_dir):
                os.makedirs(platform_dir)

            download_name = platform_info['machine_name']

            if not self.redeem_download(product_name, download_name):
                print('Could not redeem download for {0} {1}...'.format(product_name, download_name))
                continue

            filename = platform_info['url']['web']
            download_url = self.get_download_link(download_name, filename)

            print('Downloading {0} for {1}...'.format(human_name, platform_name.title()))
            Utils.download_file(download_url, download_path)

    def download_all(self):
        for product in self.get_all_products():
            self.download_product(product)

    def verify_download(self, filename, expected_size=None, expected_hash=None):
        if not os.path.exists(filename):
            raise Exception('File does not exist!')

        if expected_size is not None:
            actual_size = os.path.getsize(filename)

            if actual_size != expected_size:
                raise Exception('File size mismatch, expected {0} bytes, got {1} bytes'.format(expected_size, actual_size))

        if expected_hash is not None:
            actual_hash = Utils.create_hash(filename, 'md5')

            if expected_hash != actual_hash:
                raise Exception('MD5 mismatch, expected {0}, got {1}'.format(expected_hash, actual_hash))

        return True

    def verify_product(self, product, delete=False):
        ok = True
        human_name = product['human-name']

        if human_name in self.verified_products:
            return ok

        for platform_name, platform_info in product['downloads'].items():
            if platform_name not in self.platforms:
                continue

            filename = self.get_filename(platform_name, platform_info, human_name)

            if self.full_verify:
                print('Verifying {0} for {1}...'.format(human_name, platform_name.title()))

            try:
                self.verify_download(
                    filename,
                    expected_size=platform_info['file_size'],
                    expected_hash=platform_info['md5'] if self.full_verify else None
                )
            except Exception as e:
                ok = False

                if delete and os.path.exists(filename):
                    os.remove(filename)

                print('Verification failed for {0} for {1}: {2}'.format(human_name, platform_name.title(), e))
                continue

            self.verified_products.append(human_name)

        return ok

    def verify_all(self, delete=False):
        ok = True

        for product in self.get_all_products():
            if not self.verify_product(product, delete):
                ok = False

        return ok

if __name__ == '__main__':
    try:
        with open('cookie.txt', 'r') as f:
            cookie = f.read()
    except:
        print('Please create a `cookie.txt` file containing your Humble Bundle cookie!')

    parser = argparse.ArgumentParser()
    parser.add_argument('--windows', '-w', action='store_true', help='Download Windows game binaries.')
    parser.add_argument('--linux', '-l', action='store_true', help='Download Linux game binaries.')
    parser.add_argument('--mac', '-m', action='store_true', help='Download Mac game binaries.')
    parser.add_argument('--verify', '-v', action='store_true', help='Run a full hash verification on all games.')
    args = parser.parse_args()
    platforms = []

    if args.windows:
        platforms.append('windows')
    if args.linux:
        platforms.append('linux')
    if args.mac:
        platforms.append('mac')

    if not platforms:
        if sys.platform == 'win32':
            platforms.append('windows')
        elif sys.platform == 'linux':
            platforms.append('linux')
        elif sys.platform == 'darwin':
            platforms.append('mac')

    trove = HumbleTrove(base_dir=os.getcwd(), platforms=platforms, cookie=cookie, full_verify=args.verify)

    while not trove.verify_all(delete=True):
        trove.download_all()

    print('Complete!')