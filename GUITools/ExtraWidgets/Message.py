from GUITools.ExtraWidgets.Shared import *

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
