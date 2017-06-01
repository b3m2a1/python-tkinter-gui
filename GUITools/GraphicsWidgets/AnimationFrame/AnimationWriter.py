from .AnimationFrame import *
from ...ExtraWidgets.ShellFrame import ShellFrame
from ...TextWidgets import RichText
from ...EvaluatorWidgets import ModuleText
from ...WindowTools.Buttons import CustomButton

# from GeneralTools.Math.Geometry import load_geometry
# load_geometry("Euclidean2D")
# from GeneralTools.Math.Geometry.Euclidean2D import *

class AnimationWriter(tk.Frame):
    def __init__(self,root=None,**AF_kwargs):
        self.name=name
        super().__init__(root,bg='grey10')
        AF_kwargs['bd']=5
        AF_kwargs['relief']='groove'
        self.frame=AnimationFrame(self,**AF_kwargs)
        self.animation=Animation(self.frame)
        self.frame.grid(row=0,column=0,sticky='nsew')
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        
        self.sidebar=tk.Frame(self)
        self.sidebar.grid(row=0,column=1,sticky='nsew')
        self.sidebar.grid_rowconfigure(1,weight=1)

        self.original_name=True        
        self.namevar=tk.StringVar(value="animation")
        self.namevar.trace('w',lambda *a,s=self:(setattr(self,'original_name',False),self.name_entry.config(fg='black')) )
        self.name_entry=tk.Entry(self.sidebar,textvariable=self.namevar,relief='flat')
        self.name_entry.grid(row=0,sticky='nsew')
        
        self.animation_text=RichText(self.sidebar,width=20,highlightthickness=0,bd=2,relief='sunken',wrap='word',ReturnChar='\n'+'-'*12+'.'+'-'*12+'\n',spacing3=3)
        self.animation_text.grid(row=1,sticky='nsew')
        
        self.test_button=CustomButton(self.sidebar,text="Run Animation",command=self.test)
        self.test_button.grid(row=2,sticky='ew')

        self.save_button=CustomButton(self.sidebar,text="Save Animation",command=self.save)
        self.save_button.grid(row=3,sticky='ew')

        self.load_button=CustomButton(self.sidebar,text="Load Animation",command=self.load)
        self.load_button.grid(row=4,sticky='ew')

        self.new_button=CustomButton(self.sidebar,text="New Animation",command=self.new)
        self.new_button.grid(row=5,sticky='ew')

        self.animation_text.bind('<Command-Return>',self.test)
        self.animation_text.bind("<Command-s>",self.save)
        self.animation_text.bind("<Command-o>",self.load)
        self.animation_text.bind("<Command-n>",self.new)
                
    def test(self,event=None):
        text=self.animation_text.get('all',replace_returns=True)
        self.animation=Animation(self.frame)
        self.animation.load_string(text)
        self.animation.append(lambda *a,f=self.frame:f.flash(r=100,g=100,b=100,pause=500))
        self.animation.call()
        return 'break'

    def test_file(self,file):
        self.animation.clear()
        self.animation.load(file)
        self.animation.append(lambda *a,f=self.frame:f.flash(r=100,g=100,b=100,pause=500))
        self.animation.call()
        return 'break'

    def new(self,event=None):
        anm_string='''#{} animation loader

#This file needs to define either a function, load animation,
#or an iterable, animation
#
#The function load_animation takes an animation instance and an animation frame
#and optional arguments and keywords and must return an iterable of functions
#in no arguments.
#
#The animation iterable is an iterable of functions in no arguments
#
#If load_animation is defined the animation_instance calls it and
#adds the functions produced to its call list
#
#Otherwise if animation is defined the animation_instance adds the functions
#in the iterable to its call list

##DEFINE VIA ITERABLE##
#animation=()

##DEFINE VIA FUNCTION##
#def load_animation(animation_instance,animation_frame):
#    animation=[]

#    return animation
'''
    
    
        from tkinter.filedialog import asksaveasfilename as ask
        f=ask(parent=self,title='Choose animation file',
                defaultextension='.py',initialdir=self.source)
        with open(f,'w+') as anm:
            anm.write(anm_string.format(os.path.basename(f)))
        self.load(file=f)
        
    def save(self,event=None):
        name=self.namevar.get()
        base,ext=os.path.splitext(name)
        if ext=='':
           name=name+'.txt' 
        f=os.path.join(self.source,name)
        with open(f,'w+') as out:
            out.write(self.animation_text.get('all',replace_returns=True).strip())
        self.name_entry['fg']='gray'

    def load(self,event=None,file=None):
        if file is None:
            from tkinter.filedialog import askopenfilename as ask
            f=ask(parent=self,title='Choose animation file',
                    defaultextension='.txt',initialdir=self.source)
        else:
            f=file
            
        if f!='':
            base,ext=os.path.splitext(f)
            if ext in ('.py','.pyc'):
                new=tk.Toplevel(self)
                new.title('{} - {}'.format(os.path.basename(f),f))
                m=new.module=ModuleText(new,file=f,highlightthickness=0)
                new.grid_columnconfigure(0,weight=1)
                new.grid_rowconfigure(0,weight=1)
                new.unsaved=False
                m.grid(row=0,column=0,sticky='nsew',padx=3)
                def blah_blah(event,self=self,new=new,m=m):
                    b=m.Insert(event)
                    if not event.keysym in ("Left",'Right','Up','Down','Shift','Command',
                                            'Control_L','Caps_Lock','Shift_L','Shift_R'):
                        if not new.unsaved:
                            new.unsaved=True
                            new.title('* '+new.title()+' *')
                    return b
                m.bind('<Key>',blah_blah)
                def save_blah(event,self=self,new=new,m=m):
                    if new.unsaved:
                        new.unsaved=False
                        new.title(new.title()[2:-2])
                    m.Save(file=m.file)
                m.bind('<Command-s>',save_blah)
                m.bind('<Command-Return>',lambda e,m=m,s=self:s.test_file(m.file))
                m.sb.grid(row=0,column=1,sticky='ns')
                bar_frame=tk.Frame(new,bd=1,bg='gray70')
                bar=tk.Frame(bar_frame)
                bar_frame.grid(row=1,column=0,columnspan=2,sticky='nsew')
                bar.pack(fill='both',expand=True)
                test_button=CustomButton(bar,text='    Run   ',command=lambda self=self,m=m:self.test_file(m.file))
                test_button.grid(sticky='w',padx=3,pady=3)
            else:
                with open(f) as anm:
                    self.animation_text.Append(anm.read(),replace_sequences=('Return',))
                if self.original_name:
                    self.namevar.set(os.path.splitext(os.path.basename(f))[0])
        
    def __getattr__(self,attr):
        return getattr(self.frame,attr)
        
    
    
