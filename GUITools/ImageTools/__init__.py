#Tkinter image work
pil_flag=True
try:
    import PIL
except ImportError:
    pil_flag=False
    ImageWrapper=TkWrapper=ImageEditor=NotImplementedError
else:
    from GUITools.ImageTools.PILTools import *

from .Editor import *
from .Widgets import *
from .tkImageTools import *
from .ImageFiles import *
