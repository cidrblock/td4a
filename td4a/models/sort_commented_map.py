from ruamel.yaml.comments import CommentedMap

def sort_commented_map(commented_map):
    """ Sort a ruamel commented map

        Args:
            commented_map (CommentedMap): The cm to order

        Returns:
            CommentedMap: The sorted commented map

    """
    cmap = CommentedMap()
    for key, value in sorted(commented_map.iteritems()):
        if isinstance(value, CommentedMap):
            cmap[key] = sort_commented_map(value)
        elif isinstance(value, list):
            for i in enumerate(value):
                if isinstance(value[i[0]], CommentedMap):
                    value[i[0]] = sort_commented_map(value[i[0]])
            cmap[key] = value
        else:
            cmap[key] = value
    return cmap
