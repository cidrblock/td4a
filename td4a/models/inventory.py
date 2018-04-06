from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.module_utils._text import to_bytes
from ansible.parsing.vault import VaultSecret

class TextVaultSecret(VaultSecret):
    '''A secret piece of text. ie, a password. Tracks text encoding.
    The text encoding of the text may not be the default text encoding so
    we keep track of the encoding so we encode it to the same bytes.'''

    def __init__(self, text, encoding=None, errors=None, _bytes=None):
        super(TextVaultSecret, self).__init__()
        self.text = text
        self.encoding = encoding or 'utf-8'
        self._bytes = _bytes
        self.errors = errors or 'strict'

    @property
    def bytes(self):
        '''The text encoded with encoding, unless we specifically set _bytes.'''
        return self._bytes or to_bytes(self.text, encoding=self.encoding, errors=self.errors)

def inventory_load(inventory_sources, vault_secret):
    """ Load the inventory
    """
    loader = DataLoader()
    vault_secrets = [('default', TextVaultSecret(vault_secret))]
    loader.set_vault_secrets(vault_secrets)
    inventory = InventoryManager(loader=loader, sources=inventory_sources)
    result = {}
    for hostname in inventory.hosts:
        host = inventory.get_host(hostname)
        variable_manager = VariableManager(loader=loader, inventory=inventory)
        magic_vars = ['ansible_playbook_python', 'groups', 'group_names', 'inventory_dir',
                      'inventory_file', 'inventory_hostname', 'inventory_hostname_short',
                      'omit', 'playbook_dir']
        all_vars = variable_manager.get_vars(host=host, include_hostvars=True)
        cleaned = ({k: v for (k, v) in all_vars.items() if k not in magic_vars})
        result[hostname] = cleaned
    return result
