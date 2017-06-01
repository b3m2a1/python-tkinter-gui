from GUITools.ExtraWidgets.Shared import *

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class TabFrame(tk.Frame):

    class WTE:
        def __init__(self,wig,button,entry,callback=None):
            self.widget=wig
            self.tab=button
            self.entry=entry
            self.tup=(wig,button,entry)
            if not callback:
                callback=lambda a,b:None
            self.callback=callback
            self.tab.bind('<Button-1>',lambda e:self.call(e),add='+')
            self.entry.bind('<Button-1>',lambda e:self.call(e),add='+')
        def __getitem__(self,ind):
            return self.tup[ind]
        def call(self,event):
            self.callback(event,self.widget)       
        
    def __init__(self,root,*initialTabs,name=None,new=None,
                 newargs=(),newkwargs=None,**kwargs):

        super().__init__(root,**kwargs)
        if not new:
            new=RichText
        if not name:
            name=type(self).__name__
        self.name=name
        self.buttons=tk.Frame(self)
        self.frames=tk.Frame(self,bg='black',bd=1)
        self.map={}
        self.buttons.grid(column=0,row=0,sticky='ew')
        addF=tk.Frame(self.buttons,bd=1,bg='black')
        add=tk.Label(addF,text='+',height=1)
        add.pack()
        addF.pack(side='right',anchor='center')
        self.dir=tf.TemporaryDirectory()
        self.untNum=0
        if not new:
            new=RichText
        self.newType=new
        if not newkwargs:
            newkwargs={}
        self.newkwargs=newkwargs
        self.newargs=newargs
        for x in (add,addF):
            x.bind('<Button-1>',lambda e:self.NewTab())
        self.frames.grid(column=0,row=1,sticky='nsew')
        self.grid_rowconfigure(1,weight=1)
        self.grid_columnconfigure(0,weight=1)
        self.current=''
        if not initialTabs:
            initialTabs=[Tab('Untitled',new,)]
        for T in initialTabs:
            if not isinstance(T,Tab):
                self.AddTab(T[0],mode=T[1])
            else:
                self.AddTab(T)

    def NewTab(self):
        T=Tab(name='Untitled_{}'.format(self.untNum),mode=self.newType,
              args=self.newargs,**self.newkwargs)
        self.AddTab(T)
        self.untNum+=1
        
    def AddTab(self,nameORtab,*args,mode=tk.Frame,**kwargs):
        
        if isinstance(nameORtab,Tab):
            T=nameORtab
            name=T.name
            kwargs=T.config
            args=T.args
            mode=T.mode
        else:
            name=nameORtab
        F=mode(self.frames,*args,highlightthickness=0,**kwargs)
        B=tk.Frame(self.buttons,bg='black',bd=1)
        V=tk.StringVar(value=name)
        R=tk.Frame(B,bg='grey95')
        R.pack(side='left',fill='y')
        S=tk.Frame(R,width=5,height=5,bg='grey')
        S.bind('<Enter>',lambda*e:S.config(bg='red'))
        S.bind('<Leave>',lambda*e:S.config(bg='grey'))
        S.bind('<Button-1>',lambda*e:self.DelTab(self.current))
        S.pack()
        T=tk.Entry(B,textvariable=V,relief='flat',width=8,highlightthickness=0)
        V.trace('w',lambda*e:self.RenameTab(V.get()))
        T.pack(side='left',fill='both')
        B.bind('<Button-1>',lambda*e:self.SwitchTab(V.get()))
        T.bind('<Button-1>',lambda*e:self.SwitchTab(V.get()))
        B.pack(side='left')
        self[name]=self.WTE(F,B,T)
        self.SwitchTab(name)

    def Kill(self):
        for t in self:
            M,B,T=self[t]
            try:
                M.close()
            except AttributeError:
                pass
            
    def RenameTab(self,new):

        curr=self.current
        if curr!=new:
            tup=self[curr]
            self[new]=tup
            if curr==self.current:
                self.current=new
            self[new]=self[curr]
            del self[curr]
        
    def DelTab(self,name):

        F,B,T=self[name]
        del self[name]
        if self.current==name:
            try:
                N=next(iter(self))
                F1,B1,T1=self[N]
            except StopIteration:
                self.master.destroy()
                del self
                return None
            else:
                self.SwitchTab(N)
                F.pack_forget()
        B.pack_forget()
        try:
            F.close()
        except AttributeError:
            pass
        self.ResizeTabs()

    def ResizeTabs(self):

        #At 644 pixels, about 66 characters of entry fit
        #So scale by about 15
        size=int((self.winfo_width())/(13*self.count()))
        W=min(size,8)
        for t in self:
            if not t=='current':
                f,b,T=self[t]
                T.config(width=W)
            
    def SwitchTab(self,to,options=None):
        if not options:
            options={'fill':'both','expand':True}
        try:
            E,B1,T1=self[self.current]
        except KeyError:
            pass
        else:
            E.pack_forget()
            size=int((self.winfo_width())/5*self.count())
            T1.config(bg='white',width=min(size,8))
        F,B2,T2=self[to]
        T2.config(bg='gray95',width=10)
        F.pack(**options)
        self.current=to
        self.ResizeTabs()
        
        
    def __delitem__(self,item):

        del self.map[item]
        
    def __setitem__(self,item,value):

        self.map[item]=value

    def __getitem__(self,item):

        return self.map[item]

    def count(self):

        return len(self.map)

    def __iter__(self):

        return iter(self.map)

class Tab:

    def __init__(self,name='Untitled',mode=tk.Text,args=(),callback=None,**kwargs):
        self.name=name
        self.mode=mode
        self.args=args
        self.config=kwargs
        if not callback:
            callback=lambda:None
        self.callback=callback

    def instance(self,root):
        return self.mode(root,*self.args,**self.config)
    
    def config(self,**kwargs):
        self.config.update(kwargs) 
