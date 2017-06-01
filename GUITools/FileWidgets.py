#File-related GUITools
from .Shared import *
from .FormattingWidgets import *
from .TextWidgets import LockText
from GeneralTools.Session import Session

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class FileViewer(tk.Frame):

    import tempfile as tf,shutil,os,subprocess
    
    def __init__(self,root=None,location=None,new_dir=True,basename="",textType=LockText,name=None,archive=None,
                 callback=None,extensions=(),hide=(),initialbuttons=(),**kwargs):

        if 'bd' not in kwargs:
            kwargs['bd']=1
        if 'bg' not in kwargs:
            kwargs['bg']='grey95'
        if name is None:
            name=type(self).__name__
        self.name=name
        self.protocol=root.protocol
        super().__init__(root,bg='grey75')
        self.root=self.master=root
        self.textPane=textType(self,**kwargs)
        self.sessionPane=SessionHolder(self,name=self.name,
                                       archive=archive,callback=callback,
                                       extensions=extensions,
                                       hide=hide,
                                       location=location,
                                       initialButtons=initialbuttons,
                                       new_dir=new_dir)
        self.sessionPane.grid(column=0,row=0,padx=1,pady=1,sticky='ns')
        self.textPane.grid(column=1,row=0,padx=1,pady=1,sticky='nsew')

        self.sessionPane.bind('<Down>',lambda *e:self.after_idle(self.ViewCurrent))
        self.sessionPane.bind('<Up>',lambda *e:self.after_idle(self.ViewCurrent))
        self.sessionPane.bind('<Button-1>',lambda *e:self.after_idle(self.ViewCurrent))

        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)

    def Add(self,file,copyIn=True):
        sH=self.sessionPane
        sH.activesession.Add(file,copyIn)
        sH.LoadFiles()

    def MakeFile(self,filename=None,ext=None):
        
        return self.sessionPane.MakeFile(filename,ext)
        
    def ViewCurrent(self):
        sH=self.sessionPane
        vP=self.textPane
        c=sH.GetCurrent()
        if c:
            with open(c) as F:
                try:
                    R=F.readlines()
                except UnicodeDecodeError:
                    R=['Error Opening File {}'.format(c)]
                vP.Clear()
                vP.Insert(''.join(R))
        return c

    def __iter__(self):
        return iter(self.sessionPane.activesession)
    
    def __getitem__(self,string):

        sH=self.sessionPane
        return sH.activesession[string]
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$       
class SessionHolder(tk.Frame):
    
    def __init__(self,root=None,basename="",name=None,new_dir=True,archive=None,location=None,
                 callback=None,extensions=(),hide=(),initialButtons=None,**kwargs):
        
        if name is None:
            name=type(self).__name__
        self.name=name
        self.extensions=extensions
        super().__init__(root,**kwargs)
        if location is None:
            try:
                root.protocol('WM_DELETE_WINDOW',lambda *e:self.Kill())
            except AttributeError:
                pass
            location=self.tf.TemporaryDirectory()
            folder=location.name
        else:
            folder=location
        self.directory=location
        self.folder=folder
        self.activesession=Session(location=folder,
                                   name=name,
                                   new_dir=new_dir,
                                   extensions=extensions,
                                   hide=hide)
        self.hidden=self.activesession.hidden
        self.sessions=[self.activesession]
        self.root=self.master=root
        vf=tk.Frame(self)
        self.sessionviewer=SessionBox(vf,callback=callback)
        sb=tk.Scrollbar(vf,command=self.sessionviewer.yview)
        self.sessionviewer.pack(expand=True,side='left',fill='both');sb.pack(side='left',fill='y')
        vf.pack(expand=True,side='bottom',fill='both',padx=2,pady=2)
        self.sessionviewer.config(yscrollcommand=sb.set)
        self.namevar=tk.StringVar()
        F=tk.Frame(self)
        ##Name variable and entry
        self.activename=tk.Entry(F,textvariable=self.namevar)
        self.activename.pack(fill='x')
        bf=FormattingGrid(F,rows=0,columns=3)
        sad=FormattingElement(tk.Button,bf,text='Add Session',command=lambda:self.AddSession())
        fad=FormattingElement(tk.Button,bf,text='Add Files',command=lambda:self.AddFiles())
        mfi=FormattingElement(tk.Button,bf,text='Make File',command=lambda:self.MakeFile())
        if initialButtons is None:
            bf.AddItems(sad,fad,mfi)
        else:
            toDo=[]
            for x in initialButtons:
                if x==1:
                    toDo.append(sad)
                elif x==2:
                    toDo.append(fad)
                elif x==3:
                    toDo.append(mfi)
                else:
                    toDo.append(x(bf))
            bf.AddItems(*toDo)
            
        bf.gridConfig(sticky='w')
        self.sessButton=sad
        self.fileButton=fad
        self.makeButton=mfi
        self.activename.bind('<Return>',lambda e:self.RenameActive())
        self.activename.bind('<FocusOut>',lambda e:self.RenameActive())
        ##Session chooser
        ops=[f for f in os.listdir(self.folder)]
        self.sessionbar=tk.OptionMenu(
            self,self.namevar,*ops,
            command=lambda *e:self.ChangeActive(self.namevar.get())
            )
        self.sessionbar.pack(fill='x')
        bf.pack(anchor='w')
        F.pack(fill='x')
        self.ChangeActive(self.activesession)
        self.components=(bf,fad,mfi,sad,self.activename,self.sessionviewer)
        for c in self.components:
            c.bind('<Command-i>',lambda e:Interactor(self))
        
##    @property
##    def folder(self):
##        return self.activesession.folder
##    @property
##    def location(self):
##        return self.activesession.location
    
    def bind(self,keyEvent,callback):

        for c in self.components:
            c.bind(keyEvent,callback)

        super(SessionHolder,self).bind(keyEvent,callback)
        
    def ChangeDirectory(self,newdir):
        current=self.folder
        n=os.path.basename(newdir)
        self.name=n
        self.directory=self.folder=newdir
        for x in self.sessions:
            if current in x.folder:
                newF=newdir+x.folder.strip(current)
                x.folder=newF
                
    def GetSession(self,tag,mode='name'):
        for f in self.sessions:
            tv=getattr(f,mode)==tag
            if tv:
                return f
        else:
##            print(tag)
##            print([s.name for s in self.sessions])
            raise ValueError("Couldn't find folder named:{}".format(tag))
            
    def RenameActive(self):
        name=self.namevar.get()
        self.activesession.Rename(name)
        ind=self.sessions.index(self.activesession)
        self.sessionbar['menu'].entryconfig(
            ind,label=name,command=lambda *v:self.ChangeActive(name)
            )
        
    def ChangeActive(self,to):
        path=os.path
        if isinstance(to,str):
            to=self.GetSession(to)
        self.activesession=self.sessionviewer.session=to
        self.sessionviewer.LoadFiles()
        self.activename.delete(0,'end')
        self.activename.insert(0,to.name)
        self.namevar.set(to.name)

    def RemoveCurrent(self):
        self.RemoveSession(self.activesession)

    def RemoveSession(self,session):

        M=self.sessionbar['menu']
        i=M.index(session.name)
        if session in self.sessions:
            self.sessions.remove(session)
        M.delete(i)
        self.activesession=self.sessions[0]

    def AddSession(self,name=None,extensions=None,session=None,hide=None):
        if not session:
            if extensions is None:
                extensions=self.extensions
            if hide is None:
                hide=self.hidden
            S=Session(name=name,
                      extensions=extensions,
                      hide=hide,
                      location=self.folder)
        else:
            S=session
        self.sessionbar['menu'].add_command(
            label=S.name,command=lambda *v:self.ChangeActive(S.name)
            )
        self.sessions.append(S)
        self.ChangeActive(S)

        return S

    def Kill(self,ask=True):
        if ask:
            pass
        shutil.rmtree(self.folder)
        self.root.destroy()

    def __getattr__(self,attr):
        return getattr(self.sessionviewer,attr)
    
    def __getitem__(self,string):

        return self.activesession[string]
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$           
class SessionBox(tk.Listbox):

    def __init__(self,root=None,session=None,name=None,callback=None):
        super().__init__(root)
        if callback is None:
            callback=self.OpenCurrent
        self.callback=callback
        if name is None:
            self.name=type(self).__name__
        self.session=session
        if not session is None:
            self.LoadFiles()
        self.bind('<Return>',lambda *e:self.callback())
        self.bind('<Double-Button-1>',lambda *e:self.RenameFile())
        self.bind('<Command-o>',lambda *e:self.OpenCurrent())
        self.bind('<BackSpace>',
                                lambda *e: self.RemoveFile())
    def GetCurrent(self):
        text=self.get('active')
        ret=self[text]
        if not ret:
            raise IndexError('SessionBox.GetCurrent: no current file')
        return ret
    def SetCurrent(self,file_name):
        i=0
        for t in self:
##            t=self.get(i)
            if t==file_name:
                self.activate(i)
                break
            i+=1
    def OpenCurrent(self,app=None,openfunction=None):
        f=self.GetCurrent()
        if openfunction is None:
            if app:
                subprocess.call(['open','-a',app,f])
            else:
                subprocess.call(['open',f])
        else:
            openfunction(f)
            
    def LoadFiles(self):
        self.delete(0,'end')
        for f in self.session:
            if not os.path.isdir(f):
                N=os.path.basename(f)
                n,e=os.path.splitext(N)
                if e==".hide":
                    N=n
                self.insert('end',N)
                
    def RemoveFile(self,filenameORindex=None):

        if filenameORindex is None:
            filenameORindex=os.path.basename(self.GetCurrent())
        self.session.Delete(filenameORindex)
        self.LoadFiles()
        
    def AddFiles(self):
        fs=tk.filedialog.askopenfilenames()
        for f in fs:
            self.session.Add(f)
        self.LoadFiles()

    def MakeFile(self,filename=None,ext=None):
        F=self.session.MakeFile(filename,ext)
        self.LoadFiles()
        
        return F

    def RenameFile(self,file=None):
        
        from .ExtraWidgets import InputDialog
        
        if file is None:
            file=self.GetCurrent()
            
        base,name=os.path.split(file)
        new=InputDialog.dialoginput('New Filename:',initialvalue=name)
        os.rename(file,os.path.join(base,new))
        self.delete('anchor')
        self.insert('anchor',new)

    def __iter__(self):
        return iter(self.session)
    def __getitem__(self,string):

        return self.session[string]

