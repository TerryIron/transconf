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


from transconf.common.namebus import NameBus
from transconf.parse_form import FormParser
from transconf.model import Model
from transconf.utils import myException


class ShellTargetNotFound(myException):
    """Raised when target can not found"""
    def __init__(self, target_name):
        self.target_name = target_name

    def __str__(self):
        return "{0} cannot be found".format(self.target_name)


class ModelShell(NameBus):
    """
    模型命令行解释器
    """
    SPLIT_DOT = '.'

    def __init__(self, log=None):
        super(ModelShell, self).__init__()
        self.split = self.SPLIT_DOT
        self.environ = {}
        self.parser = FormParser(log)

    def _run(self, model, name, method, **kwargs):
        return model.run(name, method, **kwargs)

    def run(self, target_name, method_name, **kwargs):
        """
        运行命令

        Args:
            target_name: 命令对象
            method_name: 方法名
            **kwargs: 字典参数

        Returns:
            执行结果

        """
        name_lst = str(target_name).split(self.split)
        if len(name_lst) >= 1:
            model_name = name_lst[0]
            model = self.get(model_name)
            if isinstance(model, Model):
                return self._run(model, tuple(name_lst), method_name, **kwargs)
            return False
        else:
            raise ShellTargetNotFound(target_name)

    def set_env(self, key, value):
        """
        设置解释器环境变量

        Args:
            key: 变量名
            value: 变量值

        Returns:
            未实现

        """
        raise NotImplementedError()

    def get_env(self, key):
        """
        获取解释器环境变量

        Args:
            key: 变量名

        Returns:
            变量值

        """
        raise NotImplementedError()

    def preload_model(self, model_class, config=None):
        """
        预加载模型解释器

        Args:
            model_class: 模型类
            config: 配置对象

        Returns:
            None

        """
        # Check node name is exist ?
        def translate():
            model = model_class() if callable(model_class) else model_class
            model.init(config)
            self.parser.translate(model)
            return model
        model = translate()
        if model:
            for single in model.form:
                self.set(single['node'], model)
        return model

    def load_model(self, model_class, config=None):
        """
        加载并启动模型解释器

        Args:
            model_class: 模型类
            config: 配置对象

        Returns:
            None

        """
        model = self.preload_model(model_class, config)
        if model:
            model.start(config)

    def remove_model(self, name):
        """
        删除模型解释器

        Args:
            name: 解释器名

        Returns:
            None

        """
        model = self.get(name)
        if model:
            model.stop()
        self.remove(name)

    def list_models(self):
        """
        获取模型解释器列表

        Returns:
            list: 模型解释器名列表

        """
        return self.all().keys()
