#coding=utf-8

__author__ = 'chijun'


from transconf.common.namebus import NameBus
from transconf.parse_form import FormParser
from transconf.model import Model
from transconf.utils import Exception


class ShellTargetNotFound(Exception):
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

    def _run(self, model, name, method, *args, **kwargs):
        return model.run(name, method, *args, **kwargs)

    def run(self, target_name, method_name, *args, **kwargs):
        """
        运行命令

        Args:
            target_name: 命令对象
            method_name: 方法名
            *args: 列表参数
            **kwargs: 字典参数

        Returns:
            执行结果

        """
        name_lst = str(target_name).split(self.split)
        if len(name_lst) >= 1:
            model_name = name_lst[0]
            model = self.get(model_name)
            if isinstance(model, Model):
                return self._run(model, tuple(name_lst), method_name, *args, **kwargs)
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
            model = model_class()
            model.init(config)
            self.parser.translate(model)
            return model
        model = translate()
        if model:
            for single in model.FORM:
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
