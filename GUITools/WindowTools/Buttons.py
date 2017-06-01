from GUITools.Shared import *
from GUITools.SharedData import *
from GUITools.ImageTools import ImageWrapper,pil_flag
from GUITools.EventTools import Binding

mac_size=13

class ButtonABC:
    images=ButtonImages
    type_map=(
            ((str,),lambda x,k:('bg',x)),
            ((ImageWrapper,tk.PhotoImage,tk.BitmapImage),lambda x,k:('image',x)),
            ((tuple,),lambda x,k:('image',__class__.get_image(x,k))),
            ((dict,),lambda x,k:('config',x))
            )
    image_flag=pil_flag
    def __init__(self,master=None,
                 command=lambda:None,
                 baseargs=(),basekwargs=None,
                 inactive=None,
                 raised=None,
                 tint=None,
                 depressed=None,
                 image_source=None,
                 **kwargs
                 ):
        self.command=command
        self._disabled=False
        self.hold_calls=False
        self.call_wait=50
        self.tint=tint
        self.args=baseargs
        self.conf_flag=True
        self.invoke_flag=False
        self.inactive_flag=True
        self.image_hooks={}
##        self.image_stuff=[]
        if not image_source is None:
            if isinstance(image_source,tuple):
                raised=image_source
            else:
                raised=(image_source,'')
            inactive=raised
            depressed=raised
        if basekwargs is None:
            basekwargs={}
        self.kwargs=basekwargs
        if raised is None:
            raised={'bg':'grey35','fg':'white','relief':'groove'}
        if inactive is None:
            inactive={'bg':self['bg'],'fg':self['fg'],'relief':'groove'}
        maps=self.type_map
        for tup,resp in maps:
            if isinstance(raised,tup):
                raised=resp(raised,'raised')
                break
        self.raised=raised
        for tup,resp in maps:
            if isinstance(inactive,tup):
                inactive=resp(inactive,'raised')
                break
        self.inactive=inactive
        if depressed is None:
            depressed={'bg':'darkblue','fg':'white','relief':'flat'}
        for tup,resp in maps:
            if isinstance(depressed,tup):
                depressed=resp(depressed,'depressed')
                break
        self.depressed=depressed

    @classmethod
    def get_image(self,tup,key='raised'):
        if key=='depressed':
            key='_down'
        else:
            key='_up'
        return ImageWrapper(self.images.get(*tup,key=key))
    def destroy(self):
        self.conf_flag=False
        try:
            super().destroy()
        except AttributeError:
            self.disable()
            for x,n in self.button_hooks.items():
                for m in n:
                    self.canvas.delete(m)
        
    def set_image(self,tup,key='raised'):
        if key=='raised':
            self.raised=('image',self.get_image(tup,key='_up'))
        elif key=='depressed':
            self.depressed=('image',self.get_image(tup,key='_down'))
        elif key=='inactive':
            self.inactive=('image',self.get_image(tup,key='_up'))

    def in_loop(self):
        if self.mouse_in():
            self.after(10,self.in_loop)
        else:
##            pass
            self.cancel()
    def set_style(self,tup):
        self['image']=''
        maps=self.type_map
        for v,k in zip(tup,('raised','depressed','inactive')):
            for m,f in maps:
                if isinstance(v,m):
                    setattr(self,k,f(v,k))
##            if isinstance(v,tuple):
##                self.set_image(v,k)
##            else:
##                setattr(self,k,v)
        self.style=tup
        self.draw(override=True)
    
    def click_call(self,event=None):
        if self.hold_calls:
            self.cancel()
        else:
            self.depress()
            self.invoke_flag=True
            self.hold_calls=True
            self.after(self.call_wait,lambda:setattr(self,'hold_calls',False))

##        self.draw()
    def invoke(self):
        c=self.command
        return c(*self.args,**self.kwargs)

    def ready(self,event=None):
        self.inactive_flag=False
##        self.in_loop()
##        print('!')
        self.draw()

    def depress(self,event=None):
##        conf,resp=self.depressed
##        if conf=='image':
##            resp=self.process_image(resp)
##        self[conf]=resp
        pass
        
    def cancel(self,event=None):
        self.invoke_flag=False
        self.conf_flag=True
        self.inactive_flag=True
        self.draw()
        
    def kill(self,event=None):
        self.conf_flag=False

    def __setitem__(self,key,val):
        self.config(**{key:val})

    def process_image(self,image):
        w=self.width()-2
        h=self.height()-2
        if w<0 or h<0:
            w=h=max(w,h)
##        try:
##            print(self['image'])
##        except:
##            pass
        
        if isinstance(image,ImageWrapper):
            if self.image_flag:
                image.reset()
                if not self.tint is None:
                    image.tint(*self.tint)
                image.resize((max(w,2),max(h,2)))
##                print('{')
                image=image.Tk
##                image.show()
                self._image_hook=image
##                self.image_stuff.append(image)
##                print('}')
            else:
                image=tk.PhotoImage(width=5,height=5)
        return image
    

b_class=ButtonABC                
class LabelButton(tk.Label):
    type_map=b_class.type_map
    def __init__(self,master=None,
                 command=lambda:None,
                 baseargs=(),basekwargs=None,
                 tint=None,
                 inactive=None,
                 raised=None,
                 depressed=None,
                 image_source=None,
                 compound='center',**kwargs):
        kwargs['compound']=compound
        super().__init__(master,**kwargs)
        ButtonABC.__init__(self,
                           command=command,
                           baseargs=baseargs,
                           basekwargs=basekwargs,
                           inactive=inactive,
                           tint=tint,
                           raised=raised,
                           depressed=depressed,
                           image_source=image_source
                           )
        
        
##        self.depressed=depressed
        self.bindings=[Binding(key,command) for key, command in (
            ('<Enter>',self.ready),
            ('<Leave>',self.cancel),
            ('<Button-1>',self.click_call),
            ('<ButtonRelease-1>',self.draw)
            )
                       ]
        for B in self.bindings:
            B.apply(self)
        self.bind('<Configure>',self.draw)
        self.bind('<Destroy>',self.kill)
        self.width=self.winfo_width
        self.height=self.winfo_height

        self.state=tk.StringVar()
        self.state.trace('w',self.change_state)
        
    ready=b_class.ready
##    depress=b_class.depress
    invoke=b_class.invoke
    cancel=b_class.cancel
    __setitem__=b_class.__setitem__
    process_image=b_class.process_image
    kill=b_class.kill
    click_call=b_class.click_call
    set_style=b_class.set_style
    get_image=b_class.get_image
    set_image=b_class.set_image
    in_loop=b_class.in_loop
    
    def config(self,**kwargs):
        for x in ('raised','inactive','depressed','command','tint'):
            if x in kwargs:
                setattr(self,x,kwargs[x])
                del kwargs[x]
        if 'style' in kwargs:
            t=kwargs['style']
            self.set_style(t)
            del kwargs['style']
        super().config(**kwargs)

    def hide(self):
        self['image']=''
        
    def mouse_in(self):
        x=self.winfo_rootx()+self.winfo_x();y=self.winfo_rooty()+self.winfo_y()
        w=self.winfo_width();h=self.winfo_height()
        px,py=self.winfo_pointerxy()
##        print(x,y,w+x,y+h,px,py)
        return (px>=x and px<=(w+x) and py>=y and py<=h+y)
    
    def disable(self):
        if not self._disabled:
            for B in self.bindings:
                B.remove(self)
            self._disabled=True
            
    def enable(self):
        if self._disabled:
            for B in self.bindings:
                B.apply(self)
            self._disabled=False

    def set_state(self,key):
        if key=='disabled':
            self.cancel()
            self.disable()
        else:
            self.enable()

    def depress(self,event=None):
        self.change_appearance(self.depressed)

    def change_state(self,*args):
        k=self.state.get()
        if k in ('inactive','depressed','raised'):
            self.enable()
            ch=getattr(self,k)
        else:
            self.disable()
            ch=self.inactive
        self.change_appearance(ch)
        
    def change_appearance(self,pair):
        conf,resp=pair
        if conf=='image':
            resp=self.process_image(resp)
            self.image_hooks['depressed']=resp
            self[conf]=resp
        elif conf=='config':
            self.config(**resp)
        else:
            self[conf]=resp
            
    def draw(self,event=None):
        if self.winfo_height()>2 and self.winfo_width()>2:
            if self.conf_flag:
                if self.invoke_flag:
                    self.invoke()
                    self.invoke_flag=False
                if self.conf_flag:
                    choice=self.raised
                    if self.inactive_flag:
                        choice=self.inactive
                    self.change_appearance(choice)
                    self.conf_flag=False
                    self.after(50,lambda:setattr(self,'conf_flag',True))
        else:
            self.after(10,self.draw)
##        else:
##            self.after(10,
##                       lambda:(self.wait_visibility(self),self.draw()))

class CanvasButton(ButtonABC):
    
    def __init__(self,canvas,bbox=None,**kwargs):
        import random
        super().__init__(**kwargs)
        self.exp_b=Binding('<Expose>',
                           command=lambda e,self=self:(
                               self.draw(),
                               self.exp_b.remove(self.canvas),
                               print('...')
                                                       ),add='+')
        self.canvas=canvas
        self.exp_b.apply(self.canvas)
        self.bbox=bbox
        self.bind_key=''.join((
            random.choice(string.ascii_letters+string.digits)
            for i in range(6)
            ))
##        self.hook=None
        self.after=canvas.after
        self.response_time=25
        self.state=tk.StringVar(value='inactive')
        self.state.trace('w',self.change_state)
        self.compound='center'
        self.anchors={x:'center' for x in ('raised','depressed','inactive')}
        self.button_hooks=None
        self.click_flag=False
        self.tk_preserver={}
        self.bind_keys={x:self.bind_key+x for x in ('raised','depressed','inactive')}
        self.m_lock=Binding('<B1-Motion>',command=lambda e:'break',add='+')#return_value='break',add='+')
##        self.hook=self.draw(x1,y1,x2,y2)
##    @property
##    def bind_key(self):
##        bk=self.hook
##        if bk is None:
##            bk=''
##        return bk
    def width(self):
        x,y,x2,y2=self.bbox
        return x2-x
    def height(self):
        x,y,x2,y2=self.bbox
        return y2-y
    @property
    def TkImage(self):
        s=self.state.get()
        o1,o2=self.button_hooks[s]
        return self.canvas.itemcget(o1,'image')
    
    def mouse_in(self):
        if not self._disabled:
            s=self.state.get()
            n,t=self.button_hooks[s]
            old=px,py=self.canvas.winfo_pointerxy()
            px+=-self.canvas.winfo_rootx()#-(self.canvas.winfo_rootx()+self.canvas.winfo_x())
            py+=-self.canvas.winfo_rooty()#-(self.canvas.winfo_rooty()+self.canvas.winfo_y())
            crds=self.canvas.coords(n)
            if len(crds)==2:
                crds=list(crds)+[crds[0]+self.width(),crds[1]+self.height()]
            x,y,X,Y=crds
            return (px>=x and px<=X and py>=y and py<=Y)
    def change_state(self,*args):
        s=self.state.get()
##        print(s)

        if s=='disabled':
            self.disable()
        else:
            for k,v in self.bind_keys.items():
                if k==s:
                    
                    self.canvas.itemconfig(v,
                                           state='normal'
                                           )
                else:
                    try:
                        self.canvas.itemconfig(v,state='hidden')
                    except TclError:
                        conf,resp=getattr(self,k)
                        if conf=='image' and self.image_flag:
                            a=self.anchors[k]
                            self.canvas.delete(v)
                            img=self.process_image(resp)

                            self.image_hooks[s]=img
                            v=self.canvas.create_image(self.bbox[0],self.bbox[1],
                                                       tags=self.bind_keys[s],
                                                       anchor=a,
                                                       image=img)
                            o1,o2=self.button_hooks[k]
                            self.button_hooks[k]=(v,o2)
                            self.canvas.itemconfig(v,state='hidden')
                        else:
                            raise
            self.apply_bindings('all')

    def set_position(self,x=None,y=None,width=None,height=None,anchor=None):
        bx,by,bX,bY=self.bbox
            
        if x is None:
            x=bx
        if y is None:
            y=by
        if width is None:
            width=bX-bx
        if height is None:
            height=bY-by
        X=x+width
        Y=y+height
        self.bbox=bbox=(x,y,X,Y)
        
        for s,k in self.button_hooks.items():
            conf,resp=getattr(self,s)
            o1,o2=k
            if conf=='image':
                self.anchors[s]=anchor
                try:
                    self.canvas.coords(o1,x,y)
                except TclError:
                    n=self.button_hooks[s]
                    self.canvas.delete(n)
                    resp=self.process_image(resp)
##                    resp.show()
##                    print('[[[',end='')
                    self.image_hooks[s]=resp
                    bind_keys=self.bind_keys[s]
                    self.canvas.delete(bind_keys[1])
                    o1=self.canvas.create_image(x,y,
                                                image=resp,
                                                tags=bind_keys,
                                                anchor=anchor)
##                    print('{}:{}]]]'.format(o1,resp))
                    self.button_hooks[s]=(o1,o2)
                    self.apply_bindings(s)
                else:
                    self.canvas.itemconfig(o1,anchor=anchor)
            else:
##                try:
                
                self.canvas.coords(o1,x,y,X,Y)
##                self.canvas.coords
##                except TclError:
####                    print(self.TkImage)
##                    print(k)
##                    raise

            center_x=x+width//2
            center_y=y+height//2
            self.canvas.coords(o2,center_x,center_y)
            a=self.translate_anchor(self.anchors[s])
            self.canvas.itemconfig(o2,anchor=a)

    def disable(self):
        self._disabled=True
        self.state.set('inactive')
        for x,w in self.bind_keys.items():
            for k in ('<Enter>','<Button-1>',
                      '<Button-Release>','<Leave>'):
                self.canvas.tag_unbind(w,k)
    @property
    def text_anchor(self):
        s=self.anchors[self.state.get()]
##        print(s,end='->')
        r=self.translate_anchor(s)
##        print(r)
        return r
    def translate_anchor(self,anchor):
        if anchor=='center':
            anchor=='c'
        l=len(anchor)
        def rep_pair(anchor,a,b):
            anchor.replace(a,'');anchor.replace('c','')
            anchor=b+anchor
            return anchor
        if self.compound=='center':
            anchor=anchor
        if self.compound=='top':
            anchor=rep_pair(anchor,'n','s')
        elif self.compound=='bottom':
            anchor=rep_pair(anchor,'s','n')
        elif self.compound=='right':
            anchor=rep_pair(anchor,'e','w')
        elif self.compound=='left':
            anchor=rep_pair(anchor,'w','e')
        return anchor
                
    def apply_bindings(self,key='all'):

    
        def i_bind(i):
            self.canvas.tag_bind(i,'<Enter>',self.ready)
        def r_bind(r):
            self.canvas.tag_bind(r,'<Button-1>',self.click_call)
            self.canvas.tag_bind(r,'<ButtonRelease-1>',self.draw)
            self.canvas.tag_bind(r,'<Leave>',self.deactivate)
        def d_bind(d):
##            self.canvas.tag_bind(d,'<ButtonRelease-1>',self.draw)
            self.canvas.tag_bind(d,'<Enter>',self.cancel)
            self.canvas.tag_bind(d,'<Leave>',self.cancel)
        b_hook=self.bind_keys
        if key=='all':
            i=b_hook['inactive']
            r=b_hook['raised']
            d=b_hook['depressed']
            i_bind(i)
            r_bind(r)
            d_bind(d)
        elif key=='inactive':
            i=b_hook['inactive']
            i_bind(i)
        elif key=='raised':
            r=b_hook['raised']
            r_bind(r)
        elif key=='depressed':
            d=b_hook['depressed']
            d_bind(d)

    def config(self,**kwargs):
        for x in ('raised','inactive','depressed','command','tint'):
            if x in kwargs:
                setattr(self,x,kwargs[x])
                del kwargs[x]
        if 'style' in kwargs:
            t=kwargs['style']
            self.set_style(t)
            del kwargs['style']

    def click_call(self,event=None):
        self.click_flag=True
        self.m_lock.apply(self.canvas,0)
        super().click_call()
        
    def ready(self,event=None):
        self.state.set('raised')
        self.in_loop()
        
    def depress(self,event=None):
        self.state.set('depressed')
##        super

    def deactivate(self,event=None):
        if not self.click_flag:
            self.cancel()
    def cancel(self,event=None):
        self.state.set('inactive')
        self.m_lock.remove(self.canvas)
        super().cancel()

    def __getitem__(self,key):
        s=self.state.get()
        h=self.button_hooks[s]
        return self.canvas.itemcget(h,key)

    def center_point(self,state='current'):
        if state=='current':
            state=self.state.get()
        o1,o2=self.button_hooks[state]
        return self.canvas.coords(o2)
    def add_text(self,text,state='current'):
        if state=='current':
            state=(self.state.get(),)
        elif state=='all':
            state=('inactive','raised','depressed')
        elif isinstance(state,str):
            state=(state,)
        for s in state:
            o1,o2=self.button_hooks[state]
            self.canvas.itemconfig(o2,text=text)

    def hide(self):
        for x,w in self.button_hooks.items():
            self.canvas.itemconfig(x,state='hidden')
    def draw(self,bbox=None,height=0,width=0,key=None,
             override=False,**kwargs):
        if bbox is None or isinstance(bbox,tk.Event):
            bbox=self.bbox
        if not bbox is None:
            if 'anchor' in kwargs:
                for k in self.anchors:
                  self.anchors[k]=kwargs['anchor']
            if len(bbox)==2:
                bbox=(bbox[0],bbox[1],bbox[0]+width,bbox[1]+height)
            self.bbox=bbox
            if self.button_hooks is None or override:
                self.button_hooks={}
                self.image_hooks={}
                x,y,X,Y=bbox
                for k,choice in zip(
                    ('raised','depressed','inactive'),
                    (self.raised,self.depressed,self.inactive)):
                    conf,resp=choice
                    bind_keys=(self.bind_key,self.bind_key+k)
                    self.canvas.delete(bind_keys[1])
                    if conf=='image':
                        inset=''
                        resp=self.process_image(resp)
                        self.image_hooks[k]=resp
                        kwargs['anchor']=self.anchors[k]
                        o=self.canvas.create_image(x,y,image=resp,tags=bind_keys,**kwargs)
                        
                    else:
                        if 'text' in resp:
                            inset=resp['text']
                            del resp['text']
                        else:
                            inset=''
                        if 'shape' in resp:
                            self.anchors[k]='center'
                            shape=resp['shape']
                            del resp['shape']
                            f=getattr(self.canvas,'create_'+shape)
                            o=f(*bbox,tags=bind_keys,**resp)
                        elif 'window' in resp:
                            if 'anchor' in resp:
                                self.anchors[k]=resp['anchor']
                            wtype=resp['window']
                            del resp['window']
                            
                            if 'bindings' in resp:
                                bindings=resp['bindings']
                                del resp['bindings']
                            else:
                                bindings=()
                            W=wtype(self.canvas,**resp)
                            for x in bindings:
                                x.apply(W)
                            o=self.canvas.create_window(x,y,width=X-x,height=Y-y,
                                                      window=W,tags=bind_keys)
                    center_x=x+((X-x)//2)
                    center_y=y+((Y-y)//2)
                    o2=self.canvas.create_text(center_x,center_y,text=inset,
                                               tags=bind_keys,anchor=self.text_anchor)
##                    self.canvas.create_oval(center_x-1,center_y-1,center_x+1,center_y+1)
                    o=(o,o2)
                    
                    self.button_hooks[k]=o
                self.apply_bindings()
                self.state.set('inactive')
        self.conf_flag=True
        if self.invoke_flag:
            
            self.invoke_flag=False
            self.state.set('raised')
            self.after(50,self.invoke)
            self.click_flag=False
##            self.invoke()
##            if self.conf_flag:
##                self.invoke_flag=False
                
            
            
class CustomButton:
    def __init__(self,master,mode=None,**kwargs):
        t=type(self)
        if mode is None:
            if isinstance(master,tk.Canvas):
                self.__class__=type(t)('CustomButton',(t,CanvasButton),{})
                mode='canvas'
            else:
                self.__class__=type(t)('CustomButton',(t,LabelButton),{})
                mode='label'
        elif mode=='canvas':
            self.__class__=type(t)('CustomButton',(t,CanvasButton),{})
            mode='canvas'
        else:
            self.__class__=type(t)('CustomButton',(t,LabelButton),{})
            mode='mode'
        super().__init__(master,**kwargs)
        self.mode=mode

##CustomButton=LabelButton

class CloseButton(CustomButton):
    def __init__(self,master,close_what=None,
                 height=mac_size,width=mac_size,**kwargs):
        kwargs['height']=height
        kwargs['width']=width
##        wait=ImageWrapper(self.images.up('wm','red'))
##        up=ImageWrapper(self.images.up('wm','close'))
##        down=ImageWrapper(self.images.down('wm','close'))
        if close_what is None:
            close_what=master
        super().__init__(master,
                         #mode='label',#tint=(255,),#text='x',,font=('Arial',10),
                         raised=('wm','close'),depressed=('wm','close'),inactive=('wm','red'),
                         command=lambda m=close_what:self.close_proc(m),
                         **kwargs)
    def close_proc(self,close_what):
        self.destroy()
        safe_destroy(close_what)
        
class MinimizeButton(CustomButton):
    def __init__(self,master,min_what=None,
                 height=mac_size,width=mac_size,**kwargs):
        kwargs['height']=height
        kwargs['width']=width
##        wait=ImageWrapper(self.images.up('wm','yellow'))
##        up=ImageWrapper(self.images.up('wm','minimize'))
##        down=ImageWrapper(self.images.down('wm','minimize'))
        if min_what is None:
            min_what=self.master
        super().__init__(master,#tint=(255,255,),#text='x',,font=('Arial',10),
                         raised=('wm','minimize'),
                         depressed=('wm','minimize'),
                         inactive=('wm','yellow'),
                         command=self.min_proc,baseargs=(min_what,),
                         **kwargs)
        self.min_flag=False
    def min_proc(self,min_what):
##        print(min_what)
##        min_what.overrideredirect(False)
##        
        
        
        if not self.min_flag:
##            min_what.withdraw()
            
##            min_what.overrideredirect(False)
##            min_what.update_idletasks()
##            min_what.iconify()
            self.stored=[min_what.winfo_width(),min_what.winfo_height(),
                         min_what.winfo_x(),min_what.winfo_y()]
            try:
                top_height=self.master.min_y
            except AttributeError:
                top_height=22
##            try:
##                w=self.master.min_y
##            except AttributeError:
##                w=50
            h=24;w=75
            min_what.geometry('{}x{}+0+{}'.format(w,h,top_height))
            
            self.min_flag=True
        else:

            self.min_flag=False
##            min_what.deiconify()
##            min_what.overrideredirect(True)
            min_what.geometry('{}x{}+{}+{}'.format(*self.stored))
            
class MaximizeButton(CustomButton):
    def __init__(self,master,max_what=None,
                 height=mac_size,width=mac_size,**kwargs):
        kwargs['height']=height
        kwargs['width']=width
##        wait=ImageWrapper(self.images.up('wm','green'))
##        up=ImageWrapper(self.images.up('wm','maximize'))
##        down=ImageWrapper(self.images.down('wm','maximize'))
        if max_what is None:
            max_what=self.master
        super().__init__(master,#tint=(0,255,0),#text='x',,font=('Arial',10),
                         raised=('wm','maximize'),
                         depressed=('wm','maximize'),
                         inactive=('wm','green'),
                         command=lambda m=max_what:self.maximize(m),
                         **kwargs)
        self.stored=[]
        self.max_flag=False
        
    def maximize(self,max_what):
##        print('...?')
        try:
            top_height=self.master.min_y
        except AttributeError:
            top_height=20
        if not self.max_flag:
##            try:
##                x,y,X,Y=self.master.screen_box
##            except AttributeError:
            w=max_what.winfo_screenwidth()
            h=max_what.winfo_screenheight()-top_height
            x=0;y=top_height
##            else:
##                if x is None:
##                    x=0
##                if y is None:
##                    y=top_height
##                if X is None:
##                    X=max_what.winfo_screenwidth()
##                if Y is None:
##                    Y=max_what.winfo_screenheight()
##                w=X-x;h=Y-y
            cw=max_what.winfo_width();ch=max_what.winfo_height()
            cx=max_what.winfo_x();cy=max_what.winfo_y()
            self.stored=[cw,ch,cx,cy]
##            self.stored=[100,100,100,100]
            call=lambda:max_what.geometry('{}x{}+{}+{}'.format(w,h,x,y))
        else:
            call=lambda:max_what.geometry('{}x{}+{}+{}'.format(*self.stored))
        self.max_flag=(not self.max_flag)
        self.after(25,call)
        

##class ButtonStyle


class CustomRadioButton(CustomButton):
    def __init__(self,root=None,variable=None,on=None,off=None,value='',**kwargs):
        state=(not variable is None)
        if state:
            self.variable=variable
            state=variable.get()==value
        else:
            if isinstance(value,str):
                self.variable=tk.StringVar()
            elif isinstance(value,int):
                self.variable=tk.IntVar()
            elif isinstance(value,bool):
                self.variable=tk.BooleanVar()
            else:
                value=str(value)
                self.variable=tk.StringVar()
        self.on_state=tk.BooleanVar(value=state)
        self.value=value
        self.vtrace=self.variable.trace('w',self.trace_changes)
        super().__init__(root,raised=off,depressed=on,inactive=off,command=self.set_variable,**kwargs)
        if self.mode=='label':
            self.disable()
            self.bindings=[Binding('<Button-1>',self.set_variable,add='+')]
            for B in self.bindings:
                B.apply(self)

    def set_variable(self,event=None):
        self.variable.set(self.value)
        
    def trace_changes(self,*args):
        if self.variable.get()==self.value:
            self.on_state.set(True)
            self.state.set('depressed')
        else:
            self.on_state.set(False)
            self.state.set('raised')

    def apply_bindings(self,key='all'):    
        def i_bind(i):
            pass
        def r_bind(r):
            self.canvas.tag_bind(r,'<Button-1>',self.set_variable)
        def d_bind(d):
            self.canvas.tag_bind(d,'<Button-1>',self.set_variable)
        b_hook=self.bind_keys
        if key=='all':
            r=b_hook['raised']
            d=b_hook['depressed']
            r_bind(r)
            d_bind(d)
        elif key=='raised':
            r=b_hook['raised']
            r_bind(r)
        elif key=='depressed':
            d=b_hook['depressed']
            d_bind(d)
            
    def draw(self,*args,**kwargs):
        super().draw(*args,**kwargs)
        if self.on_state.get():
            self.state.set('depressed')
        else:
            self.state.set('raised')
            
class CustomCheckButton(CustomRadioButton):
    def __init__(self,root=None,variable=None,on=None,off=None,
                     value=False,**kwargs):
        if variable is None:
            variable=tk.BooleanVar(value=bool(value))
        super().__init__(root=root,variable=variable,on=on,off=off,value=True,**kwargs)
    def get(self):
        return self.variable.get()
    def set_variable(self,event=None):
        self.variable.set((not self.variable.get()))

class ButtonGrid(tk.Frame):
    
    def __init__(self,root,rows=0,columns=2,arrow_move=False,pass_button=True,button_kwargs=None,
                 command=lambda:None,raised=None,depressed=None,inactive=None,**kwargs):
        from GUITools.FormattingWidgets import FormattingGrid
        super().__init__(root)
        self.button_grid=FormattingGrid(self,rows=rows,columns=columns,arrow_move=arrow_move,**kwargs)
        self.pass_button=pass_button
        self.button_command=command
        if button_kwargs is None:
            button_kwargs={}
        self.button_kwargs=button_kwargs
        self.raised=raised
        self.depressed=depressed
        self.inactive=inactive
        for r in range(max(rows,1)):
            for c in range(max(columns,1)):
                self.AddButton(r,c)
        if arrow_move:
            self.button_grid.bind('<Return>',lambda e:e.widget.invoke(),to='children')
        self.button_grid.pack(fill='both',expand=True)

    def gridConfig(self,**kwargs):
        self.button_grid.gridConfig(**kwargs)
    def configure_rows(self,**kwargs):
        self.button_grid.configure_rows(**kwargs)
    def configure_cols(self,**kwargs):
        self.button_grid.configure_cols(**kwargs)
    def configure_buttons(self,**kwargs):
        self.button_grid.configure_all(**kwargs)
    def DeleteButton(self,i,j):
        self.button_grid.DeleteItem((i,j))
    def AddButton(self,i,j):
        B=self.button_grid.InsertFormat(i,j,CustomButton,
                                     raised=self.raised,depressed=self.depressed,inactive=self.inactive,
                                        **self.button_kwargs)
        command=self.button_command
        if self.pass_button:
            command=lambda B=B,C=command:C(B)
        B.command=command
        return B
        
class CustomChooser(tk.Frame):
    def __init__(self,root,variable,*value_config_pairs,rows=0,columns=2,arrow_move=False,on=None,off=None,**kwargs):
        from GUITools.FormattingWidgets import FormattingGrid
        super().__init__(root,**kwargs)
        self.button_grid=FormattingGrid(self,rows=rows,columns=columns,arrow_move=arrow_move)
        if not isinstance(variable,tk.Variable):
            value_config_pairs+=(variable,)
            variable=None
        self.variable=None
        for pair in value_config_pairs:
            try:
                value,config=pair
                if isinstance(config,str):
                    config=({'text':config},None)
            except (TypeError,ValueError):
                value=pair
                config=(on,off)
            if len(config)==0:
                config=(on,off)
            elif len(config)==1:
                config=(config[0],off)
            b_on,b_off=config
            text=None
            if not b_on is None:
                if 'text' in b_on:
                    text=b_on['text']
            elif not b_off is None:
                if 'text' in b_off:
                    text=b_off['text']
            if text is None:
                text=str(value)
            if self.variable is None:
                if variable is None:
                    if value is True or value is False:
                        variable.tk.BooleanVar(self)
                    elif isinstance(value,int):
                        variable=tk.IntVar(self)
                    elif isinstance(value,float):
                        variable=tk.DoubleVar(self)
                    else:
                        variable=tk.StringVar(self)
                self.variable=variable
            self.button_grid.AddFormat(CustomRadioButton,variable=variable,text=text,on=b_on,off=b_off,value=value)
            if arrow_move:
                self.button_grid.bind('<FocusIn>',lambda e:e.widget.set_variable(),'+',to_all=False,to_children=True)
        self.button_grid.pack(fill='both',expand=True)
    def get(self):
        return self.variable.get()
    def __getattr__(self,attr):
        return getattr(self.button_grid,attr)
