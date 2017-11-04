"""Utility functions for fmrest"""
import requests
from .exceptions import RequestException
from .const import TIMEOUT

"""
# http://docs.python-requests.org/en/master/api/#api-changes
#--- DEBUG
import logging
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

#--- DEBUG
"""

def request(*args, **kwargs):
    """Wrapper around requests library request call"""
    try:
        return requests.request(*args, timeout=TIMEOUT, **kwargs)
    except Exception as ex:
        raise RequestException(ex, args, kwargs) from None

def build_portal_params(portals, names_as_string=False):
    """Takes a list of dicts and returns a dict in a format as FMServer expects it

    FMS expects portals and their options to be specified in the following format:
        portal=["Portal1", "Portal2"]&offset.Portal1=1&range.Portal1=10

    This function will return a dict of params suitable for the requests module.

    Parameters
    -----------
    portals : list
        List of dicts with keys name, offset, range
        Example:
            [
                {
                    'name': 'addressPortal', # FM object name of portal
                    'offset': 1,
                    'range': 50
                },
                {
                    'name': 'notesPortal',
                    'offset': 1,
                    'range': 50
                }
            ]
    names_as_string : bool
        For GET params the list of portal names might need to be turned into
        a string. Use this to get something like '["Portal1", "Portal2"]'.
        If False, portals key will have a value of type list, like ["Portal1", "Portal2"]
    """

    portal_selector = [portal['name'] for portal in portals]
    if names_as_string:
        portal_param = "[" + ', '.join(map(lambda x: '"' + x + '"', portal_selector)) + "]"
        params = {"portal": portal_param}
    else:
        params = {'portal': portal_selector}

    for portal in portals:
        params['offset.' + portal['name']] = portal.get('offset', 1)
        params['range.' + portal['name']] = portal.get('range', 50)

    return params

def cache_generator(iterator, cache):
    """Takes iterator and cache list, caches values before yielding them.
    Eventually flagging cache as complete.

    Parameters
    ----------
    iterator : generator
        Generator to consume
    cache : list
        List holding list of cached values and state of caching.
        If cache[1] is True, all values have been cached.
    """

    for val in iterator:
        cache[0].append(val)
        yield val

    cache[1] = True # all values have been cached
