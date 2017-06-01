from GUITools.ExtraWidgets.Shared import *
from GUITools.ExtraWidgets.Message import *

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
            root=tk.Toplevel(calledfrom if isinstance(calledfrom,tk.Widget) else None)
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
