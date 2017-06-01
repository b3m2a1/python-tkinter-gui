
from collections import deque
from ..RichCanvas import *
from ...ImageTools import ImageWrapper as ImageWrapper
from ...SharedData.ImageFiles import AnimationImages

from queue import Queue

class AnimationFrame(RichCanvas):
    """A RichCanvas that supports animation usage.
Uses an animation stack to queue multiple animations and provide synchronicity.
Stores arguments to be passed to animations."""
    
    horizontal=(1,0)
    vertical=(0,1)
    Rotation=GeneralTools.PointRotation
    animation_source=os.path.join(os.path.dirname(__file__),'Animations')
    
    def __init__(self,*RichCanvas_args,animation_source=None,image_source=None,**RichCanvas_kwargs):
        super().__init__(*RichCanvas_args,**RichCanvas_kwargs)
        if animation_source is None:
            animation_source=self.animation_source
        self.source=animation_source
        self.image_source=image_source
        self.color_hold={};self.color_hold_temp={}
        self.image_hooks={}
        self.held_animations=[]
        self.bg_stack=deque(())
        self.bg=self['bg']
        self.last_made=None

    def prep_animations(self,*animations,args=None):
        """Adds *animations to the animation queue"""
        for animation in animations:
            if not args is None:
                animation.pass_obs=args
            self.held_animations.append(animation)
            animation.prep_queue()
        
    #---------------------------------------------------
    def call(self,animation,prep=True,args=None):
        """Calls an animation by iterating through its queue"""
        if prep:
            animation.prep_queue()
        if not args is None:
            animation.pass_obs=args
        for x in iter(lambda:animation.queue.get(0),'end'):
            self.hold_update(lambda:animation.evaluate(x),animation.step_rate)

    def call_animations(self,mode='ordered'):
        """Exhausts the held animation queue"""
        mode=mode.lower()
        if mode in ('o','ordered'):
            for x in self.held_animations:
                self.call(x,prep=False)
        elif mode in ('s','synchronous'):
            iters=[]
            r=0
            for a in self.held_animations:
                iters.append(iter(lambda a=a:a.queue.get(0),'end'))
                r=max(r,a.step_rate)
##            print(r)
            def step():
                do=[]
                remove=[]
                z=zip(iters,self.held_animations)
                for i,a in z:
                    try:
                        f=next(i)
                    except StopIteration:
                        remove.append((i,a))
##                        iters.remove(i)
##                        self.held_animations.remove(a)
                    else:
                        do.append((f,a))
                for i,a, in remove:
                    iters.remove(i)
                    self.held_animations.remove(a)
                if not do:
                    do='end'
                return do

            for do in iter(step,'end'):
                for f,a in do:
                    a.evaluate(f)
                self.hold_update(r)                   
                
        else:
            wait=0
            iters=[iter(lambda x=x:x.queue.get(0),'end') for x in self.held_animations]
            l=0
            init=[]
            to_remove=[]
            for x in iters:
                try:
                    f=next(x)
                except StopIteration:
                    to_remove.append((x,self.held_animations[l]))
                else:
                    init.append((f,self.held_animations[l]))
                l+=1
            for i,a in to_remove:
                iters.remove(i)
                self.held_animations.remove(a)
                
            for f,x in init:
                x.evaluate(f)
                
            while iters:
                for i in range(len(iters)):
                    it=iters[i]
                    try:
                        f=next(it)
                    except StopIteration:
                        iters.remove(it)
                        self.held_animations.pop(i)
                    else:
                        x=self.held_animations[i]
                        def call(x=x,f=f):
                            rate=x.step_rate
##                            print(rate)
                            self.after_update(rate,
                                    lambda x=x,f=f:x.evaluate(f)
                                              )
                        
                        self.after(wait,call)
        self.held_animations=[]

    @property               
    def canvas_windows(self):
        """Returns the widget objects on the animation canvas"""
        windows={}
        
        for x in self.find_type('window'):
            try:
                w=self.nametowidget(self[x,'window'])
            except:
                continue
            windows[x]=w
        return windows
            
    #----------------------------------------------------
    def delete(self,ob):
        """Removes an object from the canvas"""
        if ob=='all':
            self.color_hold={}
            self.image_hooks={}
            super().delete(ob)
        else:
            sup=super()
            def del_act(obj):
                if obj in self.image_hooks:
                    del self.image_hooks[obj]
                del self.color_hold[obj]
                sup.delete(obj)
                
            if not isinstance(ob,(str,int)):
                for o in ob:
                    del_act(o)
            else:
                del_act(ob)
            
    def delete_last(self,ago=0):
        """Deletes the last object added to the canvas and resets the tracker"""
        n=self.last_made
        self.delete(n-ago)
        if ago==0:
            self.last_made+=-1

#### MOVEMENT COMMANDS
            
    def reframe(self,obj_id,padx=3,pady=3):
        """Forces an object back within the bounds of the canvas"""
        x,y,X,Y=self.frame_distances(obj_id)
        if x<0:
            x=0
        if y<0:
            y=0
        if x or y:
            self.move(obj_id,x+padx,y+pady)
        else:
            if X>0:
                X=0
            if Y>0:
                Y=0
            self.move(obj_id,-X-padx,Y-pady)

    def anchor(self,obj_id,side='top',padx=3,pady=3):
        """Attaches an object to the specified side of the canvas.
Currently not functional."""
        raise NotImplemented
        x,y,X,Y=self.bbox(obj_id)
        cx,cy,CX,CY=self.canvas_window
        if side=='left':
            self.move
            
    def move_last(self,ago=0,x=0,y=0,repeats=1,pause=50):
        """Moves the last object added to the canvas"""
        n=self.last_made
        self.move(n-ago,x,y,repeats=repeats,pause=pause)

    def slide_to(self,obj1,obj2,steps=5,
                 slide_x=True,slide_y=True,
                 slide_by='bbox',step_rate=100,
                 mode='standard',generator=False):
        if mode=='frac':
            w,h=self.window_dimensions
            if not isinstance(obj2,(str,int)):
                crds=len(obj2)
                w,h=self.window_dimensions
                if len(obj2)==2:
                    x,y=obj2
                    x=x*w;y=y*h
                    obj2=(x,y)
                else:
                    x1,y1,x2,y2=obj2
                    x1*=w;x2*=w;y1*=h;y2*=h
                    obj2=(x1,y1,x2,y2)
            else:
                mode='standard'
        x_d,y_d=self.displacements(obj1,obj2,mode=slide_by)
        if mode=='frac':
            x_d*=1/w;y_d*=1/h
        x_step=x_d/steps;y_step=y_d/steps
        if mode!='frac':
            x_step//1;y_step//1
        if not slide_x:
            x_step=0
        if not slide_y:
            y_step=0            
        def slide_gen(self=self,obj1=obj1,x_step=x_step,y_step=y_step,
                      step_rate=step_rate):
            for s in range(steps):
                self.move(obj1,x_step,y_step,mode=mode)
                if generator:
                    yield step_rate
                else:
                    self.hold_update(step_rate)
        if generator:
            return slide_gen()
        else:
            list(slide_gen())
    
    def shake(self,quantity=50,shake_vector=None,bounces=1,step_q=1,end_pause=0,end_call=lambda self:None):
        """Shakes every object on the canvas"""
        self.shake_obs('all',quantity=quantity,shake_vector=shake_vector,
                       bounces=bounces,step_q=step_q,end_pause=end_pause,end_call=end_call)

    def shake_obs(self,*obs,quantity=50,shake_vector=None,bounces=1,step_q=1,
                  end_pause=0,end_call=lambda self:None,
                  generator=False):
        """Shakes a specified set of objects"""
        points=quantity
        if shake_vector is None:
            shake_vector=self.horizontal
        shake_vector=vector(*shake_vector)
        v1=(points//step_q)*shake_vector
        v2=(-points//step_q)*shake_vector

        def gen(self=self,obs=obs,quantity=quantity,v1=v1,v2=v2,
                bounces=bounces,step_q=step_q,end_pause=end_pause,end_call=end_call):
            for i in range(bounces):
                for x in range(step_q):
                    for o in obs:
                        self.move(o,*v1)
                    yield 0
                yield end_pause
                end_call(self)
                for x in range(step_q):
                    for o in obs:
                        self.move(o,*v2)
                    yield 0
                for x in range(step_q):
                    for o in obs:
                        self.move(o,*v2)
                    yield 0
                yield end_pause
                end_call(self)
                for x in range(step_q):
                    for o in obs:
                        self.move(o,*v1)
                    yield 0
        g=gen()
        if generator:
            return g
        else:
            for s in g:
                self.hold_update(s)

    def rock(self,theta=30,times=1,steps=3,end_pause=0,
             end_call=lambda self:None,mode='degree',
             center=None,expand=True,resample='bicubic',rotate_original=False):
        """Rocks all the objects on the canvas about a center-point (defaults to the exact center).
Currently not implemented."""
        objs=self.find_all()
        if center is None:
            center=[x/2 for x in self.window_dimensions]
        self.rock_obs(*objs,theta=theta,times=times,steps=steps,
                      end_pause=end_pause,end_call=end_call,mode=mode,
                      center=center,expand=expand,resample=resample,
                      rotate_original=rotate_original)
    
    def rock_obs(self,*obs,theta=30,times=1,steps=3,end_pause=0,
                 end_call=lambda self:None,mode='degree',
                 center=None,expand=True,resample='bicubic',rotate_original=False):
        """Rocks a given set of objects about a center point (Defaults to the object center)"""
        for i in range(times):
            angle=theta/steps*(-1**i)
            for x in range(steps):
                for o in obs:
                    self.rotate(o,angle,mode=mode,center=center,expand=expand,resample=resample,rotate_original=rotate_original)
                self.update_idletasks()
            self.hold_update(end_pause)
            end_call(self)
            angle=-angle
            for x in range(steps):
                for o in obs:
                    self.rotate(o,angle,mode=mode,center=center,expand=expand,resample=resample,rotate_original=rotate_original)
                self.update_idletasks()
            for x in range(steps):
                for o in obs:
                    self.rotate(o,angle,mode=mode,center=center,expand=expand,resample=resample,rotate_original=rotate_original)
                self.update_idletasks()
            self.hold_update(end_pause)
            end_call(self)
            angle=-angle
            for x in range(steps):
                for o in obs:
                    self.rotate(o,angle,mode=mode,center=center,expand=expand,resample=resample,rotate_original=rotate_original)
                self.update_idletasks()
                
    def rotate(self,obj_id,theta,times=1,pause=50,
                   center=None,mode='degree',expand=True,
                   resample='bicubic',rotate_original=False):
        """Rotates an object about a center point (defaults to the object center)"""
        if obj_id=='all':
            for r in range(times,0,-1):
                rthet=theta*(times-r+1)
                for x in self:
                    if r!=1:
                        self.revert_ob(x)
                    elif rotate_original:
                        self.revert_ob(x)
                    self.rotate(x,theta,mode=mode,expand=expand,resample=resample)
                if r!=1:
                    self.hold_update(pause)
                    
        else:
            if obj_id in self.image_hooks:
                if isinstance(obj_id,str):
                    obj_id=self.image_hooks[obj_id]
                im=self.image_hooks[obj_id]
                for r in range(times,0,-1):
                    if r!=1:
                        self.revert_ob(obj_id)
                    elif rotate_original:
                        self.revert_ob(obj_id)
                    rthet=theta*(times-r+1)
                    im.rotate(rthet,mode=mode,expand=expand,resample=resample)
                    self.itemconfig(obj_id,image=im.Tk)
                    if r!=1:
                        self.hold_update(pause)
            else:
                crds=iter(self.coords(obj_id))
                pairs=[]
                for x in crds:
                    y=next(crds)
                    pairs.append(vector(x,y,orientation='col'))
                if center is None:
                    center=vector(0,0,orientation='col')
                    i=0
                    for v in pairs:
                        center+=v
                        i+=1
                    center=center/i
                R=self.Rotation(center,theta,mode=mode)
                crds=[ round(y) for x in pairs for y in R*x ]
                self.coords(obj_id,*crds)
#### GENERAL PURPOSE COMMANDS
    def revert_ob(self,obj_id,keep_rotation=False):
        T=self.type(obj_id)
        if not T in ('image','bitmap'):
            self.set_colors(obj_id,*self.color_hold[obj_id])
        else:
            im_wrapper=self.image_hooks[obj_id]
            if keep_rotation:
                r=im_wrapper.rotation_angle
                im_wrapper.reset()
                im_wrapper.rotate(im_wrapper.rotation_angle)
            else:
                im_wrapper.reset()
            self.itemconfig(obj_id,image=im_wrapper.Tk)
            
    def apply_function(self,obj,func,*args,**kwargs):
        t=self.type(obj)
        if t=='image':
            img=self.image_hooks[t]
            if isinstance(func,str):
                func=getattr(img,func) 
            func(img,*args,**kwargs)
            self.itemconfig(t,image=img.Tk)
            
    def display_rectangle(self,ob,xmin=0,ymin=0,xmax=1,ymax=1):
        """Sets an image's display rectangle"""
        x=ob
##        canvas_color_function=lambda x,y,X,Y:raise
        img_function_name='display_rectangle'
        if x in self.image_hooks:
            if isinstance(x,str):
                x=self.image_hooks[x]
            w=self.image_hooks[x]
            w.display_rectangle(xmin,ymin,xmax,ymax)              
            self.itemconfig(x,image=w.Tk)

##### COLORING COMMANDS #####
    def color_transform(self,obj_id,canvas_color_function,img_function_name,
                        *args,child_windows=True):
        """Applies a color transformation to an object.
An image function name is provided for images.
A object coloring function is provided for canvas objects."""
        x=obj_id
        if x in self.image_hooks:
            if isinstance(x,str):
                x=self.image_hooks[x]
            w=self.image_hooks[x]
            getattr(w,img_function_name)(*args)                
            self.itemconfig(x,image=w.Tk)
        else:
            colors=self.get_colors(x)
            keys=('fill','outline','bg','fg')
            for i in range(4):
                c=colors[i];k=keys[i]
                if not c is None:
                    new=canvas_color_function(self.rgb_tuple(c),*args)
                    if i<2:
                        self.itemconfig(x,{k:self.rgb2hex(*new)})
                    elif child_windows:
                        window=self.nametowidget(self[x,'window'])
                        window[k]=self.rgb2hex(*new)

    def invert_colors(self):
        for ob in self:
            self.invert_ob_colors(ob)
            
    def invert_ob_colors(self,ob):
        """Inverts an object's colors"""
        canvas_color_function=lambda c:self.invert_color(c)
        img_function_name='invert'
        self.color_transform(ob,canvas_color_function,img_function_name)
        
    def increase_ob_contrast(self,ob,decimal_percentage=.1):
        """Inverts an object's constrast"""
        canvas_color_function=lambda c,d:self.increase_contrast(c,d)
        img_function_name='increase_constrast'
        self.color_transform(ob,canvas_color_function,img_function_name,decimal_percentage)

    def tint_ob(self,ob,r=0,g=0,b=0,a=255,bg=False):
        """Applies a tint to an object"""
        canvas_color_function=lambda c,r,g,b,a:self.tint_color(c,r,g,b)
        img_function_name='tint'
        self.color_transform(ob,canvas_color_function,img_function_name,r,g,b,a)
        
    def tint(self,r=0,g=0,b=0,a=255,bg=False,tint_windows=False):        
        canvas_color_function=lambda c,r,g,b,a:self.tint_color(c,r,g,b)
        """Applies a tint to all objects.
Background and child windows can be specified to tint."""
        img_function_name='tint'
        if bg:
            self['bg']=self.rgb2hex(*canvas_color_function(self.rgb_tuple(self['bg']),r,g,b,a))
        for x in self:
            self.color_transform(x,canvas_color_function,img_function_name,r,g,b,a,
                                 child_windows=tint_windows)

    def darken_ob(self,ob,decimal_percentage=.1):
        """Darkens an object"""
        canvas_color_function=self.rgb_darker
        img_function_name='darken'
        self.color_transform(ob,canvas_color_function,img_function_name,decimal_percentage)
        
    def darken(self,decimal_percentage=.1,bg=False,darken_windows=False):
        """Darkens all objects.
Background and child windows can be specified to be darkened."""
        canvas_color_function=self.rgb_darker
        img_function_name='darken'
        if bg:
            self['bg']=canvas_color_function(self.rgb_tuple(self['bg']),decimal_percentage)
        for x in self:
            self.color_transform(x,canvas_color_function,img_function_name,
                                 decimal_percentage,child_windows=darken_windows)

    def lighten_ob(self,ob,decimal_percentage=.1):
        """Lightens an object"""
        canvas_color_function=self.rgb_lighter
        img_function_name='lighten'
        self.color_transform(ob,canvas_color_function,img_function_name,decimal_percentage)
        
    def lighten(self,decimal_percentage=.1,bg=False,lighten_windows=False):
        """Lightens all objects.
Background and child windows can be specified to be lightened."""
        canvas_color_function=self.rgb_lighter
        img_function_name='lighten'
        if bg:
            self['bg']=canvas_color_function(self.rgb_tuple(self['bg']),decimal_percentage)
        for x in self:
            self.color_transform(x,canvas_color_function,img_function_name,
                                 decimal_percentage,child_windows=lighten_windows)

    def fade_ob(self,ob,decimal_percentage=.1,img_mode='fade_to'):
        rgb=self.rgb_tuple(self['bg'])
        canvas_color_function=lambda c,r,d:self.rgb_fade(c,r,d)
        img_function_name=img_mode
        self.color_transform(ob,canvas_color_function,
                             img_function_name,rgb,decimal_percentage)
        
    def fade(self,decimal_percentage=.1,img_mode='fade_to'):
        rgb=self.rgb_tuple(self['bg'])
        canvas_color_function=lambda c,r,d:self.rgb_fade(c,r,d)
        img_function_name=img_mode
        for x in self:
            self.color_transform(x,canvas_color_function,
                                 img_function_name,rgb,decimal_percentage)

    def unfade_ob(self,ob,decimal_percentage=.1,img_mode='fade_restore'):
        if ob in self.image_hooks:
            if isinstance(ob,str):
                ob=self.image_hooks[ob]
            img=self.image_hooks[ob]
            method=getattr(img,img_mode)
            method(decimal_percentage)
            self[ob,'image']=img.Tk
        else:
            tup=self.color_hold[ob]
            out,fi,fg,bg=tup
            if not out is None:
                cur=self[ob,'outline']
                fd=self.rgb_fade(self.rgb_tuple(cur),self.rgb_tuple(out),decimal_percentage)
                self[ob,'outline']=self.rgb2hex(*fd)
            if not fi is None:
                cur=self[ob,'fill']
                fd=self.rgb_fade(self.rgb_tuple(cur),self.rgb_tuple(fi),decimal_percentage)
                self[ob,'fill']=self.rgb2hex(*fd)
            if not fg is None:
                w=self[ob,'window'];w=self.nametowidget(w)
                cur=w['bg']
                fd=self.rgb_fade(self.rgb_tuple(cur),self.rgb_tuple(bg),decimal_percentage)
                w['bg']=self.rgb2hex(*fd)
                if fg:
                    cur=w['fg']
                    fd=self.rgb_fade(self.rgb_tuple(cur),self.rgb_tuple(fg),decimal_percentage)
                    w['fg']=self.rgb2hex(*fd)
                
    def unfade(self,decimal_percentage=.1,bg=False,img_mode='fade_restore'):
        for x in self:
            self.unfade_ob(x,decimal_percentage,img_mode=img_mode)
        if bg:
            cur=self['bg']
            fd=self.rgb_fade(self.rgb_tuple(cur),self.rgb_tuple(self.bg),decimal_percentage)
            self['bg']=fd

    def flash_obs(self,*obs,times=1,pause=100,spacing=25,
                  r=0,g=0,b=0,a=255,
                  invert=False,fade=0,glow=0,generator=False):
        """Makes an object flash with the specified tint.
Glow levels and fade levels may also be specified."""
        if glow==0:
            glf=lambda o,x:None
        elif glow>0:
            glf=self.lighten_ob
        else:
            glf=self.darken_ob

        if fade>0:
            fade_fun=self.fade_ob
        else:
            fade_fun=lambda o,q:None

        def gen(self=self,obs=obs,times=times,pause=pause,spacing=spacing,
                r=r,g=g,b=b,a=a,
                glow=glow,fade=fade,invert=invert,
                glf=glf,fade_fun=fade_fun,generator=generator):
            self.save_colors_temp(False)
            for i in range(times,0,-1):
                for x in obs:
                    self.tint_ob(x,r,g,b,a)
                    glf(x,glow)
                    fade_fun(x,fade)
                yield pause
                for x in obs:
                    self.revert_ob(x)
                if i>1:
                    yield spacing
            self.restore_colors_temp(False)
            self.revert_colors()
            yield 0
            
        g=gen()
        if generator:
            return g
        else:
            for s in g:
                self.hold_update(s)
            
            
    def flash(self,times=1,pause=100,r=0,g=0,b=0,a=255,spacing=25,
              glow=0,fade=0,bg=True,invert=False,child_windows=True,
              generator=False):
        """Makes all objects flash with the specified tint.
Glow levels and fade levels may also be specified.
Background may be specified not to flash, as may widgets on the canvas."""
        if glow==0:
            glf=lambda x:None
        elif glow>0:
            glf=self.lighten
        else:
            glf=self.darken

        if fade>0:
            fade_fun=self.fade
        else:
            fade_fun=lambda q:None

        def gen(self=self,times=times,pause=pause,spacing=spacing,
                r=r,g=g,b=b,a=a,glow=glow,fade=fade,
                bg=bg,invert=invert,child_windows=child_windows,
                glf=glf,fade_fun=fade_fun,generator=generator):
            self.save_colors_temp(bg=bg)
            for i in range(times,0,-1):
                if invert:
                    self.invert_colors()
                self.tint(r,g,b,a,bg=bg,tint_windows=child_windows)
                glf(glow)
                fade_fun(fade)
                yield pause
                self.revert_colors()
                if i>1:
                    yield spacing
            self.restore_colors_temp(bg=bg)
            self.revert_colors()
            yield 0

        g=gen()
        if generator:
            return g
        else:
            for s in g:
                self.hold_update(s)
                
    def get_colors(self,obj_id):
        colors=[None]*4
        ty=self.type(obj_id)
        if ty in ('polygon','arc','oval','rectangle'):
            colors[0]=self.itemcget(obj_id,'fill')
            colors[1]=self.itemcget(obj_id,'outline')
        elif ty in ('line','text'):
            colors[0]=self.itemcget(obj_id,'fill')
        elif ty=='window':
            w=self[obj_id,'window']
            if len(w)>0:
                w=self.nametowidget(w)
                k=w.keys()
                i=1
                for key in ('bg','fg'):
                    i+=1
                    if key in k:
                        v=w[key]
                        colors[i]=v
        return colors
    
    def set_colors(self,obj_id,fill=None,outline=None,bg=None,fg=None):
        ty=self.type(obj_id)
        if ty in ('polygon','arc','oval','rectangle'):
            self.itemconfig(obj_id,fill=fill)
            self.itemconfig(obj_id,outline=outline)
        elif ty in ('line','text'):
            self.itemconfig(obj_id,fill=fill)
        elif ty=='window':
            w=self[obj_id,'window']
            if len(w)>0:
                w=self.nametowidget(w)
                k=w.keys()
                if 'bg' in k:
                    w.config(bg=bg)
                if 'fg' in k:
                    w.config(fg=fg)
    
    def save_ob_colors(self,obj_id):
        
        self.color_hold[obj_id]=tuple(self.get_colors(obj_id))
    revert_ob_colors=revert_ob
    
    def save_ob_colors_temp(self,obj):
        '''Stores an objects held colors temporarily and holds its current colors''' 
        if obj in self.color_hold_temp:
            self.color_hold_temp[obj].append(self.color_hold[obj])
        else:
            self.color_hold_temp[obj]=deque((self.color_hold[obj],))
        self.save_ob_colors(obj)
        
    def restore_ob_colors_temp(self,obj):
        self.color_hold[obj]=self.color_hold_temp[obj].pop()

    def save_colors_temp(self,bg=True):
        for x in self.color_hold:
            self.save_ob_colors_temp(x)
        if bg:
            self.bg_stack.append(self.bg)
        self.save_colors(bg)

    def restore_colors_temp(self,bg=True):
        for x in self.color_hold:
            self.restore_ob_colors_temp(x)
        if bg:
            self.bg=self.bg_stack.pop()
            
    def save_colors(self,bg=True):
        for x in self.color_hold:
            self.save_ob_colors(x)
        if bg:
            self.bg=self['bg']
            
    def revert_colors(self,bg=True):
        for x in self.color_hold:
            self.revert_ob(x,keep_rotation=True)
        if bg:
            self['bg']=self.bg
            
#### DISAPPEAR AND REAPPEAR COMMANDS          
    def fade_in(self,*objs,total=1,steps=5,rate=25,img_mode='solidify',generator=False):
        """Fades an object out of the background.
(images default to having alpha channel increased)"""
        q=total/steps
        if objs[0]=='all':
            objs=self.find_all()

        def gen(self=self,objs=objs,total=total,
                steps=steps,rate=rate,img_mode=img_mode,
                     generator=generator):
            for i in range(steps):
                for obj in objs:
                    self.unfade_ob(obj,q,img_mode=img_mode)
                yield rate
            for obj in objs:
                self.unfade_ob(obj,total,img_mode=img_mode)
        
        g=gen()
        if generator:
            return g
        else:
            for s in g:
                self.hold_update(s)
                
    def fade_out(self,*objs,total=1,steps=5,rate=25,img_mode='disappear',
                 generator=False):
        """Fades an object into the background.
(images default to having alpha channel decreased)"""
        q=total/steps
        if objs[0]=='all':
            objs=self.find_all()

        def gen(self=self,objs=objs,total=total,
                steps=steps,rate=rate,img_mode=img_mode,
                     generator=generator):
            for i in range(steps):
                for obj in objs:
                    self.fade_ob(obj,q,img_mode=img_mode)
                yield rate
            for obj in objs:
                self.fade_ob(obj,total,img_mode=img_mode)

        g=gen()
        if generator:
            return g
        else:
            for s in g:
                self.hold_update(s)

    def crop_disappear(self,*objs,x_min=0,y_min=0,x_max=1,y_max=1,
                    fix_left=False,fix_top=False,fix_right=False,fix_bottom=False,
                    end=None,
                    step_q=10,step_rate=100,generator=False):
        """For images, reduces image size, to crop into a smaller and smaller area.
Needs extension to cropping about a given point."""
        x_q=int(x_max*step_q)
        y_q=int(y_max*step_q)
        l_end=step_q//2;r_end=step_q//2+1
        h_end=step_q//2;b_end=step_q//2+1
        
        if 'all' in objs:
            objs=self.find_all()

        if end is None:
            end=(0 if fix_left else 1 if fix_right else .5,
                 0 if fix_top else 1 if fix_bottom else .5,
                 1 if fix_right else 0 if fix_left else .5,
                 1 if fix_bottom else 0 if fix_top else .5)

        def crop_generator(self=self,objs=objs,
                    x_min=x_min,y_min=y_min,x_max=x_max,y_max=y_max,
                    fix_left=fix_left,fix_top=fix_top,
                    fix_right=fix_right,fix_bottom=fix_bottom,
                    start=start,
                    step_q=step_q,step_rate=step_rate,generator=generator):
            for x_i,y_i,x_j,y_j in zip(range(0,l_end,1),
                                       range(0,h_end,1),
                                       range(x_q,r_end,-1),
                                       range(y_q,b_end,-1)):
                dx1=(x_max-x_min)*x_i/step_q;dy1=(y_max-y_min)*y_i/step_q
                dx2=(x_max-x_min)*x_j/step_q;dy2=(y_max-y_min)*y_j/step_q
                if fix_left:
                    if not fix_right:
                        dx2-=dx1-x_min
                    dx1=x_min
                if fix_right:
                    if not fix_left:
                        dx1+=x_max-dx2
                    dx2=x_max
                if fix_top:
                    if not fix_bottom:
                        dy2-=dy1-y_min
                    dy1=y_min
                if fix_bottom:
                    if not fix_top:
                        dy1+=y_max-dy2
                    dy2=y_max
                for obj in objs:
                    self.revert_ob(obj);self.display_rectangle(obj,dx1,dy1,dx2,dy2)
                yield step_rate

            for obj in objs:
                self.revert_ob(obj);self.display_rectangle(obj,*end)

        g=crop_generator()
        if generator:
            return g
        else:
            for s in g:
                self.hold_update(s)

    def crop_appear(self,*objs,x_min=0,y_min=0,x_max=1,y_max=1,
                    fix_left=False,fix_top=False,fix_right=False,fix_bottom=False,
                    start=None,
                    step_q=10,step_rate=100,generator=False):
        
        """For images, increases image size, to expand into a larger and larger area.
Needs extension to expanding about a given point."""
        
        x_q=int(x_max*step_q)
        y_q=int(y_max*step_q)
        l_end=step_q//2;r_end=step_q//2+1
        h_end=step_q//2;b_end=step_q//2+1
        
        if 'all' in objs:
            objs=self.find_all()

        if start is None:
            start=(0 if fix_left else 1 if fix_right else .5,
                 0 if fix_top else 1 if fix_bottom else .5,
                 1 if fix_right else 0 if fix_left else .5,
                 1 if fix_bottom else 0 if fix_top else .5)
            
        def crop_generator(self=self,objs=objs,
                    x_min=x_min,y_min=y_min,x_max=x_max,y_max=y_max,
                    fix_left=fix_left,fix_top=fix_top,
                    fix_right=fix_right,fix_bottom=fix_bottom,
                    start=start,
                    step_q=step_q,step_rate=step_rate,generator=generator):

            for obj in objs:
                self.temporary_set();self.display_rectangle(obj,*start)
                
            for x_i,y_i,x_j,y_j in zip(range(l_end,0,-1),
                                       range(h_end,0,-1),
                                       range(r_end,x_q,1),
                                       range(b_end,y_q,1)):
                dx1=(x_max-x_min)*x_i/step_q;dy1=(y_max-y_min)*y_i/step_q
                dx2=(x_max-x_min)*x_j/step_q;dy2=(y_max-y_min)*y_j/step_q
                if fix_left:
                    if not fix_right:
                        dx2-=dx1-x_min
                    dx1=x_min
                if fix_right:
                    if not fix_left:
                        dx1+=x_max-dx2
                    dx2=x_max
                if fix_top:
                    if not fix_bottom:
                        dy2-=dy1-y_min
                    dy1=y_min
                if fix_bottom:
                    if not fix_top:
                        dy1+=y_max-dy2
                    dy2=y_max
                for obj in objs:
                    self.revert_ob(obj);self.display_rectangle(obj,dx1,dy1,dx2,dy2)
                yield step_rate

            for obj in objs:
                self.revert_ob(obj);self.display_rectangle(obj,x_min,y_min,x_max,y_max);
                self.temporary_reset(obj)

        g=crop_generator()
        if generator:
            return g
        else:
            for s in g:
                self.hold_update(s)
                
    def slide_out(self,ob,to='left',slide_x=True,slide_y=True,
                  slide_by='bbox',mode='frac',
                  steps=5,step_rate=100,
                  generator=False):
        m=mode
        mode='frac'
        if to=='left':
            to=(0,0)
            slide_y=False
        elif to=='right':
            to=(1,0)
            slide_y=False
        elif to=='top':
            to=(0,0)
            slide_x=False
        elif to=='bottom':
            to=(0,1)
            slide_x=False
        else:
            mode=m

        def slide_gen(self=self,ob=ob,to=to,slide_x=slide_x,
                      slide_y=slide_y,slide_by=slide_by,
                      mode=mode,steps=steps,step_rate=step_rate,
                          generator=generator):
            g=self.slide_to(ob,to,slide_x=slide_x,slide_y=slide_y,
                          slide_by=slide_by,mode=mode,
                          steps=steps,step_rate=step_rate,
                          generator=generator)
                
            if not g is None:
                for x in g:
                    yield(x)

            self.hide(ob)

        g=slide_gen()
        if generator:
            return g
        else:
            list(g)
                

#### CREATION COMMANDS
    def add_file(self,x,y,img_link,**kwargs):
        if self.image_source is None:
            if not os.path.exists(img_link):
                img_link=AnimationImages.get_image(img_link)
        else:
            base,ext=os.path.splitext(img_link)
            if ext=='':
                img_link+='.png'
            if not os.path.isabs(img_link):
                img_link=os.path.join(self.image_source,img_link)
        I=ImageWrapper(img_link)
        o=self.create_image(x,y,image=I.Tk,**kwargs)
        return o
    
    def create_oval(self,*args,**kwargs):
        o=super().create_oval(*args,**kwargs)
        self.color_hold[o]=self.get_colors(o)
        self.last_made=o
        return o
    def create_circle(self,*args,**kwargs):
        o=super().create_circle(*args,**kwargs)
        self.color_hold[o]=self.get_colors(o)
        self.last_made=o
        return o
    def create_line(self,*args,**kwargs):
        o=super().create_line(*args,**kwargs)
        self.color_hold[o]=self.get_colors(o)
        self.last_made=o
        return o
    def create_window(self,*args,**kwargs):
        o=super().create_window(*args,**kwargs)
        self.color_hold[o]=self.get_colors(o)
        self.last_made=o
        return o
    def create_image(self,*args,image='',**kwargs):
        o=super().create_image(*args,image=image,**kwargs)
        self.color_hold[o]=(None,None,None,None)
        self.image_hooks[o]=image.image_wrapper
        self.image_hooks[image.image_wrapper.name]=o
        self.last_made=o
        return o

#### OVERLOADING
    def __iter__(self):
        return iter(self.find_all())
