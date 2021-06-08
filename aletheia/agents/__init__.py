import os
import sys
from aletheia.settings import DOWNLOAD_URL
import hashlib


__all__ = ['download', 'ZLAGENT']


def _python2_env():
    """function to check python version for compatibility handling"""
    if sys.version_info[0] < 3:
        return True
    else:
        return False


def _python3_env():
    """function to check python version for compatibility handling"""
    return not _python2_env()


def download(download_url=None, filename_to_save=None):
    if download_url is None or download_url == '':
        print('[Agent][ERROR] - download URL missing for download()')
        return False

    if filename_to_save is None or filename_to_save == '':
        download_url_tokens = download_url.split('/')

    # if not given, use last part of url as filename to save
    if filename_to_save is None or filename_to_save == '':
        download_url_tokens = download_url.split('/')
        filename_to_save = download_url_tokens[-1]

    # delete existing file if exist to ensure freshness
    if os.path.isfile(filename_to_save):
        os.remove(filename_to_save)

    # handle case where url is invalid or has no content
    try:
        if _python2_env():
            import urllib
            urllib.urlretrieve(download_url, filename_to_save)
        else:
            import urllib.request
            urllib.request.urlretrieve(download_url, filename_to_save)

    except Exception as e:
        print('[Agent][ERROR] - failed downloading from ' + download_url + '...')
        print(str(e))
        return False

    # take the existence of downloaded file as success
    if os.path.isfile(filename_to_save):
        return True

    else:
        print('[Agent][ERROR] - failed downloading to ' + filename_to_save)
        return False


ZLAGENT = 'zlagent'


def create_agent(agent_name, path):

    download_url = DOWNLOAD_URL + '/' + agent_name + '.owl'
    download(download_url, path)
    download_url = DOWNLOAD_URL + '/' + agent_name + '.py'
    download(download_url, path)


def gen_md5(path):
    md5_hash = hashlib.md5()
    a_file = open(path, 'rb')
    content = a_file.read()
    md5_hash.update(content)

    digest = md5_hash.hexdigest()
    return digest
