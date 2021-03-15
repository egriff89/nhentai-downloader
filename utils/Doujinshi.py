from bs4 import BeautifulSoup
import requests
import os
import re

class Doujinshi:
    def __init__(self, title='nhentai', code=0):
        self.title      = title
        self.code       = code
        self.url        = f'https://nhentai.net/g/{self.code}'
        self.pages      = 0
        self.uploaded   = ''
        self.__parody     = []
        self.__characters = []
        self.__tags       = []
        self.__artists    = []
        self.__groups     = []
        self.__languages  = []
        self.__categories = []

    @property
    def parody(self):
        return self.__parody

    @parody.setter
    def parody(self, parody):
        self.__parody = parody

    @property
    def characters(self):
        return self.__characters

    @parody.setter
    def characters(self, chars):
        self.__characters = chars

    @property
    def tags(self):
        return self.__tags

    @tags.setter
    def tags(self, tags):
        self.__tags = tags

    @property
    def artists(self):
        return self.__artists
    
    @artists.setter
    def artists(self, artists):
        self.__artists = artists

    @property
    def groups(self):
        return self.__groups

    @groups.setter
    def groups(self, groups):
        self.__groups = groups

    @property
    def languages(self):
        return self.__languages

    @languages.setter
    def languages(self, langs):
        self.__languages = langs

    @property
    def categories(self):
        return self.__categories

    @categories.setter
    def categories(self, cats):
        self.__categories = cats


    def verify_tag_category(self, category):
        """Check validity of tag category before its contents can be printed
        
        :param category: Category containing tags assigned to a doujinshi
        """
        if category == 'parody':     cat = self.__parody
        if category == 'characters': cat = self.__characters
        if category == 'tags':       cat = self.__tags
        if category == 'artists':    cat = self.__artists
        if category == 'groups':     cat = self.__groups
        if category == 'languages':  cat = self.__languages
        if category == 'categories': cat = self.__categories

        if len(cat) == 0: return False
        return True


    def get_homepage(self):
        """Request the landing page relative to the provided code

        :rtype: BeautifulSoup object
        """
        # Parse the response content as HTML
        response = requests.get(self.url)
        return BeautifulSoup(response.content, 'html.parser')


    def get_random(self):
        """Get random doujinshi"""
        print('Getting random doujinshi...')
        response = requests.get('https://nhentai.net/random')
        url = response.request.url
        self.url = url

        match = re.search(r'\/g\/(\d+)\/$', url)
        if match:
            self.code = match.group(1)
        


    def get_title(self, page):
        """Get the title of the doujinshi

        :param page: Parsed contents of doujinshi homepage
        :rtype: string
        """
        element = page.find(name='title').contents[0]
        match = re.search(r'^([\w\d\W]+)\u00BB', element, flags=re.IGNORECASE)

        if match:
            self.title = match.group(1).strip()


    def get_num_pages(self, page):
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
                self.pages = int(match.group(1))


    def validate_title(self):
        """Validate title contains no illegal characters
        
        :param title:  Title to validate
        """
        invalid = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

        # Loop through title to check for invalid characters
        for char in self.title:
            for symbol in invalid:
                if char == symbol:
                    # Current character is invalid
                    return (False, symbol)
        return (True, None)


    def download_page(self, page, valid=True):
        """Retrieve the URL of each page image and write it to disk

        :param code:  Gallery code of doujinshi
        :param page:  Page number to download
        :param title: Title to construct filename. Default: 'nhentai'
        """
        # Obtain the URL of the image
        response = requests.get(f'{self.url}/{page}')
        soup = BeautifulSoup(response.content, 'html.parser')
        element = soup.find(id='image-container').contents[0]

        # Parse the image URL from the <img> element
        img_url = re.search(r'src="(.+)\.(jpe?g|png|svg)"', str(element), flags=re.IGNORECASE)
        
        # Generate the new filename
        img_ext = img_url.group(2)
        filename = f'{img_url.group(1)}.{img_ext}'

        # Validate whether title is valid (contains no illegal characters)
        valid, symbol = self.validate_title()
        if not valid: 
            self.title = self.title.replace(symbol, '-')

        # Create the download directory
        collection_path = f'collection/{self.code}-{self.title}'
        os.makedirs(collection_path, exist_ok=True)

        # Download page
        with open(f'{collection_path}/{self.code}-{page}.{img_ext}', mode='wb') as file:
            dl = requests.get(str(filename))
            file.write(dl.content)


    def get_tags(self):
        """Retrieve all tags for selected doujinshi"""
        tag_rx = re.compile(r'/(.+)/.+/', re.IGNORECASE)
        html = self.get_homepage()

        self.uploaded = html.find('time', class_='nobold').contents[0]
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
                            self.parody.append(t.contents[0].text)
                        elif match.group(1) == 'character':
                            self.characters.append(t.contents[0].text)
                        elif match.group(1) == 'tag':
                            self.tags.append(t.contents[0].text)
                        elif match.group(1) == 'artist':
                            self.artists.append(t.contents[0].text)
                        elif match.group(1) == 'group':
                            self.groups.append(t.contents[0].text)
                        elif match.group(1) == 'language':
                            self.languages.append(t.contents[0].text)
                        elif match.group(1) == 'category':
                            self.categories.append(t.contents[0].text)
                except KeyError:
                    pass


    def print_info(self):
        """Print doujinshi information"""
        
        # Grab remaining tags
        self.get_tags()

        print(f'\nTitle: {self.title}')

        if self.verify_tag_category('parody'): 
            print(f'Parodies: ', end=' ')
            for parody in self.parody:
                if parody is None: pass
                else: print(f'"{parody}"', end=' ')

        if self.verify_tag_category('characters'):
            print(f'\nCharacters: ', end='')
            for ch in self.characters: 
                if ch is None: pass
                else: print(f'"{ch}"', end=' ')

        if self.verify_tag_category('tags'):
            print(f'\nTags: ', end='')
            for tag in self.tags: 
                if tag is None: pass
                else: print(f'"{tag}"', end=' ')

        if self.verify_tag_category('artists'):
            print(f'\nArtists: ', end='')
            for artist in self.artists: 
                if artist is None: print('N/A', end=' ')
                else: print(f'"{artist}"', end=' ')

        if self.verify_tag_category('groups'):
            print(f'\nGroups: ', end='')
            for group in self.groups: 
                if group is None: print('N/A', end=' ')
                else: print(f'"{group}"', end=' ')

        if self.verify_tag_category('languages'):
            print(f'\nLanguages: ', end='')
            for lang in self.languages: 
                if lang is None: pass
                else: print(f'"{lang}"', end=' ')

        if self.verify_tag_category('categories'):
            print(f'\nCategories: ', end='')
            for cat in self.categories: 
                if cat is None: pass
                else: print(f'"{cat}"', end=' ')

        print(f'\nGallery ID: {self.code}')
        print(f'Pages: {self.pages}')
        print(f'Uploaded: {self.uploaded}\n')