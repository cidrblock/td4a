from netaddr import IPNetwork

def convert(network, netmask):
    entry = IPNetwork('%s/%s' % (network, netmask))
    answer = {}
    answer['slashbits'] = '/%s' % getattr(entry, 'prefixlen')
    answer['bits'] = '%s' % getattr(entry, 'prefixlen')
    answer['hostmask'] = str(entry.hostmask)
    answer['netmask'] = str(entry.netmask)
    answer['network'] = network
    answer['net_netmask'] = '%s/%s' % (network, answer['netmask'])
    answer['net_bits'] = '%s/%s' % (network, answer['bits'])
    answer['net_hostmask'] = '%s/%s' % (network, answer['hostmask'])
    return answer

class FilterModule(object):
    def filters(self):
        return {
            'convert': convert
        }
