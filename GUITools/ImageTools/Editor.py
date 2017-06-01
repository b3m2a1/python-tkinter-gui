from ..Shared import *
from ..FormattingWidgets import *

class ImageEditorFrame(tk.Frame):
    def __init__(self,root=None,name=None,**kwargs):
        super().__init__(root,**kwargs)
        if name is None:
            name=type(self).__name__
        self.name=name
        edFrame=tk.Frame(self)
        self.holder=ImageHolder(edFrame)
        self.list=tk.Listbox(edFrame)
        self.holder.pack()
        self.editGrid=FormattingGrid(edFrame,rows=1,columns=3)
        self.displayFrame=tk.Frame(self)
        b1=tk.Button(self.editGrid,text='Add',command=self.AddImage)
        b2=tk.Button(self.editGrid,text='Subsample',command=lambda:self.Edit('subsample',2,2))
        bs=(b1,b2)
        self.editGrid.AddItems(bs)
        self.editGrid.pack()
        edFrame.pack(side='left',anchor='n')
        self.displayFrame.pack(side='right',fill='both',expand=True)
        self.list.pack()
        self.list.bind('<Command-i>',lambda e:Interactor(self))
        self.list.bind('<Return>',lambda e:self.DisplayCurrent())
        self.displayFrame.bind('<Double-Button-1>',lambda e:self.curr.pack_forget())
        self.curr=None
        
    def Load(self):
        self.list.delete(0,'end')
        for x in self.holder:
            self.list.insert('end',x.name)
            
    def AddImage(self):
        f=tk.filedialog.askopenfilename(title='Choose Image File')
        n,ext=os.path.splitext(f)
        if ext in ('.bmp','.gif'):
            self.holder.MakeImage(file=f)
            self.Load()
            
    def Edit(self,attr,*args,index=None):
        if index is None:
            index=int(self.list.curselection()[0])
        f=getattr(self.holder,attr)
        f(index,*args)
        self.Load()
        
    def DisplayCurrent(self):
        i=int(self.list.curselection()[0])
        if not self.curr is None:
            self.curr.pack_forget()
        self.curr=self.holder.ImageLabel(i,self.displayFrame)
        self.curr.bind('<Double-Button-1>',lambda e:self.curr.pack_forget())
        self.curr.pack()
        
    def Refresh(self):
        self.Load()

class ImageHolder(tk.Button):
    def __init__(self,root=None,text='Display Images',command=None,name=None):
        if command is None:
            command=self.DisplayAll
        super().__init__(root,text=text,command=command)
        if name is None:
            name=type(self).__name__
        self.name=name
        self.root=self.master
        self.images=[]
        
    def MakeImage(self,file=None,image=None,width=125,height=125):
        self.images.append(ImageAid(self,file=file,image=image,width=width,height=height))
        
    def DisplayImage(self,i):
        im=self.get(i)
        r=tk.Toplevel()
        tk.Label(r,image=im).pack()
        
    def ImageEdit(self,i,function):
        im=self.get(i)
        self.MakeImage(image=function(im))

    def zoom(self,i,x,y=''):
        self.ImageEdit(i,lambda im:im.zoom(x,y))
        return self.images[-1]
    
    def subsample(self,i,x,y=''):
        self.ImageEdit(i,lambda im:im.subsample(x,y))
        return self.images[-1]
    
    def DisplayAll(self):
        for i in range(len(self.images)):
            self.DisplayImage(i)
            
    def __getitem__(self,i):
        return self.images[i]
    
    def get(self,i):
        return self[i].image
    def ImageLabel(self,i,root):
        return tk.Label(root,image=self.get(i))
    def __iter__(self):
        return iter(self.images)
