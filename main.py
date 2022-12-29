#!/usr/bin/env python3

import os
import sys
import sharepy
from sharepy import SharePointSession
import logging
import argparse
import re
from dotenv import dotenv_values

# Create CLI

parser = argparse.ArgumentParser(description="Sync Microsoft Sharepoint file to Nextcloud.")
parser.add_argument('-v', '--verbose', action='store_const', const=logging.DEBUG, default=logging.INFO, help='Show additional information.')
parser.add_argument('-i', '--interactive', action='store_const', const=True, default=False, help='Credentials will be read from user input instead of .env file')
parser.add_argument('-l', '--list', default='files.txt', help='Text file containing Sharepoint URLs to download files from')

args = parser.parse_args()

# Create logger
logger_format = "[%(levelname)s] %(asctime)s - %(message)s"
logging.basicConfig(stream = sys.stdout,
                    format = logger_format,
                    level = args.verbose)

logger = logging.getLogger()


def read_environment() -> dict:
    """
    Read environment and return configuration as dict
    """

    config = {
        **dotenv_values(".env"),  # load variables from .env file
        **os.environ,  # override loaded values with system environment variables
    }
    return config

def download(sharepoint_session: SharePointSession) -> None:

    download_path = 'downloads/'
    download_path_exists = os.path.exists(download_path)
    download_path_is_file = os.path.isfile(download_path)

    if download_path_is_file:
        raise NotADirectoryError(f'{download_path} is not a directory!')

    logger.info(f'Saving downloads in {download_path}')
    if not download_path_exists:
        logger.debug(f'Create folder at {download_path}')
        os.makedirs(download_path)

    url_list = open(str(args.list), 'r')
    url_lines = url_list.readlines()

    for url in url_lines:
        logger.info(f'Downloading from {url}')

        filename = re.search(r'[^/]+$', url).group(0)
        logger.debug(f'Detected filename: {filename}')

        response = sharepoint_session.getfile(url=url, filename=f'{download_path}{filename}')
        logger.debug(response)
    return

def main() -> None:
    
    config = read_environment()
    sharepoint_session: SharePointSession

    logger.debug(f'Configuration dict: {str(config)}')
    
    if args.interactive:
        """
        When only suppling the SHAREPOINT_URL the user is prompted
        for username and password by default.
        """
        logger.warning('Ignoring SHAREPOINT_USER_NAME and SHAREPOINT_USER_PASSWORD.')
        sharepoint_session = sharepy.connect(site=config['SHAREPOINT_URL'])
        download(sharepoint_session)
        return

    logger.info(f'Connecting to {config["SHAREPOINT_URL"]}')
    sharepoint_session = sharepy.connect(
        site=config['SHAREPOINT_URL'],
        username=config['SHAREPOINT_USER_NAME'],
        password=config['SHAREPOINT_USER_PASSWORD']
    )
    download(sharepoint_session)
    return

if __name__ == '__main__':
    main()
