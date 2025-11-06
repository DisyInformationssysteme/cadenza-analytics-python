from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version('cadenzaanalytics')
except PackageNotFoundError:
    __version__ = 'develop'
