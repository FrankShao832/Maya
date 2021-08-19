from pyexiv2 import Image
from collections import OrderedDict

from maya import cmds
import geoUtils, fileManage


def get_geo_connected_shaders(geo):
    """Return given geometry connected shaders.

    Args:
        geo (str): Geometry to query connected shaders

    Returns:
        dict: Shaders connected to the given geometry.
              key(shader name), value(shader node)

    """

    shaders = {}

    geo_shape = geoUtils.get_shape(node=geo, intermediate=False)

    if geo_shape:
        nodes = cmds.listHistory(geo_shape, future=True, allFuture=True)
        shading_engines = [node for node in nodes if cmds.nodeType(node) == 'shadingEngine']
        for shading_engine in shading_engines:
            shaders_nodes = cmds.listConnections('{}.surfaceShader'.format(shading_engine), destination=False)
            if shaders_nodes:
                shader = shaders_nodes[0]
                shaders[shader] = cmds.nodeType(shader)

    return shaders


def get_shader_connected_textures_files(shader):
    """Return given shader connected textures files (nodes and images files paths).

    Args:
        shader (str): Shader to query connected textures files (nodes and images files paths).

    Returns:
        dict: Textures files (nodes and images files paths) connected to the given shader.
              key(file node), value(image file path)

    """

    textures_files = {}

    for node in cmds.listHistory(shader, breadthFirst=True):
        if cmds.nodeType(node) == 'file':
            textures_files[node] = cmds.getAttr('{}.fileTextureName'.format(node))

    return textures_files


def assign_file_texture(file_node, texture_file_name, path):
    """Assign file node texture file path.

    Args:
        file_node (str): Texture file node.
        texture_file_name (str): Texture file name with file extension, '.jpg', '.png', '.tiff'....
        path (str): Texture file path

    """

    if fileManage.check_file_exist(path=path, user_file=texture_file_name):
        cmds.setAttr('{}.fileTextureName'.format(file_node), '{}/{}'.format(path, texture_file_name), type='string')


def get_image_metadata(texture_file_path):
    """Return the metadata of the given image file.

    Args:
        texture_file_path (str): The path of the image file

    Returns:
        dict: The metadata of the given image file.
              key(metadata tag name), value(metadata value)

    """

    # open the image
    image = Image(texture_file_path)
    # extracting the exif metadata
    exif_data = image.read_exif()

    metadata_dict = OrderedDict()
    metadata_dict['Artist'] = ''
    metadata_dict['DateTime'] = ''
    metadata_dict['ImageWidth'] = 0
    metadata_dict['ImageLength'] = 0
    metadata_dict['PixelXDimension'] = 0
    metadata_dict['PixelYDimension'] = 0
    metadata_dict['XResolution'] = 0
    metadata_dict['YResolution'] = 0
    metadata_dict['SamplesPerPixel'] = 0
    metadata_dict['ColorSpace'] = 0
    metadata_dict['FocalLength'] = 0
    metadata_dict['Compression'] = 0
    metadata_dict['ResolutionUnit'] = 0
    metadata_dict['BitsPerSample'] = 0
    metadata_dict['Orientation'] = 0
    metadata_dict['PhotometricInterpretation'] = 0
    metadata_dict['Software'] = ''

    for key, value in exif_data.items():
        if 'Exif.Thumbnail' not in key:
            metadata_name = key.split('.')[-1]
            if metadata_name in metadata_dict:
                metadata_dict[metadata_name] = value

    return metadata_dict
