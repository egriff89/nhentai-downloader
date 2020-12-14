from utils import utils
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--number', type=int, help='6-digit gallery number. Example: 209519')
parser.add_argument('-i', '--info', action='store_true', help='Only show infomation and tags')
parser.add_argument('-r', '--random', action='store_true', help='Select a random doujinshi')
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
    print(f'Parodies: {info["parody"][0]}')

    print(f'Characters: ', end='')
    for ch in info['characters']: print(f'"{ch}"', end=' ')

    print(f'\nTags: ', end='')
    for tag in info['tags']: print(f'"{tag}"', end=' ')

    print(f'\nArtists: ', end='')
    for artist in info['artists']: print(f'"{artist}"', end=' ')

    print(f'\nGroups: ', end='')
    for group in info['groups']: print(f'"{group}"', end=' ')

    print(f'\nLanguages: ', end='')
    for lang in info['languages']: print(f'"{lang}"', end=' ')

    print(f'\nCategories: ', end='')
    for cat in info['categories']: print(f'"{cat}"', end=' ')

    print(f'\nGallery ID: {info["code"]}')
    print(f'Pages: {info["pages"]}')
    print(f'Uploaded: {info["uploaded"]}\n')


def main():
    homepage = utils.get_homepage(info['code'])
    info['title'] = utils.get_title(homepage)
    info['pages'] = utils.get_num_pages(homepage)

    if args.info:
        print_info()
        sys.exit(0)
    else:
        # Print information and exit
        print_info()

    print('Downloading...')

    for page in range(1, info["pages"] + 1):
        utils.download_page(info["code"], page, info["title"])

    print('Done!\n')

if __name__ == '__main__':
    main()