import os
import requests


def read_file(file_name):
    with open(file_name) as f:
        text = f.read()
    f.close()
    return text


def save_file(file_name, text):
    with open(file_name, 'w') as f:
        f.write(text)
    f.close()


def url_for(ext):
    if ext.lower() == '.html':
        return 'https://html-minifier.com/raw'
    if ext.lower() == '.css':
        return 'https://cssminifier.com/raw'
    if ext.lower() == '.js':
        return 'https://javascript-minifier.com/raw'


def minify(file_name, save_as=None):
    _, ext = os.path.splitext(file_name)
    resp = requests.post(url_for(ext), data={'input': read_file(file_name)})

    fname, ext = os.path.splitext(file_name)
    save_file(save_as or f'{fname}.min{ext}', resp.text)
