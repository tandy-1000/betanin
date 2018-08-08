from dataclasses import dataclass
from enum import Enum
import importlib

from app.api import torrent_client


_remote = 'transmission'
get_torrents = importlib.import_module('app.api.torrent_client.' + _remote).get_torrents



Status = Enum('TorrentStatus', [
    'REMOTE_COMPLETED', 
    'REMOTE_DOWNLOADING',
    'REMOTE_INACTIVE',
    'COMPLETED', 
    'FAILED',
    'NEEDS_INPUT',
    'PROCESSING',
])


@dataclass
class Torrent:
    status: Status
    id: str
    progress: int
    path: str

    @property
    def is_downloaded(self):
        return self.status == Status.REMOTE_COMPLETED

    def __repr__(self):
        return f'Torrent(id={self.id})'