# sharepoint-nextcloud-bridge
Download Microsoft Sharepoint files and upload them to Nextcloud.

## Usage

```shell
usage: main.py [-h] [-v] [-i] [-l <PATH>]

Download Microsoft Sharepoint files and upload them to Nextcloud.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Show additional information for debugging purposes
  -i, --interactive     Credentials will be read from user input instead of .env file
  -l <PATH>, --list <PATH>
                        File containing Sharepoint URLs to download files from. One URL per line
```

## Environment Variables

See [`.env.example`](.env.example)

System environment variables take precedence over the `.env` file.

```shell
# Microsoft Sharepoint Credentials
SHAREPOINT_URL=my.sharepoint.com
SHAREPOINT_USER_NAME=
SHAREPOINT_USER_PASSWORD=

# Nextcloud credentials
NEXTCLOUD_URL=https://nextcloud.com
NEXTCLOUD_USER_NAME=
NEXTCLOUD_USER_PASSWORD=
NEXTCLOUD_REMOTE_PATH=sharepoint/

# Local path for files to be uploaded
FILES_DOWNLOAD_PATH=downloads/
```

# License

[MIT](LICENSE)
