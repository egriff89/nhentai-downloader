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