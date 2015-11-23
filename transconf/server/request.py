__author__ = 'chijun'


class RequestTimeout(Exception):
    """Raised when comming request is over-time."""


class InvalidRequest(Exception):
    """Raised when comming request is invalid."""


class Request(object):
    """
    客户端请求类
    """

    """Pick parameters as a request."""
    def __init__(self, **kwargs):
        self.__contains__ = kwargs

    def __getitem__(self, item):   
        return self.__contains__.get(item, None)

    def __setitem__(self, item, val):   
        self.__contains__[item] = val

    def to_dict(self):
        """
        将请求转化为字典

        Returns:
            未实现

        """
        raise NotImplementedError()
