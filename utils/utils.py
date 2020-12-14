from bs4 import BeautifulSoup
import requests
import os
import re


info = {
    'title': '',
    'parody': [],
    'characters': [],
    'tags': [],
    'artists': [],
    'groups': [],
    'languages': [],
    'categories': [],
    'pages': 0,
    'uploaded': ''
}


def get_random():
    print('Getting random doujinshi...')
    response = requests.get('https://nhentai.net/random')
    url = response.request.url
    info['url'] = url

    match = re.search(r'\/g\/(\d+)\/$', url)
    if match:
        info['code'] = match.group(1)


def get_homepage(code):
    """Request the landing page relative to the provided code

    :param code: Six-digit code referencing target doujinshi
    :rtype: BeautifulSoup object
    """
    global info
    # Parse the response content as HTML
    response = requests.get(info['url'])
    return BeautifulSoup(response.content, 'html.parser')


def get_title(page):
    """Get the title of the doujinshi

    :param page: Parsed contents of doujinshi homepage
    :rtype: string
    """
    element = page.find(name='title').contents[0]
    match = re.search(r'^([\w\d\!\-\?\s\,\.]*)', element, flags=re.IGNORECASE)

    if match:
        return match.group(1).strip()


def get_num_pages(page):
    """Return total number of pages

    :param page: Parsed contents of doujinshi homepage
    :rtype: int
    """
    # Grab the section of the page containing the doujin info
    # and the nested <span> tags with the class 'name'
    fields = page.find_all('span', class_='name')
    
    # Look for a <span> tag within 'fields' that just contains numbers
    # and return it
    regex = re.compile(r'^(\d+)$')
    for span in fields:
        match = re.search(regex, span.text)
        if match: 
            return int(match.group(1))


def download_page(code, page, title='nhentai'):
    """Retrieve the URL of each page image and write it to disk

    :param code:  Gallery code of doujinshi
    :param page:  Page number to download
    :param title: Title to construct filename. Default: 'nhentai'
    """
    # Obtain the URL of the image
    response = requests.get(f'https://nhentai.net/g/{code}/{page}')
    soup = BeautifulSoup(response.content, 'html.parser')
    element = soup.find(id='image-container').contents[0]

    # Parse the image URL from the <img> element
    img_url = re.search(r'src="(.+)\.(jpe?g|png|svg)"', str(element), flags=re.IGNORECASE)
    
    # Generate the new filename
    img_ext = img_url.group(2)
    filename = f'{img_url.group(1)}.{img_ext}'

    # Create the download directory
    try:
        os.mkdir(f'{code}-{title}')
    except OSError as error:
        # Directory exists, continuing
        pass

    # Download page
    with open(f'{code}-{title}/{code}-{page}.{img_ext}', mode='wb') as file:
        dl = requests.get(str(filename))
        file.write(dl.content)


def get_tags(code):
    """Retrieve all tags for selected doujinshi"""
    tag_rx = re.compile(r'/(.+)/.+/', re.IGNORECASE)
    html = get_homepage(code)

    info['uploaded'] = html.find('time', class_='nobold').contents[0]
    tags = html.find_all('span', class_='tags')

    for tag in tags:
        for t in tag.contents:
            try:
                match = re.search(tag_rx, t.attrs['href'])
                if match:
                    if match.group(1) == 'parody':
                        info['parody'].append(t.contents[0].text)
                    elif match.group(1) == 'character':
                        info['characters'].append(t.contents[0].text)
                    elif match.group(1) == 'tag':
                        info['tags'].append(t.contents[0].text)
                    elif match.group(1) == 'artist':
                        info['artists'].append(t.contents[0].text)
                    elif match.group(1) == 'group':
                        info['groups'].append(t.contents[0].text)
                    elif match.group(1) == 'language':
                        info['languages'].append(t.contents[0].text)
                    elif match.group(1) == 'category':
                        info['categories'].append(t.contents[0].text)
            except KeyError:
                pass