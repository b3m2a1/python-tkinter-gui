from abc import ABCMeta,abstractmethod
from GeneralTools.Math.LinearAlgebra import vector,matrix
from GeneralTools.UtilityTypes import Flattener
from ..SharedData import ImageFiles
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$        
class GraphicsPrimitive(metaclass=ABCMeta):

    def __init__(self,name=None,parent=None,boundob=None,
                 callback=lambda:None,fixed=None,priority=0,**kwargs):
        from random import choice
        
        if name is None:
            name=type(self).__name__
        self.name=name
        self.parent=parent
        self.priority=priority
        self.callback=callback
        self.fixed=fixed
        self.bound=boundob
        self.draw_map={}
        R=range(10)
        self.ID=type(self).__name__+''.join([str(choice(R)) for i in range(6)])
        self.newkwargs=kwargs
    
    @abstractmethod
    def draw_process(self,on):
        pass

    def Draw(self,*onwhat,**kwargs):
        try:
            on=onwhat[0]
        except:
            on=self.parent
        o=self.draw_process(on,**kwargs)
        self.draw_map[on]=[o]
        if self.callback:
            if self.parent:
                self.ParentBind(o)
        if self.inset:
            i=self.DrawInset(on)
            self.draw_map[on].append(i)
            
        return o
