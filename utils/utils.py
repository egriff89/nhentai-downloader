from bs4 import BeautifulSoup
import requests
import zipfile
import sys
import os
import re


# Information for the selected doujinshi
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


def verify_tag_category(category):
    """Check validity of tag category before its contents can be printed
    
    :param category: Category containing tags assigned to a doujinshi
    """
    global info
    # Provided category is empty
    if len(info[category]) == 0: return False

    # Loop through dict keys
    for key in info.keys():
        # Append 'None' type to the key's value if it's an empty list
        if type(info[key]) is list:
            if len(info[key]) == 0:
                info[key].append(None)
    return True


def get_random():
    """Get random doujinshi"""
    print('Getting random doujinshi...')
    response = requests.get('https://nhentai.net/random')
    url = response.request.url
    info['url'] = url

    match = re.search(r'\/g\/(\d+)\/$', url)
    if match:
        info['code'] = match.group(1)


def get_homepage():
    """Request the landing page relative to the provided code

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
    match = re.search(r'^([\w\d\W]+)\u00BB', element, flags=re.IGNORECASE)

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


def validate_title(title):
    """Validate title contains no illegal characters
    
    :param title:  Title to validate
    """
    invalid = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

    # Loop through title to check for invalid characters
    for char in title:
        for symbol in invalid:
            if char == symbol:
                # Current character is invalid
                return (False, symbol)
    return (True, None)

def download_page(code, page, title='nhentai', valid=True):
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

    # Validate whether title is valid (contains no illegal characters)
    valid, symbol = validate_title(title)
    if not valid: 
        title = title.replace(symbol, '-')

    # Create the download directory
    collection_path = f'collection/{code}-{title}'
    os.makedirs(collection_path, exist_ok=True)

    # Download page
    with open(f'{collection_path}/{code}-{page}.{img_ext}', mode='wb') as file:
        dl = requests.get(str(filename))
        file.write(dl.content)


def get_tags():
    """Retrieve all tags for selected doujinshi"""
    tag_rx = re.compile(r'/(.+)/.+/', re.IGNORECASE)
    html = get_homepage()

    info['uploaded'] = html.find('time', class_='nobold').contents[0]
    tags = html.find_all('span', class_='tags')

    # Loop through HTML <span> elements with the class of 'tags'
    for tag in tags:
        for t in tag.contents:

            # Query the child elements' href attribute and append their contents
            # to the appropriate list in the 'info' dict
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


def compress(dir_name):
    """Compress downloaded files into separate archive
    
    :param dir_name:  Directory name containing the downloaded images
    """
    try:
        with zipfile.ZipFile(f'{dir_name}.zip', mode='w') as zip:
            with os.scandir(dir_name) as files:
                for file in files:
                    zip.write(file)
    except OSError as e:
        print(e)
        sys.exit(1)


def remove_dir(dir_name):
    """Remove downloaded files and corresponding directory
    
    :param dir_name:  Directory name containing the downloaded images
    """
    try:
        with os.scandir(dir_name) as files:
            for file in files:
                os.remove(file)
    except OSError as e:
        print(e)
        sys.exit(1)
    os.rmdir(dir_name)