from Qt import QtGui


def edit_palette(color_setting):
    """Setting palette.

    Args:
        color_setting (dict): {
                               'WindowText': [r, g, b],
                               'Button': [r, g, b],
                               'Light': [r, g, b],
                               'Mid': [r, g, b],
                               'Dark': [r, g, b],
                               'Text': [r, g, b],
                               'BrightText': [r, g, b],
                               'Base': [r, g, b],'
                               'Window': [r, g, b],
                               'Shadow': [r, g, b],
                               'Highlight': [r, g, b],
                               'HighlightedText': [r, g, b]
    Returns:
        QtGui.QPalette: Finished palette

    """

    q_palette = QtGui.QPalette()

    q_palette.setColor(
        QtGui.QPalette.WindowText,
        QtGui.QColor(
            color_setting['WindowText'][0],
            color_setting['WindowText'][1],
            color_setting['WindowText'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.Button,
        QtGui.QColor(
            color_setting['Button'][0],
            color_setting['Button'][1],
            color_setting['Button'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.Light,
        QtGui.QColor(
            color_setting['Light'][0],
            color_setting['Light'][1],
            color_setting['Light'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.Mid,
        QtGui.QColor(
            color_setting['Mid'][0],
            color_setting['Mid'][1],
            color_setting['Mid'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.Dark,
        QtGui.QColor(
            color_setting['Dark'][0],
            color_setting['Dark'][1],
            color_setting['Dark'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.Text,
        QtGui.QColor(
            color_setting['Text'][0],
            color_setting['Text'][1],
            color_setting['Text'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.BrightText,
        QtGui.QColor(
            color_setting['BrightText'][0],
            color_setting['BrightText'][1],
            color_setting['BrightText'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.Base,
        QtGui.QColor(
            color_setting['Base'][0],
            color_setting['Base'][1],
            color_setting['Base'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.Window,
        QtGui.QColor(
            color_setting['Window'][0],
            color_setting['Window'][1],
            color_setting['Window'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.Shadow,
        QtGui.QColor(
            color_setting['Shadow'][0],
            color_setting['Shadow'][1],
            color_setting['Shadow'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.Highlight,
        QtGui.QColor(
            color_setting['Highlight'][0],
            color_setting['Highlight'][1],
            color_setting['Highlight'][2]
        )
    )
    q_palette.setColor(
        QtGui.QPalette.HighlightedText,
        QtGui.QColor(
            color_setting['HighlightedText'][0],
            color_setting['HighlightedText'][1],
            color_setting['HighlightedText'][2]
        )
    )

    return q_palette
