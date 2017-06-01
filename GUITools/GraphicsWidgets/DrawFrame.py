from ..Shared import *
from .CoordinateSpace import CoordinateSpace as CoordinateSpace

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class DrawFrame(CoordinateSpace):

    pointMap={'Shape':(3,-1),'Line':(2,-1),
              'Cylinder':(2,-1),
              'Oval':(2,2),'Circle':(1,1),
              'Sphere':(1,1),'Rectangle':(2,2),
              'Point':(1,1)}
    def __init__(self,root=None,basisvectors=((1,0,0),(0,1,0),(0,0,1)),name=None,**kwargs):
        super(DrawFrame,self).__init__(root,basisvectors=basisvectors,
                                       name=name,**kwargs)
        self.drawob=tk.StringVar()
        def setlam(*args):
            n=self.drawob.get()
            if n in self.pointMap:
                self.pointnum.set(str(self.pointMap[n][0]))
        self.drawob.trace('w',setlam)
        self.drawkwargs=tk.StringVar()
        self.drawargs=tk.StringVar()
        self.pointnum=tk.StringVar()
        self.drawob.set('Point')
        self.editor=None
        self.editpack=True
        self.actionloop.append('drag')
        def keyset(event):
            def rset():
                self.baseaction.set('rotate')
            def sset():
                self.baseaction.set('shift')
            def zset():
                self.baseaction.set('scale')
            def dset():
                self.baseaction.set('drag')
            def cset():
                self.baseaction.set('select')
            if event.keysym in ('r','s','d','z','c'):
                exec('{}set()'.format(event.keysym))
        self.bind('<Control-Key>',lambda e:keyset(e))
        self.bind('<Command-B1-Motion>',self.MakeShape)
        self.bind('<Command-Button-1>',self.MakeShape)
        self.bind('<Command-e>',lambda e:self.ShapeEditor())
        self.bind('<Command-d>',lambda e:self.Clear())
        def selectAll():
            self.Deselect('all')
            self.Select(self.objects)
                    
        self.bind('<Command-a>',lambda e:(selectAll(),self.Draw()))
        self.bind('<BackSpace>',lambda *e:(self.DeleteSelected(),self.Draw()))
        
    #-------------------------------------------------------------------------
    def MakeShape(self,event):

        coords=self.ClickCoordinates(event)
        P=Point(coords,outline='red')
        self.drawpoints.append(P)
        shape=string.capwords(self.drawob.get())
        kwargs=self.drawkwargs.get()
        args=self.drawargs.get()
        N=int(self.pointnum.get())
        if len(self.drawpoints)>=N:
            points=flatten((p.points.column(0) for p in self.drawpoints),
                           conversions={vector:tuple},endtype=tuple)
##            if args and kwargs:
            self.Create(shape,points,args,kwargs)
##            elif args:
##                self.Create(shape,points,args)
##            elif kwargs:
##                self.Create(shape,points,kwargs)
##            else:
##                self.Create(shape,points)
            self.drawpoints.Clear()

            
    #------------------------------------------------------------------------- 
    def DeleteSelected(self):
            
        self.selected.Clear()
        self.Draw()

    #----
    def ExportSelection(self,mode='PosFile'):
        pass
    #----
    def ExportAll(self,mode='PosFile'):
        pass
    #
    def GetDistance(self,shape1,shape2):
        c1,c2=(s.Center() for s in (shape1,shape2))
        v=c2-c1
        return v.magnitude
    #
    def GetAngle(self,shape1,shape2,shape3):
        c1,c2,c3=(s.Center() for s in (shape1,shape2,shape3))
        v1=c2-c1
        v2=c2-c3
        return v1.angle(v2)
    #
    def GetDihedral(self,shape1,shape2,shape3):
        c1,c2,c3,c4=(s.Center() for s in (shape1,shape2,shape3,shape4))
        v1=c2-c1
        v2=c3-c2
        v3=c4-c3
        n1=v1.cross(v2)
        n2=v2.cross(v3)
        return n1.angle(n2)
    #----
    def SetDistance(self,shape1,shape2,newD,fixed=None):
        c1,c2=(s.Center() for s in (shape1,shape2))
        v=c2-c1
        delta=newD-v.mag()
        u=v.normalized()
        if fixed:
            shape2.Shift(*(u*delta))
        else:
            shape2.Shift(*(u*(delta/2)) )
            shape1.Shift(*(u*(-delta/2)))
        shape1.send();shape2.send()
    #----
    def SetAngle(self,shape1,shape2,shape3,newA,fixed=None):
        RotationMatrix=GeneralTools.RotationMatrix
        PointRotation=GeneralTools.PointRotation
        c1,c2,c3=(s.Center() for s in (shape1,shape2,shape3))
        v1=c2-c1
        v2=c2-c3
        n=v1.cross(v2)
        delta=newA-v1.angle(v2)
        if fixed:
            T=PointRotation(c2,delta,about=n)
            shape3.Transform(T)
            c3=shape3.Center()
            v2=c2-c3
            nd=newA-v1.angle(v2)
            if abs(nd)>abs(delta):
                n*=-1
                delta=-nd+delta
                T=PointRotation(c2,delta,about=n)
                shape3.Transform(T)
            shape3.send()
        else:
            T1=PointRotation(c2,-delta/2,about=n)
            T3=PointRotation(c2,delta/2,about=n)
            shape1.Transform(T1)
            shape3.Transform(T3)
            c1=shape1.Center();c3=shape3.Center()
            v1=c2-c1
            v2=c2-c3
            nd=newA-v1.angle(v2)
            if abs(nd)>abs(delta):
                n*=-1
                delta=-nd+delta
                T1=PointRotation(c2,-delta/2,about=n)
                T3=PointRotation(c2,delta/2,about=n)
                shape1.Transform(T1)
                shape3.Transform(T3)
            shape1.send();shape3.send()
    #--
    def SetDihedral(self,shape1,shape2,shape3,shape4,newA,fixed=None):
        RotationMatrix=LinAlg.RotationMatrix
        PointRotation=LinAlg.PointRotation
        c1,c2,c3,c4=(s.Center() for s in (shape1,shape2,shape3,shape4))
        v1=c2-c1
        v2=c3-c2
        v3=c4-c3
        n1=v1.cross(v2)
        n2=v2.cross(v3)
        delta=newA-n1.angle(n2)
        if fixed:
            P=PointRotation(c3,delta,about=v2)
            shape4.Transform(P)
        else:
            P1=PointRotation(c2,-delta/2,about=v2)
            P2=PointRotation(c3,delta/2,about=v2)
            shape1.Transform(P1)
            shape4.Transform(P2)
        shape1.send();shape4.send()

    #
    def CommandChooser(self,root):
        top=tk.Frame(root)
        M=tk.LabelFrame(top,text='Action')
        r=tk.Radiobutton(M,text='Rotate',variable=self.baseaction,value='rotate')
        s=tk.Radiobutton(M,text='Shift',variable=self.baseaction,value='shift')
        d=tk.Radiobutton(M,text='Drag',variable=self.baseaction,value='drag')
        z=tk.Radiobutton(M,text='Zoom',variable=self.baseaction,value='scale')
        c=tk.Radiobutton(M,text='Select',variable=self.baseaction,value='select')
        r.grid(column=0,row=0,sticky='ensw');d.grid(column=1,row=0,sticky='ensw')
        s.grid(column=0,row=1,sticky='ensw');z.grid(column=1,row=1,sticky='ensw')
        c.grid(column=0,row=2,stick='ensw')
        M.grid_columnconfigure(0,weight=1);M.grid_columnconfigure(1,weight=1)
        M.pack(fill='x')
        return (top,M,r,s,d,c)
    #
    def ShapeChooser(self,root):
        top=tk.Frame(root)
        n=tk.LabelFrame(top,text='Number of Points')
        s=tk.LabelFrame(top,text='Shape')
        a=tk.LabelFrame(top,text='Arguments')
        k=tk.LabelFrame(top,text='Key Word Arguments')
        n.pack();s.pack();a.pack();k.pack()
        def vallam(P):
            dtup=self.pointMap[self.drawob.get()]
            try:
                i=int(P)
            except:
                return P==''
            else:
                c1=i>=dtup[0]
                c2=(dtup[1]<0 or i<=dtup[1])
                return (c1 and c2)
        vc=self.register(vallam)
        nentry=tk.Entry(n,textvar=self.pointnum,
                        validatecommand=(vc,'%P'),
                        validate='key')
        sentry=tk.Entry(s,textvar=self.drawob)
        args=tk.Entry(a,textvar=self.drawargs)
        kwargs=tk.Entry(k,textvar=self.drawkwargs)
        nentry.pack()
        sentry.pack()
        args.pack()
        kwargs.pack()
        top.grid(row=0,column=1,sticky='n')
        return (top,n,s,a,k)
    #
    def Operator(self,root):
        #Allow choice of rotation/shift/dihedral setting/whatever
        pass
    
    #-------------------------------------------------------------------------           
    def ShapeEditor(self):

        if not self.editpack:
            root=tk.Toplevel()
            root.title('Draw Editor')
        else:
            root=self.master
        if self.editor:
            if self.editpack:
                self.editor.grid_forget()
            else:
                self.editor.master.destroy()
            self.editor=None
            return
        self.editor=top=tk.Frame(root)
        def pop():
            if self.editpack:
                self.editor.grid_forget()
                self.editpack=False
            else:
                self.editor.master.destroy()
                self.editpack=True
            self.editor=None
            self.after_idle(lambda*e:self.after(100,lambda*e:self.ShapeEditor()))
        coms=self.CommandChooser(self.editor)
        shapes=self.ShapeChooser(self.editor)
        for x in coms+shapes:
            x.bind('<Double-Button-1>',lambda*e:pop())
        coms[0].pack()
        shapes[0].pack()
        self.editor.grid(row=0,column=1,sticky='n')
