from ._shared import *
from .UniformityFrame import *

class ScrollableFrame(tk.Frame):
    '''A frame with optional frame elements like scrollbars and a sizegrip'''
    class ChildTracker(UniformityFrame.ChildTracker):
        def __init__(self,parent,child_dict=None):
            super().__init__(parent,child_dict)
            self._len=len(self)-1
            self._manager_map={}
        def __setitem__(self,key,value):
            if len(self)>self._len:
                value._setup(self.parent._frame,{})
            else:
                dict.__setitem__(self,key,value)
        def pack_override(self,widget):
            def pack(widget=widget,self=self,**kwargs):
                self._manager_map[widget]='place'
                kwargs['in_']=self.parent._frame
                type(widget).pack(widget,**kwargs)
                widget.lower()
            return pack
        def grid_override(self,widget):
            def grid(widget=widget,self=self,**kwargs):
                self._manager_map[widget]='place'
                kwargs['in_']=self.parent._frame
                type(widget).grid(widget,**kwargs)
            return grid
        def place_override(self,widget):
            def place(widget=widget,self=self,**kwargs):
                self._manager_map[widget]='place'
                kwargs['in_']=self.parent._frame
                type(widget).place(widget,**kwargs)
            return place
            
    def __init__(self,root,scrollbars=(True,True),sizegrip=True,**kwargs):
        ''''''
        bd_f_kw={}
        for x in ('bd','borderwidth','highlightthickness','relief'):
            if x in kwargs:
                bd_f_kw[x]=kwargs[x]
                del kwargs[x]  
        super().__init__(root,**bd_f_kw)
        
        self._bd_frame=tk.Frame(self)
        self._frame=tk.Frame(self._bd_frame,**kwargs)
        self._frame.place(x=0,y=0)
        self._frame.position=(0,0)
        
        self._bd_frame.bind('<Configure>',lambda e:(self.yview(0,increment=True),self.xview(0,increment=True)))
        self._scroll_bar_size=sb_size=15 
        self.frame_elements=[False,False,False]
               
        from tkinter.ttk import Sizegrip
        self._sg=Sizegrip(self)
        self._y_sb=tk.Scrollbar(self,command=self.yview,orient='vertical')
        self._x_sb=tk.Scrollbar(self,command=self.xview,orient='horizontal')
        self.set_elements(scrollbars=scrollbars,sizegrip=sizegrip)
        self.children=self.ChildTracker(self,self.children)
        self.after(500,self._remap_children)
        self.lower(self._frame)
        
    @property
    def _window_dimensions(self):
        return (self.winfo_width(),self.winfo_height())
    
    def _remap_children(self,event=None):
        for w,key in self.children._manager_map.items():
            f=getattr(w,key)
            f()
    
    def set_elements(self,scrollbars=None,sizegrip=None):
        
        sb=self._scroll_bar_size
        y=self._y_sb
        x=self._x_sb
        g=self._sg
        sg=sizegrip if sizegrip is None else self.frame_elements[2]
        if not scrollbars is None:
            if scrollbars is True:
                do_y=True;do_x=True
            elif scrollbars is False:
                do_y=False;do_x=False
            else:
                do_y=scrollbars[1];do_x=scrollbars[0]
        else:
            do_y=self.frame_elements[0]
            do_x=self.frame_elements[1]
        
        self._bd_frame.place(relheight=1,relwidth=1,
                    height=-sb if (do_y or sg) else 0,width=-sb if (do_x or sg) else 0)
        if sg:
            self._sg.place(relx=1,rely=1,height=sb,width=sb,anchor='se')
        else:
            self._sg.place_forget()
        if do_y:
            self._y_sb.place(relx=1,relheight=1,
                height=-sb if sg else 0,width=sb,anchor='ne')
            self.frame_elements[0]=True
        else:
            self._y_sb.place_forget()
            self.frame_elements[0]=False
        if do_x:
            self._x_sb.place(rely=1,relwidth=1,
                height=sb if sg else 0,width=-sb,anchor='sw')
                    
        
                
                
                
            
    def xview(self,mx,offset='',increment=False):
        if mx!='scroll':
            cur_x,cur_y=self._frame.position
            w=self._frame.winfo_width();h=self._frame.winfo_height()
            mw,mh=self._window_dimensions
            if not offset=='':
                mx=offset
            if isinstance(mx,str):
                mx=float(mx)
            mx*=w
            if increment:
                cur_x+=mx
            else:
                cur_x=mx
            if abs(cur_x)>w-mw:
                cur_x=w-mw
            if cur_x<0:
                cur_x=0
            self._frame.place(x=-cur_x,y=-cur_y)
            self._y_sb.lift();self._x_sb.lift();self._sg.lift()
            self._frame.lower()
            self._frame.position=(cur_x,cur_y)
            self._x_sb.set(cur_x/w,(cur_x+mw)/w)
        
    def yview(self,my,offset='',increment=False):
        if my!='scroll':
            cur_x,cur_y=self._frame.position
            w=self._frame.winfo_width();h=self._frame.winfo_height()
            mw,mh=self._window_dimensions
            if not offset=='':
                my=offset
            if isinstance(my,str):
                my=float(my)
            my*=h
            if increment:
                cur_y+=my
            else:
                cur_y=my
            if abs(cur_y)>h-mh:
                cur_y=h-mh
            if cur_y<0:
                cur_y=0
            self._frame.place(x=-cur_x,y=-cur_y)
            self._y_sb.lift();self._x_sb.lift();self._sg.lift()
            self._frame.lower()
            self._frame.position=(cur_x,cur_y)
            self._y_sb.set(cur_y/h,(cur_y+mh)/h)