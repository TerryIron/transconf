__author__ = 'chijun'


class Response(object):
    """Response to Request Client"""
    SUCCESS, FAIL = True, False

    def __init__(self, result, err_msg="", paraminfo={}):
        self.result = result
        self.err_msg = err_msg
        self.params = paraminfo

    def as_dict(self):
        return {'result': self.result,
                'err_msg': self.err_msg,
                'params': self.params}

    @classmethod
    def fail(cls, err):
        r = cls(cls.FAIL, err_msg=str(err))
        return r.as_dict()

    @classmethod
    def success(cls, result):
        r = cls(cls.SUCCESS, paraminfo=result)
        return r.as_dict()

    def __str__(self):
        return str(self.as_dict())
