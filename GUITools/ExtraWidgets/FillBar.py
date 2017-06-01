from GUITools.ExtraWidgets.Shared import *

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$    
class FillBar(tk.Canvas):
    def __init__(self,root,current,max,color='green',outline='black',mode='rounded',**add_kw):
    
        kwargs={'highlightthickness':0};kwargs.update(add_kw)
        super().__init__(root,**kwargs)
        self.val=current
        self.max=max
        self.__color=color
        self.__outline=outline
        self.in_conf=False
        self.mode=mode
        self.bar=[]
        self.config(scrollregion=(0,0,1,1))
        self.bind('<Configure>',lambda e:self.update())

    def config(self,*dicts,**kw):
        
        self.in_conf=True
        
        for d in dicts:
            kw.update(d)

        cget_dict={}
        for k in kw:
            if k in ('fill','outline'):
                v=kw[k]
                if k=='fill':
                    self.color=v
                elif k=='outline':
                    self.outline=v
                cget_dict[k]=v
                del kw[k]

        ret=super().config(**kw)
        if len(cget_dict)>0:
            self.update()
        else:
            self.in_conf=False
        return ret

    @property
    def color(self):
        return self.__color
    
    @color.setter
    def color(self,col):
        self.__color=col
        if not self.in_conf:
            self.in_conf=True
            self.update()

    @property
    def outline(self):
        return self.__outline
    
    @outline.setter
    def outline(self,col):
        self.__outline=col
        if not self.in_conf:
            self.in_conf=True
            self.update()
        
    def update(self,new=None,total=None):
        
        for x in self.bar:
            self.delete(x)
        try:
            self.delete(self.fill)
        except:
            pass
        
        self.bar=[]
        
        if new is None:
            new=self.val
        if total is None:
            total=self.max
            
        ratio=new/total
        w=self.winfo_width()
        h=self.winfo_height()
        self.config(scrollregion=(0,0,w,h))
        if self.mode=='rounded':
        
            boundadj=10
            h=h-boundadj
            w=w-boundadj
            cutoff=max([w//25,1])
            length=((w-2*cutoff)*ratio)//1
            
            ywid=max([h//50,2])
            yshrink=ywid//2
            self.draw_props={'cutoff':cutoff,'yshrink':yshrink,'w':w}
            self.bar.extend( (
                self.create_arc(0,0,2*cutoff-1,h-1,
                                fill='black',style='chord',extent=180,start=90),
                self.create_arc(w-(2*cutoff),0,w-1,h-1,
                                fill='black',style='chord',extent=-180,start=90),
                self.create_rectangle(cutoff+yshrink,yshrink,
                                      w-cutoff-yshrink,h-yshrink,
                                      outline='black',width=ywid)
                )
                             )
##            cutoff=cutoff+ywid
            yshrink=ywid
            self.draw_props['yshrink']=yshrink
            self.fill=self.create_rectangle(cutoff,yshrink,cutoff+length,h-yshrink,
                                      fill=self.color,outline='')

        elif self.mode=='pill':
            boundadj=6
            h=h-boundadj if isinstance(boundadj,int) else h*boundadj
            w=w-boundadj
            lw=h//2
            length=(w-lw)*ratio
            l1=length*.75//2
            if ratio==1:
                join_cap='round'
            else:
                join_cap='butt'

            lw=max(lw,0)
            self.bar.extend((
                self.create_line(lw,lw,w,lw,fill='black',width=lw+2,capstyle='round'),
                self.create_line(lw,lw,lw+l1,lw,fill=self.color,width=lw,capstyle='round'),
                self.create_line(lw+length,lw,w,lw,fill='white',width=lw,capstyle='round'),
                self.create_line(lw+l1,lw,lw+length,lw,fill=self.color,width=lw,capstyle=join_cap)
                ))
            
            
        elif '-L' in self.mode:
            linewidth=4
            inc=linewidth//2
            boundadj=10
            h=h-boundadj
            w=w-boundadj
##            h=10;w=35
            length=w*ratio

            width_=max(length-inc,0)
            height_=max(h-inc,0)
            self.fill=self.create_rectangle(inc,inc,width_,height_,fill=self.color,outline='')
            if self.mode=='right-L':
                coords=(w,0,w,h,0,h)
            else:
                coords=(inc,0,inc,h,w,h)
            arrowhead=(0,5,3)
            self.bar.extend((
                    self.create_line(*coords,width=linewidth,fill='black',
                                     arrow='last',arrowshape=arrowhead),
                    ))
                        
        elif self.mode=='rectangular':
            pass

        self.in_conf=False

