from utils.Doujinshi import Doujinshi
from utils import utils
import argparse
import sys
import os

import time

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--number', type=int, help='6-digit gallery number. Example: 209519')
parser.add_argument('-i', '--info', action='store_true', help='Only show infomation and tags')
parser.add_argument('-r', '--random', action='store_true', help='Select a random doujinshi')
parser.add_argument('-z', '--zip', action='store_true', help='Compress downloaded files')
args = parser.parse_args()

# Create new doujinshi instance with default values
dj = Doujinshi()

# If no arguments provided, print help and exit
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(0)

if args.random:
    dj.get_random()

if args.number:
    dj.code = args.number
    dj.url  = f'https://nhentai.net/g/{dj.code}'

def main():
    homepage = dj.get_homepage()
    dj.get_title(homepage)
    dj.get_num_pages(homepage)

    
    if args.info:
        # Only info requested - quit
        dj.print_info()
        sys.exit(0)

    dj.print_info()

    print('Downloading...')

    # t1 = time.perf_counter()
    # Start downloading the pages.
    # Creates a collection folder if it doesn't already exist
    for page in range(1, dj.pages + 1):
        dj.download_page(page)

    # dj.download_pages(dj.pages)

    # t2 = time.perf_counter()

    # Verify title contains no illegal characters
    valid, symbol = dj.validate_title()
    if not valid:
        dj.title = dj.title.replace(symbol, '-')

    # Compress to .zip and remove original directory
    # if specified with the '-z' or '--zip' flag
    if args.zip:
        # Change to 'collection' directory. Prevents 'collection/<files>' folder structure in zip file
        os.chdir('collection')

        # Compress downloaded files into a zip file
        collection_path = f'{dj.code}-{dj.title}'
        print(f'Compressing to "{collection_path}.zip"...')
        utils.compress(collection_path)

        # Delete downloaded files as they're no longer needed
        print('Removing downloaded files...')
        utils.remove_dir(collection_path)

        # Return to root project directory
        os.chdir('..')

    print('Done!\n')

    # print(f'Time: {t2-t1} seconds')

if __name__ == '__main__':
    main()