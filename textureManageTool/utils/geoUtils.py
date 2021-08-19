from maya import cmds


def get_geos(selected):
    """Return the selected geometries or all the geometries in the scene.

    Args:
        selected (bool): Query the selected geometries or not (query all the geometries)

    Returns:
        dict: The selected geometries or all the geometries in the scene.
              key(geometry name), value(geometry node type)

    """

    geos_dict = {}

    if selected:
        nodes_list = cmds.ls(sl=True, flatten=True)
    else:
        nodes_list = cmds.ls(transforms=True)

    for node in nodes_list:
        shape = get_shape(node=node, intermediate=False)
        if shape:
            geo_type = cmds.nodeType(shape)
            if geo_type in ['mesh', 'nurbsSurface']:
                geos_dict[cmds.listRelatives(shape, parent=True)[0]] = geo_type

    return geos_dict


def get_shape(node, intermediate=False):
    """Return geometry shape node.

    Args:
        node (str): Geometry to query shape node.
        intermediate (bool): Return the geometry's intermediate shape node or not.

    Returns:
        str/None: Shape node.

    """

    if cmds.nodeType(node) == 'transform':
        shapes = cmds.listRelatives(node, shapes=True, path=True)
        if not shapes:
            shapes = []
        for shape in shapes:
            is_intermediate = cmds.getAttr('{}.intermediateObject'.format(shape))
            # sometimes there are left over intermediate shapes that are not used so
            # check the connections to make sure we get the one that is used.
            if intermediate and is_intermediate and cmds.listConnections(shape, source=False):
                return shape
            elif not intermediate and not is_intermediate:
                return shape
        if shapes:
            return shapes[0]

    elif cmds.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
        parent_node = cmds.listRelatives(node, parent=True)[0]
        if cmds.nodeType(parent_node) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
            return parent_node
        return node

    return None
