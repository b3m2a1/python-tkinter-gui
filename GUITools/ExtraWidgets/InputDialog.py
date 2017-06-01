from GUITools.ExtraWidgets.Shared import *

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
        self.out=self.val.get()
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
 
