from ._shared import *

class UniformityFrame(tk.Frame):
    """A class used to maintain options uniformity across all children.
Lookups become increasingly expensive as the number of children grows, but for
small numbers of children this is an effective way to make them act as a single
widget"""
    class ChildTracker(dict):
        def __init__(self,parent,child_dict=None):
            if child_dict is None:
                child_dict={}
            self.parent=parent
            super().__init__(**child_dict)
        def __setitem__(self,key,value):
            super().__setitem__(key,value)
            self.parent.mirror()
        def remove_child(self,widget):
            n=str(widget)
            if n in self:
##                self.parent.__config=None
                del self[n]
        @property
        def widgets(self):
            return [v for x,v in self.items()]
            
    OptionFail=TclError
    BadCommandName=TclError

    mirror_keys={'bg','bd','highlightbackground','fg'}
    follow_options={'bg':('highlightbackground',)}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.independence_map={}
##        self.__config=None
        self.children=self.ChildTracker(self,super().__getattribute__('children'))
##        self.bind('<Configure>',self.mirror)
    
    def mirror(self,event=None):
        for k in self.keys():
            try:
                o=self.cget(k)
            except self.OptionFail:
                continue
            if k in self.mirror_keys:
                self.configure({k:o})
##        self.mirror_var.set(False
    def bind(self,event,command=None,mode='+',to_all=False):
        fid=super().bind(event,command,mode)
        if not command is None and to_all:
            fid={self:fid}
            for x in self.children.widgets:
                fid.update(self.recursive_bind(x,event,command))
        return fid
    
    def keys(self):
        keys=set(super().keys())
        for c in self.children.widgets:
            keys.update(self.recursive_keys(c))
        return keys
    
    def configure(self,*dicts,**kwargs):
        
        for d in dicts:
            kwargs.update(d)
        if len(kwargs)==0:
            return super().config()
        
        for k,v in kwargs.items():
            if k in self.follow_options:
                for x in self.follow_options[k]:
                    self.config({x:v})
            try:
                super().config({k:v})
            except self.OptionFail:
                pass
        for x in self.children.widgets:
            self.set_recursive(x,**kwargs)
            
    config=configure
    def do_not_configure(self,widget,key):
        try:
            self.independence_map[key].add(widget)
        except KeyError:
            self.independence_map[key]={widget}
    def __setitem__(self,key,val):
        self.configure({key:val})
    def __getitem__(self,key):
        return self.cget(key)
    def cget(self,key):
        try:
            ret=super().cget(key)
        except self.OptionFail:
            for c,x in self.children.items():
                ret=self.get_recursive(x,key)
                if not ret is None:
                    break
            else:
                raise
        return ret
    def safe_config(self,ob,**kwargs):
        for k,v in kwargs.items():
            try:
                ws=self.independence_map[k]
            except KeyError:
                ws=[]
            if not ob in ws:
                try:
                    ks=ob.keys()
                except self.BadCommandName:
                    self.children.remove_child(ob)
                else:
                    if k in ks:
                        try:
                            ob.config({k:v})
                        except:
                            pass
    def set_recursive(self,widg,**kwargs):
        self.safe_config(widg,**kwargs)
        for k,x in widg.children.items():
            self.set_recursive(x,**kwargs)
    def recursive_keys(self,widg):
        try:
            keys=set(widg.keys())
        except self.BadCommandName:
            keys=set()
        else:
            for k,x in widg.children.items():
                keys.update(self.recursive_keys(x))
        return keys           
    def get_recursive(self,widg,key):
        #this goes depth first, but the idea is that all the properties are
        #mirrored so this really does not matter
        #It would be better written to go breadth first, though
        try:
            ws=self.independence_map[key]
        except KeyError:
            ws=[]
        ret=None
        if not widg in ws:
            ks=widg.keys()
            if key in ks:
                ret=widg.cget(key)
        for c,x in widg.children.items():
                ret=self.get_recursive(x,key)
                if not ret is None:
                    break
        return ret
    
    def recursive_bind(self,widg,string,command):
        fid=widg.bind(string,command,'+')
        fid={widg:fid}
        for c,x in widg.children.items():
            fid.update(self.recursive_bind(x,string,command))
        return fid