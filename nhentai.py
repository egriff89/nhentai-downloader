from utils import utils
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--number', type=int, help='6-digit gallery number. Example: 209519')
parser.add_argument('-i', '--info', action='store_true', help='Only show infomation and tags')
parser.add_argument('-r', '--random', action='store_true', help='Select a random doujinshi')
parser.add_argument('-z', '--zip', action='store_true', help='Compress downloaded files')
args = parser.parse_args()

info = utils.info

# If no arguments provided, print help and exit
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(0)

if args.random:
    utils.get_random()

if args.number:
    info['code'] = args.number
    info['url'] = f'https://nhentai.net/g/{info["code"]}'


def print_info():
    """Print doujinshi information"""
    
    # Grab remaining tags
    utils.get_tags(info['code'])

    print(f'\nTitle: {info["title"]}')

    if utils.verify_tag('parody'): 
        print(f'Parodies: ', end=' ')
        for parody in info['parody']:
            if parody is None: pass
            else: print (f'"{parody}"', end=' ')

    if utils.verify_tag('characters'):
        print(f'\nCharacters: ', end='')
        for ch in info['characters']: 
            if ch is None: pass
            else: print(f'"{ch}"', end=' ')

    if utils.verify_tag('tags'):
        print(f'\nTags: ', end='')
        for tag in info['tags']: 
            if tag is None: pass
            else: print(f'"{tag}"', end=' ')

    if utils.verify_tag('artists'):
        print(f'\nArtists: ', end='')
        for artist in info['artists']: 
            if artist is None: print('N/A', end=' ')
            else: print(f'"{artist}"', end=' ')

    if utils.verify_tag('groups'):
        print(f'\nGroups: ', end='')
        for group in info['groups']: 
            if group is None: print('N/A', end=' ')
            else: print(f'"{group}"', end=' ')

    if utils.verify_tag('languages'):
        print(f'\nLanguages: ', end='')
        for lang in info['languages']: 
            if lang is None: pass
            else: print(f'"{lang}"', end=' ')

    if utils.verify_tag('categories'):
        print(f'\nCategories: ', end='')
        for cat in info['categories']: 
            if cat is None: pass
            else: print(f'"{cat}"', end=' ')

    print(f'\nGallery ID: {info["code"]}')
    print(f'Pages: {info["pages"]}')
    print(f'Uploaded: {info["uploaded"]}\n')


def main():
    homepage = utils.get_homepage(info['code'])
    info['title'] = utils.get_title(homepage)
    info['pages'] = utils.get_num_pages(homepage)

    
    if args.info:
        # Only info requested - quit
        print_info()
        sys.exit(0)

    print_info()

    print('Downloading...')

    for page in range(1, info["pages"] + 1):
        utils.download_page(info["code"], page, info["title"])

    # Compress to .zip and remove original directory
    # if specified with the '-z' or '--zip' flag
    if args.zip:
        dir_name = f'{info["code"]}-{info["title"]}'
        print(f'Compressing to "{dir_name}.zip" ...')
        utils.compress(dir_name)
        print('Removing downloaded files...')
        utils.remove_dir(dir_name)

    print('Done!\n')

if __name__ == '__main__':
    main()