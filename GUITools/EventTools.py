from .Shared import *
import re


class Binding:
    def __init__(self,seq,command=None,add='',return_value=None):
        self.seq=seq
        if not return_value is None:
            command=lambda e:return_value
        self.__command=command
        self.add=add
        self.bind_map={}

    @property
    def command(self):
        return self.__command

    @command.setter
    def command(self,function=None):
        self.__command=function
        for w in self.bind_map:
            self.remove(w)
            self.apply(w)

    def clear(self):
        self.bind_map={}
        
    def apply(self,widget,position='end',command=None,**app_kwargs):
        if command is None:
            command=self.command
        if widget in self.bind_map:
            self.remove(widget)
        if position=='end':
            if self.add=='+':
                fid=widget.bind(self.seq,command,self.add,**app_kwargs)
            else:
                fid=widget.bind(self.seq,command,**app_kwargs)
        else:
            fid=insert_binding(widget,self.seq,command,position)
        self.bind_map[widget]=fid
    def remove(self,widget):
        try:
            fid=self.bind_map[widget]
        except KeyError:
            pass
        else:
            try:
                remove_funcid(widget,self.seq,fid=fid)
            except ValueError:
                pass
##            widget.unbind(self.seq,funcid=fid)
            del self.bind_map[widget]

class TemporaryBinding(Binding):
    def __init__(self,event_sequence,command=None,return_value=None,times=1):
        self.counter=times
        super().__init__(event_sequence,command=command,return_value=return_value,add='+')        
        self.command=self.command

    def apply(self,widget,position='end'):
        super().apply(widget,position=position,command=self.increment_call)
        
    def increment_call(self,event):
##        print(event.keysym)
        self.counter+=-1
        r=self.command(event)
        if self.counter<=0:
            self.remove(event.widget)
        return r
        
class BindingLock(Binding):
    def __init__(self,event_sequence):
        super().__init__(event_sequence,return_value='break',add='+')        
    def lock(self,widget):
        self.apply(widget,position=0)
    def unlock(self,widget):
        self.remove(widget)
        
def get_funcids(widget,event_sequence):
    re_key='\d+\S+'
    splits=re.findall(re_key,widget.bind(event_sequence))
    return splits

def all_bindings(widget):
    return {widget.bind_class(cls) for cls in widget.bindtags()}

def all_funcids(widget):
    return {B:get_funcids(B) for B in all_bindings(widget)}

##def real_fid(funcid):
##    return funcid.split()[1][3:]

def bind_strings(widget,sequence):
    return (x for x in widget.bind(sequence).splitlines() if x.strip())
    
def insert_binding(widget,sequence,command,position):
    fid=widget.bind(sequence,command,'+')
    bs=list(bind_strings(widget,sequence))
    if len(bs)>1:
        s=bs.pop()
        bs.insert(position,s)
        rep_string='\n'.join(bs)
        widget.tk.call('bind',widget._w,sequence,rep_string)
    return fid
    
def remove_funcid(widget,sequence,fid=None,index=None):

##    print('sequence:',sequence)
    B=list(get_funcids(widget,sequence))
    
    if not fid is None:
        index=B.index(fid)
    if  index is None:
        raise BindError('remove_funcid: no funcid or index provided')
    b_strings=list(bind_strings(widget,sequence))
    b_strings.pop(index)
    if not b_strings:
        widget.unbind(sequence)
    else:
        rep_string='\n'.join(b_strings)
        widget.deletecommand(fid)
        b_flag=False
        for b in b_strings:
            if b_flag:
                widget.tk.call('bind',widget._w,sequence,'+'+b)
            else:
                widget.tk.call('bind',widget._w,sequence,b)
                b_flag=True
    
class BindError(Exception):
    pass
