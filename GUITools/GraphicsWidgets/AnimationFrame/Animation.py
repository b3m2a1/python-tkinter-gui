from ..Shared import *
from ...ImageTools import ImageWrapper 
from queue import Queue

class Animation(list):

    from GeneralTools.ImportTools import PathLoader
    Loader=PathLoader()

    vector=vector
    def __init__(self,parent,*args,file=None,pass_obs=[],
                 animation_directory=None,step_rate=100):
        from string import ascii_lowercase,digits
        from random import choice
        super().__init__(args)
        self.parent=parent
        self.current=0
        self.key=''.join((choice(ascii_lowercase+digits) for x in range(6)))
        self.queue=Queue()
        self.step_rate=step_rate
        if animation_directory is None:
            animation_directory=self.parent.source
        self.animation_source=animation_directory
        self.call_function=None
        self.source_file=None
        if not file is None:
            self.load(file,animation_directory)
        self.pass_obj=None
        self.pass_obs=[]

        self.command_lookup={}

    def call(self,times=1,on_what=None):
        
        for x in range(times):
            self.prep_queue(on_what)
            self.empty_queue()
            
    def prep_queue(self,on_what=None):
        if on_what is None:
            on_what=self.parent
        self.current=0
        for i in range(len(self)):
            f=self[i]
            self.queue.put(f)
        self.queue.put('end')
        
    def get_image(self,image_name,ext='.png'):
        file=os.path.join(self.animation_source,'Images',image_name)
        I=ImageWrapper(file)
        return I
    
    def empty_queue(self):
        i=iter(lambda:self.queue.get(0),'end')
        for f in i:
            self.parent.hold_update(lambda:self.evaluate(f))
    
##    def __getitem__(self,i):
##        return self.process_function(self.parent,*super().__getitem__(i))

##    @staticmethod
##    def process_function(on_what,name,args=None,kwargs=None,obj_key=None):
##        if args is None:
##            args=()
##        if kwargs is None:
##            kwargs={}
##        rep=str(name)
##        if isinstance(name,str):
##            name=getattr(on_what,name)
##            name=lambda s,*a,f=name,**k:f(*a,**k)
##        if obj_key=='pass':
##            func=lambda self,animation_function=name,args=args,kwargs=kwargs:animation_function(self,self.pass_obj,*args,**kwargs)
##        else:
##            func=lambda self,animation_function=name,args=args,kwargs=kwargs:animation_function(self,*args,**kwargs)
##        if obj_key=='get':
##            func=lambda self,f=func:self.set_val(func)
##        func.__repr__=lambda s,rep=rep:rep
##        return func

    def set_obj(self,function):
        self.pass_obj=function(self)
        
    def evaluate(self,function):
        o=function(self)
        self.pass_obs.insert(0,o)
        return o
        
    def step(self):
        if self.current<len(self):
            f=self[self.current]
            self.parent.after(self.step_rate,lambda:self.evaluate(f))
            self.current+=1
        else:
            raise StopIteration
    
    def __next__(self):
        self.step()

    def wrap_parent(self,function,*args,**kwargs):
        
        n=function.__name__
        def wrapped(self,*args,**kwargs):
            return function(self,self.parent,*args,**kwargs)
        wrapped.__name__=n
        return wrapped
    
    def load(self,file,*load_args,source=None,default_ext='.txt',**load_kwargs):
        
        if source is None:
            source=self.animation_source
            
        n,e=os.path.splitext(file)
        if e=='':
            file=file+default_ext
            e=default_ext
            
        path=os.path.join(source,file)
        if os.path.exists(path):
            if e=='.txt':
                with open(path) as in_file:
                    self.load_string(in_file.read())
            elif e in ('.py','.pyc'):
                M=self.Loader.load_module(path)
                if hasattr(M,'load_animation'):
                    A=M.load_animation(self,self.parent,*load_args,**load_kwargs)
                else:
                    A=M.animation
                self.extend([self.wrap_parent(f) for f in A])
            else:
                raise ImportError('{}.load: unsure how to load files of type {}'.format(type(self).__name__,e))

            self.source_file=(file,source)
            
    def call_animation(self,animation,*call_args,source=None,**call_kwargs):
        if isinstance(animation,str):
            f=animation
            animation=type(self)(self.parent)
            animation.load(f,*call_args,source=source,**call_kwargs)
        animation.call()
        
    def load_string(self,read_string):
        import re
        
        commands=[a for x in [l.split(';') for l in read_string.splitlines()] for a in x if a!='']
        commands.reverse()
        
        prim_pat=r'[^\s()\'"\[\]=+/,;]+';prim_re=re.compile(prim_pat)
        string_pat=r'[\'"].*?[\'"]';
        par_pat=r'[[({].*?[])}]';par_re=re.compile(par_pat)
        index_pat='{0}\[\s*{0}\s*\]'.format(prim_pat)
        operation_pat=r'(({0}[+\-/])+{0})'.format('({0}|{1}|{2}|{3})'.format(prim_pat,string_pat,par_pat,index_pat))
        arg_pat="attr\[\s*"+prim_pat+"\s*\]";arg_re=re.compile(arg_pat)
        call_pat="c\(-*\)";call_re=re.compile(call_pat)
        obj_pat='|'.join( (operation_pat,arg_pat,call_pat,string_pat,par_pat,prim_pat));obj_re=re.compile(obj_pat)
        key_pat=r'({}\s*=\s*({}))'.format(prim_pat,obj_pat);key_re=re.compile(key_pat)
        bits_pattern='({}|{})'.format(key_pat,obj_pat);bits_re=re.compile(bits_pattern)

        call_innards='|'.join((prim_pat,string_pat,par_pat,operation_pat))
        call_small='({0}\(\s*(({1})\s*,\s*)*({1})?\s*\))'.format(prim_pat,call_innards)
        call_chop=re.compile(call_small)
        
        def find_calls(command):

            call_list=[]
            segments=[]
            found=list(call_chop.finditer(command))
            base_cmd=command
            while len(found)>0:
                for f in found:
                    start=f.start();end=f.end()
                    segments.append((start,end))
                    call=command[start:end]
                    command=command[:start]+'c'*(end-start)+command[end:]
                found=list(call_chop.finditer(command))

            
            while segments:
                start,end=segments.pop()
                remove=[]
                for i in range(len(segments)):
                    s,e=segments[i]
                    if s<start and end<e:
                        break
                    elif start<s and e<end:
                        remove.append(i)
                else:
                    call_list.append((start,end))
                    
                for ind in remove:
                    segments.pop(ind)                
            
            return [(base_cmd[s:e],s,e) for s,e in call_list]
    
        while commands:
            command=commands.pop()

            for r in arg_re.finditer(command):
##                            print(r.group(0))
                command=arg_re.sub('self.{}'.format(r.group(0)[5:-1]),command,1)
                            
            calls=find_calls(command)
            for c,s,e in calls:
                command=command[:s]+'c('+'-'*(e-s-3)+')'+command[e:]
            calls.reverse()
            var=None

            k_match=re.match(prim_pat+r'\s*=\s*'+'.+',command)
            c_match=call_re.match(command)
            if k_match is not None and k_match.group(0)==command.strip():
                
                var,command=command.split('=',1)
                obj_match=obj_re.match(command)
                if obj_match is not None and obj_match.group(0)==command.strip():
                    command='inert '+command
            if c_match is not None:
                print(c_match.group(0),command)
            if c_match is not None and c_match.group(0)==command.strip():
                command,s,e=calls.pop()
                self.append(lambda s=self,c=command,l=locals():exec(c,None,l))
            else:
                
                bits=[b[0] for b in re.findall(bits_pattern,command)]
##                print(bits)
                bit=bits[0].strip()
                if bit=='call':
                    bit='call_animation'
    
                if bit=='repeat':
                    try:
                        end_rep_ind=commands.index('end_repeat')
                        commands.pop(end_rep_ind)
                    except ValueError:
                        end_rep_ind=0
                    if len(bits)==1:
                        reps=2
                    else:
                        reps=eval(bits[1])
                    if reps>1:
                        base_chunk=commands[end_rep_ind:]
                        if len(bits)>2:
                            var=bits[2]
                            chunks=[base_chunk+['{0}={1}'.format(var,i)] for i in range(reps-2,-1,-1)]
                            command_chunk=['{0}={1}'.format(var,reps-1)]+[c for ch in chunks for c in ch]
                        else:
                            command_chunk=base_chunk*reps
                        commands.extend(command_chunk)
                elif bit=='delay':
                    pass
                else:
                    try:
                        func=lambda a:a
                        if bit!='inert':
                            func=self.command_lookup[bit]
                    except KeyError:
                        func=getattr(self,bit)
                    def get_bit(b,arg_re=arg_re,calls=calls):
                        ret=None
                        for c in call_re.finditer(b):
                            c,s,e=calls.pop()
                            b=b[:s]+c+b[:e]
                        if b=='obj':
                            ret=('arg',self.obj)
                        elif key_re.match(b) is not None:
                            key,val=b.split('=',1)
                            ret=('kwarg',(key,get_bit(val)[1]))
                        else:
                            ret=('arg',eval(b))
                        return ret
                    
                    def call_function(self=self,f=func,v=var,lines=bits[1:]):
                        args=[]
                        kwargs={}
                        for b in lines:
                            key,val=get_bit(b)
                            if key=='arg':
                                args.append(val)
                            else:
                                kwargs[val[0]]=val[1]
                        if v is None:
                            return f(*args,**kwargs)
                        else:
                            setattr(self,v,f(*args,**kwargs))
                        
                    self.append(call_function)
                
    def __getattr__(self,attr):
        return self.parent.__getattribute__(attr)
        
    def __repr__(self):
        return 'Animation_{}{{{}}}'.format(self.key,',\n'.join((repr(x) for x in self)))

    
