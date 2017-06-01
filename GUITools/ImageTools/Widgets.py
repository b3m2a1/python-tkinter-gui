from GUITools.ImageTools.PILTools import ImageWrapper
import tkinter as tk

class ImageLabel(tk.Label):
    
    def __init__(self,root=None,image=None, expand=True, min_size=(None,None), max_size=(None,None), resize_pause=None,**kw):
        '''Sets up the an image wrapper to constantly set the label image as itself.

expand being True forces expansion to all available space (can be an issue with grid)
expand being 'preserve' causes aspect-ration preserving expansion
expand being False causes no expansion        
'''
        if not image is None:
            image=ImageWrapper(image) if not isinstance(image,ImageWrapper) else image
            self._current=image.Tk
            kw['image']=self._current
        self.image=image
        super().__init__(root,**kw)
        self._resizing=False
        self.resize_pause=resize_pause
        self.max_size=max_size
        self.min_size=min_size
        self.expand_mode=expand
        if expand:
            self.bind('<Configure>',self.after_resize)
    
    def set_size(self,x,y):
    
        self.image.reset()
        
        mx,my=self.min_size
        MX,MY=self.max_size
        if not mx is None:
            x=x if x > mx else mx
        if not MX is None:
            x=x if x < MX else MX
        if not my is None:
            y=y if y > my else my
        if not MY is None:
            y=y if y < MY else MY

        if self.expand_mode=='preserve':
            w,h=self.image.dimensions
            if h>w:
                x=int(y*w/h)
            else:
                y=int(x*h/w)
        self.image.resize((x,y))
        self._current=self.image.Tk
        self.config(text='',image=self._current)
    
    def after_resize(self,after=None):
        if after is None or isinstance(after,tk.Event):
            after=self.resize_pause
        if not self._resizing:
            self._resizing=True
            if after is None:
                self.resize(check_resizing=False)
            elif after=='idle':
                self.after_idle(lambda:self.resize(check_resizing=False))
            else:
                self.after(after,lambda:self.resize(check_resizing=False))
                
    def resize(self,event=None,check_resizing=True):
        if not (check_resizing and self._resizing):
            self._resizing=True
            if not self.image is None:
                w_padding=6 if not isinstance(self['bd'],int) else self['bd']
                h_padding=6 if not isinstance(self['bd'],int) else self['bd']
#                 print(w_padding,h_padding)
                w=self.winfo_width();h=self.winfo_height()
                self._last=(w,h)
#                 print(self._last)
                self.set_size(w-w_padding,h-h_padding)
            else:
                self.config(image='',text='No Image')
            self._resizing=False
    
    def set_image(self,image=None):
        if not image is None:
            self.image=ImageWrapper(image)
            self.resize()
        