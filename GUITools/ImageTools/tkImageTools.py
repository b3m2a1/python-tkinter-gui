#Write wrappers for bitmaps and photoimages that allow one to do (admittedly slow)
#work on them for when PIL is unavailable

import tkinter as tk
from GUITools.ColorTools import TkColorOperations

class TkPhotoImage(tk.PhotoImage):
    alpha_cutoff=3
    show_root=None
    def __init__(self,source=None,width=None,height=None,data=None):
        self.color_ops=TkColorOperations(self)
        if isinstance(source,str):
            try:
                f=open(file)
            except:
                data=source
            else:
                data=f.read()
                f.close()
        elif not source is None:
            try:
                width,height=source.dimensions
            except AttributeError:
                try:
                    width=source.width()
                    height=source.height()
                except AttributeError:
                    if width is None:
                        width=16
                    if height is None:
                        height=16
            data=self.format_data(source,width,height)
        super().__init__(width=width,height=height)
##        self.put('#000',(0,0))
##        print(self.get(0,0))
##        self.putdata(data)
        self.copy_pixels(source)

    def putdata(self,data,position=(0,0)):
        if isinstance(data,str):
            self.put(data,to=position)
        else:
            x,y=position
            for s in data:
                if isinstance(s,str):
                    self.put(s,(x,y))
                    y+=1
                else:
                    pos,s=s
                    self.put(s,pos)
                
    def copy_pixels(self,iterable):
        #should find a way to smooth out artefacts
        w=self.width()
        h=self.height()
        i=j=0
##        last=[]
        for p in iterable:
            if len(p)==2:
                p,pos=p
            if len(p)==4:
                a=p[3]
                p=p[:3]
            else:
                a=self.alpha_cutoff+1
            if a>self.alpha_cutoff:
                c=self.color_ops.rgb_hex(p)
##                last.append(c)
                self.put(c,(i,j))
##            last=0
            i+=1
            if i>=w:
                i=0
                j+=1
                if j>=h:
                    break
    def format_data(self,iterable,width=None,height=None,to=(0,0)):
##        iterable.show()
        
        color_hex=self.color_ops.rgb_hex
        rows=[None]*height
        i,j=to
        if width is None:
            width=self.width()
        if height is None:
            height=self.height()
        iterable=iter(iterable)
        bit=next(iterable)
        row=[(j,i),'']
        j=1
        def bit_alpha(bit):
            if len(bit)==4:
                a=bit[3]
                bit=bit[:3]
            else:
                a=self.alpha_cutoff+1
            chex=' '+color_hex(bit)
            return (chex,a)
        def new_row(row=row):
            if row[1]:
                row[1]='{'+row[1]+'}'
                rows[i]=tuple(row)
            row[0]=(i,j);row[1]=''
        if len(bit)==2:
            bit,pos=bit
            x,y=pos
##            print(x,y)
            last_y=y
            bit,alpha=bit_alpha(bit)
            if alpha>self.alpha_cutoff:
                row[1]+=bit
            else:
                new_row(row)
            for bit in iterable:
                bit,pos=bit
                x,y=pos
                if y!=last_y:
                    last_y=y
                    new_row()
                    i+=1
                    row[0]=(j,i)
                    if i>=height:
                        break
                bit,a=bit_alpha(bit)
                if a>self.alpha_cutoff:                        
                    row[1]+=bit
                else:
                    new_row()
        else:
            bit,a=bit_alpha(bit)
            if a>self.alpha_cutoff:
                row[1]+=bit
            for bit in iterable:
                bit,a=bit_alpha(bit)
                if a>self.alpha_cutoff:
##                    print('.',end='')
                    row[1]+=bit
                else:
                    new_row()
                j+=1
                if j>=width:
                    new_row()
                    j=0
                    i+=1
                    row[0]=(j,i)
                    if i>=height:
                        break
        rows=[row for row in rows if not row is None]
##        print([r[0] for r in rows])
        return rows
    
    def copy_from(self,source):
        if not isinstance(source,str):
            data=self.format_data(source)
        else:
            data=source
        self.blank()
        self.putdata(data)

    def show(self):
##        from GUITools.FormattingTools import FormattingGrid
        cls=type(self)
        if cls.show_root is None:
            cls.show_root=T=tk.Toplevel()
            T.bind('<Destroy>',lambda e,cls=cls:setattr(cls,'show_root',None))
        T=cls.show_root
        self.show_label=tk.Label(T,text=str(self),image=self)
        self.show_label.grid()
        
