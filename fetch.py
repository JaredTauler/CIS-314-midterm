import requests
import re
import os

save_dir = 'cache'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

def fetch(url):
    x = requests.get(
        url
    )
    return x.text

def debug_fetch(url):
    ext = '.html'
    name = re.sub(r'\W+', '', url) # Dollar store hashing

    fname = name + ext

    found = False
    for f in os.listdir(save_dir): # TODO slow, no short circuiting
        if fname == f.__str__():
            found = True

    furi = f'{save_dir}/{fname}'
    if found:
        with open(furi, 'r') as g:
            return g.read()
    else:
        html = fetch(url)

        with open(furi, 'w') as g:
            g.write(html)


        return html

