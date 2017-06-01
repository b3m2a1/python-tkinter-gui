from ..Shared import *
from .RichCanvas import RichCanvas as RichCanvas

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Canvas3D(RichCanvas):

    flattener=LinAlg.Flattener()
    flatten=flattener.flatten
    pointFlattener=LinAlg.Flattener(endtype=list,conversions={tuple:list},frombottom=1)
    log=[]    
    def __init__(self,root=None,basisvectors=((1,0,0),(0,1,0),(0,0,1)),name=None,
                 unitscaling=1,xaxisrotation=5,zaxisrotation=65,yaxisrotation=0,**kwargs):
        super().__init__(root,**kwargs)
        self.zrotation=zaxisrotation
        self.xrotation=xaxisrotation
        self.yrotation=yaxisrotation
        zaxisrotation*=math.pi/180
        xaxisrotation*=math.pi/180
        yaxisrotation*=math.pi/180
        self.xcos=math.cos(xaxisrotation)
        self.xsin=math.sin(xaxisrotation)
        self.ycos=math.cos(yaxisrotation)
        self.ysin=math.sin(yaxisrotation)
        self.zcos=math.cos(zaxisrotation)
        self.zsin=math.sin(zaxisrotation)
        if not name:
            name=type(self).__name__
        self.name=name
        self.scale=unitscaling
        self.basis=matrix(basisvectors)
        self.unitscale=unitscaling
        self.origin=Point(0,0,0)
        self.initialbasis=tuple((vector(v) for v in self.basis))
        self.mat=matrix(self.basis,mode='row')
        self.inv=self.mat.inverse()
        self.shading=True
        
    #-------------------------------------------------------------------------
    def CoordinateTransfer(self,points,toOrtho=True):

        TM=self.inv
        if not toOrtho:
            TM=self.mat
        try:
            newp=TM*points
        except TypeError:
            m=matrix(points)
            newp=TM*m
        return newp
    #-------------------------------------------------------------------------
    def CanvasCoordinates(self,*points,unscaled=False):
        if unscaled:
            scale=1
        else:
            scale=self.scale
        points=matrix(points)
        ps=[]
        zc=self.zcos;zs=self.zsin;xc=self.xcos
        xs=self.xsin;yc=self.ycos;ys=self.ysin
        cx,cy=self.Center()
        origin=vector(self.origin,orientation='col')
        for point in self.CoordinateTransfer(points):
            x,y,z=point-origin
            ps.append((
                (x*xc-z*zs+y*ys)*scale+cx,(z*zc+x*xs-y*yc)*scale+cy
                ))
##            ps.append(((x+self.origin[0]-(z/2-self.origin[2]))*scale+cx,
##                  (-y-self.origin[1]+(z/2-self.origin[2]))*scale+cy))
        return ps
    #-------------------------------------------------------------------------
    def ClickCoordinates(self,event,z=0):
        try:
            x,y=(event.x,event.y)
        except:
            x,y=event
        xs,ys=self.flatten(self.CanvasCoordinates((0,0,0)))
        x=(x-xs)/self.scale
        y=(-(y-ys))/self.scale
        ps=vector(self.CoordinateTransfer((x,y,z),toOrtho=False))
        return ps
    #-------------------------------------------------------------------------
    def DrawablePoints(self,*points,unscaled=False):
        try:
            i=iter(points[0])
            ps=self.CanvasCoordinates(points,unscaled=unscaled)
        except TypeError:
            points=list(points)
            p=len(points)
            while not p%3==0:
                points.append(0)
                p+=1
            ps=self.CanvasCoordinates([points[3*i:3*(i+1)] for i in range(p//3)],unscaled=unscaled)
        return ps
    #--------
    def RotateAxes(self,x=0,y=0,z=0,to=False):
        if x!=0:
            self.xrotation+=x
            xaxisrotation=self.xrotation*math.pi/180
            self.xcos=math.cos(xaxisrotation)
            self.xsin=math.sin(xaxisrotation)
        if y!=0:
            self.yrotation+=y
            yaxisrotation=self.yrotation*math.pi/180
            self.ycos=math.cos(yaxisrotation)
            self.ysin=math.sin(yaxisrotation)
        if z!=0:
            self.zrotation+=z
            zaxisrotation=self.zrotation*math.pi/180
            self.zcos=math.cos(zaxisrotation)
            self.zsin=math.sin(zaxisrotation)
        
    #-------------------------------------------------------------------------
    def create_text(self,*point,unscaled=False,**kwargs):
        
        if 'font' in kwargs:
            tup=kwargs['font']
            try:
                f,s=tup
                tup=(f,int(s*self.scale/self.unitscale))
            except:
                tup=(f,int(12*self.scale/self.unitscale))
            kwargs['font']=tup
        else:
            kwargs['font']=('Purissa',int(12*self.scale/self.unitscale))
        point=self.pointFlattener.flatten(point)
        for x in point:
            while len(x)<3:
                x.append(0)
        p1,p2=flatten(self.CanvasCoordinates(point,unscaled=unscaled))
        return super().create_text(p1,p2,**kwargs)
    #-------------------------------------------------------------------------
    def create_line(self,*points,unscaled=False,**kwargs):
        points=self.pointFlattener.flatten(points)
        try:
            float(points[0])
            pset=matrix(points[i*3:(i+1)*3] for i in range(1+len(points)//3))
            pset.append([0]*len(pset)%3)                
            argpoints=self.CanvasCoordinates(pset,unscaled=unscaled)
        except (ValueError,TypeError):
            argpoints=self.CanvasCoordinates(points,unscaled=unscaled)
            
        obtype='line'
        args=(p for x in argpoints for p in x)
        return super().create_line(*args,**kwargs)
    #-------------------------------------------------------------------------
    def create_rectangle(self,*points,unscaled=False,**kwargs):
        points=self.pointFlattener.flatten(points)
        
        if len(points)==2:
            p1,p2=(points[0],points[1])
        elif len(points)==4:
            p1,p2,p3,p4=points
            p1,p2=((p1,p2,0),(p3,p4,0))
        elif len(points)==6:
            p1,p2=(points[:3],points[3:6])
        else:
            raise Exception("couldn't draw rectangle from points: {}".format(points))
        p1,p2=self.CanvasCoordinates(p1,p2,unscaled=unscaled)
        obtype='rectangle'
        args=(x for x in p1+p2)
        return super().create_rectangle(*args,**kwargs)
    #-------------------------------------------------------------------------
    def create_oval(self,*points,unscaled=False,**kwargs):
        points=self.pointFlattener.flatten(points)
        ps=self.DrawablePoints(*points,unscaled=unscaled)
        p1,p2=ps[:2]
        obtype='oval'
        args=(x for x in p1+p2)
        return super().create_oval(*args,**kwargs)
    #-------------------------------------------------------------------------
    def create_polygon(self,*points,unscaled=False,**kwargs):
        points=self.pointFlattener.flatten(points)
        try:
            float(points[0])
            pset=[points[i*3:(i+1)*3] for i in range(1+len(points)//3)]
            pset.append([0]*len(pset)%3)                
            argpoints=self.CanvasCoordinates(pset,unscaled=unscaled)
        except:
            argpoints=self.CanvasCoordinates(points,unscaled=unscaled)
        obtype='polygon'
        args=(p for x in argpoints for p in x)
        return super().create_polygon(*args,**kwargs)
    #-------------------------------------------------------------------------
    def create_circle(self,*pointsandrad,unscaled=False,**kwargs):
        pointsandrad=self.pointFlattener.flatten(pointsandrad)
        radius=self.scale*pointsandrad.pop(-1)
        points=pointsandrad
        ps=self.DrawablePoints(*points,unscaled=unscaled)
        p=ps[0]
        p1=map(lambda a:a-radius,p)
        p2=map(lambda a:a+radius,p)
        args=flatten((p1,p2))
        return super().create_oval(*args,**kwargs)
    #---
    def create_window(self,*points,**kwargs):
        points=self.DrawablePoints(self.pointFlattener.flatten(points),unscaled=unscaled)
        points=points[0][:2]
        return super().create_window(*points,**kwargs)
    #--
    def create_sphere(self,*pointsandrad,unscaled=False,**kwargs):
        pointsandrad=self.pointFlattener.flatten(pointsandrad)
        radius=self.scale*pointsandrad.pop(-1)
        points=self.DrawablePoints(pointsandrad,unscaled=unscaled)
        points=list(points[0][:2])
        points.append(radius)
        obtype='sphere'
        return super().create_sphere(*points,**kwargs)
    #--
    def create_cylinder(self,*points,unscaled=False,**kwargs):
        try:
            kwargs['width']=int(kwargs['width']*self.scale)
        except:
            kwargs['width']=1
        kwargs['capstyle']='round'
        points=self.flatten(self.DrawablePoints(points,unscaled=unscaled))
        return super().create_line(*points,**kwargs)
    #--
    def create_image(self,*points,unscaled=False,**kwargs):
        if 'image' in kwargs:
            im=kwargs['image']
            ps=self.DrawablePoints(self.pointFlattener(points),unscaled=unscaled)
            i=iter(ps)
            x,y=next(i)
            MX=mx=x
            MY=my=y
            for x,y in i:
                 MX=max(x,MX)
                 mx=min(x,mx)
                 MY=max(y,MY)
                 my=min(y,my)
            w=MX-mx
            h=MY-my
            im.resize(w,h)
            self.log.append((mx,my,MX,MY))
            return super().create_image(mx,my,anchor='nw',image=im.draw)
