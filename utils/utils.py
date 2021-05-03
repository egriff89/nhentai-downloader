import zipfile
import sys
import os


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


def verify_tags(doujinshi):
    """Verify tag category information
    
    :param doujinshi:  Reference to Doujinshi instance to verify
    """
    if doujinshi.verify_tag_category('parody'): 
        print(f'Parodies: ', end=' ')
        for parody in doujinshi.parody:
            if parody is None: pass
            else: print(f'"{parody}"', end=' ')

    if doujinshi.verify_tag_category('characters'):
        print(f'\nCharacters: ', end='')
        for ch in doujinshi.characters: 
            if ch is None: pass
            else: print(f'"{ch}"', end=' ')

    if doujinshi.verify_tag_category('tags'):
        print(f'\nTags: ', end='')
        for tag in doujinshi.tags: 
            if tag is None: pass
            else: print(f'"{tag}"', end=' ')

    if doujinshi.verify_tag_category('artists'):
        print(f'\nArtists: ', end='')
        for artist in doujinshi.artists: 
            if artist is None: print('N/A', end=' ')
            else: print(f'"{artist}"', end=' ')

    if doujinshi.verify_tag_category('groups'):
        print(f'\nGroups: ', end='')
        for group in doujinshi.groups: 
            if group is None: print('N/A', end=' ')
            else: print(f'"{group}"', end=' ')

    if doujinshi.verify_tag_category('languages'):
        print(f'\nLanguages: ', end='')
        for lang in doujinshi.languages: 
            if lang is None: pass
            else: print(f'"{lang}"', end=' ')

    if doujinshi.verify_tag_category('categories'):
        print(f'\nCategories: ', end='')
        for cat in doujinshi.categories: 
            if cat is None: pass
            else: print(f'"{cat}"', end=' ')