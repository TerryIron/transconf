from easysnmp import Session
import commands


SNMP_VARIABLES = [
    ('1.3.6.1.2.1.1.1', 'sysDescr', None),
    ('.1.3.6.1.2.1.1.3.0', 'sysContact', None),
    ('.1.3.6.1.2.1.2.2.1.10', 'ifInOctets', None),
    ('.1.3.6.1.2.1.2.2.1.16', 'ifOutOctets', None),
    ('.1.3.6.1.2.1.2.2.1.2', 'ifDescr', None),
    ('.1.3.6.1.2.1.2.2.1.8', 'ifOperStatus', None),
    ('.1.3.6.1.2.1.25.1.5.0', 'hrSystemProcesses', None),
    ('.1.3.6.1.2.1.25.1.6.0', 'hrSystemMaxProcesses', None),
    #('.1.3.6.1.2.1.25.2.3.1.3', 'hrStorageDescr', None),
    #('.1.3.6.1.2.1.25.2.3.1.4', 'hrStorageAllocationUnits', None),
    #('.1.3.6.1.2.1.25.2.3.1.5', 'hrStorageSize', None),
    #(('.1.3.6.1.2.1.25.2.3.1.6', 1), 'hrStorageUsed', None),
    #(('.1.3.6.1.2.1.25.2.3.1.6', 3), 'hrStorageUsed', None),
    #(('.1.3.6.1.2.1.25.2.3.1.6', 6), 'hrStorageUsed', None),
    #(('.1.3.6.1.2.1.25.2.3.1.6', 7), 'hrStorageUsed', None),
    #(('.1.3.6.1.2.1.25.2.3.1.6', 10), 'hrStorageUsed', None),
    #(('.1.3.6.1.2.1.25.2.3.1.6', 31), 'hrStorageUsed', None),
    #(('.1.3.6.1.2.1.25.2.3.1.6', 35), 'hrStorageUsed', None),
    #(('.1.3.6.1.2.1.25.2.3.1.6', 36), 'hrStorageUsed', None),
    ('1.3.6.1.2.1.25.3.3.1.2', 'hrProcessorLoad', None),
    ('.1.3.6.1.2.1.31.1.1.1.6', 'ifHCInOctets', None),
    ('.1.3.6.1.2.1.31.1.1.1.10', 'ifHCOutOctets', None),
    ('1.3.6.1.2.1.6.13.1.3', 'tcpConnLocalPort', None),
    ('1.3.6.1.2.1.7.5.1.2', 'udpLocalPort', None),
    ('.1.3.6.1.4.1.2021.10.1.3.1', 'laLoad1', None),
    ('.1.3.6.1.4.1.2021.10.1.3.2', 'laLoad5', None),
    ('.1.3.6.1.4.1.2021.10.1.3.3', 'laLoad15', None),
    ('.1.3.6.1.4.1.2021.13.15.1.1.2', 'devName', None),
    ('.1.3.6.1.4.1.2021.13.15.1.1.3', 'devRdByte', None),
    ('.1.3.6.1.4.1.2021.13.15.1.1.4', 'devWtByte', None),
    ('.1.3.6.1.4.1.2021.4.3.0', 'memAvailSwap', None),
    ('.1.3.6.1.4.1.2021.4.4.0', 'memTotalReal', None),
    ('.1.3.6.1.4.1.2021.4.5.0', 'memAvailReal', None),
    ('.1.3.6.1.4.1.2021.4.6.0', 'memTotalFree', None),
    ('.1.3.6.1.4.1.2021.11.9.0', 'ssCpuSystem', None),
    ('.1.3.6.1.4.1.2021.11.10.0', 'ssCpuIdle', None),
    ('.1.3.6.1.4.1.2021.11.11.0', 'ssCpuRawUser', None),
    ('.1.3.6.1.4.1.2021.11', 'ssIndex', None),
    ('.1.3.6.1.4.1.2021.11.1.0', 'ssErrorName', None),
    ('.1.3.6.1.4.1.2021.11.2.0', 'ssSwapIn', None),
    ('.1.3.6.1.4.1.2021.11.3.0', 'ssSwapOut', None),
    ('.1.3.6.1.4.1.2021.11.4.0', 'ssIOSent', None),
    ('.1.3.6.1.4.1.2021.11.5.0', 'ssIOReceive', None),
    ('.1.3.6.1.4.1.2021.11.6.0', 'ssSysInterrupts', None),
    ('.1.3.6.1.4.1.2021.11.7.0', 'ssSysContext', None),
    ('.1.3.6.1.4.1.2021.11.8.0', 'ssCpuUser', None),
    ('.1.3.6.1.4.1.2021.11.9.0', 'ssCpuSystem', None),
    ('.1.3.6.1.4.1.2021.11.10.0', 'ssCpuIdle', None),
    ('.1.3.6.1.4.1.2021.11.11.0', 'ssCpuRawUser', None),
    ('.1.3.6.1.4.1.2021.11.50.0', 'ssCpuRawNice', None),
    ('.1.3.6.1.4.1.2021.11.51.0', 'ssCpuRawSystem', None),
    ('.1.3.6.1.4.1.2021.11.52.0', 'ssCpuRawIdle', None),
    ('.1.3.6.1.4.1.2021.11.53.0', 'ssCpuRawWait', None),
    ('.1.3.6.1.4.1.2021.11.54.0', 'ssCpuRawKernel', None),
    ('.1.3.6.1.4.1.2021.11.55.0', 'ssCpuRawInterrupt', None),
    ('.1.3.6.1.4.1.2021.11.56.0', 'ssIORawSent', None),
    ('.1.3.6.1.4.1.2021.11.57.0', 'ssIORawReceived', None),
    ('.1.3.6.1.4.1.2021.11.58.0', 'ssRawInterrupts', None),
    ('.1.3.6.1.4.1.2021.11.59.0', 'ssRawContexts', None),
    ('.1.3.6.1.4.1.2021.11.60.0', 'ssCpuRawSoftIRQ', None),
    ('.1.3.6.1.4.1.2021.11.61.0', 'ssRawSwapIn', None),
    ('.1.3.6.1.4.1.2021.11.62.0', 'ssRawSwapOut', None),
]


class SNMPBus(object):
    SNMP_VARIABLES = SNMP_VARIABLES
    def __init__(self, ip, community):
        self.var_oid, self.var_name, self.callable = list(), list(), list()
        for k, v, c in self.SNMP_VARIABLES:
            self.var_oid.append(k)
            self.var_name.append(v)
            self.callable.append(c)
        self.var_oid = tuple(self.var_oid)
        self.var_name = tuple(self.var_name)
        self.callable = tuple(self.callable)
        self._dict = dict()
        self.session = Session(hostname=ip, community=community, version=2)
        self._device_update = "snmpbulkget -v 2c -c {0} {1} .1.3.6.1.2.1.25.2.3.1.3 .1.3.6.1.2.1.25.2.3.1.4 .1.3.6.1.2.1.25.2.3.1.5 .1.3.6.1.2.1.25.2.3.1.6 | awk '!a[$0]++' | grep 'hrStorageUsed\|hrStorageSize\|hrStorageAllocationUnits\|hrStorageDescr'".format(community, ip)

    def __getitem__(self, item):
        if item in self._dict:
            return self._dict[item]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def _checkout_variables(self, varlist):
        _varlist = list()
        _varname = list()
        _callable = list()
        for var in varlist:
            if var in self.var_name:
                i = self.var_name.index(var)
                _varlist.append(var)
                _varname.append(self.var_name[i])
                _callable.append(self.callable[i])
        return _varlist, _varname, _callable

    def _gen_default_variables(self):
        return list(self.var_oid), list(self.var_name), list(self.callable)

    def update(self, varlist=None):
        if not varlist:
            varlist, varname, call = self._gen_default_variables()
        else:
            varlist, varname, call = self._checkout_variables(varlist)
        data = self.session.get_bulk(varlist,1,1)
        #print "data: ",data
        #print data[11]
        for i in range(len(data)):
            d = str(data[i]).split(' ')[1].split('=')[1].strip("'")
            if not callable(call[i]):
                print 'varname', varname[i], ':', d
                self.__setitem__(varname[i], d)
            else:
                self.__setitem__(varname[i], call[i](d))

    def update_devices(self):
        _d = dict()
        data = commands.getoutput(self._device_update).split('\n')
        while data:
            _desc = data.pop(0).split('=')[1].split(':')[1].strip()
            _d[_desc] = dict()
            _unit = data.pop(0).split('=')[1].split(':')[1].strip()
            _d[_desc]['unit'] = _unit
            _size = data.pop(0).split('=')[1].split(':')[1].strip()
            _d[_desc]['size'] = _size
            _used = data.pop(0).split('=')[1].split(':')[1].strip()
            _d[_desc]['used'] = _used
        return _d
            

bus = SNMPBus('10.0.3.30', 'Yovole.C0m')
bus.update()
bus.update_devices()
