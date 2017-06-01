from ..Shared import *
class Cell:
    
    class FullException(Exception):
        def __init__(self):
            super().__init__('Cell Full')        
    Full=FullException()
    event_keys=(('enter','exit','spawn','kill','fail','exit_window')+
                tuple(('{}_{}'.format(x,y)
                        for x in ('up','down','left','right') for y in ('enter','exit')
                        ))
                )
                
    def __init__(self,parent,i,j,space=None,obs=None,image=None,
                 draw_mode='below',full=None,**kwargs):
        if not obs:
            obs=()
        self.image=image
        self.draw_mode=draw_mode
        if not image is None:
            self.set_background(image)
        if full is None:
            def full():
                raise self.Full
        self.full=full
        self.pos=(i,j)
        self.events=self.new_event_dict()
        self.obs=OrderedSet(*obs)
        self.__space=space
        self.base_space=space
        self.drawn=[None]
        self.parent=parent
        self.kwargs=kwargs
        self.draw_mode=draw_mode

        self.InactiveException=self.parent.InactiveException

    @classmethod
    def new_event_dict(cls):
        base={x:[] for x in cls.event_keys}
        base.update({None:()})
        return base
    def bbox(self,incs=None):
        return self.parent.BBox(*(self.pos),incs=incs)

    def call(self,trigger,ob,cell=None,source=None,mode='append',lock=False):
        
        if cell is None:
            cell=self
            
        if source is None:
            source=self.events

        Q=self.parent.event_queue
        if Q.is_processing:
            if mode=='now':
                Q.execute_events(*((lambda o,c=cell,x=x:x.call(c,o),ob) for x in source[trigger]))
            else:
                for x in source[trigger]:
                    if mode=='append':
                        Q.append(lambda o,c=cell,x=x:x.call(c,o),ob)
                    elif mode=='prepend':
                        Q.prepend(lambda o,c=cell,x=x:x.call(c,o),ob)
        else:
            for x in source[trigger]:
                Q.add(lambda o,c=cell,x=x:x.call(c,o),ob,name='{}.{}_response on {}'.format(cell,trigger,ob))
            self.parent.step(queue_lock=lock)
    
    def clear_events(self,trigger=None):
        if trigger is None:
            self.events=self.new_event_dict()
        else:
            evs=self.events[trigger] #for the KeyError
            self.events[trigger]=[]
        
    def bind(self,callback,frequency=1,trigger='enter',name='',to='events'):
        E=self.parent.Event(callback,frequency,trigger,name)
        evs=getattr(self,to)
        evs[trigger].append(E)
        
    def config(self,**kwargs):
        self.kwargs.update(kwargs)
        self.parent.backgroundFlag=True
        
    def cget(self,c):
        return self.kwargs[c]

    @property
    def space(self):
        N=self.__space
        if not N is None:
            for x in self.obs:
                if not x is None:
                    N+=-x.size
        return N
    @space.setter
    def space(self,val):
        for x in self.obs:
            val+=x.size
        self.__space=val

    @property
    def total_space(self):
        return self.__space
        
    def append(self,ob,triggers=('enter',),override=False):
        if isinstance(ob,GridGraphic):
            flag=True
            if not (override or self.space is None):
                if ob.size>self.space:
                    flag=False
                    self.full()
            if flag:
                self.obs.add(ob)
                #ob.cell[:]=self.pos
                for t in triggers:
                    self.call(t,ob)
                    
    def activate_here(self):
        self.parent.current.extend(self.obs)
        
    def deactivate_here(self):
        for x in self.obs:
            try:
                self.parent.current.remove(x)
            except ValueError:
                pass
        
    def set_background(self,image_source):
        if not image_source is None:
            self.image=GridImage(image_source,parent=self.parent)
        else:
            self.image=None
        self.parent.backgroundFlag=True
        
    def remove(self,ob,triggers=('exit',)):
        self.obs.remove(ob)
        for t in triggers:
            self.call(t,ob)
            
    def clear_objects(self,triggers=()):
        for o in self.obs:
            self.remove(o,triggers=triggers)
##        self.space=self.__space
        
    def __getitem__(self,i):
        return self.obs[i]

    def __str__(self):
        return '[{0[0]!s},{0[1]!s}]'.format(self.pos)

    def Background(self,border=None,incs=None,tags=()):
        if border:
            self.kwargs['outline']='black'
        else:
            self.kwargs['outline']=''
        bbox=self.bbox(incs)
        if not isinstance(tags,tuple):
            tags=tuple(tags)
        tags+=('background',)
    
        if self.image is None:
            self.drawn[0]=(self.parent.create_rectangle(*bbox,tags=tags,**self.kwargs))
        else:
            self.drawn[0]=(self.image.Draw(self.parent,bbox,tags=tags))
            
    def Draw(self,border=None,incs=None,tags=()):
        bbox=self.bbox(incs)
        if not isinstance(tags,tuple):
            tags=tuple(tags)
        tags+=('objects',)
        self.drawn.extend((ob.Draw(self.parent,bbox=bbox,tags=tags) for ob in self.obs))
        if self.draw_mode=='above':
            if not self.drawn[0] is None:
                for x in self.drawn[1:]:
                    try:
                        self.parent.tag_lower(x,self.drawn[0])
                    except:
                        break
