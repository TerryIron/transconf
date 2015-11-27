#coding=utf-8

__author_ = 'chijun'

__all__ = ['BaseModel']


from transconf.common.namebus import NameBus


class BaseModel(NameBus):
    """
    基本底层模型对象
    支持基本操作run， init， start， stop

    """
    STRUCT = None
    FORM = None
    SPLIT_DOT = '.'
    MEMBER_SPLIT_DOT = ':'

    def __init__(self):
        NameBus.__init__(self)
        self._form = self.FORM
        self._struct = self.STRUCT
        self.split = self.SPLIT_DOT
        self.member_split = self.MEMBER_SPLIT_DOT

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

    def run(self, target_name, method_name, *args, **kwargs):
        """
        运行节点对象

        Args:
            target_name(str): 对象名
            method_name(str): 方法名
            *args(list): 方法列表参数
            **kwargs(dict): 方法字典参数

        Returns:
            未实现

        """
        raise NotImplementedError()

    @property
    def form(self):
        """

        Returns:
            list: 模型表

        """
        return self._form
        
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
