import requests
from lxml import etree
from lxml.cssselect import CSSSelector as css
from lxml.etree import tostring
import os, json, sys

from PIL import Image

CACHE = 'output/flags.cache'

def download():
    if not os.path.exists(CACHE):
        raise OSError('Run parse() to generate the cache file first.')

    lines = [line.rstrip("\n") for line in open(CACHE, 'r')]
    
    for line in lines:
        tag, path = line.split('-', 1)
        print(tag, path)
        output = 'output/flags/{0}.{1}'.format(tag, path.split('.')[-1])
        print(output)

        # download and save
        r = requests.get('http://eu4.paradoxwikis.com' + path)

        with open(output, 'wb') as f:
            f.write(r.content)

def parse():
    url = 'http://eu4.paradoxwikis.com/Countries'
    r = requests.get(url)
    parser = etree.HTML(r.content)

    #url = 'Countries - Europa Universalis 4 Wiki.html'
    #with open(url, 'r') as f:
    #    parser = etree.HTML(f.read())

    # CSS selectors
    sel = css('table.wikitable tr')

    flags = []

    for row in sel(parser):
        children = row.getchildren()

        tdflag = children[1]
        tdtag = children[2]

        flag = tdflag.cssselect('img')

        if len(flag) == 0:
            continue
        
        # Original sauce
        src = flag[0].get('src')
        src = src.split('/')
        del src[-1]
        del src[2]

        src = "/".join(src)

        tag = str(tostring(tdtag)[5:8])[2:-1]

        flags.append(str(tag) + "-" + src)

    with open(CACHE, 'w') as f:
        f.write("\n".join(flags))
        print('Wrote {0} countries to file'.format(len(flags)))

def thumbnails():
    src = os.path.join('output', 'flags')
    dest = os.path.join(src, '32')
    size = (32,32)

    for root, dirs, files in os.walk(src):
        for f in files:
            if f.endswith('png'):
                # resize
                try:
                    im = Image.open(os.path.join(root, f))
                    im.thumbnail(size)
                    im.save(os.path.join(dest, f), 'PNG')
                    print('Created thumbnail for', f)
                except IOError:
                    print('Cannot create thumbnail for', f)
                    raise

if __name__ == '__main__':
    a = sys.argv[1]
    if a == 'dl':
        download()
    elif a == 'thumbnails':
        thumbnails()
    else:
        parse()