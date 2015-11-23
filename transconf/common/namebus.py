__author__ = 'chijun'


"""
    Target name's structure is like below:
                ---->  NAMEBUS.NAMEBUS[MODEL_TYPE]
                |
    ns.run('bus.driver[MODEL_A]', 'stop_bus') == True
    ns.getattr('bus.driver[MODEL_B]', 'stop_bus') == None
    ns.getattr('bus[MODEL_B]', 'stop_times') == 0
    ns.setattr('bus.driver[MODEL_A]' == False
          ||
          \/
     {
       'bus': {
           'MODEL_A': {'is_started': A_DRV_API, 'is_stop': A_DRV_API},
           'MODEL_B': {'is_started': B_DRV_API, 'stop_times': B_DRV_API},
       },
       'bus.driver': {
           'MODEL_A': {'start_bus': A_API, 'stop_bus': A_API},
           'MODEL_B': {'start_bus': B_API, 'stop_bus': B_API},
       }
     }

                ---->  $NAMEBUS.NAMEBUS[MODEL_TYPE]
                |
    ns.run('$bus.database[MODEL_A]', 'name') == False
    ns.getattr('bus.database[MODEL_A]', 'name') == 'ABC'
    ns.setattr('bus.database[MODEL_A]', 'name', 'ABC') == True
     {
       'bus': {
           'MODEL_A': {'is_started': A_API, 'is_stop': A_API},
           'MODEL_B': {'is_started': B_API, 'is_stop': B_API},
       },
       'bus.driver': {
           'MODEL_A': {'start_bus': A_API, 'stop_bus': A_API},
           'MODEL_B': {'start_bus': B_API, 'stop_bus': B_API},
       },
       'bus.database': {
           'MODEL_A': {'name': A_API)
           'MODEL_B': {'name': B_API)
       }
     }

"""


class NameBus(object):
    """
    空间总线
    作为模型类和模型命令解释器的内置空间

    """
    
    def __init__(self):
        self.namebus = {}

    def get_namebus(self, key):
        """
        获取总线对象

        Args:
            key(str): 对象名称

        Returns:
            object: 总线对象

        """
        return self.namebus.get(key, None)

    def set_namebus(self, key, value, force=False):
        """
        设置总线对象

        Args:
            key(str): 对象名称
            value(object): 总线对象
            force(bool): 是否强制，默认为False

        Returns:
            bool: True或False

        """
        if force:
            self.namebus[key] = value
            return True
        else:
            if key not in self.namebus:
                if callable(value):
                    self.namebus[key] = value()
                else:
                    self.namebus[key] = value
                return True
        return False

    def remove_namebus(self, key):
        """
        删除总线对象

        Args:
            key: 对象名称

        Returns:
            None

        """
        if key in self.namebus:
            self.namebus.pop(key)

    def list_namebus(self):
        """
        获取对象列表

        Returns:
            object: 对象表

        """
        return self.namebus.keys()
