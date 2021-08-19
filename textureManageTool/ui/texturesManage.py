__author__ = "Frank Shao"
__copyright__ = "Copyright 2021, The Textures Manage Tools"

__license__ = "GPL"
__version__ = "001"
__maintainer__ = "Frank Shao"
__email__ = "shaoyupu.318@gmail.com"


import os
from functools import partial

from maya import cmds
from Qt import QtWidgets, QtCore, QtGui, QtCompat, QtOpenGL
import DATA_ITEMS, treeView
from utils import fileManage, geoUtils, textureUtils


# Get the current maya root workspace
current_maya_root_workspace = fileManage.current_maya_root_workspace()
# Get the current python module path
current_module_path = os.path.abspath(os.path.dirname(__file__))
# Get the main ui file path
ui_file = current_module_path + '/texturesManageUI.ui'
# initial DATA ITEMS
DATA_ITEMS = DATA_ITEMS.DATA_ITEMS


# -------------------------------- Main UI Window --------------------------------
# initial app
app = None


class TexturesManage(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        """Skin Tool Main window.

        """

        super(TexturesManage, self).__init__(parent)

        # load the designer UI
        self.ui = QtCompat.loadUi(ui_file)
        self.setCentralWidget(self.ui)
        # set UI title
        self.setWindowTitle(self.ui.windowTitle())
        # set UI size
        self.resize(900, 650)

        # build menu
        self.setMenuBar(self.ui.menubar)
        self.setStatusBar(self.ui.statusbar)

        # set focus policy
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # initial tree view and setup
        self.geometriesTreeView = None
        self.shadersTreeView = None
        self.texturesTreeView = None
        self.texturesLabsTreeView = None
        self.setup_treeview_widget()

        # initial status bar message
        self.ui.statusbar.showMessage("Welcome to Frank's Textures Manage V1.0! ---------- ")

        # make signal connections
        self.make_connections()

    def setup_treeview_widget(self):
        """Create and setting treeview widget.
           geometriesTreeView, shadersTreeView, texturesTreeView, texturesLabsTreeView

        """

        # tree view color --------------------------------------------------------------------
        treeview_color_setting = {
            'WindowText': [26, 209, 255],
            'Button': [50, 50, 50],
            'Light': [255, 255, 255],
            'Mid': [110, 110, 110],
            'Dark': [45, 45, 45],
            'Text': [175, 175, 175],
            'BrightText': [255, 255, 255],
            'Base': [50, 50, 50],
            'Window': [50, 50, 50],
            'Shadow': [45, 45, 45],
            'Highlight': [0, 120, 215],
            'HighlightedText': [255, 255, 255]
        }

        # geometriesTreeView --------------------------------------------------------------------
        self.geometriesTreeView = treeView.TreeView(color_setting=treeview_color_setting)
        # add tree view widget to ui layout
        self.ui.geometries_treeView_verticalLayout.addWidget(self.geometriesTreeView)
        # set the headers
        self.geometriesTreeView.add_headers(
            headers=[
                ('Type', QtWidgets.QHeaderView.ResizeToContents),
                ('Name', QtWidgets.QHeaderView.Stretch)
            ]
        )
        # set drag mode
        self.geometriesTreeView.setDragEnabled(False)
        self.geometriesTreeView.setDragDropMode(self.geometriesTreeView.NoDragDrop)
        self.geometriesTreeView.setSelectionMode(self.geometriesTreeView.SingleSelection)

        # shadersTreeView --------------------------------------------------------------------
        self.shadersTreeView = treeView.TreeView(color_setting=treeview_color_setting)
        # add tree view widget to ui layout
        self.ui.shaders_treeView_verticalLayout.addWidget(self.shadersTreeView)
        # set the headers
        self.shadersTreeView.add_headers(
            headers=[
                ('Type', QtWidgets.QHeaderView.ResizeToContents),
                ('Name', QtWidgets.QHeaderView.Stretch)
            ]
        )
        # set drag mode
        self.shadersTreeView.setDragEnabled(False)
        self.shadersTreeView.setDragDropMode(self.shadersTreeView.NoDragDrop)
        self.shadersTreeView.setSelectionMode(self.shadersTreeView.SingleSelection)

        # texturesTreeView --------------------------------------------------------------------
        self.texturesTreeView = treeView.TreeView(color_setting=treeview_color_setting)
        # add tree view widget to ui layout
        self.ui.textures_treeView_verticalLayout.addWidget(self.texturesTreeView)
        # set the headers
        self.texturesTreeView.add_headers(
            headers=[
                ('File Node', QtWidgets.QHeaderView.Stretch),
                ('File Name', QtWidgets.QHeaderView.Stretch)
            ]
        )
        # set drag mode
        self.texturesTreeView.setDragEnabled(False)
        self.texturesTreeView.setDragDropMode(self.texturesTreeView.NoDragDrop)
        self.texturesTreeView.setSelectionMode(self.texturesTreeView.SingleSelection)

        # texturesLabsTreeView --------------------------------------------------------------------
        self.texturesLabsTreeView = treeView.TreeView(color_setting=treeview_color_setting)
        # add tree view widget to ui layout
        self.ui.texturesLabs_treeView_verticalLayout.addWidget(self.texturesLabsTreeView)
        # set the headers
        self.texturesLabsTreeView.add_headers(
            headers=[
                ('File Name', QtWidgets.QHeaderView.Stretch)
            ]
        )
        # set drag mode
        self.texturesLabsTreeView.setDragEnabled(False)
        self.texturesLabsTreeView.setDragDropMode(self.texturesLabsTreeView.NoDragDrop)
        self.texturesLabsTreeView.setSelectionMode(self.texturesLabsTreeView.SingleSelection)

    def load_geometries(self, selected):
        """Load geometries into geometriesTreeView, so to query connected shaders later on.

        Args:
            selected (bool): Query the selected geometries or not (query all the geometries)

        """

        # refresh all the tree view
        self.geometriesTreeView.refresh()
        self.shadersTreeView.refresh()
        self.texturesTreeView.refresh()

        # load geometries
        geos_dict = geoUtils.get_geos(selected=selected)

        if geos_dict:
            geos_kwargs_to_add = []
            for geo, geo_type in geos_dict.items():
                type_kwargs = DATA_ITEMS['str'].copy()
                type_kwargs['default'] = geo_type
                type_kwargs['bg_color'] = [50, 50, 50]
                type_kwargs['bg_alpha'] = 255
                type_kwargs['text_color'] = [175, 175, 175]
                type_kwargs['text_alpha'] = 255
                type_kwargs['size'] = 9
                type_kwargs['bold'] = False
                type_kwargs['column_size'] = 125
                type_kwargs['editable'] = False
                type_kwargs['paint'] = False

                geo_kwargs = DATA_ITEMS['str'].copy()
                geo_kwargs['default'] = geo
                geo_kwargs['bg_color'] = [40, 40, 40]
                geo_kwargs['bg_alpha'] = 255
                geo_kwargs['text_color'] = [175, 175, 175]
                geo_kwargs['text_alpha'] = 255
                geo_kwargs['size'] = 9
                geo_kwargs['bold'] = False
                geo_kwargs['column_size'] = 250
                geo_kwargs['editable'] = False
                geo_kwargs['paint'] = False

                geos_kwargs_to_add.append([type_kwargs, geo_kwargs])

            self.geometriesTreeView.add_items(items_kwargs=geos_kwargs_to_add, unique_name=False, parent_item=None)

    def load_shaders(self):
        """Load selected geometry's connected shaders into shadersTreeView, so to query connected textures later on.

        """

        # refresh shaders, textures tree view
        self.shadersTreeView.refresh()
        self.texturesTreeView.refresh()

        # load shaders
        indexes = self.geometriesTreeView.selectedIndexes()
        if indexes:
            items = self.geometriesTreeView.get_items()
            geo_item = items[0]['children'][0][1]

            if cmds.objExists(geo_item['kwargs']['default']):
                geo = geo_item['kwargs']['default']

                shaders = textureUtils.get_geo_connected_shaders(geo=geo)
                shaders_kwargs_to_add = []
                for shader, shader_node in shaders.items():
                    node_kwargs = DATA_ITEMS['str'].copy()
                    node_kwargs['default'] = shader_node
                    node_kwargs['bg_color'] = [50, 50, 50]
                    node_kwargs['bg_alpha'] = 255
                    node_kwargs['text_color'] = [175, 175, 175]
                    node_kwargs['text_alpha'] = 255
                    node_kwargs['size'] = 9
                    node_kwargs['bold'] = False
                    node_kwargs['column_size'] = 125
                    node_kwargs['editable'] = False
                    node_kwargs['paint'] = False

                    shader_kwargs = DATA_ITEMS['str'].copy()
                    shader_kwargs['default'] = shader
                    shader_kwargs['bg_color'] = [40, 40, 40]
                    shader_kwargs['bg_alpha'] = 255
                    shader_kwargs['text_color'] = [175, 175, 175]
                    shader_kwargs['text_alpha'] = 255
                    shader_kwargs['size'] = 9
                    shader_kwargs['bold'] = False
                    shader_kwargs['column_size'] = 250
                    shader_kwargs['editable'] = False
                    shader_kwargs['paint'] = False

                    shaders_kwargs_to_add.append([node_kwargs, shader_kwargs])

                if shaders_kwargs_to_add:
                    self.shadersTreeView.add_items(
                        items_kwargs=shaders_kwargs_to_add, unique_name=False, parent_item=None
                    )

    def load_textures(self):
        """Load selected shader's connected texture files into texturesTreeView

        """

        # refresh textures tree view
        self.texturesTreeView.refresh()

        # load shaders
        indexes = self.shadersTreeView.selectedIndexes()
        if indexes:
            items = self.shadersTreeView.get_items()
            shader_item = items[0]['children'][0][1]

            if cmds.objExists(shader_item['kwargs']['default']):
                shader = shader_item['kwargs']['default']

                textures_files = textureUtils.get_shader_connected_textures_files(shader=shader)
                textures_files_kwargs_to_add = []
                for file_node, texture_file_path in textures_files.items():
                    node_kwargs = DATA_ITEMS['str'].copy()
                    node_kwargs['default'] = file_node
                    node_kwargs['bg_color'] = [50, 50, 50]
                    node_kwargs['bg_alpha'] = 255
                    node_kwargs['text_color'] = [175, 175, 175]
                    node_kwargs['text_alpha'] = 255
                    node_kwargs['size'] = 9
                    node_kwargs['bold'] = False
                    node_kwargs['column_size'] = 125
                    node_kwargs['editable'] = False
                    node_kwargs['paint'] = False

                    path_kwargs = DATA_ITEMS['str'].copy()
                    path_kwargs['default'] = texture_file_path.split('/')[-1]
                    path_kwargs['bg_color'] = [40, 40, 40]
                    path_kwargs['bg_alpha'] = 255
                    path_kwargs['text_color'] = [175, 175, 175]
                    path_kwargs['text_alpha'] = 255
                    path_kwargs['size'] = 9
                    path_kwargs['bold'] = False
                    path_kwargs['column_size'] = 250
                    path_kwargs['editable'] = False
                    path_kwargs['paint'] = False
                    path_kwargs['toolTip'] = texture_file_path

                    textures_files_kwargs_to_add.append([node_kwargs, path_kwargs])

                if textures_files_kwargs_to_add:
                    self.texturesTreeView.add_items(
                        items_kwargs=textures_files_kwargs_to_add, unique_name=False, parent_item=None
                    )

    def set_textures_labs_path(self):
        """Set textures labs path to load textures files to the texturesLabsTreeView

        """

        textures_labs_path = fileManage.maya_file_dialog(
            caption='Find Textures',
            file_filter='',
            file_mode=3,
            starting_directory='{}/sourceimages'.format(current_maya_root_workspace)
        )

        if textures_labs_path:

            # refresh textures labs tree view
            self.texturesLabsTreeView.refresh()

            images_types = [".jpg", ".tif", ".png", ".JPG", "JPEG", "JPE", "PNG", "TIF", "TIFF"]
            images = []
            for image_type in images_types:
                type_images = fileManage.get_all_files(
                    path=textures_labs_path, file_extension=image_type, return_without_ext=False
                )
                images.extend(type_images)

            textures_labs_files_kwargs_to_add = []
            for image in images:
                image_path_kwargs = DATA_ITEMS['str'].copy()
                image_path_kwargs['default'] = image
                image_path_kwargs['bg_color'] = [50, 50, 50]
                image_path_kwargs['bg_alpha'] = 255
                image_path_kwargs['text_color'] = [175, 175, 175]
                image_path_kwargs['text_alpha'] = 255
                image_path_kwargs['size'] = 9
                image_path_kwargs['bold'] = False
                image_path_kwargs['column_size'] = 250
                image_path_kwargs['editable'] = False
                image_path_kwargs['paint'] = False
                image_path_kwargs['toolTip'] = '{}/{}'.format(textures_labs_path, image)

                textures_labs_files_kwargs_to_add.append([image_path_kwargs])

            if textures_labs_files_kwargs_to_add:
                self.texturesLabsTreeView.add_items(
                    items_kwargs=textures_labs_files_kwargs_to_add, unique_name=False, parent_item=None
                )

    def load_texture_to_preview_and_metadata_box(self):
        """Load selected texture into preview label
           and selected texture metadata into texturesMetaData textEdit

        """

        # load texture
        texture_pixmap = QtGui.QPixmap('')
        texture_metadata_info = ''

        indexes = self.texturesTreeView.selectedIndexes()
        if indexes:
            items = self.texturesTreeView.get_items()
            texture_item = items[0]['children'][0][1]
            texture_file_path = texture_item['kwargs']['toolTip'].rpartition('/')
            texture_path, texture_file = texture_file_path[0], texture_file_path[-1]

            if fileManage.check_file_exist(path=texture_path, user_file=texture_file):
                # set texture pixmap for preview
                texture_pixmap = QtGui.QPixmap(texture_item['kwargs']['toolTip'])
                # get texture metadata for information display
                texture_metadata_dict = textureUtils.get_image_metadata(
                    texture_file_path=texture_item['kwargs']['toolTip']
                )
                for key, value in texture_metadata_dict.items():
                    texture_metadata_info += ("{:20}: {}\r".format(key, value))

        # set pixmap to label
        self.ui.texturesPreview_label.setPixmap(
            texture_pixmap.scaled(
                self.ui.texturesPreview_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
        )
        # set text to text edit
        self.ui.texturesMetaData_textEdit.setText(texture_metadata_info)

    def load_texture_to_labs_preview_and_metadata_box(self):
        """Load selected texture in the textures labs into labs preview label
           and selected texture metadata into texturesLabsMetaData textEdit

        """

        # load texture
        labs_texture_pixmap = QtGui.QPixmap('')
        lab_texture_metadata_info = ''

        indexes = self.texturesLabsTreeView.selectedIndexes()
        if indexes:
            items = self.texturesLabsTreeView.get_items()
            texture_lab_item = items[0]['children'][0][0]
            texture_lab_file_path = texture_lab_item['kwargs']['toolTip'].rpartition('/')
            texture_lab_path, texture_lab_file = texture_lab_file_path[0], texture_lab_file_path[-1]

            if fileManage.check_file_exist(path=texture_lab_path, user_file=texture_lab_file):
                labs_texture_pixmap = QtGui.QPixmap(texture_lab_item['kwargs']['toolTip'])

                # get lab texture metadata for information display
                lab_texture_metadata_dict = textureUtils.get_image_metadata(
                    texture_file_path=texture_lab_item['kwargs']['toolTip']
                )
                for key, value in lab_texture_metadata_dict.items():
                    lab_texture_metadata_info += ("{:20}: {}\r".format(key, value))

        self.ui.texturesLabsPreview_label.setPixmap(
            labs_texture_pixmap.scaled(
                self.ui.texturesLabsPreview_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
        )
        # set text to text edit
        self.ui.texturesLabsMetaData_textEdit.setText(lab_texture_metadata_info)

    def reassign_texture(self):
        """reassign texture for geometry and change it in texturesTreeView.

        """

        current_textures_indexes = self.texturesTreeView.selectedIndexes()
        current_textures_labs_indexes = self.texturesLabsTreeView.selectedIndexes()

        if current_textures_indexes and current_textures_labs_indexes:
            current_textures_items = self.texturesTreeView.get_items()
            current_texture_item = current_textures_items[0]['children'][0][1]
            current_file_node_item = current_textures_items[0]['children'][0][0]
            current_file_node = current_file_node_item['kwargs']['default']

            textures_labs_items = self.texturesLabsTreeView.get_items()
            texture_lab_item = textures_labs_items[0]['children'][0][0]
            texture_lab_file_path = texture_lab_item['kwargs']['toolTip'].rpartition('/')
            texture_lab_path, texture_lab_file = texture_lab_file_path[0], texture_lab_file_path[-1]

            # change texture in the scene
            textureUtils.assign_file_texture(
                file_node=current_file_node, texture_file_name=texture_lab_file, path=texture_lab_path
            )

            # new texture kwargs
            path_kwargs = DATA_ITEMS['str'].copy()
            path_kwargs['default'] = texture_lab_file
            path_kwargs['bg_color'] = [40, 40, 40]
            path_kwargs['bg_alpha'] = 255
            path_kwargs['text_color'] = [175, 175, 175]
            path_kwargs['text_alpha'] = 255
            path_kwargs['size'] = 9
            path_kwargs['bold'] = False
            path_kwargs['column_size'] = 250
            path_kwargs['editable'] = False
            path_kwargs['paint'] = False
            path_kwargs['toolTip'] = texture_lab_item['kwargs']['toolTip']

            # change texture name in the tree view
            self.texturesTreeView.edit_item(
                item=current_texture_item['item'], item_kwargs=path_kwargs, unique_name=False
            )

            # change texture display in the preview label
            texture_pixmap = QtGui.QPixmap(texture_lab_item['kwargs']['toolTip'])
            self.ui.texturesPreview_label.setPixmap(
                texture_pixmap.scaled(
                    self.ui.texturesPreview_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
                )
            )

    def select_geometry(self):
        """Select geometry item in the geometriesTreeView, select corresponding actual geometry in the scene.

        """

        indexes = self.geometriesTreeView.selectedIndexes()
        if indexes:
            items = self.geometriesTreeView.get_items()
            geo_item = items[0]['children'][0][1]

            if cmds.objExists(geo_item['kwargs']['default']):
                cmds.select(geo_item['kwargs']['default'])

    def select_shader(self):
        """Select shader item in the shadersTreeView, select corresponding actual shader node in the scene.

        """

        indexes = self.shadersTreeView.selectedIndexes()
        if indexes:
            items = self.shadersTreeView.get_items()
            shader_item = items[0]['children'][0][1]

            if cmds.objExists(shader_item['kwargs']['default']):
                cmds.select(shader_item['kwargs']['default'])

    def select_texture(self):
        """Select texture item in the texturesTreeView, select corresponding actual texture file node in the scene.

        """

        indexes = self.texturesTreeView.selectedIndexes()
        if indexes:
            items = self.texturesTreeView.get_items()
            texture_item = items[0]['children'][0][0]

            if cmds.objExists(texture_item['kwargs']['default']):
                cmds.select(texture_item['kwargs']['default'])

    def focusOutEvent(self, event):
        """Overwrite focus out event.

        """

        pass

    # --------------------------------Buttons Connections--------------------------------
    def make_connections(self):
        """Make buttons connected to functions.

        """

        self.ui.geometriesLoadSelected_pushButton.clicked.connect(partial(self.load_geometries, selected=True))
        self.ui.geometriesLoadAll_pushButton.clicked.connect(partial(self.load_geometries, selected=False))
        self.geometriesTreeView.selectionModel().selectionChanged.connect(self.load_shaders)
        self.shadersTreeView.selectionModel().selectionChanged.connect(self.load_textures)
        self.texturesTreeView.selectionModel().selectionChanged.connect(self.load_texture_to_preview_and_metadata_box)
        self.ui.texturesLabsSetPath_pushButton.clicked.connect(self.set_textures_labs_path)
        self.texturesLabsTreeView.selectionModel().selectionChanged.connect(
            self.load_texture_to_labs_preview_and_metadata_box
        )
        self.ui.texturesReassign_pushButton.clicked.connect(self.reassign_texture)
        self.ui.geometriesSelect_pushButton.clicked.connect(self.select_geometry)
        self.ui.shadersSelect_pushButton.clicked.connect(self.select_shader)
        self.ui.texturesSelect_pushButton.clicked.connect(self.select_texture)


def close():
    """Close the UI windows.

    """

    for QtTopWidget in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(QtTopWidget, TexturesManage):
            QtTopWidget.close()


def show():
    """Show the UI windows, close current one if it is already open.

    """

    global app

    # Find instance of TexturesManage and close it if it is already open
    close()

    # Use a shared instance of QApplication
    app = QtWidgets.QApplication.instance()

    # Get a pointer to the maya main window
    from maya import OpenMayaUI
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    # Use wrap instance utility
    win = QtCompat.wrapInstance(long(ptr), QtWidgets.QWidget)
    form = TexturesManage(win)

    form.show()
