import re

import athos

def command(**options):
    def decorator(func):
        def decorated(*args, **kwargs):
            # decorated() calls the decorated function
            func(*args, **kwargs)

        # add _athos parameter to function
        decorated._athos = options

        # decorator() returns a decorated function
        return decorated

    # command() returns a decorator
    return decorator


class Plugin(object):
    def __init__(self, matrix, athos, config):
        self.matrix = matrix
        self.athos = athos
        self.config = config


class Matcher(object):
    """
    Base matcher method

    Returns always true
    """

    def __init__(self):
        pass

    def check(self, event):
        return True

class TypeMatcher(Matcher):
    """
    Matches a message type
    """
    def __init__(self, typ):
        """
        :param typ str: A message type
        """
        self.typ  = re.compile(typ)

    def check(self, event):
        return event['content']['msgtype'] == self.typ

class RegexMatcher(Matcher):
    """
    Matches using regex
    """
    def __init__(self, pattern):
        """
        :param pattern str: A regex string
        """
        self.pattern  = re.compile(pattern)

    def check(self, event):
        match = re.match(self.pattern, event['content']['body'])
        if match:
            return {'match': match}
        else:
            return False