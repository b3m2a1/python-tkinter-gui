from .Shared import *

#WRITE MORE EFFICIENT MATRIX WRAPPER AND USE THAT

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class RichCanvas(tk.Canvas):

    type_tags={'window':'canvas_window_object',
               'image':'canvas_image_object',
               'text':'canvas_text_object',
               'polygon':'canvas_polygon_object',
               'rectangle':'canvas_rectangle_object',
               'oval':'canvas_oval_object',
               'arc':'canvas_arc_object'
               }
    from time import time,sleep
    named_colors=('red','orange','yellow','green','blue','blue4','violet')
##    ColorOperator=
    
    def __init__(self,*args,name=None,**kwargs):
        self.color_ops=TkColorOperations(self)
        from GUITools.ExtraWidgets import Interactor
        self.Interactor=Interactor
        super().__init__(*args,**kwargs)
        self.bind('<Command-i>',lambda e:Interactor(self))
        
        if name is None:
            name=type(self).__name__
        self.name=name

    #-------------------------------------------------------------------------                  
    def Center(self):
        
        return (self.winfo_width()/2,self.winfo_height()/2)
    
    @property
    def window_dimensions(self):
        return (self.winfo_width(),self.winfo_height())
    @property
    def canvas_window(self):
        w,h=self.window_dimensions
        return (self.canvasx(0),self.canvasy(0),self.canvasx(w),self.canvasy(h))
    @property   
    def scroll_region(self):
        s=self['scrollregion']
        if s=='':
            s=('inf','inf','inf','inf')
        return s

    @scroll_region.setter
    def scroll_region(self,tup):
        crds=[None]*4
        for i in range(len(tup)):
            v=tup[i]
            try:
                which,num=v
            except TypeError:
                crds[i]=v
            else:
                if which in ('x','xmin'):
                    crds[0]=num
                elif which in ('y','ymin'):
                    crds[1]=num
                elif which in ('X','xmax'):
                    crds[2]=num
                elif which in ('Y','ymax'):
                    crds[3]=num
                else:
                    raise TypeError('canvas_dimensions.set: unknown dimension spec {}'.format(which))
        self.set_scroll(*crds)

    def set_scroll(self,xmin=None,ymin=None,xmax=None,ymax=None):
        x,y,X,Y=s=self.scroll_region
        if s==('inf','inf','inf','inf'):
            X=Y=pow(10,6)
            x=y=-X
        if not xmin is None:
            x=xmin
        if not ymin is None:
            y=ymin
        if not xmax is None:
            X=xmax
        if not ymax is None:
            Y=ymax
        self['scrollregion']=(x,y,X,Y)
    #--
    def WindowDimensions(self):

        return self.window_dimensions
    
    def frame_distances(self,obj):
        x,y,X,Y=self.bbox(obj)
        cx,cy,cX,cY=self.canvas_window
##        sx,sy,sX,sY=self.canvas_dimensions
        intersections=[cx-x,cy-y,X-cX,Y-cY]
##        if x<0:
##            intersections.append('left')
##        if y<0:
##            intersections.append('top')
##        if X>w:
##            intersections.append('right')
##        if Y>h:
##            intersections.append('bottom')
        return intersections

    def find_type(self,t):
        return self.find_withtag(self.type_tags[t])
    
    def hide(self,obj):
        self.itemconfig(obj,state='hidden')
    def hide_type(self,obj_type):
        self.hide(self.type_tags[obj_type])
            
    def unhide(self,obj,state='normal'):
        self.itemconfig(obj,state=state)
    def unhide_type(self,obj_type,state='normal'):
        self.unhide(self.type_tags[obj_type])
        
    def move(self,obj,x,y,mode='standard',repeats=1,pause=50):
        if mode=='frac':
            w,h=self.window_dimensions
            x=int(w*x)
            y=int(h*y)
        if not isinstance(obj,(int,str)):
            sup=super()
            for r in range(repeats,0,-1):
                for o in obj:
                    sup.move(o,x,y)
                if not r==1:
                    self.hold_update(pause)
        else:
            for r in range(repeats,0,-1):
                super().move(obj,x,y)
                if not r==1:
                    self.hold_update(pause)

    def displacements(self,obj1,obj2,mode='bbox'):
        
        if isinstance(obj1,(str,int)):
            if mode=='anchor':
                crds=self.coords(obj1)
                if len(crds)==2:
                    x,y=crds
                else:
                    ax1,ay1,ax2,ay2=self.bbox(obj1)
                    x=(ax1+ax2)/2;y=(ay1+ay2)/2
                ax1,ay1,ax2,ay2=(x,y,x,y)
            else:
                ax1,ay1,ax2,ay2=self.bbox(obj1)
        else:
            l=tuple(obj1)
            if len(l)>2:
                ax1,ay1,ax2,ay2=l
            else:
                x,y=l
                ax1,ay1,ax2,ay2=(x,y,x,y)
                
        if isinstance(obj2,(str,int)):
            if mode=='anchor':
                crds=self.coords(obj2)
                if len(crds)==2:
                    x,y=crds
                else:
                    bx1,by1,bx2,by2=self.bbox(obj2)
                    x=(bx1+bx2)/2;y=(by1+by2)/2
                bx1,by1,bx2,by2=(x,y,x,y)
            else:
                bx1,by1,bx2,by2=self.bbox(obj2)
        else:
            l=tuple(obj2)
            if len(l)>2:
                bx1,by1,bx2,by2=l
            else:
                x,y=l
                bx1,by1,bx2,by2=(x,y,x,y)

        if ax2<bx1:
            x_d=bx1-ax2
        elif ax1>bx2:
            x_d=bx2-ax1
        else:
            x_d=0
            
        if ay2<by1:
            y_d=by1-ay2
        elif ay1>by2:
            y_d=by2-ay1
        else:
            y_d=0

        return (x_d,y_d)

    def distance(self,obj1,obj2):
        x,y=self.displacements(obj1,obj2)
        return math.sqrt(x**2+y**2)

##    def center(self,obj):
##        pass
    
    def coords(self,obj,*crds,x=None,y=None,mode='standard'):
        if crds==() and (x is None or y is None):
            if not isinstance(obj,(int,str)):
                sup=super()
                return [sup.coords(o) for o in obj]
            else:
                return super().coords(obj)
        else:
            if crds==():
                crds=(x,y)
            if mode=='frac':
                w,h=self.window_dimensions
                crds=[w*p if i%2==0 else h*p for p,i in zip(crds,range(len(crds)))]
            if not isinstance(obj,(int,str)):
                sup=super()
                return [sup.coords(o,*crds) for o in obj]
            else:
                return super().coords(obj,*crds)
    def frac_coords(self,*crds):
        if not isinstance(crds[0],int):
            crds=crds[0]
        w,h=self.window_dimensions
        ret=tuple((r/w if i%2==0 else r/h for r,i in zip(crds,range(len(crds)))))
        return ret
    def abs_coords(self,*crds):
        if not isinstance(crds[0],(int,float)):
            crds=crds[0]
        w,h=self.window_dimensions
        ret=tuple((int(r*w if i%2==0 else r*h) for r,i in zip(crds,range(len(crds)))))
        return ret
            
        
    def removed_bbox(self,*obj,mode='standard'):
        if len(obj)!=1:
            bbox=super().bbox(*obj)
        else:
            t=self.type(obj)
            if t in ('window','image','bitmap'):
                w=self.itemcget(obj,t)
                x,y=self.coords(obj)
                anchor=self.itemcget(obj,'anchor')
                if t=='window':
                    w=self.nametowidget(w)
                    h=self.winfo_height(w)
                    w=self.winfo_width(w)
                else:
                    w=w.width
                    h=w.height

                if anchor=='center':
                    w_even=w%2==0
                    x1=x - w//2
                    x2=x + w//2 + 1 if not w_even else 0
                    h_even=h%2==0
                    y1=y - h//2
                    y2=y + h//2 + 1 if not h_even else 0                   
                    
                else:
                    if 'n' in anchor:
                        y1=y
                        y2=y+h
                    elif 's' in anchor:
                        y1=y-h
                        y2=h
                    if 'w' in anchor:
                        x1=x
                        x2=x+w
                    elif 'e' in anchor:
                        x1=x-w
                        x2=x+w

                bbox=(x1,y1,x2,y2)
                
                    
            else:
                bbox=super().bbox(t)

        if mode=='frac':
            pass

        return bbox

    def hold_update(self,pause=50,minimum=25,force_pause=True):
        '''Holds for pause milliseconds after calling update_idletasks'''
        
        self.update_idletasks()
        if pause > 0:
            if force_pause:
                self.sleep(pause/1000)
            else:
                self.pause(pause,minimum)

    def after_update(self,pause,task):
        t=self.time()
        self.pause(pause)
        self.sleep(pause/1000)
        task()
        t2=self.time()
##        print(round(pause-(t2-t),3))
        self.hold_update(5)
        
    def pause(self,pause,minimum=25):
        hold_var=tk.BooleanVar(value=True)
##        self.sleep(.001)
##        _hold_flag=tk.BooleanVar(value=False)
        if not callable(pause):
            pause=max(pause,minimum)
            self.after(pause,lambda:hold_var.set(False))
        else:
            #just use an internal time
            def pause_call(self=self,p=pause,m=minimum):
                t1=self.time()
                p()
                t2=self.time()
                d=max(5,int(m-(t2-t1)))
                self.after(d,lambda:hold_var.set(False))
##            def flag_set(pause=pause,minimum=minimum,wait=hold_var):
##                v1=tk.BooleanVar(value=False)
##                v2=tk.BooleanVar(value=False)
##                self.after(minimum,lambda:v1.set(True))
##                self.after(100,lambda:(pause(),v2.set(True)))
##                if not v1.get():
##                    self.wait_variable(v1)
##                if not v2.get():
##                    self.wait_variable(v2)
##                wait.set(False)
            self.after(5,pause_call)
        if hold_var.get():
            self.wait_variable(hold_var)
        
    def rgb2hex(self,*color_tuple):
        return self.color_ops.rgb2hex(*color_tuple)
    def name2rgb(self,name):
        return self.color_ops.name2rgb(name)
    def rgb_hex(self,rgb_id):
        return self.color_ops.rgb_hex(rgb_id)
    def rgb_tuple(self,rgb_id):
        return self.color_ops.rgb_tuple(rgb_id)
    def rgb_lighter(self,color_tuple,decimal_percentage):
        return self.color_ops.rgb_lighter(color_tuple,decimal_percentage)
    def rgb_darker(self,color_tuple,decimal_percentage):
        return self.color_ops.rgb_darker(color_tuple,decimal_percentage)
    def rgb_fade(self,color1,color2,decimal_percentage):
        return self.color_ops.rgb_fade(color1,color2,decimal_percentage)
    def increase_contrast(self,color,decimal_percentage):
        return self.color_ops.increase_contrast(color,decimal_percentage)
    def invert_color(self,color):
        return self.color_ops.invert_color(color)
    def tint_color(self,color,r,g,b):
        return self.color_ops.tint_color(color,r,g,b)

    def random_position(self):
        from random import choice
        w,h=self.canvas_window
        w_range=range(w);h_range=range(h)
        w1=choice(w_range);w1=choice(h_range)
        return (w1,h1)
    
    def random_box(self,pos=None,mode='coord'):
        from random import choice
        x=None;y=None
        if not pos is None:
            x,y=pos
        w,h=self.window_dimensions
        if mode=='frac':
            if x is not None:
                x=w*x
            if y is not None:
                y=h*y
        
        
        if x is None:
            w_range=range(w);
            w1=choice(w_range)
            w2=choice(w_range)
            wm=min(w1,w2);wM=max(w1,w2)
            
        else:
            r=choice(range(round(min(x,w-x))))
            wm=x-r
            wM=x+r
        
        
        if y is None:
            h_range=range(h)
            h1=choice(h_range)
            h2=choice(h_range)
            hm=min(h1,h2);hM=max(h1,h2)
        else:
            r=choice(range(round(min(y,h-y))))
            hm=y-r
            hM=y+r
        
        return (wm,hm,wM,hM)

    def random_color(self,mode='names'):
        from random import choice
        if mode=='names':
            color=choice(self.named_colors)
        else:
            R=range(256)
            color=[choice(R) for i in range(3)]
            
        return color
    
    def make_random(self,obj='oval',pos=None,num=1,pos_mode='coord'):
        
        if isinstance(obj,tk.Event):
            pos=(obj.x,obj.y)
            obj="oval"
            
        def rand_proc():
            color=self.random_color()
            box=self.random_box(pos=pos,mode=pos_mode)
            method=getattr(self,'create_'+obj)
            return method(*box,fill=color)
        return [rand_proc() for i in range(num)]
    #--------------------------------------------------------------------------
    def create_oval(self,x1,y1,x2,y2,mode='coords',make_polygon=False,**kwargs):
        if mode=='frac':
            w,h=self.window_dimensions
            x1=round(w*x1);x2=round(w*x2)
            y1=round(h*y1);y2=round(h*y2)
        ret=None
        if make_polygon:
            ret=super().create_polygon(*self.calculate_polygon(x1,y1,x2,y2,'oval'),**kwargs)
        else:
            ret=super().create_oval(x1,y1,x2,y2,**kwargs)
        self.addtag_withtag(self.type_tags['oval'],ret)
        return ret
        
    def create_rectangle(self,x1,y1,x2,y2,mode='coords',make_polygon=False,**kwargs):
        if mode=='frac':
            w,h=self.window_dimensions
            x1=round(w*x1);x2=round(w*x2)
            y1=round(h*y1);y2=round(h*y2)
        ret=None
        if make_polygon:
            ret=super().create_polygon(*self.calculate_polygon(x1,y1,x2,y2,'rectangle'),**kwargs)
        else:
            ret=super().create_rectangle(x1,y1,x2,y2,**kwargs)
        self.addtag_withtag(self.type_tags['rectangle'],ret)
        return ret
        
    def create_polygon(self,*points,mode='coords',**kwargs):
        if mode=='frac':
            w,h=self.window_dimensions
            points=(round(w*p) if i%2==0 else round(h*p) for p,i in zip(points,range(len(points))))
        super().create_polygon(*points,**kwargs)
        self.addtag_withtag(self.type_tags['window'],o)
        return o

    def create_window(self,x,y,mode='coords',**kwargs):
        if mode=='frac':
            w,h=self.window_dimensions
            x=round(w*x);y=round(h*y)
        o=super().create_window(x,y,**kwargs)
        self.addtag_withtag(self.type_tags['window'],o)
        return o

    def create_image(self,x,y,mode='coords',**kwargs):
        if mode=='frac':
            w,h=self.window_dimensions
            x=round(w*x);y=round(h*y)
        
        o=super().create_image(x,y,**kwargs)
        self.addtag_withtag(self.type_tags['image'],o)
        return o
    
    #-------------------------------------------------------------------------
    def create_circle(self,x,y,r,**kwargs):
        return self.create_oval(
            x-r,y-r,x+r,y+r,**kwargs
            )
    #
    def create_square(self,x,y,l,**kwargs):
        return self.create_rectangle(x,y,x+l,y+l,**kwargs)
    #-------------------------------------------------------------------------
    def create_sphere(self,x,y,r,**kwargs):
        spherenum=100
        half=spherenum//2
        if 'fill' in kwargs:
            basefill=kwargs['fill']
            del kwargs['fill']
        else:
            basefill='black'
        if 'outline' in kwargs:
            outline=kwargs['outline']
            del kwargs['outline']
        else:
            outline=basefill
        rgb=[int((n/256)//1) for n in self.winfo_rgb(basefill)]
        shifts=[255-c for c in rgb]
        try:
            ret=[self.create_circle(x,y,r,fill=basefill,width=2,outline=outline)]
        except:
            ret=[RichCanvas.create_circle(self,x,y,r,fill=basefill,width=2,outline=outline)]
        for i in range(1,spherenum):
            scale=i*1/spherenum
            newrgb=[min(255,int((rgb[j]+scale*shifts[j])//1))
                            for j in range(3)]
            keys=[hex(s) for s in newrgb]
            keys=[k[1+k.index('x'):] for k in keys]
            keys=['0'+k if len(k)==1 else k for k in keys]
            c='#{}'.format(''.join(keys))
            shift=r*scale
            pshift=shift/3
            try:
                ret.append(self.create_circle(
                    x-pshift,y-pshift,r-shift,fill=c,outline=c,**kwargs
                    ))
            except:
                ret.append(RichCanvas.create_circle(self,
                    x-pshift,y-pshift,r-shift,fill=c,outline=c,**kwargs
                    ))
        return ret
    #-------------------------------------------------------------------------
    def create_sad_sphere(self,x,y,r,**kwargs):
        p1=(x-r//2,y-.96*r);p3=(x-.96*r,y)
        p2=(x,y+.95*r);p4=(x+.95*r,y+r//2)
        ob=self.create_circle(x,y,r,**kwargs)
        self.create_arc(*(p1+p2),style='arc',start=90,extent=180)
        self.create_arc(*(p3+p4),style='arc',start=180,extent=180)
        return ob
    #
    def calculate_polygon(self,x1,y1,x2,y2,obj_type,points_used=40):
        points=None
        if obj_type=='rectangle':
            side_points=round(points_used/4)
            w_spread=(x2-x1)/max((side_points-1),1)
            w_points=[x1+i*w_spread for i in range(side_points)]
            h_spread=(y2-y1)/max((side_points-1),1)
            h_points=[y1+i*h_spread for i in range(side_points)]
            zip1=tuple(zip(w_points,(y1,)*len(w_points)));
            zip2=tuple(zip((x2,)*len(h_points),h_points))
            w_points.reverse()
            h_points.reverse()
            zip3=zip(w_points,(y2,)*len(w_points))
            zip4=zip((x1,)*len(h_points),h_points)
            points=[v for l in (zip1,zip2,zip3,zip4) for p in l for v in p]
            
        return points
                    
    def __getitem__(self,propORpair):
        if isinstance(propORpair,str):
            return super().__getitem__(propORpair)
        else:
            x,t=propORpair
            return self.itemcget(x,t)
    def __setitem__(self,propORpair,val):
        if isinstance(propORpair,str):
            return super().__setitem__(propORpair,val)
        else:
            x,t=propORpair
            return self.itemconfig(x,{t:val})
