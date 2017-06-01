
import tkinter as tk,string,tempfile as tf,code
from _tkinter import TclError
import sys,os,shutil,subprocess
import traceback as tb,multiprocessing as mp,queue
from tkinter import ttk,tix,font
##import LinearAlgebra as LinAlg
import GeneralTools
import math,collections

vector=GeneralTools.vector
matrix=GeneralTools.matrix
flatten=GeneralTools.flatten
OrderedSet=GeneralTools.OrderedSet
#patching to keep old code functional
LinAlg=GeneralTools

from .EventTools import *
from .ColorTools import *
from . import SharedData

def setname(self,name=None):
    if name is None:
        name=type(self).__name__
    setattr(self,'name',name)

new_vals=('fill','children','bg','bd')
#add more to this later
def reparent(widget,new_parent):
    t=type(widget)
    kw={}
    for v in new_vals:
        try:
            kw[v]=widget.cget(v)
        except:
            pass
    return t(new_parent,**kw)

def FontObject(fontORwidget):
    if isinstance(fontORwidget,font.Font):
        F=fontORwidget
    elif isinstance(fontORwidget,dict):
        F=font.Font(**fontORwidget)
    else:
        if fontORwidget is None:
            fontORwidet='tkTextFont'
        elif isinstance(fontORwidget,str):
            fontORwidget=fontORwidget['font']
        F=font.Font(fontORwidget)
    return F
def text_to_pixels(string,fontORwidget=None):
    F=FontObject(fontORwidget)
    return F.measure(string)

def hide_decorations(window,mode='mac'):
    if mode=='mac':
        window.tk.call("::tk::unsupported::MacWindowStyle", "style",
                       window._w, "plain", "none")

class ChildRerouter(dict):
    def __init__(self,parent,route_children_to,child_dict=None):
        if child_dict is None:
            child_dict=self.parent.children
        super().__init__(**child_dict)
        self.parent=parent
        self.reroute=route_children_to
        self._len=len(self)-1
    def __setitem__(self,key,value):
        if len(self)>self._len:
            value._setup(self.reroute,{})
        else:
            dict.__setitem__(self,key,value)
            
def safe_destroy(window):
##    try:
##        window.geometry('1x1+1000+1000')
##    except:
##        pass
##    window.update_idletasks()
    
    if window.master is None:# and not isinstance(window,tk.Toplevel):
        window.withdraw()
        window.quit()
    else:
        window.destroy()
