import json


def parse_json(filename):
    """Takes a str as a filepath and returns the parsed json."""
    if not isinstance(filename, str):
        return None

    try:
        with open(filename, 'rb') as fp:
            return json.loads(fp.read())
    except IOError:
        raise IOError('{} not found!'.format(filename))
    except ValueError:
        raise
