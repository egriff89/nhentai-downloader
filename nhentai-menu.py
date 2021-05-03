from utils.Doujinshi import Doujinshi
from utils import utils
import sys
import os


def clear():
    '''Clear terminal screen'''
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def choose_again():
    again = input('Do you want to choose another? (y/n): ').strip()
    if again == 'y':
        clear()
        return True
    else:
        sys.exit(1)

def main():
    while True:
        print('**************************')
        print('*   nhentai Downloader   *')
        print('**************************', end='\n')

        gallery_id = input("Enter gallery id, or 'r' for random: ").strip()
        info = input('Summary only, or download? (s/d): ').strip()

        if info == 'd':
            archive = input('Archive after downloading? (y/n): ').strip()
        else:
            archive = False
        
        # Check if user selected random
        if gallery_id == 'r':
            dj = Doujinshi()
            dj.get_random()
            dj.url = f'https://nhentai.net/g/{dj.code}'
        else:
            dj = Doujinshi(code=gallery_id)

        homepage = dj.get_homepage()
        dj.get_title(homepage)
        dj.get_num_pages(homepage)

        # Check if the user only wants a summary printed
        if info == 's':
            dj.print_info()
            if choose_again():
                continue
        
        # Print info and start downloading
        dj.print_info()

        print('Downloading...')
        for page in range(1, dj.pages + 1):
            dj.download_page(page)

         # Verify title contains no illegal characters
        valid, symbol = dj.validate_title()
        if not valid:
            dj.title = dj.title.replace(symbol, '-')

        if archive == 'y':
            # Change to 'collection' directory. Prevents 'collection/<files>' folder structure in zip file
            os.chdir(dj.collection)

            # Compress downloaded files into a zip file
            print(f'Compressing to "{dj.dl_path}.zip"...')
            utils.compress(dj.dl_path)

            # Delete downloaded files as they're no longer needed
            print('Removing downloaded files...')
            utils.remove_dir(dj.dl_path)

            # Return to root project directory
            os.chdir('..')

        print('Done!\n')

        if choose_again():
            continue

if __name__ == '__main__':
    main()