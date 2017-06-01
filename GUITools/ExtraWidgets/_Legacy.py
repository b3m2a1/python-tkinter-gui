from GUITools.Widgets import *

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Interactor(tk.Frame):

    import string,sys,traceback
    from GUITools.EvaluatorWidgets import ModuleText
    from importlib.abc import SourceLoader

    class Loader(SourceLoader):
        def get_data(self,file):
            with open(file,'rb') as f:
                return f.read()
        def get_filename(self,fullname):
            return fullname
    ModuleLoader=Loader()            
    
    class InteractionText(ModuleText):
        
        def __init__(self,root,**kwargs):
            self.root=root
            self.outframe=root.outframe
            super().__init__(root,newThread=False,**kwargs)
            
        def ExecuteAndWrite(self,string,write=True,message=True):
            if string:
                if message:
                    self.root.AddMessage(string)
                    message=string
                self.writeOutput(*self.Execute(string),write=write,message=message)
            return 'break'
        def writeOutput(self,output,tag,write=True,message=None):
            if write:
                if message:
                    if tag!='output':
                        self.root.AddError(output,message)
                self.SelectAll()
                self.outframe.unlock('0.0','end')
                self.outframe.Clear()
                self.outframe.Insert(output,tag)
                self.outframe.lock('0.0','end')
            self.root.Refresh()
            return 'break'
    #--
    def __init__(self,calledfrom=None,initiallocals=None,**kwargs):
        
        import queue,sys

        if not initiallocals:
            initiallocals={}
        if not (calledfrom is None):
            root=tk.Toplevel()
            try:
                initiallocals[calledfrom.name]=calledfrom
            except AttributeError:
                initiallocals[type(calledfrom).__name__]=calledfrom
            initiallocals['main']=calledfrom
        else:
            root=tk.Tk()
        super().__init__(root)
        self.repetitionTimes=100
        self.pack()
        initiallocals['self']=self
        initiallocals['load']=self.ModuleLoader.load_module
        self.root=root
        self.object=calledfrom
        c=calledfrom
        if c:
            try:
                n=c.name
            except:
                n=type(c).__name__
            title='on {}'.format(n)
        else:
            title=''
        root.title('Interactor Session {}'.format(title))
        if not 'undo' in kwargs:
            kwargs['undo']=True
        if not 'wrap' in kwargs:
            kwargs['wrap']='word'
        #Creates output area
        OF=tk.LabelFrame(
            self,text='Output'
            )
        v=self.outframe=LockText(OF,width=50,height=5)
        v.tag_configure('output',foreground='blue')
        v.tag_configure('error',foreground='red')
        v.LockAll()
        sb=tk.Scrollbar(OF,command=v.yview)
        v.config(yscrollcommand=sb.set)
        v.pack(side='left',expand=True,fill='both')
        v.bind('<Shift-1>',lambda *e:self.PopOutput())
        sb.pack(side='right',fill='y')
        #Creates main code area
        self.interactor=self.InteractionText(
            self,variables=initiallocals,width=75,highlightthickness=0,bd=2,relief='sunken',**kwargs
            )
        self.interactor.pack(padx=10,pady=10)
        self.errorcache=MessageContainer(root=self,name='Errors')
        self.codecache=MessageContainer(root=self,name='Code Cache')
        OF.pack(side='left',anchor='s',expand=True,fill='both')
        self.interactor.bind('<Command-l>',lambda *e: self.ViewLocals())
        #Makes run button, code cache buttons
        bf=tk.Frame(
            self
            )
        run=tk.Button(
            bf,text='Run',command=self.interactor.ExecuteAndWrite(*self.interactor.getString())
            )
        run.grid(row=0,column=0,sticky='ew')
        self.animateflag=tk.IntVar()
        animate=tk.Checkbutton(
            bf,text='Continuous Run',variable=self.animateflag
            )
        repeat=tk.Button(
            bf,text='Repeated Run',command=lambda *e:self.RepeatedRun(continuous=self.animateflag.get())
            )
        repeat.grid(row=0,column=1,sticky='ew')
        cc=tk.Button(
            bf,text='Code Cache',command=lambda *e:self.codecache.Generate()
            )
        cc.grid(row=1,column=0,sticky='ew')
        er=tk.Button(
            bf,text='View Errors',command=lambda *e:self.errorcache.Generate()
            )
        er.grid(row=1,column=1,sticky='ew')
        animate.grid(row=2,column=1,sticky='se')
        bf.pack(side='right',anchor='center',expand=True)
        #Prime the thing
        self.interactor.ExecuteAndWrite("'Welcome!'")
        self.codecache.Clear()
        self.errorcache.Clear()
        self.interactor.DeselectAll()

    #-------------------------------------------------------------------------
    def Generate(self):
        pass

    #-------------------------------------------------------------------------
    def RepeatedRun(self,times=None,continuous=False):
        if times is None:
            times=self.repetitionTimes
        if continuous:            
            def animate(self):
                
                if self.interactor.ExecuteAndWrite(self.interactor.getString(),write=False):
                    self.interactor.update_idletasks()
                    if self.animateflag.get():
                        self.interactor.after(10,animate,self)
            animate(self)
        else:
            for x in range(times):
                if not self.interactor.ExecuteAndWrite(self.interactor.getString(),write=False):
                    break
                else:
                    self.interactor.update_idletasks()
    #
    def AddMessage(self,text):
        ls=len(text.splitlines())
        M=Message(text,messageheader='Code:',name=str(ls)+' Lines',
                  interaction=(lambda:self.interactor.Insert(text),'Insert'))
        self.codecache.AddMessage(M)
    #
    def AddError(self,error,code):
        ls=error.splitlines()
        name=ls[-1]
        while not name.strip():
            ls.pop()
            name=ls[-1]
        name=name.split(':')[0]
        M=Message(error,objects=[code],messageheader='Error:',objectheader='Code:',name=name)
        self.errorcache.AddMessage(M)
    #-------------------------------------------------------------------------
    def PopOutput(self):

        top=tk.Toplevel()
        text=self.outframe.get('1.0','end')
        top.title('Output')
        t=LockText(top)
        t.Insert(text)
        t.LockAll()
        t.pack(fill='both',expand=True)
        top.mainloop()
    #-------------------------------------------------------------------------
    def ViewLocals(self):

        test=globals()
        top=tk.Toplevel()
        top.title('Bound Variables')
        s=self.interactor.evaluator.locals
        s={k:s[k] for k in s if k not in test}
        text='\n'.join(['{}:{}'.format(k,s[k]) for k in s])
        T=LockText(top)
        T.Insert(text)
        T.LockAll()
        T.pack()
        
    #-------------------------------------------------------------------------
    def Refresh(self):

        try:
            self.object.Refresh()
        except:
            try:
                self.object.Draw()
            except:
                pass
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
       
class ModuleFrame(TabFrame):

    def __init__(self,root=None,name='Untitled',new=None,tabOps=None,**kwargs):
        if not new:
            new=ModuleText
        if not tabOps:
            tabOps={'font':'Helvetica'}
        iFs=(
            Tab('Interpreter',InterpreterText,config=tabOps),
            Tab(name,ModuleText,config=tabOps),
            Tab('Description',RichText,config=tabOps)
            )
        super().__init__(root,*iFs,name=name,new=new,newkwargs=tabOps,**kwargs)
        self.irp,B,T=self['Interpreter']
        self.mod,B,T=self[name]
        self.des,B,T=self['Description']
        self.file=None
        for x in (self,self.mod):
            x.bind('<Command-Return>',lambda*e:self.runModule())
        self.SwitchTab('Interpreter')
        self.mod.bind('<Command-s>',lambda*e:self.Save(self.file))
        self.untNum=1

    def Save(self,file=None):

        if not file:
            file=tk.filedialog.asksaveasfilename()
            self.file=file
            
        text='#{}\n{}'.format(
            '\n#'.join(self.des.getAll().splitlines()),
            self.mod.getAll())
            
        if file:
            if isinstance(file,str):
                    with open(file,'w+') as F:
                        F.write(text)
            else:
                 file.write(text)

    def NewTab(self):
        K=self.newkwargs
        N='Untitled_{}'
        D={x:K[x] for x in K}
        D['evalfile']=os.path.join(self.dir.name,N,'.txt')
        T=Tab(name=N.format(self.untNum),mode=self.newType,
              args=self.newargs,config=D)
        self.AddTab(T)
        self.untNum+=1
    def runModule(self):
        T=self.mod.getString()
        self.irp.Append('='*73)
        R,t=self.mod.Execute(T)
        self.SwitchTab('Interpreter')
        self.irp.writeOutput(R,t)
        
class CodingGround(FileViewer):

    def __init__(self,root=None,basename="",name=None,archive=None,
                 callback=None,**kwargs):

        if name is None:
            name=type(self).__name__
        super().__init__(root,basename=basename,name=name,archive=archive,
                         callback=callback,extensions=('.hide'),**kwargs)
        self.textPane.__togglero__()
        S=self.sessionPane.activesession
        self.AddPyEnv('Py File')
        self.sessionPane.RemoveSession(S)
        self.sessionPane.makeButton.grid_forget()
        self.sessionPane.sessButton.config(text='Add File',command=lambda *e:self.AddPyEnv())
        self.sessionPane.fileButton.config(text='Add Class',
                               command=lambda *e:(
                                   self.sessionPane.activesession.AddClass(),
                                   self.sessionPane.LoadFiles()))
        self.editFile=[None]
        self.textPane.bind('<FocusIn>',
                lambda*e:self.editFile.insert(0,self.sessionPane.GetCurrent()))
        self.textPane.bind('<FocusOut>',lambda*e:self.SaveChanges())
        
    def AddPyEnv(self,name=None):

        if not name:
            name='Py File {}'.format(len(self.sessionPane.sessions))
        P=PyEnvironment(name=name)
        self.sessionPane.AddSession(session=P)

    def SaveChanges(self):

        F=self.editFile[0]
        if F:
            T=self.textPane.getAll()
            with open(F,'w+') as f:
                f.write(T)
            self.editFile=[None]
        

class PyEnvironment(Session):

    def __init__(self,name=None,location=None):

        super().__init__(name=name,extensions=('.hide',),location=None)
        self.classes=[]
        self.AddClass('main')

    def RunActive(self):

        exec(self.activefile)

    def AddClass(self,name=None):

        if not name:
            name=dialoginput('Class Name:')
        self.MakeFile(name=name,ext='.hide')
        self.classes.append(name)
        
    def Compile(self):

        for c in self.classes:
            pass

    def _stringParse(self,string):

        pass

    def Test(self):

        pass

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class InputDialog(tk.Frame):

    def __init__(self,root=None,inputmessage='Input:',initialtext='',**kwargs):

        if not root:
            root=tk.Toplevel()
        super().__init__(root,**kwargs)
        F=tk.LabelFrame(self,text=inputmessage)
        self.val=tk.StringVar()
        self.val.set(initialtext)
        E=tk.Entry(F,textvariable=self.val)
        F.pack(padx=10,pady=10)
        E.pack()
        self.root=root
        self.pack()
        bits=(self,E)
        for x in bits:
            x.bind('<Return>',lambda *e:self.Return())
        B=tk.Button(self,text='Ok',command=self.Return)

    def Return(self):
        self.quit()
        self.root.destroy()
        self.out=self.val.get()
        return self.out
    
    @staticmethod
    def dialoginput(message='Input:',root=None,initialvalue=''):
        I=InputDialog(root=root,inputmessage=message,initialtext=initialvalue)
        I.mainloop()
        return I.out
    
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class Message:

    def __init__(self,message,root=None,objects=None,messageheader='Message:',
                 objectheader='Objects:',name=None,interaction=None):

        self.root=root
        if name is None:
            name=type(self).__name__
        self.message=message
        self.name=name
        self.mHead=messageheader
        self.oHead=objectheader
        if not interaction is None:
            try:
                if len(interaction)<2:
                    interaction=(interaction[0],'Interact')
            except:
                interaction=(interaction,'Interact')
        self.interaction=interaction
        if isinstance(objects,str):
            self.objects=[objects]
        else:
            try:
                b=objects[-1]
                self.objects=objects
            except:
                self.objects=[objects]
    #-------------------------------------------------------------------------
    def Display(self):
        
        if not self.root:
            r=tk.Tk()
        else:
            r=tk.Toplevel()
        r.title(self.name)
        self.display_root=r
        mf=tk.Frame(r)
        mtex=LockText(mf,bd=0)
        if not self.interaction is None:
            f,n=self.interaction
            self.intbutt=b=tk.Button(mf,text=n,command=f)
            b.pack(anchor='w')
            for x in (r,mtex):
                x.bind('<Return>',lambda*e:f())
        me='{}\n{}'.format(self.mHead,self.message)
        if any(self.objects):
            ob='{}\n\t{}'.format(self.oHead,'\n\t'.join([str(o) for o in self.objects]))
            m='{}\n{}'.format(ob,me)
        else:
            m=me
        mtex.insert(1.0,m)
        mtex.pack(fill='both',expand=True)
        mf.pack(fill='both',expand=True)
        mtex.LockAll()
        mtex.unbind('<Command-u>')
        if not self.root:
            r.mainloop()
    #--
    def Exit(self):
        if not self.display_root is None:
            self.display_root.destroy()
        self.display_root=None
    #-------------------------------------------------------------------------
    def __repr__(self):
        return self.name
    
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class PropertyMessage(Message):

    def __init__(self,ob,root=None):
        head='Properties of {}'.format(str(ob))
        message='\n'.join([str(x) for x in dir(ob)])
        super().__init__(message,root=root,messageheader=head)
    
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ErrorMessage(Message):

    def __init__(self,exception,root=None):
        usestr=exception.__repr__()
        name=usestr[:usestr.index('(')]
        if not hasattr(exception,'debug'):
            interaction=None
        else:
            interaction=exception.debug
        super(ErrorMessage,self).__init__(exception.args[0],root=root,name=name,interaction=interaction)
    #-------------------------------------------------------------------------
    def Display(self):

        if not self.root:
            r=tk.Tk()
        else:
            r=tk.Toplevel()
        r.title(self.name)
        mf=tk.Frame(r)
        if self.interaction:
            b=tk.Button(mf,text="Debug",command=lambda *e:self.Interact())
            b.pack(anchor='w')
        mtex=ROText(mf,bd=0)
        me='Arguments:\n{}'.format(self.message)
        ob='Objects: \n_{}'.format('\n_'.join([str(o) for o in self.objects]))
        m='{}\n{}'.format(ob,me)
        mtex.insert(1.0,m)
        mtex.pack(fill='both',expand=True)
        mf.pack(fill='both',expand=True)
        if not self.root:
            r.mainloop()
            
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class MessageContainer:

    class MessageList(tk.Listbox):
        def __init__(self,root,messageHolder,**kwargs):
            super().__init__(root,**kwargs)

            self.session=messageHolder
            self.root=root
            self.bind('<Return>',lambda*e:self.DisplayCurrent())
            self.bind('<BackSpace>',lambda*e:self.DelMessage())
            self.bind('<Double-Button-1>',lambda*e:self.RenameMessage())
            
        def GetCurrent(self):
            ind=int(self.curselection()[0])
            m=self.session.messages[ind]
            return m
        #-------------------------------------------------------------------------
        def DisplayCurrent(self):

            m=self.GetCurrent()
            store=m.root
            m.root=self.root
            m.Display()
            m.root=store
        #--
        def LoadMessages(self):
            self.delete(0,'end')
            for m in self.session.messages:
                self.insert('end',m.name)
        #--
        def RenameMessage(self,message=None):
            if message is None:
                message=self.GetCurrent()
            name=message.name
            new=InputDialog.dialoginput('New Filename:',initialvalue=name)
            message.name=new
            self.delete('anchor')
            self.insert('anchor',new)
            
    class FrameShit(tk.Frame):
        def __init__(self,root,messageHolder,**kwargs):
            super().__init__(root,**kwargs)

            F=tk.Frame(self)
            self.messageviewer=messageHolder.MessageList(F,messageHolder,bd=2,relief='sunken')
            scroll=tk.Scrollbar(F,command=self.messageviewer.yview)
            self.messageviewer.pack(side='left',fill='both',expand=True,padx=2,pady=2)
            self.messageviewer.config(yscrollcommand=scroll.set)
            scroll.pack(side='left',fill='y')
            db=tk.Button(
                self,text='Display',command=lambda *e:self.messageviewer.DisplayCurrent()
                )
            F.grid(row=0,column=0,sticky='nsew')
            self.grid_rowconfigure(0,weight=1)
            self.grid_columnconfigure(0,weight=1)
            self.messageviewer.LoadMessages()
            db.grid(row=1,column=0,sticky='ew')
        
    def __init__(self,root=None,initialmessages=None,name=None):

        if not initialmessages:
            initialmessages=[]
        self.root=root
        if name is None:
            name=type(self).__name__
        self.name=name
        if isinstance(initialmessages,Message):
            self.messages=[initialmessages]
        else:
            self.messages=initialmessages
        self.frame=None
        self.forward=None
        
    #-------------------------------------------------------------------------
    def Generate(self):

        if self.root is None:
            r=tk.Tk()
        else:
            r=tk.Toplevel()
        self.forward=r
        r.protocol('WM_DELETE_WINDOW',lambda*e:self.OnEnd())
        self.frame=F=self.FrameShit(r,self)
        F.pack(fill='both',expand=True)
        r.title(self.name)
        if self.root is None:
            r.mainloop()
    #-------------------------------------------------------------------------
    def OnEnd(self):

        self.frame.master.destroy()
        self.frame=None
        self.forward=None
    
    #-------------------------------------------------------------------------
    def AddMessage(self,message):
        if not message in self.messages:
            self.messages.append(message)
            if self.frame:
                self.frame.messageviewer.LoadMessages()
                
    #-------------------------------------------------------------------------
    def DelMessage(self,message=None):
        if message is None:
            message=self.messageviewer.GetCurrent()
        if message in self.messages:
            self.messages.remove(message)
            if self.frame:
                self.frame.messageviewer.LoadMessages()
    #-
    def Clear(self):
        self.messages=[]
        if self.frame:
            self.frame.messageviewer.LoadMessages()
    
    
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ErrorHolder(MessageContainer):

    def __init__(self,root=None,initialerrors=None,name='Error Holder'):
        super().__init__(root=root,initialmessages=initialerrors,name=name)
    #-------------------------------------------------------------------------
    def AddMessage(self,message):

        self.AddError(message)
    #-------------------------------------------------------------------------
    def AddError(self,error):

        message=ErrorMessage(error)
        super().AddMessage(message)
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$    
class FillBar(tk.Canvas):
    def __init__(self,root,current,max,color='green',mode='rounded',**kwargs):
        super().__init__(root,**kwargs)
        self.val=current
        self.max=max
        self.color=color
        self.mode=mode
        self.bar=[]
        self.config(scrollregion=(0,0,1,1))
        self.bind('<Configure>',lambda e:self.update())
        
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
        w=self.winfo_width()#//1.15
        h=self.winfo_height()#//1.75
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
            boundadj=10
            h=h-boundadj
            w=w-boundadj
            lw=h//2
            length=(w-lw)*ratio
            l1=length*.75//2
            if ratio==1:
                join_cap='round'
            else:
                join_cap='butt'
                
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
            self.fill=self.create_rectangle(inc,inc,length-inc,h-inc,fill=self.color,outline='')
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
