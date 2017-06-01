from collections import deque
from time import sleep as pause,time
import traceback as tb

class LockedEvent:
    def __init__(self,cmd):
        self.locked=True
        self.iter=iter(())
    def __call__(self,ob):
        self.iter=self.cmd(ob)
        return self
    def __iter__(self):
        self.iter

class EventQueue:
    InactiveException=type('InactiveException',(Exception,),{})
    NotProcessing=InactiveException('Not Currently Processing Events')
    #used to synchronize map events, like walking
    #The first queue object is a list of things to be done in sync.
    #These are done, then the world is redrawn
    #Then the same is done for the second event.
    #A given object has its events placed at successive positions in the queue

    from tkinter import BooleanVar
        
    def __init__(self,parent):
        
        self.call_depth=0
        self.queue=[]
        self.processing_errors=deque()
        self.event_buffer=deque()
        self._obs=set()
        self.processing=None
        self.obj_map={}
        self.parent=parent
        self.cancel_flag=False
        self.hold_var=self.BooleanVar()
        self.locked=False

    def add(self,event,obj,name=None,position=None):

        if self.is_processing:
            self.buffer_events((event,obj,name,position))
        else:
            locked=event.locked if isinstance(event,LockedEvent) else False
            if not locked or event in self._obs:
                if name is None:
                    name=str(event)
                to_add=(event,obj,name)
                if position is None:
                    try:
                        position=self.obj_map[obj]
                    except KeyError:
                        position=0
                        self.obj_map[obj]=0
                try:
                    self.queue[position].append(to_add)
                except IndexError:
                    self.queue.append([to_add])
                self.obj_map[obj]+=1            

    def append(self,event,obj,trigger='append'):
        if self.processing is None:
            raise self.NotProcessing
        self.processing.append((event,obj,trigger))
                
    def prepend(self,event,obj,trigger='insert'):
        if self.is_processing:
            self.processing.appendleft((event,obj,trigger))
        else:
            self.add((event,obj,trigger,0))
        
    def hold_draw(self,q=10):
        if q==0:
            self.parent.DrawNow()
        else:
            if not isinstance(q,int):
                q=int(q*1000)
            def dp(self=self):
                self.hold_var.set(False)
                self.hold_var.set(True)
            self.parent.DrawNow()
            self.parent.after(q,dp)
            self.parent.wait_variable(self.hold_var)
    
    def process_command(self,G,wait,to_do):
    
        if isinstance(G,LockedEvent):
            G.locked=True
        try:
            r=next(G)
        except StopIteration:
            if isinstance(G,LockedEvent):
                G.locked=False
            r=None
        except Exception as E:
            self.processing_errors.append((E,tb.format_exc()))
#             tb.print_exc()
            r='break'

        if isinstance(r,(float,int)):
            if not to_do is None:
                to_do.append(G)
            wait=max(wait,r)
        elif r=='draw':
            if not to_do is None:
                to_do.append(G)
            self.parent.DrawNow()
        elif r=='break':
            if isinstance(G,LockedEvent):
                G.locked=False
            wait=r
            
        return wait
        
    def process_start(self): 
        '''Parses all events up until a 'break' or until the events are exhausted
        
If a 'break' occurs, all events that were started before hand are exhausted before going on.'''
        
        to_do=deque()
        wait=0
        
        while self.processing:
            e,o,n=self.processing.popleft()
            self.obj_map[o]+=-1
            G=e(o)
            r=self.process_command(G,wait,to_do)
            if r=='break':
                break
            else:
                wait=r    
        self.processing=to_do
        self.pause(wait,True)
    
    def process_finish(self):
        
        to_do=self.processing
        wait=0
        
        while self.processing:
            wait=0
            G=self.processing.popleft()
            if isinstance(G,tuple):
                G=G[0](G[1])
            r=self.process_command(G,wait,to_do)
            if r=='break':
                self.processing.clear()
                break
            else:
                wait=r
            self.pause(wait)
        else:
            self.pause(wait,True)
        
    def process(self):
        self.process_start()
        self.process_finish()
        
    def __next__(self):
        
        if self.queue:
            draw_flag=True
            self.processing=deque(self.queue.pop(0))
            self.process()
    
    def execute_events(self,*events):
        if len(events)>0:
            eq=type(self)(self.parent)
            if not isinstance(events[0],tuple):
                events=(events,)
            for e in events:
                eq.add(*e)
            eq.empty_queue()
            
    def pause(self,wait,draw=False):
#         self.hold_draw(wait)
        if draw:
            self.parent.DrawNow()
        pause(wait)
    
    def lock(self):
        if self.is_processing:
            self.locked=True
            
    def buffer_events(self,*events):
        if not self.locked:
            self.event_buffer.extend(events)
    
    def empty_buffer(self):
        if not self.is_processing:
            for e in self.event_buffer:
                self.add(*e)
            self.event_buffer.clear()
    
    def empty_queue(self,lock=False):
        
        self.call_depth+=1
        if lock:
            self.processing=True
            self.lock()
        while self.queue:
            if self.cancel_flag:
                break
            next(self)
        if (not self.processing is True) and self.processing:
            self.process_finish()
        if self.call_depth==1:
            self.processing=None
            self.queue.clear()
            self.empty_buffer()
            self.cancel_flag=False
            self.locked=False
        self.call_depth-=1
        
    @property
    def is_processing(self):
        return (not self.processing is None)
    
    def __repr__(self):
        q=self.processing if self.is_processing else self.queue
        s='EventQueue{}'.format([x for x in q])
        return s

