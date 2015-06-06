import json


def parse_json(filename=None):
    """Takes a str as a filepath or a json and returns the parsed json."""
    if not filename or not isinstance(filename, str):
        return None

    try:
        with open(filename, 'rb') as fp:
            return json.loads(fp.read())
    except IOError:
        return json.loads(filename)
    except ValueError:
        raise


class JSONParserMixin(object):
    """Mixin to support JSON parsing in init."""
    class UnrecognizedFormat(Exception):
        """Raised when an invalid JSON format is passed in."""
        pass

    def __init__(self, *args, **kwargs):
        """
        Intercepts a kwarg json_input and puts the output in self.parsed_json.
        """
        json_file = kwargs.pop('json', None)
        try:
            self.parsed_json = parse_json(json_file)
        except ValueError:
            raise JSONParserMixin.UnrecognizedFormat(
                'Could not parse {} as a json.'.format(json_file)
            )
        super(JSONParserMixin, self).__init__(*args, **kwargs)
