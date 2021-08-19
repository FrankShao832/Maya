import os, re

from maya import cmds


def check_file_exist(path, user_file):
    """Check if the file exists or not under the path.

    Args:
        path (str): Path where to check if the file exists or not.
        user_file (str): The file name.

    Returns:
        bool: True if the file exists or False if not.

    """

    return os.path.exists("{}/{}".format(path, user_file))


def get_all_files(path, file_extension='', return_without_ext=True):
    """Return all the files / all the files with certain extension under the path.

    Args:
        path (str): Path where to return all the files.
        file_extension (str): File extension name, example: '.ma'/'.mb'/'.py'.
        return_without_ext (bool): Return file name with extension or not.

    Returns:
        list: Return all the files / all the files with certain extension under the path.

    """

    if not os.path.exists(path):
        return []

    all_files = [user_file for user_file in os.listdir(path) if os.path.isfile("{}/{}".format(path, user_file))]

    # return all the files with certain file extension
    if file_extension:
        return_files = []
        for user_file in all_files:
            if os.path.splitext(user_file)[1] == file_extension:
                if return_without_ext:
                    return_files.append(str(user_file).rpartition(file_extension)[0])
                else:
                    return_files.append(user_file)
        return return_files

    # return all the files
    if return_without_ext:
        return [os.path.splitext(user_file)[0] for user_file in all_files]
    else:
        return all_files


def maya_file_dialog(caption, file_filter, file_mode=1, starting_directory=''):
    """Create Open/Save maya file dialog .

    Args:
        caption (str): The title for the dialog window.
        file_filter (str): File type to filter specification. Such as: '*.json'/'*.ma'/'*.mb'.
        file_mode (int): Save file if 0, Open if 1.
        starting_directory (str): The starting directory for the dialog.

    Returns:
        str/None: The opened/saved file path.

    """

    return_files = cmds.fileDialog2(
        caption=caption,
        dialogStyle=2,
        fileFilter=file_filter,
        fileMode=file_mode,
        startingDirectory=starting_directory
    )
    if return_files:
        return return_files[0]

    return None


def current_maya_path():
    """Return the current maya file path.

    Returns:
        str: The current maya file path.

    """

    return (cmds.file(q=True, location=True)).rpartition("/")[0]


def current_maya_root_workspace():
    """Return the current maya root workspace path.

    Returns:
        str: The current maya root workspace path.

    """

    return cmds.workspace(q=True, rootDirectory=True)


def find_highest_trailing_number(names, base_name):
    """Return the highest version number.

    Args:
        names (list): A list of versioned file names, example: ['base_name_v001', 'base_name_v002', 'base_name_v003'].
        base_name (str): Base name of these versioned file names, example: 'base_name_v'.

    Returns:
        int: The highest version number.

    """

    highest_value = 0

    base_name_suffix_m = re.search(r'\d+$', base_name)
    if base_name_suffix_m:
        base_name_suffix = base_name_suffix_m.group()
        base_name = base_name.rpartition(base_name_suffix)[0]

    for name in names:
        if base_name in name:
            suffix = name.partition(base_name)[2]
            if suffix and re.match("^[0-9]*$", suffix):
                num = int(suffix)
                if num > highest_value:
                    highest_value = num

    return highest_value


def unique_name(names, name):
    """Create unique name

    Args:
        names (list): A list of versioned file names, example: ['base_name_v001', 'base_name_v002', 'base_name_v003'].
        name (str): Name to check if it is unique, if not, rename it.

    Returns:
        str: Unique name

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

        if base_name in names:
            highest_num = find_highest_trailing_number(names=names, base_name=base_name)
            name = '{}{}'.format(base_name, highest_num+1)

    return name


def contain_special_characters(str_name):
    """Check a string name has special characters or not

    Args:
        str_name (str): String name to check if it has special characters.

    Returns:
        bool: Return True if has, False if not.

    """

    string_check = re.compile('[@!#$%^&*()<>?/\|}{~:]')

    if string_check.search(str_name):

        return True
    else:
        return False


def convert_special_characters_to_underscore(str_name):
    """Convert all the special characters in a string into underscore, including while space.

    Args:
        str_name (str): String name to convert all the special characters into underscore, including while space.

    Returns:
        str: The converted string name.

    """

    return re.sub(r'[^a-zA-Z0-9\n\.]', '_', str_name)
