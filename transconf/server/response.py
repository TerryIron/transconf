# coding=utf-8

#########################################################################
# 
# Copyright (c) 2015-2018  Terry Xi
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#########################################################################


__author__ = 'chijun'


class Response(object):
    """
    服务器响应类
    """

    SUCCESS, FAIL = True, False

    """Response to Request Client"""
    def __init__(self, result, err_msg="", paraminfo={}):
        self.result = result
        self.err_msg = err_msg
        self.params = paraminfo

    def as_dict(self):
        """
        将结果作为字典返回

        Returns:
            dict: 处理后结果

        """
        return {'result': self.result,
                'err_msg': self.err_msg,
                'params': self.params}

    @classmethod
    def from_dict(cls, result):
        """
        从字典读取结果

        Args:
            result: 字典数据

        Returns:
            结果

        """
        try:
            return result['result'] 
        except:
            return None

    @classmethod
    def fail(cls, err):
        """
        返回失败结果

        Args:
            err: 错误异常

        Returns:
            dict: 处理后结果

        """
        if hasattr(err, 'value'):
            r = cls(cls.FAIL, err_msg=str(err.value))
        else:
            r = cls(cls.FAIL, err_msg=str(err))
        return r.as_dict()

    @classmethod
    def success(cls, result):
        """
        返回成功结果

        Args:
            result: 结果数据

        Returns:
            dict: 处理后结果
        """
        r = cls(cls.SUCCESS, paraminfo=result)
        return r.as_dict()

    def __str__(self):
        return str(self.as_dict())
