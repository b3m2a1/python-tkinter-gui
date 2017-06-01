from .GraphicsPrimitive import *
class GridGraphic(GraphicsPrimitive):
    def __init__(self,position=None,cell=None,parent=None,size=1,anchor='nw',posprec=3,**kwargs):
        super().__init__()
        if cell is None:
            cell=[0,0]
        self.cell=list(cell)
        if position is None:
            position=[0,0]
        self.position=list(position)
        self.parent=parent
        self.size=size
        self.kwargs=kwargs
        self.anchor=anchor.lower()
        self.posprec=3

    def Scale(self,factor):
        self.width*=factor
        self.height*=factor
        
    def Shift(self,x=0,y=0):
        move=(x,y)
        self.position[0]+=x
        self.position[1]+=y
        c=list(self.cell)
        self.position=[round(x,self.posprec) for x in self.position]
        for i in range(2):
            cInd=(i+1)%2
            if self.position[i]>=1 or self.position[i]<0:
                v=self.position[i];
                s=int(v)
                if v<0 and s==0:
                    s+=-1
                self.cell[cInd]+=s
                self.position[i]=v-s

        return (c,self.cell)
    
    def Position_Width_Height(self,bbox):
        w=bbox[2]-bbox[0]
        h=bbox[3]-bbox[1]
        x=w*self.position[0]+bbox[0]
        y=h*self.position[1]+bbox[1]
        for s,p in (
            ('nw',(0,0)),
            ('c',(.5,.5)),
            ('n',(.5,0)),
            ('e',(1,.5)),
            ('s',(.5,1)),
            ('w',(0,.5)),
            ('ne',(1,0)),
            ('sw',(0,1)),
            ('se',(1,1))
            ):
            if self.anchor==s:
                x+=w*p[0]
                y+=h*p[1]
                break
        return (x,y,w,h)
    
    def config(self,**kwargs):
        self.kwargs.update(kwargs)

    @abstractmethod
    def Draw(self):
        pass
    def draw_process(self,*args,**kwargs):
        Draw(self,*args,**kwargs)

class GridOval(GridGraphic):
    def __init__(self,width=1,height=1,position=None,cell=None,parent=None,**kwargs):
        superKwargs={'position':position,'cell':cell,'parent':parent}
        superKwargs.update(**kwargs)
        super().__init__(**superKwargs)
        self.width=width
        self.height=height
        
    def Draw(self,onwhat=None,bbox=None,tags=()):
        if onwhat is None:
            onwhat=self.parent
        if bbox is None:
            bbox=onwhat.BBox(*self.cell)
        x,y,w,h=self.Position_Width_Height(bbox)
        w*=self.width
        h*=self.height
        return onwhat.create_oval(x,y,x+w,y+h,tags=tags,**self.kwargs)

class GridCircle(GridGraphic):
    def __init__(self,radius=.5,position=None,cell=None,parent=None,anchor='c',**kwargs):
        superKwargs={'position':position,'cell':cell,'parent':parent,'anchor':anchor}
        superKwargs.update(**kwargs)
        super().__init__(**superKwargs)
        self.radius=radius
    def Scale(self,factor):
        self.radius*=factor
    def Draw(self,onwhat=None,bbox=None,tags=()):
        if onwhat is None:
            onwhat=self.parent
        if bbox is None:
            bbox=onwhat.BBox(*self.cell)
        x,y,w,h=self.Position_Width_Height(bbox)
        m=min(w,h)*self.radius
        return onwhat.create_oval(x-m,y-m,x+m,y+m,tags=tags,**self.kwargs)

class GridRectangle(GridGraphic):
    def __init__(self,width=1,height=1,position=None,cell=None,parent=None,**kwargs):
        superKwargs={'position':position,'cell':cell,'parent':parent}
        superKwargs.update(**kwargs)
        super().__init__(**superKwargs)
    def Draw(self,onwhat=None,bbox=None,tags=()):
        if onwhat is None:
            onwhat=self.parent
        if bbox is None:
            bbox=onwhat.BBox(*self.cell)
        x,y,w,h=self.Position_Width_Height(bbox)
        return onwhat.create_rectangle(x,y,x+w,y+h,tags=tags,**self.kwargs)
    
class GridWindow(GridGraphic):

    def __init__(self,window=None,width=1,height=1,position=None,cell=None,parent=None,**kwargs):
        superKwargs={'position':position,'cell':cell,'parent':parent}
        superKwargs.update(**kwargs)
        super().__init__(**superKwargs)
        self.width=width
        self.height=height
        self.window=window
        
    def Draw(self,onwhat=None,bbox=None,tags=()):
        if onwhat is None:
            onwhat=self.parent
        if bbox is None:
            bbox=onwhat.BBox(*self.cell)
        x,y,w,h=self.Position_Width_Height(bbox)
        w*=self.width
        h*=self.height
        return onwhat.create_window(x,y,anchor='nw',width=w-1,height=h-1,tags=tags,window=self.window)
        
class GridImage(GridGraphic):

    try:
        from PIL import Image,ImageTk
    except ImportError:
        pass
    else:
        from ..ImageTools import ImageWrapper
        PhotoImage=ImageTk.PhotoImage
    
    def __init__(self,image=None,width=1,height=1,
                 wtol=10,htol=10,hadd=0,wadd=0,position=None,cell=None,parent=None,**kwargs):
        superKwargs={'position':position,'cell':cell,'parent':parent}
        superKwargs.update(**kwargs)
        super().__init__(**superKwargs)
        self.width=1
        self.height=1
        if image is None:
            raise Exception("No image source provided")
        if not isinstance(image,self.ImageWrapper):
            image=self.ImageWrapper(image)
        self.base=self.image=image
        self.draw=self.image.Tk
        self.resetFlag=False
        self.wtol=wtol
        self.htol=htol
        self.wadd=wadd
        self.hadd=hadd
        self.rotation=0
        self.flips=[False,False]

    def __getattr__(self,attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError as E:
            try:
                r=getattr(self.image,attr)
                if not attr=='toTk':
                    self.resetFlag=True
                return r
            except:
                raise E

    def ChangeImage(self,newsource):
        self.image.load_link(newsource)
        self.draw=self.image.toTk()
        
    def Resize(self,w,h):
        self.draw_size=(w,h)

    def Rotate(self,q):
        self.rotation=(self.rotation+q)%360
        
    def Flip(self,mode):
        if mode=='horizontal':
            self.flips[0]=(not self.flips[0])
        elif mode=='vertical':
            self.flips[1]=(not self.flips[1])
    def adjust_color(self,r=1,g=1,b=1,a=1):
        t=(r,g,b,a)
        self.image=self.image.recolored(*t)
        self.draw=self.image.toTk()
        self.color=t
            
    def recolor(self,colorname):
        color=[max(1,x) for x in self.image.getcolor(colorname)]
        sf=1/255
        self.image=self.base.recolored(*map(lambda x:x*sf,color))
        self.draw=self.image.toTk()
        
    def Draw(self,onwhat=None,bbox=None,tags=()):
        if onwhat is None:
            onwhat=self.parent
        if bbox is None:
            bbox=onwhat.BBox(*self.cell)
        a=self.anchor
        self.anchor='nw'
        x,y,w,h=self.Position_Width_Height(bbox)
        self.anchor=a
        w*=self.width
        h*=self.height
        self.image.reset()
        self.image.rotate(self.rotation)#,expand=True)
        if self.flips[0]:
            self.image.transpose('flip horizontal')
        if self.flips[1]:
            self.image.transpose('flip vertical')
        self.image.resize((int(w),int(h)))
        self.draw=self.image.Tk
        return onwhat.create_image(x,y,anchor=self.anchor,image=self.draw,tags=tags,**self.kwargs)
