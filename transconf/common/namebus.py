__author__ = 'chijun'

class NameBus(object):
    
    def __init__(self):
        self.namebus = {}

    """
        Target name's structure is like below:
        Sample 1 for memory mode:
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

        Sample 2 for database mode:
                    ---->  $NAMEBUS.NAMEBUS[MODEL_TYPE]
                    |                  
        ns.run('$bus.database[MODEL_A]', 'name') == False
        ns.getattr('$bus.database[MODEL_A]', 'name') == 'ABC'
        ns.setattr('$bus.database[MODEL_A]', 'name', 'ABC') == True
         {
           '$bus': {
               'MODEL_A': {'is_started': A_API, 'is_stop': A_API},
               'MODEL_B': {'is_started': B_API, 'is_stop': B_API},
           },
           '$bus.driver': {
               'MODEL_A': {'start_bus': A_API, 'stop_bus': A_API},
               'MODEL_B': {'start_bus': B_API, 'stop_bus': B_API},
           },
           '$bus.database': {
               'MODEL_A': {'name': A_API)
               'MODEL_B': {'name': B_API)
           }
         }

    """

    def run(self, target_name, method_name, *args, **kwargs):
        raise NotImplementedError()

    def getattr(self, target_name, property_name):
        raise NotImplementedError()

    def setattr(self, target_name, property_name, value):
        raise NotImplementedError()
