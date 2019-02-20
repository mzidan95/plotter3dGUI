from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,
                                                NavigationToolbar2QT)
from matplotlib.figure import Figure
from mpl_toolkits import mplot3d
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
import numpy as np


sin = np.sin
cos = np.cos
exp = np.exp
pi = np.pi


class ApplicationWindow(QtWidgets.QWidget):
    def __init__(self, title='', size=(1200, 800)):
        super(ApplicationWindow, self).__init__()

        self.resize(*size)
        self.setWindowTitle(title)

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.content = PlotCanvas(self._draw)
        self.sidebar = Sidebar()

        vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        vsplitter.addWidget(self.content)
        vsplitter.setStretchFactor(0, 1)
        vsplitter.setStretchFactor(1, 0)

        hsplitter = QtWidgets.QSplitter()
        hsplitter.addWidget(self.sidebar)
        hsplitter.addWidget(vsplitter)
        hsplitter.setStretchFactor(0, 0)
        hsplitter.setStretchFactor(1, 1)

        self.layout().addWidget(hsplitter)

    def show_error_dialog(self, message):
        QtWidgets.QMessageBox.critical(self, 'Error', message)

    @classmethod
    def run(cls, *args, **kwargs):
        app = QtWidgets.QApplication([])

        app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))

        widget = cls(*args, **kwargs)
        widget._build(widget)

        widget.show()

        widget._started()

        app.exec_()
    
    def _build(self, context):
        sidebar_builder = WidgetBuilder(self.sidebar._ground, context)
        self._build_sidebar(sidebar_builder)
        self.redraw()

    def redraw(self):
        self.content.redraw()
    
    def _started(self):
        pass



class Widget(QtWidgets.QWidget):
    def __init__(self):
        super(Widget, self).__init__()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._ground = layout

    def _build(self, context):
        builder = WidgetBuilder(self._ground, context)
        self.build(builder)

    def build(self, builder):
        pass



class WidgetBuilder(object):
    def __init__(self, ground, context):
        self._ground = ground
        self.context = context

    def _add_widget(self, widget):
        self._ground.addWidget(widget)

    def add(self, widget_type):
        widget = widget_type()
        builder = WidgetBuilder(self._ground, self.context)
        widget.build(builder)
        self._add_widget(widget)

    def add_space(self):
        spacer_item = QtWidgets.QSpacerItem(16, 16)
        self._ground.addItem(spacer_item)

    def add_stretch(self):
        self._ground.addStretch(1)

    def add_label(self, label):
        label_widget = QtWidgets.QLabel(label)
        self._add_widget(label_widget)

    def add_button(self, label, action):
        button_widget = QtWidgets.QPushButton(label)
        self._add_widget(button_widget)

        button_widget.clicked.connect(action)

    def add_textbox(self, label, option, prefix=None, postfix=None,
                    validate=None, readonly=False):
        if label:
            label_widget = QtWidgets.QLabel(label)
            self._add_widget(label_widget)

        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_widget.setLayout(row_layout)
        self._add_widget(row_widget)

        if prefix:
            prefix_widget = QtWidgets.QLabel(prefix)
            row_layout.addWidget(prefix_widget)

        textbox_widget = QtWidgets.QLineEdit()
        textbox_widget.setText(str(option.value))
        textbox_widget.setReadOnly(readonly)

        row_layout.addWidget(textbox_widget, 1)

        if option:
            option.connect(lambda value: textbox_widget.setText(str(value)))
            textbox_widget.editingFinished.connect(
                lambda: option.change(textbox_widget.text()))

        if postfix:
            postfix_widget = QtWidgets.QLabel(postfix)
            row_layout.addWidget(postfix_widget)

    def add_spinbox(self, label, option, prefix=None, postfix=None,
                    dtype=float, minimum=None, maximum=None, step=None,
                    decimals=None):
        if label:
            label_widget = QtWidgets.QLabel(label)
            self._add_widget(label_widget)

        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_widget.setLayout(row_layout)
        self._add_widget(row_widget)

        if prefix:
            prefix_widget = QtWidgets.QLabel(prefix)
            row_layout.addWidget(prefix_widget)

        if dtype is int:
            spinbox_widget = QtWidgets.QSpinBox()
            spinbox_widget.setValue(option.value)
            spinbox_widget.setMinimum(minimum or -2147483648)
            spinbox_widget.setMaximum(maximum or 2147483647)
            spinbox_widget.setSingleStep(step or 1)
        elif dtype is float:
            spinbox_widget = QtWidgets.QDoubleSpinBox()
            spinbox_widget.setValue(option.value)
            spinbox_widget.setMinimum(minimum or -Qt.qInf())
            spinbox_widget.setMaximum(maximum or Qt.qInf())
            spinbox_widget.setSingleStep(step or 0.1)
            spinbox_widget.setDecimals(decimals or 5)
        else:
            raise ValueError(f'Invalid dtype "{dtype.__name__}"')

        spinbox_widget.setKeyboardTracking(False)
        row_layout.addWidget(spinbox_widget, 1)

        if option:
            option.connect(spinbox_widget.setValue)
            spinbox_widget.valueChanged.connect(option.change)

        if postfix:
            postfix_widget = QtWidgets.QLabel(postfix)
            row_layout.addWidget(postfix_widget)
    
    def add_group(self, label, content):
        group_widget = QtWidgets.QGroupBox(label)
        self._add_widget(group_widget)

        group_layout = QtWidgets.QVBoxLayout()
        group_widget.setLayout(group_layout)

        content_widget = content()
        content_widget._build(self.context)

        group_layout.addWidget(content_widget)


    def add_slider(self, label, option, minimum=None, maximum=None, interval=None):
        if label:
            label_widget = QtWidgets.QLabel(label)
            self._add_widget(label_widget)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(minimum or 1)
        slider.setMaximum(maximum or 10)
        slider.setTickInterval(interval or 1)
        slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        slider.setValue(option.value)
        slider.valueChanged.connect(option.change)
        self._add_widget(slider)


    def add_combobox(self, items, option, label=None):
        if label:
            label_widget = QtWidgets.QLabel(label)
            self._add_widget(label_widget)

        combobox_widget = QtWidgets.QComboBox()
        self._add_widget(combobox_widget)

        for item in items:
            combobox_widget.addItem(str(item))

        if option:
            option.connect(combobox_widget.setCurrentIndex)
            combobox_widget.currentIndexChanged.connect(option.change)



class Option(QtCore.QObject):
    _changed = QtCore.pyqtSignal(object)

    def __init__(self, value, action=None):
        super(Option, self).__init__()
        self.value = value

        if action:
            self.connect(action)

    def connect(self, action):
        self._changed.connect(action)

    def change(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.emit()

    def emit(self):
        self._changed.emit(self._value)



class Sidebar(QtWidgets.QScrollArea):
    def __init__(self):
        super(Sidebar, self).__init__()

        widget = Widget()

        self._ground = widget._ground

        self.setWidget(widget)
        self._ground.setContentsMargins(8, 8, 8, 8)
        self.horizontalScrollBar().setEnabled(False)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setWidgetResizable(True)
        self.setMinimumWidth(300)



class PlotCanvas(QtWidgets.QWidget):
    _redraw = QtCore.pyqtSignal(object)

    def __init__(self, redraw):
        super(PlotCanvas, self).__init__()

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        figure = Figure()
        canvas = FigureCanvasQTAgg(figure)
        canvas.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(canvas, 1, 1, 1, 1)
        self._canvas = canvas

        toolbar = NavigationToolbar2QT(canvas, self)
        layout.addWidget(toolbar, 2, 1, 1, 1)

        plot = figure.add_subplot(111, projection='3d')
        # plot.set_aspect('equal')
        self._plot = plot

        self._redraw.connect(redraw)

    def redraw(self):
        plot = self._plot
        plot.clear()
        self._redraw.emit(plot)
        self._canvas.draw()



class PlotSettings(Widget):
    def build(self, builder):
        builder.add_spinbox(dtype=float, label=None, prefix='minimum X', option=builder.context.options['xmin'])
        builder.add_spinbox(dtype=float, label=None, prefix='maximum X', option=builder.context.options['xmax'])
        builder.add_spinbox(dtype=float, label=None, prefix='minimum Y', option=builder.context.options['ymin'])
        builder.add_spinbox(dtype=float, label=None, prefix='maximum Y', option=builder.context.options['ymax'])
        builder.add_space()
        builder.add_slider(label='Resolution', option=builder.context.options['resolution'], minimum=10, maximum=100, interval=2)
        builder.add_space()
        builder.add_combobox(label='Color Map', items=builder.context.color_maps.values(), option=builder.context.options['cmap_idx'])
        builder.add_stretch()
        
class Main(ApplicationWindow):
    def __init__(self):
        super(Main, self).__init__(title='Custom 3d plotter')
        self.options={}
        self.options['xmin'] = Option(-50.0, self.redraw)
        self.options['xmax'] = Option(50.0, self.redraw)
        self.options['ymin'] = Option(-50.0, self.redraw)
        self.options['ymax'] = Option(50.0, self.redraw)
        self.options['resolution'] = Option(20, self.redraw)
        self.options['cmap_idx'] = Option(0, self.redraw)
        self.options['plotting_function'] = Option('x**2 + y**2')
        self.color_maps = {
            0 : 'viridis',
            1 : 'plasma',
            2 : 'inferno',
            3 : 'magma',
            4 : 'jet',
            5 : 'coolwarm'}

    def _build_sidebar(self, builder):
        builder.add_textbox(label=None, prefix='Function to plot', option=self.options['plotting_function'])
        builder.add_space()
        builder.add_group('Plot Settings', PlotSettings)
        builder.add_space()
        builder.add_button(label='Redraw', action=self.redraw)
        builder.add_stretch()


    def _draw(self, ax):
        xmin = self.options['xmin'].value
        xmax = self.options['xmax'].value
        ymin = self.options['ymin'].value
        ymax = self.options['ymax'].value
        res = self.options['resolution'].value
        X = np.linspace(xmin, xmax, res)
        Y = np.linspace(ymin, ymax, res)

        x, y = np.meshgrid(X, Y)

        plotting_function_string = self.options['plotting_function'].value
        try:
            F = eval(plotting_function_string)
            cmap = self.color_maps[self.options['cmap_idx'].value]
            ax.plot_surface(x, y, F, cmap=cmap, edgecolors='black', linewidth=0.25)
        except NameError:
            self.show_error_dialog('Oops!\n\nError plotting function')

if __name__ == '__main__':
    Main.run()
