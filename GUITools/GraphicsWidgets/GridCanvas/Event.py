class Event:
    def __init__(self,callback,frequency=1,trigger='enter',name=''):
        from random import random

        self.f=frequency
        self.c=callback
        self.t=trigger
        self.r=random
        self.n=str(name)

    def __hash__(self):
        return hash((self.f,self.c,self.t,self.r,self.n))
    
    @property
    def null(self):
        yield 'done'
    
    @property
    def name(self):
        return self.n
    @property
    def trigger(self):
        return self.t
    @property
    def frequency(self):
        return self.f
    @property
    def callback(self):
        return self.c
                
    def __str__(self):
        return '{}*{}*{}'.format(self.t,self.f,self.n)
    
    def __repr__(self):
        return 'GridCanvas.Event[{!s}]'.format(self)

    def call(self,cell,ob):
        if self.r()<self.f:
            return self.c(cell,ob,self.t)
        else:
            return self.null
                
        
