import sys
from .utils import download

USAGE = """Usage:
    python -m spacy_affixes download lang [version]

Parameters:
- lang. Two characters code for a language
- version. (Optional) Version to use (defaults to '4.1')

For example, the default behaviour is:
    python -m spacy_affixes download es 4.1
"""
# pragma: no cover
if __name__ == "__main__":
    argv_len = len(sys.argv)
    if 2 <= argv_len <= 4 and sys.argv[1] == "download":
        version = sys.argv[3] if argv_len == 4 else None
        download(lang=sys.argv[2], version=version)
    else:
        sys.stdout.write(USAGE)
