import ast, re, warnings

from Qt import QtWidgets, QtCore, QtGui
from utils import fileManage

import widgetUtils


class TreeView(QtWidgets.QTreeView):
    """Derived class from QtWidgets.QTreeView

    """

    def __init__(self, color_setting=None):
        """Initial setting for TreeView.

        Args:
            color_setting (dict): {
                                   'WindowText': [r, g, b],
                                   'Button': [r, g, b],
                                   'Light': [r, g, b],
                                   'Mid': [r, g, b],
                                   'Dark': [r, g, b],
                                   'Text': [r, g, b],
                                   'BrightText': [r, g, b],
                                   'Base': [r, g, b],
                                   'Window': [r, g, b],
                                   'Shadow': [r, g, b],
                                   'Highlight': [r, g, b],
                                   'HighlightedText': [r, g, b]
                                   }
        """

        super(TreeView, self).__init__()

        # hide header initially, add later on
        self.setHeaderHidden(True)

        # if treeview doesn't have any items, create new model.
        self.model = self.model()
        if not self.model:
            self.model = QtGui.QStandardItemModel(0, 1)
            self.setModel(self.model)

        # set different color each row
        self.setAlternatingRowColors(True)

        # set size policy
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.setSizePolicy(size_policy)

        # set word wrap
        self.setWordWrap(True)

        # set scroll policy
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # set focus policy
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # set context menu policy
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # set edit triggers
        self.setEditTriggers(self.DoubleClicked | self.EditKeyPressed)

        # set expand method
        self.setExpandsOnDoubleClick(True)
        self.setItemsExpandable(True)

        # set selection mode and behavior
        self.setSelectionMode(self.ExtendedSelection)
        self.setSelectionBehavior(self.SelectRows)

        # set drag mode
        self.setDragEnabled(True)
        self.setDragDropMode(self.InternalMove)

        # initial drop indicator
        self.dropIndicatorPosition = self.OnViewport
        self.drop_indicator_rect = QtCore.QRect()

        # set color
        q_palette = widgetUtils.edit_palette(color_setting=color_setting)
        self.setPalette(q_palette)
        self.setStyleSheet("""
                color: rgb({}, {}, {});
                background-color: rgb({}, {}, {});
                alternate-background-color: rgb({}, {}, {})
            """.format(
            color_setting['Text'][0], color_setting['Text'][1], color_setting['Text'][2],
            color_setting['Base'][0], color_setting['Base'][1], color_setting['Base'][2],
            color_setting['Dark'][0], color_setting['Dark'][1], color_setting['Dark'][2]
        )
        )

        # delegate
        delegate = ItemDelegate(parent=self)
        self.setItemDelegate(delegate)

    def refresh(self):
        """Refresh the treeview, keep headers

        """

        # restore headers items
        headers = []
        for i in range(self.model.columnCount()):
            header_text = self.model.headerData(i, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            header_resize_mode = self.header().sectionResizeMode(i)
            headers.append((header_text, header_resize_mode))

        # if treeview have model/items, clear it
        self.model.clear()

        # add headers
        self.add_headers(headers=headers)

    def _unique_item_name(self, name):
        """Create unique name for treeview

        Args:
            name (str): Name to check if it is unique in the treeview, if not, rename it.

        Returns:
            str: Unique item name

        """

        # check if name exist, name can be '' empty string in the treeview.
        if name:
            # initial base name
            base_name = name
            # strip possible suffix number to get base name
            name_suffix_m = re.search(r'\d+$', name)
            if name_suffix_m:
                name_suffix = name_suffix_m.group()
                base_name = name.rpartition(name_suffix)[0]

            match_items = self.model.findItems(base_name, QtCore.Qt.MatchStartsWith | QtCore.Qt.MatchRecursive)
            if match_items:
                match_items_names = [str(match_item.data(role=QtCore.Qt.DisplayRole)) for match_item in match_items]
                highest_num = fileManage.find_highest_trailing_number(names=match_items_names, base_name=base_name)
                name = '{}{}'.format(base_name, highest_num+1)

        return name

    def add_headers(self, headers):
        """Add headers to treeview

        Args:
            headers (list): The headers list of treeview.
                            [(header name, resize mode), ]

        """

        # show header.
        self.setHeaderHidden(False)

        # match the columns count with numbers of headers.
        self.model.setColumnCount(len(headers))

        # set headers
        for i in range(len(headers)):
            header_item = QtGui.QStandardItem(headers[i][0])

            # header text font -----------------------------------------------------------
            q_font = QtGui.QFont()
            q_font.setFamily('Segoe UI')
            q_font.setPointSize(9)
            q_font.setBold(True)

            header_item.setFont(q_font)

            self.model.setHorizontalHeaderItem(i, header_item)

            # initial columns sizes, treeview width / len(headers)
            self.setColumnWidth(i, self.width()/len(headers))
            # set column resize mode
            self.header().setSectionResizeMode(i, headers[i][1])

        self.header().setStretchLastSection(False)

    def _create_item(self, item_kwargs, unique_name=True):
        """Create QtGui.QStandardItem based on given item kwargs setting value

        Args:
            item_kwargs (dict): Item setting dictionary
                              {
                              'default': column name,
                              'bg_color': [int, int, int],
                              'bg_alpha': int,
                              'text_color': [int, int, int],
                              'text_alpha': int,
                              'size': int,
                              'bold': bool,
                              'column_size': int,
                              'editable': bool,
                              'expand': bool,
                              'paint': bool,
                              'toolTip': str
                              }
            unique_name (bool): Make item name unique or not in the treeview.

        Returns:
            QtGui.QStandardItem: QtGui.QStandardItem about to add on to the treeview.

        """

        if unique_name:
            # only make string unique, but not in enum, list, dict type delegated widget.
            if isinstance(item_kwargs['default'], str):
                if 'enum' not in item_kwargs and 'template' not in item_kwargs:
                    item_kwargs['default'] = self._unique_item_name(name=item_kwargs['default'])

        # set name
        item = QtGui.QStandardItem(str(item_kwargs['default']))

        # item back ground color -----------------------------------------------------------
        bg_q_color = QtGui.QColor(
            item_kwargs['bg_color'][0],
            item_kwargs['bg_color'][1],
            item_kwargs['bg_color'][2],
            item_kwargs['bg_alpha']
        )

        bg_q_brush = QtGui.QBrush()
        bg_q_brush.setColor(bg_q_color)

        item.setBackground(bg_q_brush)

        # item text color -----------------------------------------------------------
        text_q_color = QtGui.QColor(
            item_kwargs['text_color'][0],
            item_kwargs['text_color'][1],
            item_kwargs['text_color'][2],
            item_kwargs['text_alpha']
        )

        text_q_brush = QtGui.QBrush()
        text_q_brush.setColor(text_q_color)

        item.setForeground(text_q_brush)

        # item text font -----------------------------------------------------------
        q_font = QtGui.QFont()
        q_font.setFamily('Segoe UI')
        q_font.setPointSize(item_kwargs['size'])
        q_font.setBold(item_kwargs['bold'])

        item.setFont(q_font)

        # item column width -----------------------------------------------------------
        q_size = QtCore.QSize(item_kwargs['column_size'], 35)
        item.setData(q_size, role=QtCore.Qt.SizeHintRole)

        # item tooltip -----------------------------------------------------------
        item.setToolTip(item_kwargs['toolTip'])

        # item editable -----------------------------------------------------------
        if item_kwargs['editable']:
            item.setEditable(True)
        else:
            item.setEditable(False)

        # item widget to pass to delegate -----------------------------------------------------------
        item.setData(item_kwargs, role=QtCore.Qt.UserRole + 2)

        return item

    def edit_item(self, item, item_kwargs, unique_name=True):
        """Edit QtGui.QStandardItem based on given item kwargs setting value

        Args:
            item (QtGui.QStandardItem): Item needs to be edited.
            item_kwargs (dict): Item setting dictionary
                              {
                              'default': column name,
                              'bg_color': [int, int, int],
                              'bg_alpha': int,
                              'text_color': [int, int, int],
                              'text_alpha': int,
                              'size': int,
                              'bold': bool,
                              'column_size': int,
                              'editable': bool,
                              'expand': bool,
                              'paint': bool
                              }
            unique_name (bool): Make item name unique or not in the treeview.

        """

        if unique_name:
            # only make string unique, but not in enum, list, dict type delegated widget.
            if isinstance(item_kwargs['default'], str):
                if 'enum' not in item_kwargs and 'template' not in item_kwargs:
                    item_kwargs['default'] = self._unique_item_name(name=item_kwargs['default'])

        # item back ground color -----------------------------------------------------------
        bg_q_color = QtGui.QColor(
            item_kwargs['bg_color'][0],
            item_kwargs['bg_color'][1],
            item_kwargs['bg_color'][2],
            item_kwargs['bg_alpha']
        )

        bg_q_brush = QtGui.QBrush()
        bg_q_brush.setColor(bg_q_color)

        item.setBackground(bg_q_brush)

        # item text color -----------------------------------------------------------
        text_q_color = QtGui.QColor(
            item_kwargs['text_color'][0],
            item_kwargs['text_color'][1],
            item_kwargs['text_color'][2],
            item_kwargs['text_alpha']
        )

        text_q_brush = QtGui.QBrush()
        text_q_brush.setColor(text_q_color)

        item.setForeground(text_q_brush)

        # item text font -----------------------------------------------------------
        q_font = QtGui.QFont()
        q_font.setFamily('Segoe UI')
        q_font.setPointSize(item_kwargs['size'])
        q_font.setBold(item_kwargs['bold'])

        item.setFont(q_font)

        # item column width -----------------------------------------------------------
        q_size = QtCore.QSize(item_kwargs['column_size'], 25)
        item.setData(q_size, role=QtCore.Qt.SizeHintRole)

        # item tooltip -----------------------------------------------------------
        item.setToolTip(item_kwargs['toolTip'])

        # item editable -----------------------------------------------------------
        if item_kwargs['editable']:
            item.setEditable(True)
        else:
            item.setEditable(False)

        # item expand -----------------------------------------------------------
        if item_kwargs['expand']:
            self.expand(item.index())
        else:
            self.collapse(item.index())

        # item widget to pass to delegate -----------------------------------------------------------
        item.setText(str(item_kwargs['default']))
        item.setData(item_kwargs, role=QtCore.Qt.UserRole + 2)

    def add_items(self, items_kwargs, unique_name=True, parent_item=None):
        """Add items to treeview in order.

        Args:
            items_kwargs (list): The list of rows with list of columns dictionaries on each row
                              [[
                              {
                              'default': column name,
                              'bg_color': [int, int, int],
                              'bg_alpha': int,
                              'text_color': [int, int, int],
                              'text_alpha': int,
                              'size': int,
                              'bold': bool,
                              'column_size': int,
                              'editable': bool,
                              'expand': bool,
                              'paint': bool
                              },
                              ],]
            unique_name (bool): Make item name unique or not in the treeview.
            parent_item (QtGui.QStandardItem/None): Parent item which items are added to.

        Returns:
            list: The list of rows with list of columns items on each row [[columns items],]

        """

        model = self.model

        # if parent item exist.
        if parent_item:
            if isinstance(parent_item, QtGui.QStandardItem):
                model = parent_item

        # match the columns count with the columns count of items.
        model.setColumnCount(len(items_kwargs[0]))
        # initial columns sizes.
        for i in range(len(items_kwargs[0])):
            self.setColumnWidth(i, items_kwargs[0][i]['column_size'])

        # initial return items list
        items = []
        # setting
        for row_items_kwargs in items_kwargs:
            # initial columns items list
            columns_items = []
            for column_item_kwargs in row_items_kwargs:
                # set column item
                column_item = self._create_item(item_kwargs=column_item_kwargs, unique_name=unique_name)

                # append to columns items list
                columns_items.append(column_item)

            items.append(columns_items)

            # append row to parent
            model.appendRow(columns_items)

        return items

    def remove_items(self):
        """Remove selected / all items from treeview.

        Returns:
            list/None: The list of removed hierarchies dictionaries with
                      [{
                      key ('parent'):
                      value ({'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': parent_kwargs}),
                      key ('children'):
                      value ([[{'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': child_kwargs}, ]])
                            The list of rows with list of columns information dictionaries on each row.
                      },]
                      None, remove all.

        """

        # query current selected indexes
        indexes = self.selectedIndexes()

        # if selected, query selected
        if indexes:
            # query current selected items
            items = self.get_items()

            # hierarchy level
            for hierarchy in items:
                parent_item = hierarchy['parent']['item']

                # rows level
                # delete a row will delete all the columns in this row, so only need to access first child column.
                # hierarchy_dict['children'][row index][column index]['position'][0] is row num.
                rows_nums = [row[0]['position'][0] for row in hierarchy['children']]
                # avoiding parent's rows index changes, delete from back -> forward.
                rows_nums.sort(reverse=True)

                for row_num in rows_nums:
                    try:
                        parent_item.removeRow(row_num)
                    except (RuntimeError, Exception):
                        pass

            return items

        # if not selected, avoid calling self.get_items to query all the items, just refresh the whole tree
        else:
            self.refresh()

            return None

    def duplicate_items(self, leaves=True):
        """Duplicate selected / all items from treeview.

        Args:
            leaves (bool): Duplicate item's leaves if True, else No.

        Returns:
            list/None: The list of duplicated hierarchies dictionaries with
                      [{
                      key ('parent'):
                      value ({'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': parent_kwargs}),
                      key ('children'):
                      value ([[{'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': child_kwargs}, ]])
                            The list of rows with list of columns information dictionaries on each row.
                      },]

        """

        # query current selected indexes
        indexes = self.selectedIndexes()

        # if selected, query selected
        if indexes:
            # query current selected items
            items = self.get_items()

            # initial duplicated items
            duplicated_items = []

            # hierarchy level
            for hierarchy in items:
                parent_item = hierarchy['parent']['item']
                parent_position = hierarchy['parent']['position']
                parent_kwargs = hierarchy['parent']['kwargs']

                duplicated_hierarchy_dict = {
                    'parent': {'item': parent_item, 'position': parent_position, 'kwargs': parent_kwargs},
                    'children': []
                }

                # rows level
                for row in hierarchy['children']:
                    # row num increase while adding duplicated new row of children
                    row_num = parent_item.rowCount()
                    duplicated_children_columns_items = []
                    # columns level
                    for column in row:
                        column_item = column['item']
                        column_kwargs = column['kwargs']

                        # create duplicated new column item
                        new_column_item = self._create_item(item_kwargs=column_kwargs, unique_name=True)
                        parent_item.setChild(row_num, column['position'][1], new_column_item)

                        # if leaves, duplicate column item itself, with duplicate its leaves.
                        if leaves and column_item.hasChildren():
                            self._iter_duplicate_items(start=(column_item, new_column_item))

                        duplicated_children_columns_items.append(
                            {
                                'item': new_column_item,
                                'position': (new_column_item.row(), new_column_item.column()),
                                'kwargs': column_kwargs
                            }
                        )

                    duplicated_hierarchy_dict['children'].append(duplicated_children_columns_items)

                duplicated_items.append(duplicated_hierarchy_dict)

            return duplicated_items

        # if not selected, avoid calling self.get_items to query all the items.
        else:
            warnings.warn('No items in the TreeView are selected to be duplicated!')

            return None

    def _iter_duplicate_items(self, start):
        """Iteration starts from start column item to downstream, duplicate all the leaves below it.

        Args:
            start (tuple): (QtGui.QStandardItem, QtGui.QStandardItem),
                           The 1st QtGui.QStandardItem is the start column item,
                           The 2nd QtGui.QStandardItem is the new duplicated start column item.

        """

        # start iterating -----------------------------------------------------------
        # start=(column_item, new_column_item)
        stack = [start]

        while stack:
            start_item, new_start_item = stack.pop(0)

            for i in range(start_item.rowCount()):
                # row num increase while adding duplicated new row of children
                row = new_start_item.rowCount()
                for j in range(start_item.columnCount()):
                    child_item = start_item.child(i, j)
                    child_kwargs = child_item.data(role=QtCore.Qt.UserRole + 2)

                    # create duplicated new child item
                    new_child_item = self._create_item(item_kwargs=child_kwargs, unique_name=True)
                    new_start_item.setChild(row, j, new_child_item)

                    if child_item.hasChildren():
                        stack.append((child_item, new_child_item))

    def get_item(self, name):
        """Given a display name to find corresponding item in the treeview.

        Args:
            name (str/int/float/bool): The given display name.

        Returns:
            dict/None: {'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': item_kwargs}
                       if exist, None if not.

        """

        item = self.model.findItems(str(name), QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
        if item:
            item_kwargs = item[0].data(role=QtCore.Qt.UserRole + 2)

            return {'item': item[0], 'position': (item[0].row(), item[0].column()), 'kwargs': item_kwargs}

    def get_current_item(self):
        """Get current selected item.

        Returns:
            dict/None: {'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': item_kwargs}
                       if exist, None if not.

        """

        index = self.currentIndex()
        # there is case when item just created but not parent to the layout, so index.model is None.
        if index and index.model():
            item = index.model().itemFromIndex(index)
            item_kwargs = item.data(role=QtCore.Qt.UserRole + 2)

            return {'item': item, 'position': (item.row(), item.column()), 'kwargs': item_kwargs}

    def select_items(self, names):
        """Given a list of display names to select corresponding items in the treeview.

        Args:
            names (list): The given list of display names.

        """

        rows_indexes = []
        for name in names:
            item = self.model.findItems(str(name), QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
            if item:
                model = self.model
                # if parent item exist.
                parent_item = item[0].parent()
                if parent_item:
                    if isinstance(parent_item, QtGui.QStandardItem):
                        model = parent_item

                column_num = model.columnCount() - 1
                rows_indexes.append((model.index(item[0].row(), 0), model.index(item[0].row(), column_num)))

        flags = QtCore.QItemSelectionModel.Select
        selection = QtCore.QItemSelection()
        for row_index in rows_indexes:
            if selection.indexes():
                selection.merge(QtCore.QItemSelection(row_index[0], row_index[1]), flags)
            else:
                selection.select(row_index[0], row_index[1])

        self.selectionModel().clear()
        self.selectionModel().select(selection, flags)

    def get_items(self):
        """Get selected / all items from treeview.

        Returns:
            list: The list of hierarchies dictionaries with
                  [{
                  key ('parent'):
                  value ({'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': parent_kwargs}),
                  key ('children'):
                  value ([[{'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': child_kwargs}, ]])
                        The list of rows with list of columns information dictionaries on each row.
                  },]

        """

        # initial return items list
        items = []

        # query current selected items indexes
        indexes = self.selectedIndexes()

        # if selected, query selected
        if indexes:
            # parents and children list to store items unique str(QStandardItem) for checking purpose
            parents_list = []
            children_list = []

            for index in indexes:
                child_item = index.model().itemFromIndex(index)
                # check if child item is already added, if so, skip, if not, process.
                if str(child_item) not in children_list:
                    parent_item = child_item.parent()
                    # if parent item doesn't exist,
                    # then child item must be top level item has invisibleRootItem as parent
                    if not parent_item:
                        parent_item = self.model.invisibleRootItem()

                    # check if parent item is already added, if so, skip, if not, process.
                    if str(parent_item) not in parents_list:
                        parent_kwargs = parent_item.data(role=QtCore.Qt.UserRole + 2)
                        hierarchy_dict = {
                            'parent': {
                                'item': parent_item,
                                'position': (parent_item.row(), parent_item.column()),
                                'kwargs': parent_kwargs
                            },
                            'children': []
                        }
                        # appending parent item str(QStandardItem) to parent_list
                        # and appending hierarchy_dict to items in same order
                        parents_list.append(str(parent_item))
                        items.append(hierarchy_dict)

                    # query other children in the same row but different columns
                    # because when select, it returns the whole row with all the columns
                    children_columns_items = []
                    for i in range(parent_item.columnCount()):
                        child_column_item = parent_item.child(child_item.row(), i)
                        child_column_kwargs = child_column_item.data(role=QtCore.Qt.UserRole + 2)
                        children_columns_items.append(
                            {
                                'item': child_column_item,
                                'position': (child_item.row(), i),
                                'kwargs': child_column_kwargs
                            }
                        )

                        # appending child column item str(QStandardItem) to children_list
                        children_list.append(str(child_column_item))

                    parent_id = parents_list.index(str(parent_item))
                    items[parent_id]['children'].append(children_columns_items)

        # if not selected, query all
        else:
            items = self.iter_get_items(start_item=self.model.invisibleRootItem())

        return items

    @staticmethod
    def iter_get_items(start_item):
        """Get all items from start column item to downstream.

        Args:
            start_item (QtGui.QStandardItem): The start column item.

        Returns:
            list: The list of hierarchies dictionaries with
                  [{
                  key ('parent'):
                  value ({'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': parent_kwargs}),
                  key ('children'):
                  value ([[{'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': child_kwargs}, ]])
                        The list of rows with list of columns information dictionaries on each row.
                  },]

        """

        # initial return items list
        items = []

        stack = [start_item]

        while stack:
            parent_item = stack.pop(0)
            parent_kwargs = parent_item.data(role=QtCore.Qt.UserRole + 2)

            hierarchy_dict = {
                'parent': {
                    'item': parent_item,
                    'position': (parent_item.row(), parent_item.column()),
                    'kwargs': parent_kwargs
                },
                'children': []
            }

            items.append(hierarchy_dict)

            for i in range(parent_item.rowCount()):
                children_columns_items = []
                for j in range(parent_item.columnCount()):
                    child_column_item = parent_item.child(i, j)
                    child_column_kwargs = child_column_item.data(role=QtCore.Qt.UserRole + 2)
                    children_columns_items.append(
                        {
                            'item': child_column_item,
                            'position': (i, j),
                            'kwargs': child_column_kwargs
                        }
                    )

                    if child_column_item.hasChildren():
                        stack.append(child_column_item)

                hierarchy_dict['children'].append(children_columns_items)

        return items

    def get_item_path(self, start_item):
        """Get all the items from start item to upwards.

        Args:
            start_item (QtGui.QStandardItem): The start item to get all the items upwards .

        Returns:
            list: All the items from start item to upwards, in a start_item -> upper parent -> upper parent order.

        """

        # initial return path items list
        path_items = [start_item]

        stack = [start_item]

        while stack:
            child_item = stack.pop(0)

            parent_item = child_item.parent()
            if parent_item:
                path_items.append(parent_item)
                stack.append(parent_item)
            else:
                path_items.append(self.model.invisibleRootItem())
                break

        return path_items

    def parent_items(self):
        """Parent items in treeview based on selection,
           select items to parent first, then select item to get parented last.

        Returns:
            dict/None: The parent children hierarchies dictionary with
                      {
                      key ('parent'):
                      value ({'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': parent_kwargs}),
                      key ('children'):
                      value ([[{'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': child_kwargs}, ], ])
                            The list of rows with list of columns information dictionaries on each row.
                      }

        """

        # query current selected indexes
        indexes = self.selectedIndexes()

        # if selected, query selected
        if indexes:
            # get parents columns items -----------------------------------------------------
            last_parent_column_item = indexes[-1].model().itemFromIndex(indexes[-1])
            last_parent_column_num = last_parent_column_item.column()

            parents_indexes = indexes[-(last_parent_column_num + 1):]
            parents_columns_items = []
            for parent_index in parents_indexes:
                parents_columns_items.append(parent_index.model().itemFromIndex(parent_index))

            parent_row_num = parents_columns_items[0].rowCount()
            parent_path_items = self.get_item_path(start_item=parents_columns_items[0])

            # parents list with unique str(QStandardItem) for checking purpose
            parents_list = [str(parents_columns_items[i]) for i in range(len(parents_columns_items))]
            parent_path_list = [str(parent_path_items[i]) for i in range(len(parent_path_items))]

            # query current selected items -----------------------------------------------------
            items = self.get_items()

            # initial parent children items
            parent_children_items = {
                'parent': {
                    'item': parents_columns_items[0],
                    'position': (parents_columns_items[0].row(), parents_columns_items[0].column()),
                    'kwargs': parents_columns_items[0].data(role=QtCore.Qt.UserRole + 2)
                },
                'children': []
            }

            # hierarchy level
            for hierarchy in items:
                parent_item = hierarchy['parent']['item']
                # only process if selected items' parent is not in parents_list.
                if str(parent_item) not in parents_list:
                    # rows level
                    rows_nums = [
                        row[0]['position'][0] for row in hierarchy['children']
                        if str(row[0]['item']) not in parents_list and str(row[0]['item']) not in parent_path_list[1:]
                    ]
                    # avoiding parent's rows index changes, remove from back -> forward.
                    rows_nums.sort(reverse=True)

                    # temporary save newly parented children items
                    children_items = []
                    for row_num in rows_nums:
                        columns_items = parent_item.takeRow(row_num)
                        parents_columns_items[0].insertRow(parent_row_num, columns_items)
                        children_items.append(columns_items)

                    # add to parent_children_items
                    for row_items in children_items:
                        parent_children_columns_items = []
                        for column_item in row_items:
                            column_item_kwargs = column_item.data(role=QtCore.Qt.UserRole + 2)
                            parent_children_columns_items.append(
                                {
                                    'item': column_item,
                                    'position': (column_item.row(), column_item.column()),
                                    'kwargs': column_item_kwargs
                                }
                            )
                        parent_children_items['children'].append(parent_children_columns_items)

            return parent_children_items

        # if not selected, avoid calling self.get_items to query all the items.
        else:
            warnings.warn('No items in the TreeView are selected to get parented!')

            return None

    def unparent_items(self):
        """Unparent items in treeview based on selection.

        Returns:
            dict/None: The unparent children hierarchies dictionary with
                      {
                      key ('parent'):
                      value ({'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': parent_kwargs}),
                      key ('children'):
                      value ([[{'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': child_kwargs}, ]])
                            The list of rows with list of columns information dictionaries on each row.
                      }

        """

        # query current selected indexes
        indexes = self.selectedIndexes()

        # if selected, query selected
        if indexes:
            # query current selected items -----------------------------------------------------
            items = self.get_items()
            root_row_num = self.model.invisibleRootItem().rowCount()

            # initial unparent children items
            unparent_children_items = {
                'parent': {
                    'item': self.model.invisibleRootItem(),
                    'position': (self.model.invisibleRootItem().row(), self.model.invisibleRootItem().column()),
                    'kwargs': None
                },
                'children': []
            }

            # hierarchy level
            for hierarchy in items:
                parent_item = hierarchy['parent']['item']
                # only process if selected items' parent is not root parent.
                if str(parent_item) != str(self.model.invisibleRootItem()):
                    # rows level
                    rows_nums = [row[0]['position'][0] for row in hierarchy['children']]
                    # avoiding parent's rows index changes, remove from back -> forward.
                    rows_nums.sort(reverse=True)

                    # temporary save newly unparent children items
                    children_items = []
                    for row_num in rows_nums:
                        columns_items = parent_item.takeRow(row_num)
                        self.model.invisibleRootItem().insertRow(root_row_num, columns_items)
                        children_items.append(columns_items)

                    # add to unparent_children_hierarchy_dict
                    for row_items in children_items:
                        unparent_children_columns_items = []
                        for column_item in row_items:
                            column_item_kwargs = column_item.data(role=QtCore.Qt.UserRole + 2)
                            unparent_children_columns_items.append(
                                {
                                    'item': column_item,
                                    'position': (column_item.row(), column_item.column()),
                                    'kwargs': column_item_kwargs
                                }
                            )
                        unparent_children_items['children'].append(unparent_children_columns_items)

            return unparent_children_items

        # if not selected, avoid calling self.get_items to query all the items.
        else:
            warnings.warn('No items in the TreeView are selected to get un parented!')

            return None

    def group_items(self, group_columns_kwargs):
        """Group items in treeview based on selection.

        Args:
            group_columns_kwargs (list): The list of columns kwargs dictionaries for group setting
                                          [
                                          {
                                          'default': column name,
                                          'bg_color': [int, int, int],
                                          'bg_alpha': int,
                                          'text_color': [int, int, int],
                                          'text_alpha': int,
                                          'size': int,
                                          'bold': bool,
                                          'column_size': int,
                                          'editable': bool,
                                          'expand': bool,
                                          'paint': bool
                                          },
                                          ]

        Returns:
            dict: The group children hierarchies dictionary with
                  {
                  key ('parent'):
                  value ({'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': parent_kwargs}),
                  key ('children'):
                  value ([[{'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': child_kwargs}, ]])
                        The list of rows with list of columns information dictionaries on each row.
                  }

        """

        group_items = self.add_items(
            items_kwargs=[group_columns_kwargs], unique_name=True, parent_item=None
        )
        group_row_num = group_items[0][0].rowCount()

        # initial group children items
        group_children_items = {
            'parent': {
                'item': group_items[0][0],
                'position': (group_items[0][0].row(), group_items[0][0].column()),
                'kwargs': group_items[0][0].data(role=QtCore.Qt.UserRole + 2)
            },
            'children': []
        }

        # query current selected indexes
        indexes = self.selectedIndexes()

        # if selected, query selected
        if indexes:
            # query current selected items -----------------------------------------------------
            items = self.get_items()

            # hierarchy level
            for hierarchy in items:
                parent_item = hierarchy['parent']['item']
                # rows level
                rows_nums = [row[0]['position'][0] for row in hierarchy['children']]
                # avoiding parent's rows index changes, remove from back -> forward.
                rows_nums.sort(reverse=True)

                # temporary save newly group children items
                children_items = []
                for row_num in rows_nums:
                    columns_items = parent_item.takeRow(row_num)
                    group_items[0][0].insertRow(group_row_num, columns_items)
                    children_items.append(columns_items)

                # add to group_children_items
                for row_items in children_items:
                    group_children_columns_items = []
                    for column_item in row_items:
                        column_item_kwargs = column_item.data(role=QtCore.Qt.UserRole + 2)
                        group_children_columns_items.append(
                            {
                                'item': column_item,
                                'position': (column_item.row(), column_item.column()),
                                'kwargs': column_item_kwargs
                            }
                        )
                    group_children_items['children'].append(group_children_columns_items)

        # if not selected, avoid calling self.get_items to query all the items.
        else:
            warnings.warn('No items in the TreeView are selected to group! An empty group created.')

        return group_children_items

    def ungroup_items(self):
        """Ungroup items in treeview to the upper parent lever, based on selection.

        Returns:
            list/None: The list of new ungroup children hierarchies dictionaries with
                      [{
                      key ('parent'):
                      value ({'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': parent_kwargs}),
                      key ('children'):
                      value ([[{'item': QtGui.QStandardItem, 'position': (row, column), 'kwargs': child_kwargs}, ]])
                            The list of rows with list of columns information dictionaries on each row.
                      },]

        """

        # query current selected indexes
        indexes = self.selectedIndexes()

        # if selected, query selected
        if indexes:
            # query current selected items -----------------------------------------------------
            items = self.get_items()

            # initial ungroup children items
            ungroup_children_items = []

            # hierarchy level
            for hierarchy in items:
                parent_item = hierarchy['parent']['item']
                parent_position = hierarchy['parent']['position']
                parent_kwargs = hierarchy['parent']['kwargs']

                try:
                    # there is cases groups already be ungroup and deleted.
                    row_num = parent_item.rowCount()

                    # rows level
                    groups_rows_nums = []
                    children_items = []
                    for row in hierarchy['children']:
                        groups_rows_nums.append(row[0]['position'][0])
                        # columns level
                        for i in reversed(range(row[0]['item'].rowCount())):
                            child_columns_items = row[0]['item'].takeRow(i)
                            parent_item.insertRow(row_num, child_columns_items)
                            children_items.append(child_columns_items)

                    # only delete groups if have children
                    if children_items:
                        # avoiding parent's rows index changes, delete from back -> forward.
                        groups_rows_nums.sort(reverse=True)
                        for group_row_num in groups_rows_nums:
                            try:
                                parent_item.removeRow(group_row_num)
                            except (RuntimeError, Exception):
                                pass

                        ungroup_children_hierarchy_dict = {
                            'parent': {'item': parent_item, 'position': parent_position, 'kwargs': parent_kwargs},
                            'children': []
                        }

                        # add to ungroup_children_hierarchy_dict
                        for row_items in children_items:
                            ungroup_children_columns_items = []
                            for column_item in row_items:
                                column_item_kwargs = column_item.data(role=QtCore.Qt.UserRole + 2)
                                ungroup_children_columns_items.append(
                                    {
                                        'item': column_item,
                                        'position': (column_item.row(), column_item.column()),
                                        'kwargs': column_item_kwargs
                                    }
                                )
                            ungroup_children_hierarchy_dict['children'].append(ungroup_children_columns_items)

                        ungroup_children_items.append(ungroup_children_hierarchy_dict)

                except (RuntimeError, Exception):
                    pass

            return ungroup_children_items

        # if not selected, avoid calling self.get_items to query all the items.
        else:
            warnings.warn('No items in the TreeView are selected to ungroup!')

            return None

    def paintEvent(self, event):
        """ Reimplementing paint event for drop indicator.

        """

        painter = QtGui.QPainter(self.viewport())
        self.drawTree(painter, event.region())
        self.paint_drop_indicator(painter)

    def paint_drop_indicator(self, painter):
        """ Paint the drop indicator.

        """

        if self.state() == QtWidgets.QAbstractItemView.DraggingState:
            option = QtWidgets.QStyleOption()
            option.init(self)
            option.rect = self.drop_indicator_rect
            rect = option.rect

            if rect.height() == 0:
                pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.DashLine)
                painter.setPen(pen)
                painter.drawLine(rect.bottomLeft(), rect.bottomRight())
            else:
                pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.DashLine)
                painter.setPen(pen)
                painter.drawRect(rect)

    def dragEnterEvent(self, event):
        """ Reimplementing drag enter event.

        """

        event.accept()

    def dragMoveEvent(self, event):
        """ Reimplementing drag move event, only move within 0 column items.

        """

        # get item index at drag move event position
        index = self.indexAt(event.pos())
        if index.model():
            rect = self.visualRect(index)
            rect_left = self.visualRect(index.sibling(index.row(), 0))
            rect_right = self.visualRect(index.sibling(index.row(), self.model.columnCount() - 1))

            # get drop indicator position
            self.dropIndicatorPosition = self._position(event.pos(), rect, index)

            # only move within 0 column items.
            if index.column() == 0:
                if self.dropIndicatorPosition == self.AboveItem:
                    self.drop_indicator_rect = QtCore.QRect(
                        rect_left.left(), rect_left.top(), rect_right.right() - rect_left.left(), 0
                    )
                    event.accept()

                elif self.dropIndicatorPosition == self.BelowItem:
                    self.drop_indicator_rect = QtCore.QRect(
                        rect_left.left(), rect_left.bottom(), rect_right.right() - rect_left.left(), 0
                    )
                    event.accept()

                elif self.dropIndicatorPosition == self.OnItem:
                    self.drop_indicator_rect = QtCore.QRect(
                        rect_left.left(), rect_left.top(), rect_right.right() - rect_left.left(), rect.height()
                    )
                    event.accept()

                else:
                    self.drop_indicator_rect = QtCore.QRect()

            else:
                event.ignore()

            self.model.setData(index, self.dropIndicatorPosition, QtCore.Qt.UserRole)

        self.viewport().update()

    @staticmethod
    def _position(pos, rect, index):
        """ Get drop indicator position

        Args:
            pos (QPoint): Drag move event stop position.
            rect (QRect): Drop indicator QRect shape.
            index (QModelIndex): Drag item QModelIndex.

        Returns:
            DropIndicatorPosition: Drop Indicator Position.

        """

        drop_indicator_position = QtWidgets.QAbstractItemView.OnViewport
        # margin*2 must be smaller than row height, or the drop onItem rect won't show
        margin = 2
        if pos.y() - rect.top() < margin:
            drop_indicator_position = QtWidgets.QAbstractItemView.AboveItem
        elif rect.bottom() - pos.y() < margin:
            drop_indicator_position = QtWidgets.QAbstractItemView.BelowItem
        elif pos.y() - rect.top() > margin and rect.bottom() - pos.y() > margin:
            drop_indicator_position = QtWidgets.QAbstractItemView.OnItem

        return drop_indicator_position


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    """Base class for ItemDelegate, will create the correct widget base on item type

    """

    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        """Paint item.

        """

        item = index.model().itemFromIndex(index)
        item_kwargs = item.data(role=QtCore.Qt.UserRole + 2)

        if item_kwargs['paint']:
            if option.state & QtWidgets.QStyle.State_Selected:
                # item back ground color -----------------------------------------------------------
                bg_q_color = QtGui.QColor(
                    item_kwargs['bg_color'][0],
                    item_kwargs['bg_color'][1],
                    item_kwargs['bg_color'][2],
                    item_kwargs['bg_alpha']
                )
                # item text color -----------------------------------------------------------
                text_q_color = QtGui.QColor(
                    item_kwargs['text_color'][0],
                    item_kwargs['text_color'][1],
                    item_kwargs['text_color'][2],
                    item_kwargs['text_alpha']
                )
            else:
                # item back ground color -----------------------------------------------------------
                bg_q_color = item.data(role=QtCore.Qt.BackgroundColorRole).color()
                # item text color -----------------------------------------------------------
                text_q_color = item.data(role=QtCore.Qt.ForegroundRole).color()

            painter.save()
            # item back ground -----------------------------------------------------------
            painter.fillRect(option.rect, bg_q_color)
            # item text -----------------------------------------------------------
            text = str(item.data(role=QtCore.Qt.DisplayRole))

            q_font = QtGui.QFont()
            q_font.setFamily('Segoe UI')
            q_font.setPointSize(item_kwargs['size'])
            q_font.setBold(item_kwargs['bold'])

            painter.setFont(q_font)
            painter.setPen(QtGui.QPen(text_q_color))

            painter.drawText(option.rect, QtCore.Qt.AlignLeft, text)

            painter.restore()

        else:
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        """Create item delegate.

        """

        item = index.model().itemFromIndex(index)
        text = str(item.data(role=QtCore.Qt.DisplayRole))
        item_kwargs = item.data(role=QtCore.Qt.UserRole + 2)

        if item_kwargs:
            # create delegated widget -----------------------------------------------------------
            # create widget based on item_kwargs['widget']
            widget = item_kwargs['widget'](parent)

        # create QLineEdit as general if no item_kwargs
        else:
            widget = QtWidgets.QLineEdit(parent)

        # setting default values for widget-----------------------------------------------------------
        # setting value for QComboBox widget
        if isinstance(widget, QtWidgets.QComboBox):
            # set enum
            widget.addItems(item_kwargs['enum'])
            widget.setCurrentText(text)

        # setting value for QSpinBox and QDoubleSpinBox widget
        elif isinstance(widget, QtWidgets.QDoubleSpinBox) or isinstance(widget, QtWidgets.QSpinBox):
            # set range
            if 'min' in item_kwargs:
                widget.setMinimum(item_kwargs['min'])
            else:
                widget.setMinimum(-9999)

            if 'max' in item_kwargs:
                widget.setMaximum(item_kwargs['max'])
            else:
                widget.setMaximum(9999)

            widget.setSingleStep(item_kwargs['step'])

        # setting for QLineEdit
        elif isinstance(widget, QtWidgets.QLineEdit):
            widget.editingFinished.connect(self.commitAndCloseEditor)
            widget.setFrame(False)

        return widget

    def commitAndCloseEditor(self):
        """Close Editor after finishing editing QLineEdit/QTextEdit.

        """

        editor = self.sender()
        if isinstance(editor, (QtWidgets.QLineEdit, QtWidgets.QTextEdit)):
            # The commitData signal must be emitted when we've finished editing
            # and need to write our changed back to the model.
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)

    def setEditorData(self, editor, index):
        """ Sets the data to be displayed and edited by our custom editor,
            it is the function to get rid of non legal characters/set some boundaries.

        """

        item = index.model().itemFromIndex(index)
        text = str(item.data(role=QtCore.Qt.DisplayRole))
        item_kwargs = item.data(role=QtCore.Qt.UserRole + 2)

        if isinstance(editor, (QtWidgets.QLineEdit, QtWidgets.QTextEdit)):
            # correct input text in QLineEdit, QTextEdit if there is item_kwargs and editor is editable
            if item_kwargs and item_kwargs['editable']:
                editor.setText(fileManage.convert_special_characters_to_underscore(text))

        elif isinstance(editor, QtWidgets.QComboBox):
            i = editor.findText(text)
            if i == -1:
                i = 0
            editor.setCurrentIndex(i)

        else:
            QtWidgets.QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        """ Get the data from our custom editor and stuff it into the model.

        """

        item = index.model().itemFromIndex(index)
        item_kwargs = item.data(role=QtCore.Qt.UserRole + 2)

        # set data, so when edit with invalid characters, it will show immediately the converted (string) value.
        super(ItemDelegate, self).setModelData(editor, model, index)

        if item_kwargs:
            if isinstance(editor, (QtWidgets.QLineEdit, QtWidgets.QTextEdit)):
                model.setData(index, str(editor.text()))
                # update editor.text() to item_kwargs['default']
                item_kwargs['default'] = str(editor.text())

            elif isinstance(editor, QtWidgets.QComboBox):
                model.setData(index, str(editor.currentText()))
                # update editor.text() to item_kwargs['default']
                item_kwargs['default'] = str(editor.currentText())

            else:
                value = ast.literal_eval(str(editor.text()))
                model.setData(index, value)
                # update value to item_kwargs['default']
                item_kwargs['default'] = value

            model.setData(index, item_kwargs, role=QtCore.Qt.UserRole + 2)

        else:
            QtWidgets.QStyledItemDelegate.setModelData(self, editor, model, index)
