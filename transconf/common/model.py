#coding=utf-8

__author_ = 'chijun'

__all__ = ['BaseModel']


from transconf.common.namebus import NameBus
from transconf.common.reg import register_model_target


class BaseResource(NameBus):
    FORM = None

    def __init__(self):
        NameBus.__init__(self)
        self._form = self.FORM

    def build_rule(self, target, method, func, **kwargs):
        raise NotImplementedError()

    def add_rule(self, target, method, func, **kwargs):
        if not self._form:
            self._form = list()

        if callable(func):
            rule = self.build_rule(target, method, func, **kwargs)
            self._form.append(rule)
        else:
            _func = getattr(self, func)
            if callable(_func):
                rule = self.build_rule(target, method, _func, **kwargs)
                self._form.append(rule)

    @property
    def form(self):
        """

        Returns:
            list: 模型表

        """
        return self._form

    def route(self, target, method, **kwargs):
        """
        路由装饰器

        Args:
            target: 路由对象名
            method: 路由方法名
            **kwargs: 字典参数

        Returns:
            运行结果

        """

        def _wrapper(f):
            self.add_rule(target, method, f, **kwargs)

            def __wrapper(*_args, **_kwargs):
                return f(*_args, **_kwargs)
            return __wrapper
        return _wrapper


class BaseModel(BaseResource):
    """
    基本底层模型对象
    支持基本操作run， init， start， stop

    """
    STRUCT = None
    SPLIT_DOT = '.'
    MEMBER_SPLIT_DOT = ':'

    def __init__(self):
        BaseResource.__init__(self)
        self._struct = self.STRUCT
        self.split = self.SPLIT_DOT
        self.member_split = self.MEMBER_SPLIT_DOT
        self.register()

    def _build_real_nodename(self, lst):
        """
        组建基本节点名

        Args:
            lst(list): 节点名列表

        Returns:
            str: 节点名

        """
        return self.split.join(lst)

    def set_node_member(self, name_lst, key, value):
        """
        设置节点对象的属性和方法

        Args:
            name_lst(list): 节点名列表
            key(str): 属性名，方法名
            value(object): 属性，方法

        Returns:
            bool: 设置成功失败

        """
        real_name = self._build_real_nodename(name_lst)
        n = self.get(real_name)
        if isinstance(n, dict):
            n[key] = value
            return True
        return False

    def init_nodeobj(self, name_lst):
        """
        初始化节点

        Args:
            name_lst(list): 节点名列表

        Returns:
            无

        """
        real_name = self._build_real_nodename(name_lst)
        self.set(real_name, {})

    def get_nodeobj(self, name_lst):
        """
        获取节点对象

        Args:
            name_lst(list): 节点名列表

        Returns:
            object: 节点对象

        """
        real_name = self._build_real_nodename(name_lst)
        return self.get(real_name)

    def register(self):
        register_model_target(self)

    def run(self, target_name, method_name, **kwargs):
        """
        运行节点对象

        Args:
            target_name(str): 对象名
            method_name(str): 方法名
            **kwargs(dict): 方法字典参数

        Returns:
            未实现

        """
        raise NotImplementedError()

    @property
    def struct(self):
        """

        Returns:
            object: 结构对象

        """
        return self._struct

    def init(self, config=None):
        """
        模型初始化过程

        Args:
            config(object): 配置

        Returns:
            未实现

        """
        pass

    def start(self, config=None):
        """
        模型启动过程

        Args:
            config(object): 配置

        Returns:
            未实现

        """
        pass

    def stop(self, config=None):
        """
        模型停止过程

        Args:
            config(object): 配置

        Returns:
            未实现

        """
        pass
