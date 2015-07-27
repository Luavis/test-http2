"""

    HTTP type class(response, request, status..)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


class Response(object):
    """
    Response object
    """

    def __init__(self, status=None, headers=None, content=None):
        self.status = status
        self.headers = headers
        self.content = content


class Request(object):
    """
    Request object
    """

    def __init__(self, status=None, headers=None, content=None):
        self.status = status
        self.headers = headers
        self.content = content


class Header(object):
    """
    Header object
    """

    def __init__(self, name='', value=''):
        self.name = name
        self.value = value

    def __repr__(self):
        return '<{name}: {value}>'.format(name=self.name, value=self.value)


class HTTPMessage(object):
    """
    HTTPMessage object
    """

    REQ = 'req'
    RES = 'res'

    VERSION_1 = 0x1

    VERSION_1_1 = 0x2

    VERSION_2 = 0x3

    def __init__(self, method='', path='', code=0, type=REQ, verb='', protocol_version=VERSION_1_1):
        self.path = path
        self.method = method
        self.code = code
        self.type = type
        self.verb = verb
        self.protocol_version = protocol_version

    def __repr__(self):
        repr = ''
        if self.type == HTTPMessage.REQ:
            repr = '<verb: {verb}, path: {path}, version: {version}>'.format(
                verb=self.verb, path=self.path, version=self.protocol_version)
        else:
            repr = '<code: {code}, version: {version}>'.format(
                code=self.code, version=self.protocol_version)

        return repr
