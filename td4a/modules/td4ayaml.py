from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

class Td4aYaml(YAML):
    """ Build a string dumper for ruamel
    """
    def dump(self, data, stream=None, **kw):
        """ dump as string
        """
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()
