#Imports everything from each package file
import GUITools

import_errors=[]
from GUITools.Shared import *
from GUITools.FormattingWidgets import *
from GUITools.GraphicsWidgets import *
from GUITools.TextWidgets import *
from GUITools.FileWidgets import *
from GUITools.EvaluatorWidgets import *
try:
    from GUITools.ImageTools import *
except ImportError:
    import_errors.append('ImageTools')
from GUITools.ExtraWidgets import *
from GUITools.WindowTools import *
