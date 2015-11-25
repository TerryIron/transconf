#coding=utf-8

__author__ = 'chijun'


from transconf.common.model_driver import *


class ComputeResource(declarative_base()):
    __tablename__ = 'vm_compute_resource'
    
    cpu = IntColumn()
    cpu_used = IntColumn()
    memory = IntColumn()
    memory_used = IntColumn()
    disk = IntColumn()
    disk_used = IntColumn()

    def __init__(self, cpu, cpu_used, memory, memory_used, disk, disk_used):
        self.cpu = cpu 
        self.cpu_used = cpu_used 
        self.memory = memory
        self.memory_used = memory_used
        self.disk = disk
        self.disk_used = disk_used


class ComputeVM(declarative_base()):
    __tablename__ = 'vm_host'

    vm_host_ip = StrColumn(16)
    vm_uuid = StrColumn(36)

    def __init__(self, vm_host_ip, vm_uuid):
        self.vm_host_ip = vm_host_ip
        self.vm_uuid = vm_uuid


class ComputeVMStatus(declarative_base()):
    __tablename__ = 'vm_status'

    vm_uuid = StrColumn(36)
    power_stat = StrColumn(10)
    event_stat = StrColumn(10)

    def __init__(self, vm_uuid, power_stat, event_stat):
        self.vm_uuid = vm_uuid
        self.power_stat = power_stat
        self.event_stat = event_stat


class ComputeResource(BaseModelDriver):
    def create(self):
        self.define_table(ComputeResource)

    def delete(self):
        self.undefine_table(ComputeResource)

    def clear(self):
        self.clear_table(ComputeResource)


class ComputeVM(BaseModelDriver):
    def create(self):
        self.define_table(ComputeVM)

    def delete(self):
        self.undefine_table(ComputeVM)

    def clear(self):
        self.clear_table(ComputeVM)


class ComputeVMStatus(BaseModelDriver):
    def create(self):
        self.define_table(ComputeVMStatus)

    def delete(self):
        self.undefine_table(ComputeVMStatus)

    def clear(self):
        self.clear_table(ComputeVMStatus)
