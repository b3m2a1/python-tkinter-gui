from ..GridCanvas import *

class WalkerCanvas(GridCanvas):
    from .Walker import Walker
    def __init__(self,root,visible_rows,visible_cols,initialwalkers=1,**kwargs):
        super().__init__(root,visible_rows,visible_cols,**kwargs)
        self.walkerKwargs={'fill':'green'}
        self.current=[None]*initialwalkers
        self.down_keys={}
        for i in range(initialwalkers):
            w=self.Walker(self,**self.walkerKwargs)
            self.current[i]=w
            self.AddObject(w)
        self.key_wait=250

        self.bind('<Command-d>',lambda e:(self.Clear(),self.Draw()))
        self.arrow_waiters={'Up':False,'Down':False,'Left':False,'Right':False}
        for key,value in (
            ('Up',90),
            ('Down',270),
            ('Right',0),
            ('Left',180)):
            self.bind('<{}>'.format(key),self.ArrowMove)
        self.arrow_lock=tk.BooleanVar(self,value=True)
        self.arrow_delay=50
    
    def ArrowMove(self,arrow):
        
#         if self.arrow_lock.get():
#             self.arrow_lock.set(False)
        if isinstance(arrow,tk.Event):
            arrow=arrow.keysym
#         if not self.arrow_waiters[arrow]:
        if arrow=='Up':
            v=90
        elif arrow=='Down':
            v=270
        elif arrow=='Right':
            v=0
        elif arrow=='Left':
            v=180
        WalkerCanvas.MoveWalkers(self,rotate=v,setfacing=True)
#             self.after(self.arrow_delay,lambda:self.arrow_lock.set(True))
                
    def MoveWalkers(self,event=None,rotate=0,speed=None,setfacing=False):
        
        if not self.event_queue.is_processing:
            for W in self.current:
                if W.facing!=math.radians(rotate):
                    self.event_queue.add(lambda W=W,r=rotate:W.setfacing(r),W,
                                         name='{}.setfacing({})'.format(W,rotate))
                elif (not setfacing and rotate>0):
                    self.event_queue.add(lambda W=W,r=rotate:W.turn(r),W,
                                         name='{}.turn({})'.format(W,rotate))
                else:
                    self.event_queue.add(lambda W=W,s=speed:W.move(s),W,
                                         name='{}.move({})'.format(W,speed))

    def WalkerConfig(self,**kwargs):
        if 'widget' in kwargs:
            self.walkerKwargs={}
        self.walkerKwargs.update(kwargs)
    
    def NewWalker(self,i=0,j=0):
        kw=dict(**self.walkerKwargs)
        kw.update({'initialcell':[i,j]})
        w=self.Walker(self,**kw)
        self.AddObject(w)
        self.current.append(w)
        
    def Clear(self):
        for x in self.current:
            self.cellget(x.cell).remove(x,triggers=())
        self.current=[]
        
    def KillCurrent(self):
        for x in self.current:
            C=self.cellget(x.cell)
            C.remove(x,triggers=('kill',))
        self.current=[]
