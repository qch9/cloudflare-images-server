import os
import sys
from dataclasses import dataclass

from loguru import logger


@dataclass(frozen=True)
class Config:
    hostname: str  # name of the host where cloudflare-images-server is available
    debug: bool  # print verbose logs
    persistence: bool  # save the app state after restarting

    create_default_account: bool
    default_account = {
        'account_id': 'bfbdec2a2da54ab1bc801b051ebed06a',
        'account_hash': '573a5ca1603c440',
    }
    images_storage = '/var/www/images/'


def load_config() -> Config:
    try:
        hostname = os.environ['HOSTNAME']
    except KeyError:
        logger.error('`HOSTNAME` environment variable is required.')
        sys.exit(1)

    return Config(
        hostname=hostname,
        debug=bool(os.environ.get('DEBUG', False)),
        persistence=bool(os.environ.get('PERSISTENCE', False)),
        create_default_account=bool(os.environ.get('CREATE_DEFAULT_ACCOUNT', False)),
    )
