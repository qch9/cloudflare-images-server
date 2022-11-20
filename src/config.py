import os
import pathlib
import sys
from dataclasses import dataclass

from loguru import logger


@dataclass(frozen=True)
class Config:
    hostname: str  # name of the host where cloudflare-images-server is available
    debug: bool  # print verbose logs
    persistence: bool  # save the app state after restarting
    images_storage: pathlib.Path  # dir to store uploaded image
    videos_storage: pathlib.Path  # dir to store uploaded videos
    internalstate_path: str  # where to save the state of the app. needed only if persistence=True

    create_default_account: bool
    default_account = {
        'account_id': 'bfbdec2a2da54ab1bc801b051ebed06a',
        'account_hash': '573a5ca1603c440',
    }

    @property
    def internal_db_name(self):
        return self.internalstate_path if self.persistence else ':memory:'


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
        images_storage=os.environ.get('IMAGES_STORAGE_PATH', pathlib.Path('../images')),
        videos_storage=os.environ.get('VIDEOS_STORAGE_PATH', pathlib.Path('../videos')),
        create_default_account=bool(os.environ.get('CREATE_DEFAULT_ACCOUNT', False)),
        internalstate_path=os.environ.get('INTERNAL_STATE_PATH', 'cloudflare.db')
    )
