from gevent.queue import Queue
import gevent
import subprocess

import re

from betanin.api import events
from betanin.api.orm.models.torrent import Torrent
from betanin.extensions import db
from betanin.api.status import BetaStatus
from betanin.api.torrent_client import calc_import_path

ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
PROCESSES = {}
QUEUE = Queue()


def _clean_line(line):
    return ANSI_ESCAPE.sub('', line)


def _add_line(torrent, index, data):
    torrent.add_line(index, data)
    db.session.commit()
    events.line_read(torrent.id, index, data)


def _import_torrent(torrent):
    torrent.delete_lines()
    _add_line(torrent, -1, '[betanin] starting beets cli..')
    proc = subprocess.Popen(
        ['beet', 'import', '-c',
            calc_import_path(torrent.remote.id, torrent.path, torrent.name)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1,
    )
    PROCESSES[torrent.id] = proc
    for i, raw_line in enumerate(iter(proc.stdout.readline, '')):
        # TODO: add regex here to update beta_status to
        # possibly update NEEDS_INPUT
        data = _clean_line(raw_line.rstrip())
        _add_line(torrent, i, data)
    proc.stdout.close()
    proc.wait()
    return proc


def _torrent_from_id(torrent_id):
    return db.session.query(Torrent).get(torrent_id)


def add(torrent):
    QUEUE.put_nowait(torrent)


def start():
    while True:
        torrent_id = QUEUE.get()
        torrent = _torrent_from_id(torrent_id)
        torrent.set_status(BetaStatus.PROCESSING)
        db.session.commit()
        proc = _import_torrent(torrent)
        if proc.returncode == 0:
            torrent.set_status(BetaStatus.COMPLETED)
        else:
            torrent.set_status(BetaStatus.FAILED)
        db.session.commit()
        gevent.sleep(0)