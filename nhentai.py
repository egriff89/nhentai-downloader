from bs4 import BeautifulSoup
import requests
import sys
import os
import re

if len(sys.argv) > 0:
    code = sys.argv[1].strip()
else:
    sys.exit(1)

def get_homepage(code):
    # Request the landing page relative to the provided code
    # Parse the response content as HTML
    response = requests.get(f'https://nhentai.net/g/{code}')
    return BeautifulSoup(response.content, 'html.parser')

def get_title(page):
    element = page.find(name='title').contents[0]
    match = re.search(r'^([\w\d\!\-\?\s\,\.]*)', element, flags=re.IGNORECASE)

    if match:
        return match.group(1).strip()

def get_num_pages(page):    
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

def main():
    homepage = get_homepage(code)
    title = get_title(homepage)
    pages = get_num_pages(homepage)

    print(f'Title: {title}')
    print(f'Pages: {pages}')
    print(f'Gallery ID: {code}')

    with open('history.txt', mode='a') as f:
        f.write(f'{code} - {title}\n')

    print('Downloading...')

    for page in range(1, pages + 1):
        download_page(code, page, title)

    print('Done!')

if __name__ == '__main__':
    main()
