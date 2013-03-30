import json


def read_json(text):
    """
    Convert the raw json-text to a python data structure, ignoring
    python-esque comments (lines starting with a #) since json doesn't
    have native comments.
    """
    without_comments = [line for line in text.splitlines()
                        if not line.startswith('#')]
    return json.loads('\n'.join(without_comments))

def read_file_or_die(fname):
    """
    Read a file and return the raw data.
    Throws exception if it doesn't exist.
    """
    with open(fname, encoding='utf-8') as f:
        return f.read()
