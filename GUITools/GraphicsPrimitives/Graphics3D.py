from .GraphicsPrimitive import *
        
class Shape(GraphicsPrimitive):

    pointFlattener=Flattener(endtype=list)
    flatten=pointFlattener
    
    def __init__(self,points=None,name=None,priority=0,boundob=None,parent=None,
                 callback=lambda *e:None,fixed=False,filled=True,shadable=True,
                 inset=None,send=lambda s:None,**kwargs):
        super().__init__(name=name,parent=parent,boundob=boundob,callback=callback,fixed=fixed,priority=priority)

        #The connection points which will be used whenever moving a shape in a parent frame
        self.connected=[]
        self.connectionpoints={}
        #The multishapes in which it's contained
        self.multishapes=[]
        #A flag which tells its parent widget whether to draw it or not. Is configured whenever one of the mutation
        #functions is called on it (i.e., Shift,__mul__,Transform,etc.)
        self.drawFlag=True
        #Sets the initial points, with (0,0,0) as the default center
        if points:
            points=matrix(((0,0,0),points))
        else:
            points=matrix((0,0,0))
        self.__points=points
        #Calculates the center of the shape
        self.Center(True)
        #A flag to determine whether it can be shaded or not
        self.shadable=shadable
        #Sets the text to be inset into the shape
        if inset:
            inset=Text(self.points.column(0),inset,boundob=boundob,callback=callback)
        self.inset=inset
        #Sets the basefill for shading
        if 'fill' in kwargs:
            self.basefill=kwargs['fill']
        else:
            self.basefill=None
        if 'outline' in kwargs:
            self.baseoutline=kwargs['outline']
        else:
            self.baseoutline=None
        #Callback for when double clicked in a frame
        self.callback=callback
        #Send function for configuring a bound object
        self.send=lambda self=self:send(self)
        #these kwargs will screw up the canvas draw function
        for key in ['parent','boundob','ID','filled','callback','send','inset']:
            if key in kwargs:
                del kwargs[key]
        #sets the draw_tags
        self.kwargs=kwargs
        if 'tag' in self.kwargs:
            t=self.kwargs['tag']
            if not isinstance(t,str):
                t=list(t)+[self.ID]
            else:
                t=(self.ID,t)
            self.kwargs['tag']=t
        else:
            self.kwargs['tag']=self.ID
        self.newargs=[]
        self.newkwargs={}
        self.newkwargs['priority']=priority
        self.newkwargs['parent']=parent
        self.newkwargs['boundob']=boundob
        self.newkwargs['filled']=filled
        self.newkwargs['shadable']=shadable
        self.newkwargs['inset']=inset
        self.drops={'outline'}
        if filled:
            self.drops.add('fill')
    #--
    def __getattr__(self,attrname):
        try:
            super().__getattribute__(attrname)
        except Exception as E:
            try:
                return super().__getattribute__('bound').__getattribute__(attrname)
            except:
                raise E
    @property
    def points(self):
        self.drawFlag=True
        for p,o in self.draw_map.items():
            p.addtag_withtag('moved',o)
        return self.__points
    @points.setter
    def points(self,value):
        self.drawFlag=True
        for p,o in self.draw_map.items():
            p.addtag_withtag('moved',o)
        self.__points=value
    
    @abstractmethod
    def draw_process(self):
        pass
    
    #---
    def Delete(self):
        for shape in self.connected:
            self.Detach(shape)
        for m in self.multishapes:
            try:
                m.remove(self)
            except:
##                print(m,self.multishapes)
                pass
            if not m:
                m.Delete()
    #------------------------------------------------------------------------- 
    def AttachTo(self,shape,point,reciprocate=True):
        shape.connected.append(self)
        try:
            i=self.points.index(point)
        except ValueError:
            p1=vector(*point,orientation='col')
            p=min(self.points, key=lambda P:(p1-P).mag())
            i=self.points.index(p)
        self.connectionpoints[shape]=i
        if reciprocate:
            shape.AttachTo(self,point,reciprocate=False)
    #--
    def Detach(self,other):
        for x,y in ((self,other),(other,self)):
            try:
                other.connected.remove(self)
                del other.connectionpoints[self]
            except ValueError:
                pass
    #------------------------------------------------------------------------- 
    def Shift(self,x=0,y=0,z=0,to=False,moveconnected=True,override=False):

        def move():
            l=self.points.cols
            v=vector(x,y,z,orientation='col')
            if to:
                c=self.Center()
                v+=-c
            r=range(3)
            for p in self.points:
                for i,q in zip(r,v):
                    p[i]+=q
            if moveconnected:
                for shape in self.connected:
                    pIndex=shape.connectionpoints[self]
                    P=shape.points.column(pIndex)
                    newp=map(lambda a,b:a+b,P,v)
                    shape.points[pIndex]=newp
        if (not self.fixed) or override:
            move()
    #-------------------------------------------------------------------------
    def Center(self,recalc=False):
        if recalc:
            vs=self.points.columniter()
            s=next(vs)
            s=next(vs)
            for v in vs:
                s+=v
            s=s/(self.points.cols-1)
            for i in range(3):
                self.points[i,0]=s[i]
        return self.points.vectors[0]
    #--
    def DrawInset(self,on):
        self.inset.points[0]=self.points.column(0)
        ob=self.inset.Draw(on)
    #--
    def ParentBind(self,*obs):
        for ob in obs:
            self.parent.tag_bind(ob,'<Command-Double-Button-1>',lambda *e:self.callback(e))
    def PostDraw(self,callback_ob=None,inset_on=None):
        if not callback_ob is None:
            if self.callback:
                    if self.parent:
                        ob=self.parent.shapeFlattener.flatten(callback_ob)
                        self.ParentBind(*ob)
        if not inset_on is None:
            if self.inset:
                self.DrawInset(inset_on)
    #--
    def DrawPoints(self):
        return list(self.points)[1:]
    #-------------------------------------------------------------------------
    def Shade(self,onwhat,shadefloat,color=None,mode='fill'):

        if not self.shadable:
            shadefloat=1
        if color:
            c=[min(shadefloat*float(x)/256,255) for x in onwhat.winfo_rgb(color)]
        else:
            if mode=='fill':
                if self.basefill:
                    c=[min(shadefloat*float(x)/256,255) for x in onwhat.winfo_rgb(self.basefill)]
                else:
                    c=[min(shadefloat*float(x)/256,255) for x in onwhat.winfo_rgb('black')]
            elif mode=='outline':
                if self.baseoutline:
                    c=[min(shadefloat*float(x)/256,255) for x in onwhat.winfo_rgb(self.baseoutline)]
                else:
                    c=[min(shadefloat*float(x)/256,255) for x in onwhat.winfo_rgb('black')]
        for i in range(3):
            q=int(round(c.pop(0),0))
            h=hex(q).split('x')[1]
            if len(h)==1:
                h='0'+h
            if len(h)>2:
                raise
            c.append(h)               
        hkey='#{}{}{}'.format(*c)
        if mode in self.drops:
            self.kwargs[mode]=hkey
        else:
            self.kwargs['fill']=hkey
                
    #--
    def Transform(self,transformation,moveconnected=True):
        if not self.fixed:
            self.points=transformation.apply(self.points)
            if moveconnected:
                for shape in self.connected:
                    pIndex=shape.connectionpoints[self]
                    P=shape.points.column(pIndex)
                    newp=transformation.apply(P)
                    shape.points[pIndex]=newp
        
    def MatrixTransformation(self,mat,moveconnected=True):
        if not self.fixed:
            self.points=mat*self.points
            if moveconnected:
                for shape in self.connected:
                    pIndex=shape.connectionpoints[self]
                    P=shape.points.column(pIndex)
                    newp=mat*P
                    shape.points[pIndex]=newp

        
    #--------------------------------------------------------------------------
    def __mul__(self,s):

        pset=s*self.points
        T=type(self)
        ret=T(pset,*self.newargs,**self.newkwargs)
        for k in vars(self):
            setattr(ret,k,getattr(self,k))
        ret.points=pset
        return ret
    #
    __rmul__=__mul__
    #--
    def __getitem__(self,key):
        return self.kwargs[key]
    #--
    def __setitem__(self,key,val):
        self.kwargs[key]=val
    #--
    def __iter__(self):
        return iter(self.points)
    #--
    def __str__(self):
        t=type(self)
        cls=t.__name__
        p=list((tuple(x) for x in self.points))
        if t==Shape:
            p[-1]=None
        a=str(tuple((x for x in p if not x is None)))
        kw=','.join(('{}={}'.format(x,y) for (x,y) in self.newkwargs.items()))
        return '{}({},{})'.format(cls,a,kw)
    def __repr__(self):
        classname=self.ID
        return classname
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$    
class Polygon(Shape):

    def __init__(self,*points,**shapekwargs):
        super().__init__(*points,**shapekwargs)
        points.append(points.column(1))

    #-------------------------------------------------------------------------
    def draw_process(self,on,quality='good',**kwargs):
        pset=self.DrawPoints()
        if not 'outline' in kwargs:
            kwargs['outline']='black'
        if kwargs:
            kw=self.kwargs.copy()
            for k in kwargs:
                kw[k]=kwargs[k]
        if self.filled:
            drawtype='polygon'
        else:
            drawtype='line'
        cf=getattr(onwhat,'create_'+drawtype)
        ob=cf(pset,**kw)

        return ob
        
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Line(Shape):

    def __init__(self,*points,priority=0,boundob=None,parent=None,fixed=False,**kwargs):
        super(Line,self).__init__(points=points,priority=priority,fixed=fixed,
                                  parent=parent,boundob=boundob,**kwargs)
        self.Center(True)
        self.drops={'fill'}
        
    def draw_process(self,*onwhat,quality='good',**kwargs):
        points=self.DrawPoints()
        kw=self.kwargs.copy()
        for k in kwargs:
            kw[k]=kwargs[k]
        if not onwhat:
            on=self.parent
        else:
            on=onwhat[0]
        cf=getattr(on,'create_line')
        ob=cf(*points,**kw)
        if self.callback:
            if self.parent:
                self.ParentBind(ob)
        return ob
#$$$$$$
class Cylinder(Line):

    def __init__(self,*points,radius=1,priority=0,boundob=None,parent=None,fixed=False,**kwargs):
        kwargs['width']=radius
        self.radius=radius
        for x in ('boundob','priority','parent','fixed'):
            kwargs[x]=eval(x)
        super().__init__(*points,**kwargs)
    def draw_process(self,*onwhat,quality='good',**kwargs):
        points=self.DrawPoints()
        kw=dict(self.kwargs,**kwargs)
        for k in kwargs:
            kw[k]=kwargs[k]
        if not onwhat:
            on=self.parent
        else:
            on=onwhat[0]
        cf=getattr(on,'create_cylinder')
        ob=cf(*points,**kw)
        if self.callback:
            if self.parent:
                self.ParentBind(ob)

        return ob
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Oval(Shape):

    def __init__(self,*bbox,priority=0,boundob=None,parent=None,fixed=False,**kwargs):
        super(Oval,self).__init__(priority=priority,fixed=fixed,
                                  parent=parent,boundob=boundob,**kwargs)
        bbox=self.pointFlatten.flatten(bbox)
        if len(bbox)<6:
            bbox.insert(2,0)
            bbox.insert(5,0)
            bbox+=[0]*(6-len(bbox))
        self.points.pop(-1)
        self.points.extend((bbox[:3],bbox[3:6]))
        self.initialposition=matrix(self.points)
        self.Center(True)
    #-------------------------------------------------------------------------
    def draw_process(self,*onwhat,quality='good',**kwargs):
        c,p1,p2=self.points
        kw=self.kwargs.copy()
        for k in kwargs:
            kw[k]=kwargs[k]
        if not onwhat:
            on='self.parent'
        else:
            onwhat=onwhat[0]
            on='onwhat'
        ob=eval('{}.create_oval(p1,p2,**kw)'.format(on))
        if self.callback:
            if self.parent:
                self.ParentBind(ob)
        if self.inset:
            self.DrawInset(on)
        return ob

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Circle(Oval):
    
    def __init__(self,center,radius=2,priority=0,
                 boundob=None,parent=None,fixed=False,**kwargs):
        c=vector(center)
        v=vector(radius,radius,0)
        p1=c-v
        p2=c+v
        super().__init__(p1,p2,priority=priority,
                 boundob=boundob,parent=parent,fixed=fixed,**kwargs)
        self.newargs.append(radius)
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Sphere(Shape):

    def __init__(self,center,radius=2,priority=0,
                 boundob=None,parent=None,fixed=False,threedflag=False,**kwargs):
        m=matrix(center)
        c=m.column(0).rowvector()
##        c=vector(center)
        p1=c-vector(radius,0,0)
        p2=c+vector(radius,0,0)
        p3=c-vector(0,radius,0)
        p4=c+vector(0,radius,0)
        p5=c-vector(0,0,radius)
        p6=c+vector(0,0,radius)
        
        super(Sphere,self).__init__(priority=priority,parent=parent,points=[c,p1,p2,p3,p4,p5,p6],
                                    boundob=boundob,fixed=fixed,**kwargs)
        self.points.pop(-1)
        self.points.pop(0)
        if threedflag:
            self.hq='good'
        else:
            self.hq='never'
        self.radius=radius
    #-------------------------------------------------------------------------
    def draw_process(self,*onwhat,quality='good',**kwargs):
        point=self.points.column(0)
        kw=self.kwargs.copy()
        for k in kwargs:
            kw[k]=kwargs[k]
        if not onwhat:
            on=self.parent
        else:
            on=onwhat[0]
        if quality==self.hq:
            cf=on.create_sphere
            ob=cf(point,self.radius,**kw)
        else:
            try:
                cf=on.create_circle
                ob=cf(point,self.radius,**kw)
            except:
                cf=on.create_oval
                p1,p2,z=map(lambda p:p+self.radius,point)
                p3,p4,z=map(lambda p:p-self.radius,point)
                ob=cf(p1,p2,p3,p4,**kw)
            ob=[ob]
        self.PostDraw(ob,on)
        return ob[0]
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Point(Sphere):
    def __init__(self,*center,priority=0,boundob=None,parent=None,fixed=False,**kwargs):
        if not 'fill' in kwargs:
            kwargs['fill']='black'
        if 'inset' in kwargs:
            kwargs['inset']=None
        super().__init__(center,radius=2,priority=priority,
                                   parent=parent,boundob=boundob,fixed=fixed,**kwargs)
        self.points=matrix(self.points.column(0))
    #--
    def draw_process(self,*onwhat,**kwargs):
        kwargs['quality']='fast'
        return super().draw_process(*onwhat,**kwargs)
    #-------------------------------------------------------------------------
    def __getitem__(self,i):
        return self.points[i,0]
    #-----------------------------------------------------------------------
    def __repr__(self):
        return str(self.points.column(0).rowvector())
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Rectangle(Shape):

    def __init__(self,*bbox,priority=0,boundob=None,parent=None,fixed=False,**kwargs):
        super(Rectangle,self).__init__(priority=priority,parent=parent,
                                       fixed=fixed,boundob=boundob,**kwargs)
        bbox=self.pointFlatten.flatten(bbox)
        if len(bbox)<6:
            bbox.insert(2,0)
            bbox.insert(5,0)
            bbox+=[0]*(6-len(bbox))
        self.points.pop(-1)
        self.points.extend((bbox[:3],bbox[3:6]))
        self.Center(True)
    #-------------------------------------------------------------------------
    def draw_process(self,*onwhat,quality='good',**kwargs):
        c,p1,p2=self.points
        kw=self.kwargs.copy()
        for k in kwargs:
            kw[k]=kwargs[k]
        if not onwhat:
            on=self.parent
        else:
            on=onwhat[0]
        ob=on.create_rectangle(p1,p2,**kw)
        self.PostDraw(ob,on)

        return ob
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Square(Rectangle):

    def __init__(self,corner,sidelength,priority=0,
                 boundob=None,parent=None,fixed=False,**kwargs):
        v1=vector(corner)
        second=v1+vector(1,1,0)*sidelength
        super(Square,self).__init__((list(corner)+list(second)),
                                    boundob=boundob,parent=parent,fixed=fixed,**kwargs)      
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Text(Shape):

    def __init__(self,point,text='',priority=0,filled=False,boundob=None,parent=None,fixed=False,**kwargs):
        
        for k in ('priority','filled','boundob','parent','fixed'):
            kwargs[k]=eval(k)
        super().__init__(points=[point],**kwargs)
        self.text=text
        self.kwargs['text']=text

    def draw_process(self,on,**kwargs):
        point=self.points.column(0)
        for x in ('outline',):
            if x in self.kwargs:
                del self.kwargs[x]
        if self.kwargs:
            kw=self.kwargs.copy()
            for k in kwargs:
                kw[k]=kwargs[k]
        else:
            kw=kwargs
        drawtype='text'
        cf=getattr(on,'create_text')
        ob=cf(point,**kw)

        return ob

#$$$
class GraphicsWindow(Shape):

    def __init__(self,coords,priority=-1,filled=False,boundob=None,parent=None,fixed=True,**kwargs):
        for k in ('priority','filled','boundob','parent','fixed'):
            kwargs[k]=eval(k)
        super().__init__(coords,**kwargs)

    def draw_process(self,*onwhat,**kwargs):
        pset=self.DrawPoints()
        for x in ('fill','outline'):
            if x in self.kwargs:
                del self.kwargs[x]
        if self.kwargs:
            kw=self.kwargs.copy()
            for k in kwargs:
                kw[k]=kwargs[k]
        else:
            kw=kwargs
        drawtype='window'
        if not onwhat:
            on=self.parent
        else:
            on=onwhat[0]
        cf=getattr(on,'create_window')
        ob=cr(pset,**kw)
        if self.callback:
            if on is self.parent:
                self.ParentBind(ob)

        return ob
    
class GraphicsImage(Shape):

    def __init__(self,points,source,root=None,wtol=10,htol=10,**kwargs):
        from ..ImageTools import ImageWrapper
        super().__init__(points=points,**kwargs)
        self.points.pop(-1)
        self.base=ImageWrapper(source)
        self.image=self.colored=ImageWrapper(source)
        self.upscaleFactor=10
        try:
            self.draw=self.image.toTk()
        except:
            self.draw=None
        self.color=(1,1,1,1)
        self.wtol=wtol
        self.htol=htol

    def __getattr__(self,attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError as E:
            try:
                return getattr(self.image,attr)
            except:
                raise E
            
    def resize(self,w,h):
        wq=self.draw.width()-w
        hq=self.draw.height()-h
        rob=None
        rf=False
        if abs(wq)>self.wtol:
            rf=True
            if wq<0:
                rob=self.colored
        if abs(hq)>self.htol:
            rf=True
            if rob is None:
                if hq<0:
                    rob=self.colored
        if rf:
            if rob is None:
                rob=self.image
            self.image=type(self.image)(rob.resize((int(w),int(h))))
            self.draw=self.image.toTk()

    def adjust_color(self,r=1,g=1,b=1,a=1):
        t=(r,g,b,a)
        if self.color!=t:
            self.image=self.image.recolored(*t)
            self.draw=self.image.toTk()
            self.color=t
            
    def recolor(self,colorname):
        color=[max(1,x) for x in self.image.getcolor(colorname)]
        sf=1/255
        self.colored=self.base.recolored(*map(lambda x:x*sf,color))
        self.image=self.colored
        self.draw=self.image.toTk()

    def initialize(self):
        try:
            self.draw=self.image.toTk()
        except:
            self.draw=None
        
    def draw_process(self,on,**kwargs):
        pset=self.DrawPoints()
        kw=dict(self.kwargs,**kwargs)
        if 'fill' in kw:
            c=self.image.recolor(kw['fill'])
        if self.draw is None:
            self.draw=self.im.toTk()
        drawtype='image'
        cf=getattr(on,'create_{}'.format(drawtype))
        ob=cf(pset,image=self)
        if self.callback:
            if on is self.parent:
                self.ParentBind(ob)

        return ob
            
#$$$$
class SphereImage(GraphicsImage):
    file=ImageFiles.Sphere

    def __init__(self,center,radius=2,root=None,wtol=1,htol=1,**kwargs):
        m=matrix(center)
        c=m.column(0).row_form
##        c=vector(center)
        v=vector(radius,0,0)
        p1=c-v
        p2=c+v
        v=vector(0,radius,0)
        p3=c-v
        p4=c+v
        v=vector(0,0,radius)
        p5=c-v
        p6=c+v
        super().__init__((p1,p2,p3,p4,p5,p6),self.file)
##        self.points.pop(-1)
    def resize(self,w,h):
        x=max(w,h)
        super().resize(x,x)
        
        
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class MultiShape(GraphicsPrimitive):
    
    flattener=Flattener(endtype=list,dontExpand=(Shape,))
    shapeflatten=flattener.flatten
    genflattener=Flattener(endtype='generator',frombottom=1)
    genflatten=genflattener.flatten
    def __init__(self,*shapeset,name=None,parent=None,callback=lambda:None,
                 boundob=None,send=lambda :None,fixed=False,priority=0):
        super().__init__(name=name,parent=parent,boundob=boundob,
                         callback=callback,fixed=fixed,priority=priority)
        flattener=Flattener(endtype=list,dontExpand=(Shape,MultiShape))
        flatten=flattener.flatten
        slist=flatten(shapeset)
        self.shapes=slist
        self.multishapes=[]
        self.points=matrix(dim=(3,1))
        self.flatshapes=set()
        self.obpoints=[]
        self.send=send
        self.drawFlag=True
        self.bound=boundob
        self.inset=None
        fs=self.shapeflatten(self.shapes)
        self.flatshapes.update(fs)
        for shape in self.shapes:
            m=shape.multishapes
            if not self in m:
                m.append(self)
            try:
                self.points.extend(shape.points)
                self.obpoints.append(shape.points)
            except:
                self.points.extend(flatten(shape))
    #-------------------------------------------------------------------------
    def Center(self):
        vs=self.points.cols
        s=next(vs)
        for v in vs:
            s+=v
        return s/self.points.cols
    #--
    def PropogateAttribute(self,attr,val):
        self.__setattr__(attr,val)
        for s in self:
            try:
                s.PropogateAttribute(attr,val)
            except AttributeError:
                s.__setattr__(attr,val)        
    #--
    def Sorted(self,mode='yz',use_all=False):

        flatten=self.genflatten
        def maxsort(s):
            s=flatten(s)
##            print(l)
            try:
                return max((p[2] for p in s))
            except ValueError:
                return -1

        def centersort(s):
            s=flatten(s)
            return next(s)[2,0]

        def yzsort(s):
            s=flatten(s)
            try:
                return max((p[1]+p[2] for p in s))
            except ValueError:
                return -1
        
        evmap={'max':maxsort,'center':centersort,'yz':yzsort}
        use=self.shapes
        if use_all:
            use=(x for x in use if x.drawFlag)
        return sorted(self.shapeflatten(use),
                      key=lambda s:s.priority+evmap[mode](s))
    #-------------------------------------------------------------------------
    def draw_process(self,on,dimensions=None,quality='good',draw_all=False,**kwargs):

        res=[]
        self.draw_map[on]=res
        if dimensions:
            maxz,minz=dimensions
            depth=abs(maxz-minz)
            bound=min(1-depth/1000,.85)
        if 'color' in kwargs:
            c=kwargs['color']
            del kwargs['color']
        else:
            c=None

        for s in self.Sorted(use_all=draw_all):
            if dimensions:
                x,y,z=s.Center()
                scale=max(bound,(z-minz)/depth)
                s.Shade(scale,color=c)
            o=(s.Draw(on,quality=quality,**kwargs),s)
            res.append(o)
            yield o
            
        return res

    #-------------------------------------------------------------------------
    def Shade(self,onwhat,shadefloat,**kwargs):

        for s in self.shapeflatten(self.shapes):
            s.Shade(onwhat,shadefloat,**kwargs)
    #--
    def Clear(self):
        self.shapes=[]
        self.points=matrix(dim=(3,1))
        
    #------------------------------------------------------------------------
    def Shift(self,x=0,y=0,z=0,moveconnected=True):
        if not self.fixed:
            for shape in self.shapes:
                shape.Shift(x=x,y=y,z=z,moveconnected=moveconnected)
    def Delete(self):
        for shape in self.shapes:
            shape.Delete()            
    def MatrixTransformation(self,mat,moveconnected=True):
        if not self.fixed:
            for shape in self.shapes:
                shape.MatrixTransformation(mat,moveconnected=moveconnected)
    #--
    def __mul__(self,ob):
        return MultiShape((x*ob for x in self),
                          parent=self.parent,priority=self.priority,boundob=self.bound)
    __rmul__=__mul__
    #--
    def remove(self,item):
        for shape in self:
            if item==shape:
                self.shapes.remove(shape)
                for v in shape.points:
                    self.points.remove(v)
                break
        else:
            raise ValueError('MultiShape.remove(x): x not in MultiShape')
    #--
    def append(self,item):
        fs=self.shapeflatten(item)
        self.flatshapes.update(fs)
        self.shapes.append(item)
        self.points.extend(item.points)
        m=item.multishapes
        if not self in m:
            item.multishapes.append(self)
    #--
    def pop(self,i):
        self.points.pop(i)
        return self.shapes.pop(i)
    #--
    def index(self,item):
        return self.shapes.index(item)
    #--
    def __len__(self):
        return len(self.shapes)
    #--
    def __getitem__(self,i):
        return self.shapes[i]
    #-------------------------------------------------------------------------
    def __iter__(self):
        return iter(self.shapes)
    #--
    def __repr__(self):
        if not self.name:
            return super().__repr__()
        return self.name
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Prism(MultiShape):
    #let N be the number of points
    #Needs:
    #   3(N-2) edges
    #   2(N-2) faces
    #   Each point has at least floor(6(N-2)/N) lines
    #   If N is odd, a few have floor(6(N-2)/N)+1 lines


    def __init__(self,*points,filled=False,priority=0,
                 boundob=None,parent=None,fixed=False,**kwargs):
        for key in ('priority','filled','boundob','parent','fixed'):
            kwargs[key]=eval(key)
        shapes=[]
        pvs=[vector(p) for p in points]
        linedict={p:[] for p in pvs}
        N=len(pvs)
        faces=2*(N-2)
        edges=3*(N-2)
        connections=(2*edges)//N + (N%2)
        vm=vector(0,0,0)
        for v in pvs:
            vm+=v
        c=vm/N
        shapes.append(Point(c,parent=parent,boundob=self,
                            callback=lambda e:self.parent.Select(self)))

        PVS=iter(pvs)
        
        if filled:
            S=faces+edges
        else:
            S=edges
        i=0
        while len(shapes)<S+1:
            try:
                p=next(PVS)
            except:
                break
                PVS=iter(pvs)
                p=next(PVS)
            i+=1
            use=[]
            
            newc=c
            for v in linedict[p]:
                newc+=v
            newc=newc/(len(linedict[p])+1)
            s=iter(sorted(pvs,key=lambda x:(p-x).angle(newc-x) if any(p-x) else 0,reverse=True))
            
            while len(linedict[p])<connections:
                t=next(s)
                if len(linedict[t])<connections and not (t in linedict[p]):
                    use.append(t)
                    linedict[p].append(t)
                    linedict[t].append(p)
                    newc=c
                    for v in linedict[p]:
                        newc+=v
                    newc=newc/(len(linedict[p])+1)
                    s=iter(
                        sorted(pvs,key=lambda x:(p-x).angle(newc-x) if any(p-x) else 0,reverse=True)
                        )
                    
            if not filled:
                lset=[Line(p,u,**kwargs)
                      for u in use]
                shapes.extend(lset)
            else:
                for v in use:
                    sset=[Shape(points=(p,u,v),**kwargs)
                          for u in use]
                    shapes.extend(sset)
                    
        super(Prism,self).__init__(*shapes,parent=parent)
                
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Cube(Prism):

    def __init__(self,corner,sidelength,filled=False,boundob=None,parent=None,fixed=False,**kwargs):
        v1=vector(corner)
        p2=v1+vector(1,1,0)*sidelength
        p3=v1+vector(0,1,1)*sidelength
        p4=v1+vector(1,0,1)*sidelength
        p5=v1+vector(1,0,0)*sidelength
        p6=v1+vector(0,1,0)*sidelength
        p7=v1+vector(0,0,1)*sidelength
        p8=v1+vector(1,1,1)*sidelength
        super(Cube,self).__init__(v1,p2,p3,p4,p5,p6,p7,p8,filled=filled,
                                      boundob=boundob,parent=parent,fixed=fixed,**kwargs)


    
        
        
        
    
    
