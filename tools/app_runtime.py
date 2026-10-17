"""Paths shared by source runs and the standalone Windows executable."""
from pathlib import Path
import sys

VERSION = '1.0.1'
FROZEN = bool(getattr(sys, 'frozen', False))
ROOT = (Path(sys._MEIPASS) / 'resources') if FROZEN else Path(__file__).resolve().parents[1]

def default_output():
    return Path.home() / 'Videos' / 'STVideo'

def worker_command(log_file, arguments):
    entry = [sys.executable] if FROZEN else [sys.executable, str(ROOT / 'tools' / 'app.py')]
    return entry + ['--encode', '--log-file', str(log_file)] + list(arguments)
