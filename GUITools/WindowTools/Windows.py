from GUITools.Shared import *
from GUITools.WindowTools.Buttons import *
from GUITools.WindowTools.WindowStyles import WindowStyler
##from GUITools import SharedData
##from GUITools.ImageTools import ImageWrapper

mac_bar_height=22
class WindowGrab(tk.Canvas):
    image_flag=pil_flag
    def __init__(self,window,to_move=None,bg='gray',
                 height=mac_bar_height,width=mac_bar_height,
                 vector=(1,1),padx=0,pady=0,screen_box=(None,mac_bar_height,None,None),
                 buttons=('kill','min','max'),
                 title='Custom Window',
                 relief='raised',highlightthickness=0,bd=2,
                 fill='black',font='systemFont',
                 orientation='top',button_positioning='left',
                 image=('mac','bar'),
                 **kwargs):
        self.fill=fill
        self.font=font
        self.orientation=orientation
        self.button_positioning=button_positioning
        self.background_image=''
        if to_move is None:
            to_move=window
        self.to_move=to_move
        r=to_move
##        print(r)
        def rec_check(r):
            if hasattr(r,'geometry'):
                ret=r
            else:
                ret=rec_check(r.master)
            return r
        self.abs_root=rec_check(r)
        kwargs['height']=height
        kwargs['width']=width
        kwargs['bg']=bg
        kwargs['relief']=relief
        kwargs['highlightthickness']=highlightthickness
        kwargs['bd']=bd
        super().__init__(window,**kwargs)
        self['scrollregion']=(0,0,3000,3000)
        self.bind('<B1-Motion>',self.grab_drag)
        self.bind('<ButtonRelease-1>',self.end_action)
        self.pad=bd=7
        self.bd_store=None
        self.button_spacing=2
        self.button_width=mac_bar_height
##        but_w=self.button_width+self.button_spacing
        self.screen_box=screen_box
        self.buttons={}
        self.button_order=[]
        self.waiter=tk.BooleanVar(value=False)
        self.draw_buttons(buttons)

        if image:
            self.set_image(*image)
            
        self.last=None
        self.vector=vector
        self.title_hold=title
        self.text_hook=None
        self.bind('<Expose>',self.initialize)
        self.bind('<Configure>',self.resize)

    def initialize(self,event=None):
        
        if not self.winfo_viewable():
            self.wait_visibility(self)
        j=0
        self.resize(override=True)
        for i,b in self.buttons.items():
            j+=1
            if isinstance(b,CanvasButton):
                b.state.set('inactive')
            else:
                b.after(100,b.draw)
        if self.text_hook is None:
            mx,my,a,a,ank=self.button_bbox(j,total=1+len(self.buttons))
            if self.orientation in ('top','bottom'):
                wrap=0
            else:
                wrap=1
            self.text_hook=self.create_text(mx,my,
##                                            width=self.button_spacing,
##                                            height=self.winfo_height()-2*self.pad,
                                        text=self.title_hold,anchor=ank,width=wrap,
                                            fill=self.fill,font=self.font)
    def draw_buttons(self,buttons):
##        if self.winfo_height()>1 and self.winfo_width()>2:
            
            window=self.to_move
            for x in buttons:
                i=0
                if x=='kill':
                    b=CloseButton(self,window,bg=self['bg'])
                elif x=='min':
                    b=MinimizeButton(self,window,bg=self['bg'])
                elif x=='max':
                    b=MaximizeButton(self,window,bg=self['bg'])
                else:
                    b=x
                    x=b.__name_
                mx,my,mw,mh,ank=self.button_bbox(i,total=len(buttons)+1)
                if isinstance(b,(tk.Button,LabelButton)):
                    bid=self.create_window(mx,my,width=mw,height=mh,
                                           window=b,anchor=ank)
                else:
                    mh=mw
                    b.draw((mx,my),width=mw,height=mh,anchor=ank)
                    bid=b.bind_key
                self.buttons[x]=b
                self.buttons[bid]=b
                self.button_order.append(bid)
    ##            b.draw()
                i+=1
##            self.waiter.set(True)
##        else:
##            self.after(25,lambda b=buttons:self.draw_buttons(b))
    
    def button_bbox(self,i,total=None):
        orientation=self.orientation;button_positioning=self.button_positioning
##        mbd=int(self['bd'])
##        ht=int(self['highlightthickness'])
        bd=self.pad#-(mbd+ht)
        w=self.winfo_width()
        
        but_w=self.button_width+self.button_spacing
        if  orientation in ('top','bottom'):
            ank='n'
            mw=self.button_width-bd;mh=self.winfo_height()-2*bd#;print(mh)
            
            if button_positioning=='left':
                ank+='w'
                mx=bd+i*but_w;my=bd
            elif button_positioning=='center':
                mx=int(w/2-(total-i)*but_w+bd);my=bd
                ank+='w'
            else:
                mx=w-(bd+i*but_w);my=bd
                ank+='e'
        else:
            ank='w'
            mw=self.winfo_width()-2*bd;mh=self.button_width-bd
            if button_positioning=='top':
                ank='n'+ank
                mx=bd;my=bd+i*but_w
            elif button_positioning=='center':
                pass
            else:
                ank='s'+ank
                mx=bd;my=self.winfo_height()-bd+i*but_w

        return (mx,my,mw,mh,ank)

    def reload_image(self):
        if not self.background_image=='':
            self.delete(self.background_image.hook)
            self.background_image.reset()
            self.set_image(self.background_image)
        
    def set_image(self,*path_elements,mode='stretch'):
        h=self.winfo_height()
        w=self.winfo_width()
        if not self.image_flag:
            path_elements=['']
        if path_elements[0]=='':
            if not self.background_image is '':
                self.delete('background_image')
                self.background_image=''
                bd=int(self.bd_store[0])
                ht=int(self.bd_store[1])
                self.bd_store=None
                self['bd']=bd
                self['highlightthickness']=ht
        else:
            if self.bd_store is None:
                bd=self['bd']
                self.bd_store=(bd,self['highlightthickness'])
                self['bd']=0
                self['highlightthickness']=0
            if all((isinstance(x,str) for x in path_elements)):
                f=SharedData.ButtonImages.up(*path_elements)
            else:
                f=path_elements[0]
            if isinstance(f,str):
                f=ImageWrapper(f)
            
            self.background_image=B=f
##            print(self.background_image)
            r_q=0
            if self.orientation=='left':
                r_q=90
            elif self.orientation=='right':
                r_q=-90
            if r_q!=0:
##                print(r_q)
                B.rotate(r_q,expand=True)
                B.set_base_image()
                B.show()
            B.hook=self.create_image(0,0,image=B.Tk,anchor='nw',
                                     tags='background_image')
            self.tag_lower(B.hook)
##            self.resize(override=True)
        bd=int(self['bd'])
        ht=int(self['highlightthickness'])
        h=h-2*(bd+ht)
        w=w-2*(bd+ht)
##        print(bd,ht)
        if h>1:
            self['height']=h
        if w>1:
            self['width']=w
        self.resize(override=True)
    def resize(self,event=None,override=False):
        
        if not self.background_image=='':
            w=self.winfo_width()
            h=self.winfo_height()
            self.background_image.reset()
            self.background_image.resize((w,h))
            self.itemconfig(self.background_image.hook,
                            image=self.background_image.Tk)
        i=0
        t=len(self.button_order)+1
        if override or not (self.orientation=='top' and self.button_positioning=='left'):
            for k in self.button_order:
                b=self.buttons[k]
                mx,my,mw,mh,a=self.button_bbox(i,total=t)
                if isinstance(b,(tk.Button,LabelButton)):
                    
                    self.coords(k,mx,my)
                    self.itemconfig(k,anchor=a)
                else:
                    #print(mw,mh)
                    b.set_position(mx,my,mw,mh,a)
##                    b.draw((mx,my),width=mw,height=mh,anchor=a)
##                    try:
##                        self.coords(b.bind_key,mx,my,mx+mw,my+mh)
##                    except:
##                        self.coords(b.bind_key,mx,my)
##                        self.itemconfig(k,anchor=a)#,width=mw,height=mh)
                i+=1
            mx,my,mw,mh,a=self.button_bbox(i,total=t)
            try:
                self.coords(self.text_hook,mx,my)
            except (TclError,AttributeError):
##                print(mx,my)
                pass
            else:
                wrap=0
                if self.orientation in ('right','left'):
                    wrap=1
                self.itemconfig(self.text_hook,width=wrap,anchor=a)
                
                
    def title(self,new=None):
        if new is None:
            return self.itemcget(self.text_hook,'text')
        self.itemconfig(self.text_hook,text=new)
        self.title_hold=new

    def config(self,**kwargs):
        resize_call=False
        text_kwargs={}
        for k in ('fill','font'):
            if k in kwargs:
                v=kwargs[k]
                text_kwargs[k]=v
                setattr(self,k,v)
                del kwargs[k]
        if text_kwargs:
            self.itemconfig(self.text_hook,**text_kwargs)
        for x in ('button_positioning','orientation','pad',
                  'button_spacing','button_width','screen_box'):
            if x in kwargs:
                setattr(self,x,kwargs[x])
                del kwargs[x]
                resize_call=True
        if 'image' in kwargs:
            k=kwargs['image']
            if isinstance(k,str):
                k=(k,)
            self.set_image(*k)
            resize_call=True
            del kwargs['image']
        super().config(**kwargs)
        if 'bg' in kwargs:
            c=kwargs['bg']
            for x,b in self.buttons.items():
                b['bg']=c
        if resize_call:
            self.resize(override=True)
    def button_config(self,button='kill',**kwargs):
##        pass
##        if not self.waiter.get():
##            self.wait_variable(self.waiter)
        self.buttons[button].config(**kwargs)

    def toggle_buttons(self,mode='active'):
        if mode=='active':
            for k,w in self.buttons.items():
                if isinstance(w,CanvasButton):
                    w.state.set('inactive')
                else:
                    self.itemconfig(w,state='normal')
        else:
            for k,w in self.buttons.items():
                if isinstance(w,CanvasButton):
                    w.hide()
                else:
                    self.itemconfig(w,state='hidden')
    def grab_drag(self,event):
##        self.move_points.append((event.x,event.y))
##        if len(self.move_points)>1:
##            x1,y1=self.move_points[0]
##            x2,y2=self.move_points[1]
##            self.move_window((x2-x1),(y2-y1))
##            self.move_points=[]

##        try:
##            rel=self.rel_pos[0]
        if self.last is None:
##            last=list(self.abs_root.winfo_pointerxy())
##            last[0]+=-self.abs_root.winfo_x()
##            last[1]+=-self.abs_root.winfo_y()
            self.last=(event.x,event.y)#(event.x_root,event.y_root)
##        x,y=self.abs_root.winfo_pointerxy()
##        x+=-self.abs_root.winfo_x()
##        y+=-self.abs_root.winfo_y()
            
        
##        print(x,y)
##        print(self.last)
        move_func=self.move_window
##        print(move_func)
##        print(x,y,*self.last)
        
        offset_x=self.to_move.winfo_rootx()-self.winfo_rootx()
        offset_y=self.to_move.winfo_rooty()-self.winfo_rooty()
##        cursor_diff_x=event.x-self.last[0]
##        cursor_diff_y=event.y-self.last[1]
        x_move=event.x-self.last[0]
        y_move=event.y-self.last[1]
##        print(x_move,y_move)
        x=x_move#offset_x+x_move
        y=y_move#offset_y+y_move

        
##        print(x,y)
        move_func(x,y)#,to=True)
##        return 'break'
                      
    def end_action(self,event):
        if not self.last is None:
            self.grab_drag(event)
            self.last=None
        
    def move_window(self,dx,dy,window=None,to=False):

        if window is None:
            window=self.to_move
        m=window
        w=m.winfo_width()
        h=m.winfo_height()
        if to:
            x=dx;y=dy
        else:
            x=m.winfo_x();x=int(x+self.vector[0]*dx)
            y=m.winfo_y();y=int(y+self.vector[1]*dy)
##        print(x,y)
        x_flag=True
        y_flag=True
        mx,my,Mx,My=self.screen_box
##        print((x,y,w,h),(mx,my,Mx,My))
        if mx is None:
            mx=0
        else:
            if x<mx:
                x=mx
                x_flag=False            
        if not Mx is None:
            if x+w>Mx:
                x=max(Mx-w,mx)
                x_flag=False
        if my is None:
            my=0
        else:
            if y<my:
                y=my
                y_flag=False 
        if not Mx is None:
            if y+h>My:
                y=max(My-h,my)
                y_flag=False
##        print
        new='{}x{}+{}+{}'.format(w,h,x,y)
        old=m.geometry()
##        print(new,old,(dx,dy))
        flag=new!=old
        if flag:
            m.geometry(new)
##        print(flag)
        return (x_flag,y_flag)
        
class Expander(tk.Frame):
    def __init__(self,master,expand_window=None,
                 activebg='grey',active_width=2,activebd='flat',
                 vector=(2,0),screen_box=(75,25,None,None),**kwargs):
        if expand_window is None:
            expand_window=master
        self.to_expand=expand_window
        
        self.vector=vector
        x,y=[abs(q) for q in self.vector]
        if x>y:
            c='resizeleftright'
            w=active_width
            h=0
        elif y>x:
            c='resizeupdown'
            h=active_width
            w=0
        else:
            h=active_width
            w=active_width
            c='crosshair'
        super().__init__(master,width=w,height=h,**kwargs)
        self.cursor=c
        self.activebg=activebg
        self.activewidth=active_width
        self.activebd=activebd
        self.screen_box=screen_box
        self.config(cursor=self.cursor)
        self.last=None
        self.bind('<B1-Motion>',self.grab_expand)
        self.bind('<ButtonRelease-1>',self.end_action)
        self.bind('<Enter>',self.ready)
        self.bind('<Leave>',self.deactivate)

    def grab_expand(self,event):
##        x,y=self.winfo_pointerxy()
        if self.last is None:
            self.last=self.winfo_pointerxy()
        x,y=self.winfo_pointerxy()
##        x=event.x;y=event.y
##        self.move_points.append((x,y))
##        if len(self.move_points)>1:
##            x1,y1=self.move_points[0]
##            x2,y2=self.move_points[1]
##            self.expand_window((x2-x1),(y2-y1))
##            self.move_points=[]
        self.expand_window(x-self.last[0],y-self.last[1])
        self.last=(x,y)

    def config(self,**kwargs):
        if 'size' in kwargs:
            v=kwargs['size']
            if self.vector[0]:
                super().config(width=v)
            if self.vector[1]:
                super().config(height=v)
            del kwargs['size']
        for k in ('activebg','activewidth','activebd'):
            if k in kwargs:
                setattr(self,k,kwargs[k])
                del kwargs[k]
        
        super().config(**kwargs)
    def ready(self,event=None):
        keys=('cursor','bg','bd','relief')
        self.old_ops={x:self[x] for x in keys}
        ops={'cursor':self.cursor,
             'bg':self.activebg,
             'relief':self.activebd
             }
        if self.vector[0]:
            self.old_ops['width']=self.winfo_width()
            ops['width']=self.activewidth
        if self.vector[1]:
            self.old_ops['height']=self.winfo_height()
            ops['height']=self.activewidth
        super().config(**ops)
##        self.after(100,
##                   lambda:self.config(bg=self.old_bg,bd=self.activewidth)
##                   )
    def deactivate(self,event=None):
        super().config(**self.old_ops)
        self.old_ops={}
    def end_action(self,event):
        self.last=None
    def expand_window(self,dx,dy,to=False):
        
        m=self.to_expand
        vx,vy=v=self.vector
        w=cw=m.winfo_width();h=ch=m.winfo_height()
        x=m.winfo_x();y=m.winfo_y()

        if not to:
            w=int(w+vx*dx)
            h=int(h+vy*dy)
        else:
            if vx:
                w=dx-x
                dx=w-cw
            if vy:
                h=dy-y
                dx=h-ch
        
        if vx<0:
            x+=dx
####            w=cw
        if vy<0:
            y+=dy
##            diff=(ch-h)
##            y=dy
        
##        print(m.geometry(),new)
        mx,my,Mx,My=self.screen_box
        if (not mx is None) and w<mx:
            w=mx
        elif (not Mx is None) and w>Mx:
            w=Mx
        if (not my is None) and h<my:
            h=my
        elif (not My is None) and h>My:
            h=My
        new='{}x{}+{}+{}'.format(w,h,x,y)
        m.geometry(new)
    

class CustomWindow:
    r_props={'winfo_{}'.format(x) for x in ('height','width',
                                            'x','y',
                                            'viewable','pointerxy',
                                            )}|{'quit'}
    Styler=WindowStyler()
    def __init__(self,master=None,
                 grab_bar=True,
                 expand=None,
                 orientation='top',
                 style='classic',
                 screen_box=(None,22,None,None),
                 geom=(575,515,0,mac_bar_height),
                 use_wm=False,
                 **kwargs):
        if master is None:
            master=tk.Tk()
            self.parent=None
        else:
            self.parent=master
            master=tk.Toplevel()

        if use_wm:
            expand=(None,None,None,None)
            grab_bar=False
        else:
##            master.update_idletasks()
            hide_decorations(master)
            
##            master.bind('<Expose>',lambda e:master.overrideredirect(True))
##            master.deiconify()
##            master.overrideredirect(True)
            
##            master.update_idletasks()
        self.r=master
        self.main=tk.Frame(self.r)
        self.w=WindowGrab(self.r,self,orientation=orientation)
#                          button_positioning=button_positioning)
        self.e_t=Expander(self.r,self,vector=(0,-1))
        self.e_b=Expander(self.r,self,vector=(0,1))
        self.e_l=Expander(self.r,self,vector=(-1,0))
        self.e_r=Expander(self.r,self,vector=(1,0))
        self.e_nw=Expander(self.r,self,vector=(-1,-1))
        self.e_ne=Expander(self.r,self,vector=(1,-1))
        self.e_se=Expander(self.r,self,vector=(1,1))
        self.e_sw=Expander(self.r,self,vector=(-1,1))
        
        self.f=tk.Frame(self.r,**kwargs)

        self.show_grab_bar(grab_bar)
        if expand is None:
            if orientation=='top':
                expand=(True,True,False,True)
            if orientation=='left':
                expand=(False,True,True,True)
            if orientation=='right':
                expand=(True,False,True,True)
            elif orientation=='bottom':
                expand=(True,True,True,False)
        self.expand_tuple=expand
        self.allow_expand(*expand)
        
        self.screen_box=screen_box
##        for i in range(1,3):
##            self.r.grid_rowconfigure(i,weight=1,minsize=2)
##        for i in range(0,3):
##            self.r.grid_columnconfigure(i,weight=1,minsize=2)
        self.r.grid_columnconfigure(1,weight=1)
        self.r.grid_rowconfigure(1,weight=1)

        self.f.grid(row=1,column=1,sticky='nsew')

        self.frame=self.f

        self.child_windows=set()
        self.bind('<Configure>',self.readjust)
        self.bind('<Command-w>',lambda:self.w.buttons['kill'].invoke())
        self.w.bind('<Button-1>',lambda e:self.focus_set())

        self.title=self.w.title
        if len(geom)==2:
            self.geometry('{}x{}'.format(*geom))
        else:
            self.geometry('{}x{}+{}+{}'.format(*geom))

        self.Styler.apply(self,style)

    def destroy(self,destroy_function=safe_destroy):
        return destroy_function(self.r)
    
    def geometry(self,string=None):
        if string is None:
            return self.r.geometry(string)
        wx,wy,Wx,Wy=self.screen_box
        w,rest=string.split('x')
        rest=rest.split('+')
        if len(rest)==1:
            h=rest[0]
            x=self.winfo_x()
            y=self.winfo_y()
        elif len(rest)==2:
            h=rest[0]
            x=rest[1]
            y=self.winfo_y()
        else:
            h=rest[0]
            x=rest[1]
            y=rest[2]

        w,h,x,y=(int(q) for q in (w,h,x,y))

        xf=wx is None;yf=wy is None
        XF=Wx is None;YF=Wy is None
        if not (XF or xf):
            if w>(Wx-wx):
                w=(Wx-wx)
        if not (YF or yf):
            if h>(Wy-wy):
                h=(Wy-wy)
        if  (not xf) and x<wx:
            x=wx
##            print(x)
        if  (not yf) and y<wy:
            y=wy
##            print(y)
        if (not XF) and (x+w)>Wx:
##            if x>Wx:
                x=Wx-w
##            else:
##                w=Wx-x
        if (not YF) and (y+h)>Wy:
##            if y>Wy:
                y=Wy-h
##            else:
##                h=Wy-y
        self.r.geometry('{}x{}+{}+{}'.format(w,h,x,y))
        
    def screen_restrict(self,min_x='',min_y='',max_x='',max_y='',
                        min_relx='',min_rely='',max_relx='',max_rely=''):
        wx,wy,Wx,Wy=self.screen_box
##        ww,wh,Ww,Wh=self.e_b.screen_box

        w=self.winfo_screenwidth()
        h=self.winfo_screenheight()            
        if min_x!='':
            if min_x is None:
                wx=min_x
            else:
                if min_relx=='':
                    min_relx=0
                wx=min_x+(w*min_relx)
        elif min_relx!='':
            wx=w*min_relx
            
        if min_y!='':
            if min_y is None:
                wy=min_y
            else:
                if min_rely=='':
                    min_rely=0
                wy=min_y+(h*min_rely)
        elif min_rely!='':
            wy=h*min_rely
            
        if max_x!='':
            if max_x is None:
                Wx=max_x
            else:
                if max_relx=='':
                    max_relx=0
                Wx=max_x+(w*max_relx)
        elif max_relx!='':
            Wx=w*max_relx

        if max_y!='':
            if max_y is None:
                Wy=max_y
            else:
                if max_rely=='':
                    max_rely=0
                Wy=max_y+(h*max_rely)
        elif max_rely!='':
            Wy=h*max_rely

            
        self.screen_box=(wx,wy,Wx,Wy)
        self.w.screen_box=(wx,wy,Wx,Wy)
        self.geometry(self.geometry())
##        wx,wy,Wx,Wy=self.screen_box                
            
            
    def show_grab_bar(self,value=True,side=None):
        if side is None:
            side=self.w.orientation
        if value:
            if side=='top':
                row=0;column=0;rowspan=1;columnspan=3;sticky='new'
            elif side=='left':
                row=0;column=0;rowspan=3;columnspan=1;sticky='nsw'
            elif side=='right':
                row=0;column=2;rowspan=3;columnspan=1;sticky='nse'
            else:
                row=2;column=0;rowspan=1;columnspan=3;sticky='sew'
##            self.w.place(x=0,y=0,anchor='nw')#,relwidth=1)
            self.w.grid(row=row,column=column,
                        rowspan=rowspan,columnspan=columnspan,
                        sticky=sticky)
        else:
            self.w.grid_forget()

        self.grab_visible=value
    def redraw_bar(self):
        if self.grab_visible:
            self.show_grab_bar(False)
            self.show_grab_bar(True)
        
    def allow_expand(self,left=None,right=None,top=None,bottom=None):
        if left is None and right is None and top is None and bottom is None:
            return self.expand_tuple
        tup=self.expand_tuple
        while len(tup)<4:
            tup=tup+(None,)
        exp=[None,None,None,None]
        if left:
            exp[0]=True
            self.e_l.grid(row=1,column=0,rowspan=1,sticky='nsw')
        elif left is None:
            exp[0]=tup[0]
        else:
            exp[0]=False
            self.e_l.grid_forget()
        if right:
            exp[1]=True
            self.e_r.grid(row=1,column=2,rowspan=1,sticky='nse')
        elif right is None:
            exp[1]=tup[1]
        else:
            exp[1]=False
            self.e_r.grid_forget()
        if top:
            exp[2]=True
            self.e_t.grid(row=0,column=1,columnspan=1,sticky='ewn')
        elif top is None:
            exp[2]=tup[2]
        else:
            exp[2]=False
            self.e_t.grid_forget()
        if bottom:
            exp[3]=True
            self.e_b.grid(row=2,column=1,columnspan=1,sticky='ews')
        elif bottom is None:
            exp[3]=tup[3]
        else:
            exp[3]=False
            self.e_b.grid_forget()
            
        if left and top:
            self.e_nw.grid(row=0,column=0,sticky='nw')
        else:
            self.e_nw.grid_forget()
        if right and top:
            self.e_ne.grid(row=0,column=2,sticky='ne')
        else:
            self.e_ne.grid_forget()
        if left and bottom:
            self.e_sw.grid(row=2,column=0,sticky='sw')
        else:
            self.e_sw.grid_forget()
        if right and bottom:
            self.e_se.grid(row=2,column=2,sticky='se')
        else:
            self.e_se.grid_forget()

        self.expand_tuple=tuple(exp)

    def rotate_bar(self,new_orientation,flip=None):
        b=self.w.button_positioning
        o=self.w.orientation
        e=self.allow_expand()

        if isinstance(new_orientation,str):
                r_map={
                    'top':{'left':90,'bottom':180,'right':270},
                    'left':{'bottom':90,'right':180,'top':270},
                    'right':{'top':90,'left':180,'bottom':270}
                    }
                d=r_map[o][new_orientation]
        else:
            d=int(new_orientation)
        if d>0:
            rotate={
                90:{'top':'left','left':'bottom','bottom':'right','right':'top'},
                180:{'top':'bottom','left':'right','bottom':'top','right':'top'},
                270:{'top':'right','left':'top','bottom':'left','right':'bottom'}
                }
            r_map=rotate[d]
            new_o=r_map[o]
            new_bp=r_map[b]
            new_l=r_map['left']
            new_r=r_map['right']
            new_t=r_map['top']
            new_b=r_map['bottom']
            new_e=['left','right','top','bottom']
            for x,v in zip(
                (new_l,new_r,new_t,new_b),
                [bool(x) for x in e]
                ):
                i=new_e.index(x)
                new_e[i]=v
            if flip is None:
                if new_o in ('left','right'):
                    new_bp='top'
                else:
                    new_bp='left'
            self.bar_config(orientation=new_o,button_positioning=new_bp)
            self.allow_expand(*new_e)
            
            if flip:
                if new_o in ('left','right'):
                    mode='vertical'
                else:
                    mode='horizontal'
                self.flip_bar(mode=mode)
            
    def flip_bar(self,mode='horizontal'):
        o=self.w.orientation
        b=self.w.button_positioning
        flip_map={'v':
                  {'top':'bottom','left':'left','right':'right','bottom':'top'},
                  'h':
                  {'top':'top','left':'right','right':'left','bottom':'bottom'}
                  }
        f_map=flip_map[mode[0]]
        new_o=f_map[o]
        new_b=f_map[b]
        self.bar_config(orientation=new_o,button_positioning=new_b)
        
    def readjust(self,event=None):
##        self.w.place(x=0,y=0,relwidth=1,height=22)
        self=self.r
        w=self.winfo_width();h=self.winfo_height()
        x=self.winfo_x();y=self.winfo_y()
        mx=self.winfo_screenwidth();my=self.winfo_screenheight()
        diff_x=mx-(w+x);diff_y=my-(h+y)
        conf_f=False
        if diff_x<0:
            w=mx-x
            conf_f=True
        if diff_y<0:
            h=my-y
            conf_f=True
        if conf_f:
            self.geometry("{}x{}+{}+{}".format(w,h,x,y))

    def focus_set(self,w=None):
        if w is None:
            for x,w in self.f.children.items():
                break
        if not w is None:
            self.overrideredirect(False)
            w.focus_set()
            binding=None
            binding=w.bind('<FocusIn>',lambda e:(self.overrideredirect(True),
                                               w.unbind(binding)),'+')
##        self.after(5000,lambda:(print('...'),
##                                self.overrideredirect(True))
##                   )
##            self.overrideredirect(True)
##            w.focus_force()
##            w.grab_set()
    def __str__(self):
        return str(self.r)
    def __getattr__(self,attr):
##        print(self.r_props)
        if attr in ('f','r'):
            return super().__getattribute__(attr)
        if attr in self.r_props:
            E=getattr(self.r,attr)
        else:
            try:
                E=getattr(self.f,attr)
            except AttributeError:
                E=getattr(self.r,attr)
        return E

    
    def bar_config(self,**kwargs):
        self.w.config(**kwargs)
        if 'orientation' in kwargs:
            self.redraw_bar()
    def resizer_config(self,**kwargs):
        for x in (
            self.e_nw,self.e_t,self.e_ne,
            self.e_l,self.e_r,
            self.e_sw,self.e_b,self.e_se):
            x.config(**kwargs)
    def config(self,**kwargs):
        for k,v in kwargs.items():
            try:
                self.f[k]=v
            except:
                self.r[k]=v
    def button_config(self,button,**kwargs):
        self.w.button_config(button,**kwargs)
    def __getitem__(self,attr):
        return self.f.__getitem__(attr)
    def __setitem__(self,attr,val):
        self.f.__setitem__(attr,val)

    def restyle(self,newstyle):
        self.Styler.apply(self,newstyle)
        
class ParentWindow(CustomWindow):
    def __init__(self,master=None,windows=(),**kwargs):
        super().__init__(master,**kwargs)
        self.child_windows=set(windows)
        self.w.move_window=self.move_windows

    def destroy(self):
        for x in self.child_windows:
            x.destroy()
        self.r.destroy()

    def add_child(self,window=None,relative_geom=(1,1,.5,.5),**kwargs):
        if window is None:
            g=self.geometry()
            w,rest=g.split('x')
            h,x,y=rest.split('+')
            geom=[int(x) for x in (w,h,x,y)]
            #geom[2]+=10
            #geom[3]+=10
            i=0
            for x in relative_geom:
                if not x is None:
                    if i<2:
                        geom[i]=int(geom[i]*x)
                    else:
                        geom[i]+=int(geom[i-2]*x)
                    #geom[i]+=v*x
                i+=1
            
            window=CustomWindow(self,geom=geom,**kwargs)
##            window.show_grab_bar(False)
        self.child_windows.add(window)
        return window

    def move_windows(self,dx,dy,to=False):
        move_func=type(self.w).move_window
        def move(window,x_diff,y_diff,to):
            return move_func(self.w,x_diff,y_diff,window=window,to=to)
        base_x=self.winfo_x()
        base_y=self.winfo_y()
        S=self.geometry()
        x_f,y_f=move(self,dx,dy,to)
        G=self.geometry()
        if S!=G:
            w,rest=G.split('x')
            h,x,y=rest.split('+')
            new_x=int(x)
            new_y=int(y)
            
            dx=new_x-base_x;dy=new_y-base_y
##            print(dx,dy)
            dead=[]
            for x in self.child_windows:
                try:
                    ddx=x.r.winfo_x()
                except:
                    dead.append(x)
                    continue
                ddy=x.r.winfo_y()
                new_x=dx+ddx
                new_y=dy+ddy
                move(x,new_x,new_y,True)
            for x in dead:
                self.child_windows.remove(x)
