from .Shared import *
from .Canvas3D import Canvas3D as Canvas3D
from .ActionBuffer import ActionBuffer as ActionBuffer
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class CoordinateSpace(Canvas3D):

    shapeFlattener=LinAlg.Flattener(endtype='gen',dontExpand=(Shape,str))
    addFlattener=LinAlg.Flattener(endtype='gen',dontExpand=(Shape,MultiShape,str))
    def __init__(self,root=None,basisvectors=((1,0,0),(0,1,0),(0,0,1)),
                 name=None,unitscaling=1,zrotation=20,**kwargs):
        self.frame=tk.Frame(root)
        if not 'bg' in kwargs:
            kwargs['bg']='grey95'
        super().__init__(self.frame,**kwargs)
        self.zrot=math
        self.xdims=(0,0)
        self.ydims=(0,0)
        self.zdims=(0,0)
        #Setting the axes, etc.
        self.unitscale=unitscaling
        self.scale*=unitscaling
        pD=0
        P=Point(0,0,0,priority=pD)
        P.radius=P.radius/self.unitscale
        self.axes=MultiShape(
            P,
            Line((0,0,0),self.basis[0]          ,priority=pD),
            Line((0,0,0),self.basis[0]*-1,dash=2,priority=pD),
            Line((0,0,0),self.basis[1]          ,priority=pD),
            Line((0,0,0),self.basis[1]*-1,dash=2,priority=pD),
            Line((0,0,0),self.basis[2]          ,priority=pD),
            Line((0,0,0),self.basis[2]*-1,dash=2,priority=pD),
            )
        self.axes.shapes=self.axes.Sorted()
        #Object container intializations
        self.objectmap={}
        self.axesFlag=True
        self.eventpoints=[]
        self.actionBuffer=ActionBuffer(maxlen=35)
        self.selected=MultiShape(name='Selected')
        self.drawpoints=MultiShape(name='Drawing Points')
        self.objects=MultiShape(self.selected,self.drawpoints)
        #Interactivity bindings
        self.baseaction=tk.StringVar()
        self.baseaction.set('rotate')
        self.actionloop=['rotate','scale','shift']
        self.bind('<Button-1>',lambda e:self.focus_set())
        self.bind('<Command-i>',lambda *e:self.Interact())
        self.bind('<Command-r>',lambda *e:self.ResetPosition())
        self.bind('<Configure>',lambda *e:self.Draw(draw_all=True))
        def mulamb():
            i=self.actionloop.index(self.baseaction)
            i=(i+1)%len(self.actionloop)
            self.baseaction.set(self.actionloop[i])
        self.bind('<Tab>',lambda *e:mulamb())
        self.bind('<B1-Motion>',
                  lambda e:(
                      self.LineAction(e,action=self.baseaction.get()),self.Draw(quality='fast'))
                  )
        self.bind('<Alt-B1-Motion>',lambda e:(
            self.LineAction(e,action=self.baseaction.get(),rounding=True),self.Draw(quality='fast'))
                  )
        for x in ('Up','Down','Right','Left'):
            self.bind('<{}>'.format(x),lambda e:(self.ArrowAction(e,action=self.baseaction.get()),self.Draw()))
        self.arrowspeed=1
        self.bind('<Control-B1-Motion>',
                  lambda e:(self.LineAction(e,action='scale'),self.Draw())
                  )
        def keyset(event):
            def rset():
                self.baseaction.set('rotate')
            def sset():
                self.baseaction.set('shift')
            def zset():
                self.baseaction.set('scale')
            if event.keysym in ('r','s','z'):
                exec('{}set()'.format(event.keysym))
        self.bind('<Control-Key>',lambda e:keyset(e))
        self.bind('<Shift-B1-Motion>',lambda e:(self.LineAction(e,action='shift'),self.Draw(quality='fast')))
        self.bind('<ButtonRelease-1>',self.EndAction)
        self.bind('<Command-g>',lambda e:self.GroupSelected())
        self.bind('<Shift-Button-1>',lambda e:(self.focus_set(),self.Select(e),self.Draw()))
        self.bind('<Command-z>',lambda e:(self.actionBuffer.undo(),self.Draw()))
        self.bind('<Command-y>',lambda e:(self.actionBuffer.redo(),self.Draw()))
        self.selRec=None

        self.bind('<Control-Shift-Button-1>',lambda e:(self.SelectConnected(e),self.Draw()))
        #Making it so the frame it's packed in configures correctly
        self.grid(row=0,column=0,sticky='nsew')
        self.frame.grid_columnconfigure(0,weight=1)
        self.frame.grid_rowconfigure(0,weight=1)
        for x in ('pack','grid','place'):
            for ext in ('','_forget'):
                setattr(self,x+ext,getattr(self.frame,x+ext))
        for y in ('row','column'):
            name='grid_{}configure'.format(y)
            setattr(self,name,getattr(self.frame,name))

    #--
    @staticmethod
    def priority_function(ob):

        ret=max((p[1]+p[2] for p in ob.points))
        return ret+ob.priority
    #-------------------------------------------------------------------------
    def Draw(self,quality='good',draw_all=True):

        self.objectmap={}
        ## Create Objects

        if draw_all:
            self.delete('all')
        use=self.objects
        use.Shade(self,1,mode='outline')
        use[0].Shade(self,1,color='yellow',mode='outline')
        
        if self.axesFlag:
##            self.Dimensions(True)
            maxz,minz=self.zdims
            depth=abs(maxz-minz)
            bound=min(1-depth/1000,.85)
            m=max(maxz,bound)
            S=self.axes*1000
            i=zip(S,S.Draw(self,draw_all=draw_all))
            a,l=next(i)
            af=True
            ##MultiShape.Draw returns an iterator
            D=use.Draw(self,quality=quality,draw_all=draw_all)
            for o,s in D:
                self.objectmap[o]=s
                while af:
                    if self.priority_function(s)<self.priority_function(a):
                        break
##                        self.lift(a)
                    else:
                        self.lift(o)
                        try:
                            a,l=next(i)
                        except StopIteration:
                            af=False
            for x in i:
                pass
                        
        else:
            D=use.Draw(self,quality=quality,draw_all=draw_all)
            for o,s in D:
                self.objectmap[o]=s

##        self.delete('moved')
          
    #-------------------------------------------------------------------------
    def AddObjects(self,*objects,dimensioncall=True,buffer=True):

        for ob in self.addFlattener.flatten(objects):
            if not ob in self.objects:
                self.objects.append(ob)
                ob.multishapes.pop(-1)
                if dimensioncall:
                    mx,MX=self.xdims
                    my,MY=self.ydims
                    mz,MZ=self.zdims
                    xs,ys,zs=ob.points.rowiter()
                    for x in xs:
                        if x<mx:
                            mx=x
                        elif x>MX:
                            MX=x
                    self.xdims=(mx,MX)
                    for y in ys:
                        if y<my:
                            my=y
                        elif y>MY:
                            MY=y
                    self.ydims=(my,MY)
                    for z in zs:
                        if z<mz:
                            mz=z
                        elif z>MZ:
                            MZ=z
                    self.zdims=(mz,MZ)
        if buffer:
            u=lambda a:self.Delete(*a,buffer=False)
            r=lambda a:self.AddObjects(*a,buffer=False)
            self.actionBuffer.append(self.actionBuffer.Action(objects,u,r))
                    
    #-------------------------------------------------------------------------
    def Create(self,objecttype,points,*otherargs,**kwargs):
        
        args='({})'.format(','.join((str(p) for p in points)))
        otherargs=tuple(x for x in otherargs if x)
        if otherargs:
            args+=',{}'.format(','.join((str(x) for x in otherargs)))
        try:
            O=eval('{}({},parent=self,**kwargs)'.format(objecttype,args))
        except:
            print(args)
            raise
        self.AddObjects(O)
        self.Refresh()
        return O
    #--
    @staticmethod
    def recurseRemove(shape,tryob):
        def recurseRemove(shape,tryob):
            try:
                tryob.remove(shape)
                return True
            except ValueError:
                for x in tryob:
                    if recurseRemove(shape,x):
                        break
                else:
                    return False
            except AttributeError:
                return False
            
        return recurseRemove(shape,tryob)
    #-------------------------------------------------------------------------
    def Delete(self,*objects,buffer=True):
        readd=[]
        for ob in objects:
            if self.recurseRemove(ob,self.objects):
                readd.append(ob)
                ob.Delete()
        if buffer:
                u=lambda a:self.AddObjects(*a,buffer=False)
                r=lambda a:self.Delete(*a,buffer=False)
                self.actionBuffer.append(self.actionBuffer.Action(readd,u,r))
    #-------------------------------------------------------------------------
    def Dimensions(self,reset=False):

        obs=(o.points for o in self.objects.flatshapes)      
        if reset:
            mx=my=mz=MX=MY=MZ=0
            for pset in obs:
                xs,ys,zs=pset.rowiter()
                for x in xs:
                    if x<mx:
                        mx=x
                    elif x>MX:
                        MX=x
                self.xdims=(mx,MX)
                for y in ys:
                    if y<my:
                        my=y
                    elif y>MY:
                        MY=y
                self.ydims=(my,MY)
                for z in zs:
                    if z<mz:
                        mz=z
                    elif z>MZ:
                        MZ=z
                self.zdims=(mz,MZ)
                
        return (self.xdims,self.ydims,self.zdims)
    
    #-------------------------------------------------------------------------
    def Shade(self,ob,degree,**kwargs):
        
        try:
            ob.Shade(self,degree,*kwargs)
        except AttributeError:
            raise Exception("Can't Shade this shit")


    #-------------------------------------------------------------------------
    def Clear(self,reset=False):
        self.selected=MultiShape(name='Selected')
        self.drawpoints=MultiShape(name='Drawing Points')
        self.objects=MultiShape(self.selected,self.drawpoints)
        if reset:
            self.ResetPosition()
        self.xdims=(0,0)
        self.ydims=(0,0)
        self.zdims=(0,0)
        self.Refresh()
    #-------------------------------------------------------------------------
    def Refresh(self):
        self.Draw()
    #-------------------------------------------------------------------------
    def Shift(self,x=0,y=0,z=0,moveto=False,wrap=True):

        v=vector(x,y,z)
        if not moveto:
            self.origin.Shift(*v)
        else:
            c=vector(self.Center())
            v=v-c
            self.origin.Shift(*v)
        if wrap:
            c=self.Center()
            if abs(self.origin[0])>c[0]:
                self.origin.Shift(x=-2*self.origin[0])
            if abs(self.origin[1])>c[1]:
                self.origin.Shift(y=-2*self.origin[1])
        self.Dimensions(True)

    #--
    def Deselect(self,*objects):
        if isinstance(objects[0],str):
            if objects[0].lower()=='all':
                objects=tuple(self.selected)
        readd=[]
        for x in objects:
            self.recurseRemove(x,self.selected)
            tf=False
            for m in x.multishapes:
                tf=True
                m.append(x)
            if tf:
                continue
            readd.append(x)
        self.AddObjects(readd,buffer=False)
    #-------------------------------------------------------------------------
    def Select(self,*objects):

        selobs=self.shapeFlattener.flatten(self.selected)
        objects=self.shapeFlattener.flatten(objects)
        def addprocess(ob):
            nonlocal objects,selobs
            if ob in selobs:
                self.Deselect(ob)
            else:
                self.recurseRemove(ob,self.objects)
                self.selected.append(ob)
                ob.multishapes.pop(-1)
        
        for O in objects:
            if isinstance(O,tk.Event):
                ob=self.find_withtag('current')
                if ob:
                    try:
                        ob=self.objectmap[ob[0]]
                    except:
                        pass
                    else:
                        addprocess(ob)
                else:
                    self.Deselect('all')
            else:
                addprocess(O)
                
    #-------------------------------------------------------------------------
    def SelectGroup(self,*objects):

        flatten=self.shapeFlattener.flatten
        selobs=flatten(self.selected)
        objects=flatten(objects)
        
        def addprocess(ob,objects=objects,selobs=selobs):
            if ob in selobs:
                for gob in self.selected:
                    if gob==ob:
                        self.selected.remove(gob)
##                for m in ob.multishapes:
##                    addprocess(flatten(m))
            else:
                if any(ob.multishapes):
                    for m in ob.multishapes:
                        for ob in flatten(m):
                            self.selected.append(ob)
                else:
                    self.selected.append(ob)
            
        for O in objects:
            if isinstance(O,tk.Event):
                ob=self.find_withtag('current')
                if ob:
                    ob=self.objectmap[ob[0]]
                    addprocess(ob)
                else:
                    self.Deselect('all')
            else:
                addprocess(O)
                
    SelectConnected=SelectGroup
    #-------------------------------------------------------------------------
    def Scale(self,degree,mode='mult'):
        if mode=='add':
            self.scale+=degree
        else:
            self.scale*=degree
        if self.scale<.25:
            self.scale=.25
            
    #-------------------------------------------------------------------------
    def Rotate(self,x=0,y=0,z=0,mode='degree',withbasis=False,moveconnected=False):
        moveflag=moveconnected
        for q,ab in zip((x,y,z),('x','y','z')):
            if q!=0:
                R=LinAlg.RotationMatrix(q,mode=mode,about=ab)
                if not self.selected:
                    obs=self.objects
                else:
                    moveflag=True
                    obs=self.selected
                for shape in obs:
                    shape.MatrixTransformation(R,moveconnected=moveflag)

    #--
    def ArrowAction(self,event,action='rotate'):
        moveFlag=False
        if action=='select':
            pass
        else:
            x=0;y=0;z=0
            arr=event.keysym
            if arr=='Up':
                y+=-self.arrowspeed
            elif arr=='Down':
                y+=self.arrowspeed
            elif arr=='Left':
                x+=self.arrowspeed
            elif arr=='Right':
                x+=-self.arrowspeed
            else:
                return None
            if action=='rotate':
                self.Rotate(-y,x,z,moveconnected=moveFlag)
            elif action=='scale':
                self.Scale(y/5,mode='add')
            elif action=='shift':
                self.Shift(*(q/self.scale for q in (x,y,z)))
            elif action=='drag':
                if self.selected:
                    moveFlag=True
                    obs=self.selected
                else:
                    obs=self.objects
                obs.Shift(*(-q/self.scale for q in (x,y,z)),moveconnected=moveFlag)
    #-------------------------------------------------------------------------
    def LineAction(self,event,action='rotate',rounding=False):

        from math import cos
        moveFlag=True
        if len(self.objects)>20:
            self.shading=False
        
        if len(self.eventpoints)<2:
            p=(event.x,event.y)
            self.eventpoints.append(p)
        elif len(self.eventpoints)==2:
            p1,p2=[vector(p) for p in self.eventpoints]
            v=p1-p2
            if action!='select':
                if action=='rotate':
    ##                l=v.__mag__()
    ##                a1=v.angle(vector(1,0));a2=v.angle(vector(0,1))
    ##                m=max(a1,a2)
                    a2,a1=v
                    if rounding:
                        a2,a1=(round(x,0) for x in (a2,a1))
                    self.Rotate(a1,a2,0,moveconnected=moveFlag)
                elif action=='shift':
                    v*=2
                    v.append(0)
                    v[1]*=-1
                    self.Shift(*v/self.scale)
                elif action=='scale':
                    self.Scale(v[1],mode='add')
                elif action=='drag':
                    u=v;u[0]=-u[0]
                    if self.selected:
                        obs=self.selected
                        moveFlag=True
                    else:
                        obs=self.objects
                    obs.Shift(*(u/self.scale),moveconnected=moveFlag)                
                self.eventpoints=[]
            else:
                if self.selRec:
                    self.selRec.points[1]=self.ClickCoordinates(self.eventpoints.pop(1))
                else:
                    self.selRec=Rectangle(
                        (self.ClickCoordinates(e) for e in self.eventpoints),
                        priority=100,dash=2
                        )
                    self.drawpoints.append(self.selRec)                    
        else:
            self.eventpoints=self.eventpoints[:2]
    #-------------------------------------------------------------------------
    def CurrentCallback(self,event):

        try:
            ob=self.find_withtag('current')[0]
        except IndexError:
            pass
        else:
            ob=self.objectmap[ob]
            ob.callback()
    #-------------------------------------------------------------------------
    def EndAction(self,event):
        self.eventpoints.append((event.x,event.y))
        if self.selRec:
            try:
                self.Delete(self.selRec)
            except ValueError:
                self.selRec=None
            else:
                self.Deselect('all')
                es=self.find_overlapping(*(flatten(self.eventpoints,endtype=list)[:4]))
                for x in es:
                    try:
                        O=self.objectmap[x]
                    except KeyError:
                         continue
                    if not O==self.selRec:
                        self.Select(O)
            self.selRec=None
        self.eventpoints=[]
        self.shading=True
        self.Draw()
    #-------------------------------------------------------------------------
    def Interact(self):
        from .ExtraWidgets import Interactor
        
        Interactor(self)
    #-------------------------------------------------------------------------
    def ResetPosition(self):
        
        self.basis=[vector(v) for v in self.initialbasis]
        self.mat=matrix(self.basis)
        self.inv=self.mat.inverse()
        self.origin=Point(0,0,0)
        self.scale=self.unitscale
        self.Draw()

    #-------------------------------------------------------------------------
    def GroupSelected(self):

        self.GroupShapes('selected')
    #------------------------------------------------------------------------- 
    def GroupShapes(self,*shapes,bound=None):
        
        shapes=list(self.shapeFlattener.flatten(shapes))
        s=shapes[0]
        if s=='all':
            shapes=self.shapeFlattener(self.objects)
        elif s=='selected':
            shapes=self.shapeFlattener(self.selected)
            self.Deselect('all')
            self.Draw()
        shapes=list(shapes)
        M=MultiShape(shapes,parent=self,boundob=bound)
        for shape in shapes:
            if not self.recurseRemove(shape,self.objects):
                print(shape)
                          
        self.AddObjects(M)

    
    #-------------------------------------------------------------------------
    def __iter__(self):

        return iter(self.objects)
