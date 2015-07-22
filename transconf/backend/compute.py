__author__ = 'chijun'


from transconf.common.model_driver import *


class ComputeResource(declarative_base()):
    __tablename__ = 'compute_resource'
    
    cpu = IntColumn()
    cpu_used = IntColumn()
    memory = IntColumn()
    memory_used = IntColumn()

    def __init__(self, cpu, cpu_used, memory, memory_used):
        self.cpu = cpu 
        self.cpu_used = cpu_used 
        self.memory = memory
        self.memory_used = memory_used


class ComputeVMConf(declarative_base()):
    __tablename__ = 'vm_config'

    host_ip = StrColumn(16)
    vm_uuid = StrColumn(36)
    vm_name = StrColumn(36)
    vm_sys = StrColumn(16)
    vm_cpu = IntColumn()
    vm_mem = IntColumn()

    def __init__(self, host_ip, vm_uuid, vm_name, vm_sys, vm_cpu, vm_mem):
        self.host_ip = host_ip
        self.vm_uuid = vm_uuid
        self.vm_name = vm_name
        self.vm_sys = vm_sys
        self.vm_cpu = vm_cpu
        self.vm_mem = vm_mem


class ComputeVMStatus(declarative_base()):
    __tablename__ = 'vm_status'

    host_ip = StrColumn(16)
    vm_uuid = StrColumn(36)
    power_stat = StrColumn(10)
    event_stat = StrColumn(10)

    def __init__(self, host_ip, vm_uuid, power_stat, event_stat):
        self.host_ip = host_ip
        self.vm_uuid = vm_uuid
        self.power_stat = power_stat
        self.event_stat = event_stat


class ComputeResourceBackend(BaseModelDriver):
    def create(self):
        self.define_table(ComputeResource)

    def delete(self):
        self.undefine_table(ComputeResource)

    def clear(self):
        self.clear_table(ComputeResource)


class ComputeVMConfBackend(BaseModelDriver):
    def create(self):
        self.define_table(ComputeVMConf)

    def delete(self):
        self.undefine_table(ComputeVMConf)

    def clear(self):
        self.clear_table(ComputeVMConf)


class ComputeVMStatusBackend(BaseModelDriver):
    def create(self):
        self.define_table(ComputeVMStatus)

    def delete(self):
        self.undefine_table(ComputeVMStatus)

    def clear(self):
        self.clear_table(ComputeVMStatus)
