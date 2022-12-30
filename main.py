#!/usr/bin/env python3

import os
import sys
import sharepy
from sharepy import SharePointSession
import logging
import argparse
import re
import nextcloud_client
from dotenv import dotenv_values

# Create CLI

parser = argparse.ArgumentParser(description="Download Microsoft Sharepoint files and upload them to Nextcloud.")
parser.add_argument('-v', '--verbose', action='store_const', const=logging.DEBUG, default=logging.INFO, help='Show additional information for debugging purposes')
parser.add_argument('-i', '--interactive', action='store_const', const=True, default=False, help='Credentials will be read from user input instead of .env file')
parser.add_argument('-l', '--list', default='files.txt', metavar='<PATH>', help='File containing Sharepoint URLs to download files from. One URL per line')

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

def upload(nextcloud_session: nextcloud_client.Client, config: dict) -> None:
    """
    Upload all files within FILES_DOWNLOAD_PATH to NEXTCLOUD_REMOTE_PATH at NEXTCLOUD_URL
    """
    try:
        nextcloud_session.mkdir(config['NEXTCLOUD_REMOTE_PATH'])
    except nextcloud_client.HTTPResponseError as e:
        if e.status_code == 405:
            logger.info('NEXTCLOUD_REMOTE_PATH already exists')
        else:
            logger.exception(e)
    
    logger.info(f'Start uploading files to Nextcloud at {config["NEXTCLOUD_URL"]}')
    for file in os.listdir(config['FILES_DOWNLOAD_PATH']):
        logger.debug(f'Uploading {file} to {config["NEXTCLOUD_REMOTE_PATH"]}{file}')
        nextcloud_session.put_file(config['NEXTCLOUD_REMOTE_PATH'], f'{config["FILES_DOWNLOAD_PATH"]}{file}')
    
    return

def download(sharepoint_session: SharePointSession, config: dict) -> None:
    """
    Download all files from --list option to FILES_DOWNLOAD_PATH
    """

    download_path = config['FILES_DOWNLOAD_PATH']
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
    nextcloud_session = nextcloud_client.Client(config['NEXTCLOUD_URL'])

    logger.debug(f'Configuration dict: {str(config)}')
    
    if args.interactive:
        """
        When only suppling the SHAREPOINT_URL the user is prompted
        for username and password by default.
        """
        logger.warning('Ignoring SHAREPOINT_USER_NAME and SHAREPOINT_USER_PASSWORD.')
        sharepoint_session = sharepy.connect(site=config['SHAREPOINT_URL'])

        logger.warning('Ignoring NEXTCLOUD_USER_NAME and SHAREPOINT_USER_PASSWORD.')
        nc_username = input("Nextcloud username:")
        nc_password = input("Nextcloud password:")

        nextcloud_session.login(nc_username, nc_password)
        
        download(sharepoint_session, config)
        upload(nextcloud_session, config)
        return

    logger.info(f'Connecting to {config["SHAREPOINT_URL"]}')
    sharepoint_session = sharepy.connect(
        site=config['SHAREPOINT_URL'],
        username=config['SHAREPOINT_USER_NAME'],
        password=config['SHAREPOINT_USER_PASSWORD']
    )

    nextcloud_session.login(config['NEXTCLOUD_USER_NAME'], config['NEXTCLOUD_USER_PASSWORD'])
    
    download(sharepoint_session, config)
    upload(nextcloud_session, config)
    return

if __name__ == '__main__':
    main()
