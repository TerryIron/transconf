__author__ = 'chijun'

__all__ = ['NodeItemNotFound', 'NodeItemTypeNotSupport', 'NodeItemStructError', 'NodeStruct']


class NodeItemNotFound(Exception):
    """ Raised when value name not found"""


class NodeItemTypeNotSupport(Exception):
    """ Raised when value's type not support"""


class NodeItemStructError(Exception):
    """ Raised when struct is bad"""


class NodeStruct(object):
    """
        节点结构对象

    """

    SUPPORT_TYPES = None

    def __init__(self):
        self.support_types = self.SUPPORT_TYPES
        self.dic = dict()
        self.branch = set()
        self.name = None

    def set_nodename(self, name):
        """
        设置节点名

        Args:
            name: 节点名

        Returns:
            None

        """
        self.name = name

    @property
    def nodename(self):
        """
        Returns:
            str: 节点名

        """
        return self.name

    def set_branchname(self, name):
        """
        设置添加分支名

        Args:
            name: 分支名

        Returns:
            None

        """
        self.branch.add(name)

    @property
    def branchname(self):
        """
        Returns:
            str: 分支名

        """
        return self.branch

    def exist_branch(self, name):
        """
        检测是否存在分支

        Args:
            name: 分支名

        Returns:
            bool: True或False

        """
        if name not in self.branch:
            return False
        else:
            return True
        
    def keys(self):
        return self.dic.keys()

    def items(self):
        return self.dic.items()

    def set_default(self, var_name, var_type, len=10, default_value=None):
        """
        设置默认值

        Args:
            var_name: 变量名
            var_type: 变量类型
            len: 长度
            default_value: 默认值

        Returns:

        """
        self.dic[var_name] = [[], (default_value), var_type, len]
        return True

    def _check_struct_base(self, struct):
        if not (len(struct) == 4 and type(struct) == list):
            raise NodeItemStructError()

    def _get(self, var_name):
        if var_name in self.dic:
            self._check_struct_base(self.dic[var_name])
            return self.dic[var_name]
        raise NodeItemNotFound('Can not found variable:{0}'.format(var_name))

    def _get_len(self, item):
        return item[3]

    def _get_type(self, item):
        return item[2]

    def _check_type(self, item, data):
        _type = self._get_type(item)
        return _type.check(data)

    def _get_default(self, item):
        return item[1]

    def _get_value(self, item):
        return item[0]

    def get_value(self, var_name):
        """
        获取变量值, 若不存在返回默认值

        Args:
            var_name: 变量名

        Returns:
            object: 值

        """
        item = self._get(var_name)
        v = self._get_value(item)
        if len(v) > 0:
            return v
        else:
            return self._get_default(item)

    def get_default(self, var_name):
        """
        获取默认值

        Args:
            var_name: 变量名

        Returns:
            object: 默认值

        """
        item = self._get(var_name)
        return self._get_default(item)

    def get_type(self, var_name):
        """
        获取变量类型

        Args:
            var_name: 变量名

        Returns:
            str: 类型名

        """
        item = self._get(var_name)
        return self._get_type(item)

    def get_len(self, var_name):
        """
        获取变量长度

        Args:
            var_name: 变量名

        Returns:
            int: 长度

        """
        item = self._get(var_name)
        return self._get_len(item)

    def set(self, var_name, value):
        """
        设置变量值

        Args:
            var_name: 变量名
            value: 值

        Returns:
            bool: True

        """
        _v = self._get(var_name)
        if self._check_type(_v, value):
            _v[0].append(value)
            if len(_v[0]) > self._get_len(_v):
                _v.pop(0)
            return True
        else:
            raise NodeItemTypeNotSupport('Type: {0} not in {1}'.format(_v, self.support_types))

    def check_input(self, key, value):
        """
        检查数据输入

        Args:
            key: 变量名
            value: 变量值

        Returns:
            未实现

        """
        raise NotImplementedError()
