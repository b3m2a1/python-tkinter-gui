from GUITools.ExtraWidgets.Shared import *

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ShellFrame(tk.Frame):

    from GUITools.EvaluatorWidgets import InterpreterText

    def __init__(self,root=None,frame_widget=None,variable_dict=None,**kwargs):
        
        self._configured=False
        super().__init__(root,**kwargs)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,minsize=100,weight=1)
        self.grid_columnconfigure(0,weight=1)
        
        self.shell_frame=tk.Frame(self,
                                  bg="gray95",bd=2,relief="sunken")
        self.shell_frame.pack_propagate(False)
        
        if variable_dict is None:
            variable_dict={}
        variable_dict["main"]=self
        
        if not frame_widget is None:
            variable_dict["widget"]=frame_widget
        
        self.shell=InterpreterText(self.shell_frame,
            variables=variable_dict,
            newThread=False)
            
        self.shell.pack(fill="both",expand=True)
        
        
        self.widget=frame_widget
        if frame_widget is not None:
            self.widget.grid(in_=self,row=0,column=0,sticky="nsew")
        
        self.shell_frame.grid(row=1,column=0,sticky="nsew")
        self._shell=True
        
        self.after(100,lambda self=self:self.grid_rowconfigure(1,weight=0))
        self._configured=True
    def __setattr__(self,attr,val):
        super().__setattr__(attr,val)
        if attr!='_configured' and self._configured:
            setattr(self.shell,attr,val)
    def toggle_shell(self):
        if self._shell:
            self.shell_frame.grid_forget()
            self._shell=False
            self.grid_rowconfigure(1,minsize=0)
        else:
            self.shell_frame.grid(row=1,column=0,sticky="nsew")
            self.grid_rowconfigure(1,minsize=100)
            self._shell=True
            
    def set_widget(self,widget):
        if self.widget is not None:
            self.widget.grid_forget()
        self.widget=widget
        self.widget.grid(in_=self,row=0,column=0,sticky="nsew")
