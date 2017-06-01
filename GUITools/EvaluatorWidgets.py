#Evaluation related GUITools
from .TextWidgets import *
from .FileWidgets import *

class TextEvaluator:

    ###This is simply a wrapper for the Evaluator class which implements the
    ###process loop. It will take strings and receieve strings.
    def __init__(self,parent=None,variables=None,outputFile=None,newThread=False):

        import signal
        
        self.input=mp.Queue(1)
        self.output=mp.Queue()
        self.evaluator=Evaluator(reciever=self.input,sender=self.output,
                                 locals=variables,outputFile=outputFile)
        if not outputFile:
            outputFile=self.evaluator.baseout
        self.outputFile=outputFile
        self.parent=parent
        self.running=False
        self.exitQueue=mp.Queue()
        self.newThread=newThread

    def put(self,item,*args,**kwargs):

        ###CHECK THAT ITEM IS A STRING
        self.input.put(item,*args,**kwargs)

    def get(self,lock=True):

        R=self.output.get(lock)
        return R

    def setVariable(self,name,value):
        if self.running:
            self.evaluator.variableQueue.put((name,value))
        else:
            self.evaluator.locals[name]=value

    def valueRequest(self,name):
        if self.running:
            self.evaluator.requestQueue.put(name)
            self.signal.alarm(1)
            r=self.evaluator.responseQueue.get()
            self.signal.alarm(0)
            return r
        else:
            return getattr(self.evaluator,name)
    
    def REP(self,string,mode='print',quantity='full'):

        self.put(string)
        self.evaluator.Evaluate()
        x=self.get()
        if mode=='print':
            O=self._formatOutput(x,mode=quantity)
            print(O.rstrip('\n'),file=self.outputFile)
            return None
        return x

    def _formatOutput(self,outTrip,mode='full'):
        def spaceJoin(x):
            return '\n'.join(x)
        if mode=='full':
            T="""Output:
{}
Variables:
{}
Errors:
{}
""".format(spaceJoin(outTrip[0]),spaceJoin(outTrip[1]),spaceJoin(outTrip[2]))
        else:
            T=spaceJoin(outTrip[0])
            if not T:
                T=spaceJoin(outTrip[2])
        return T
    
    def run(self,ret=False):

        if self.newThread:
            def runprocess():

                killFlag=False
                evaluator=self.evaluator
                while not killFlag:
                    try:
                        k=self.exitQueue.get(0)
                    except queue.Empty:
                        pass
                    else:
                        killFlag=k
                evaluator.close()
            self.loop=mp.Process(target=runprocess)
            self.loop.daemon=True
            self.loop.start()
            self.running=True
        else:
            I=input('>> ')
            while not I=='kill':
                self.REP(I,quantity='out')
                I=input('>> ')
                
    def __del__(self):
        self.kill()
        try:
            super().__del__()
        except:
            pass

    def kill(self):

        self.input.put('')
        self.exitQueue.put(True)
        self.evaluator.outFile.close()

    def __getattribute__(self,attr):

        try:
            return super().__getattribute__(attr)
        except AttributeError as E:
            try:
                return self.evaluator.__getattribute__(attr)
            except KeyError:
                pass
            raise E
        
class Evaluator(code.InteractiveConsole):

    import signal,re,io,threading
    
    def __init__(self,reciever=None,sender=None,name=None,
                 outputFile=None,locals=None):

        ###NEW STRUCTURE: LET THIS ACT AS A CONSTANT EVALUATION LISTENER
        ###PUT IT IN AN EVAL LOOP PROCESS WHICH SPITS OUT EVALUATED STRINGS
        ###KEEP ALL VARIABLES SAVED TO THE CLASS AND ONLY EVER RETURN STRINGS
        ###BASICALLY JUST A VARIABLE SAVER + EXECUTION FUNCTION
        ###INPUT STRING|->PARSING + EVALUATION|->STRING RESULT
        
        import sys,tempfile as tf
        super().__init__(locals=locals)
        if not name:
            name=type(self).__name__
        self.name=name
        if not reciever:
            reciever=mp.Queue()
        if not sender:
            sender=mp.Queue()
        self.variableQueue=mp.Queue()
        self.requestQueue=mp.Queue()
        self.responseQueue=mp.Queue()
        self.reciever=reciever
        self.sender=sender
        self.outTrip=([],[],[])
        if not outputFile:
            outputFile=tf.TemporaryFile(mode='w+')
            self.mode='temp'
        else:
            self.mode='str'
            self.filestr=outputFile
        self.outFile=outputFile
        self.baseout=sys.stdout
        signal=self.signal
        self.sys=sys
        
        def handle(signum,frame):

            self.outTrip[2].append('Timeout Error'.format(frame))
            self.signal.alarm(0)
        
        signal.signal(signal.SIGALRM,handle)

    def __getattr__(self,attr):

        try:
            super().__getattribute__(attr)
        except AttributeError as E:
            try:
                return super().__getattribute__('locals')[attr]
            except AttributeError:
                pass
            raise E
        
    def put(self,ob,**kwargs):

        self.reciever.put(ob,**kwargs)

    @staticmethod
    def queueFlush(queue):
        while True:
            try:
                yield queue.get(0)
            except:
                break

    def variable_set(self):

        n,v=self.variableQueue.get()
        if not n is None:
            self.locals[n]=v

    def variable_response(self):

        x=self.requestQueue.get()
        if not x is None:
            try:
                v=getattr(self,x)
            except:
                v=tb.format_exc()
            self.responseQueue.put(v)

    
    def start(self):
        
        Thread=self.threading.Thread
        Event=self.threading.Event
        kill=self.killEvent=Event()
        def loop(killEvent,func):
            while not killEvent.is_set():
                func()
                
        self.setThread=sT=Thread(target=loop,args=(kill,self.variable_set))
        self.respThread=rT=Thread(target=loop,args=(kill,self.variable_response))
        self.execThread=eT=Thread(target=loop,args=(kill,self.Evaluate))
        self.running=True
        sT.daemon=True;sT.start();rT.daemon=True;rT.start();eT.daemon=True;eT.start()        
        
    def close(self):

        self.running=False
        self.killEvent.set()
        self.variableQueue.put((None,None));self.requestQueue.put(None);self.reciever.put('')
        self.setThread.join();self.respThread.join();self.execThread.join()
        self.outFile.close()
        
    def get(self,lock=True):
        
        return self.sender.get(lock)

    def send(self):

        self.outFile.seek(0)
        R=self.outFile.read().strip()
        self.outTrip[0].append(R)
        self.outFile.seek(0)
        self.outFile.truncate()
        self.outTrip[1].extend(self.locals)
        out=tuple([tuple(x) for x in self.outTrip])
        self.sender.put(out)
        for x in self.outTrip:
            x[:]=[]

    def push(self,source):
        sys=self.sys
        if isinstance(self.outFile,self.io.IOBase):
            sys.stdout=self.outFile
        try:
            m=''
            try:
                c=code.compile_command(source,self.name,'eval')
                m='eval'
            except SyntaxError as E:
                try:
                    c=code.compile_command(source,self.name,'exec')
                    m='exec'
                except SyntaxError:
                    t,e,tr=sys.exc_info()
##                    self.outTrip[2].append(tb.format_exc(chain=False))
                    arg_string,arg_tup=e.args
                    file,line,pos,err_string=arg_tup
                    if file==self.name:
                        base='Error in line {}'.format(line)
                    else:
                        base='File: {}, line {}'.format(file,line)
                    lines=['Traceback (most recent call last):',
                           '\t'+base,
                           '\t\t{}'.format(err_string.strip()),
                           '\t\t{}^'.format((pos-1)*' '),
                           '{}: {}'.format(t.__name__,arg_string)]
                    self.outTrip[2].extend(lines)
                    
                    
                    
##                    self.outTrip[2].append(str(e.args))
                                           
##                    raise SyntaxError(*new).#tb.TracebackException.from_exception(E,limit=4)
            if m:
                self.runcode(c,mode=m)
        except:
            raise
        finally:
            sys.stdout=self.baseout
        
##    def runsource(self,source,filename=None,symbol='exec',**kwargs):
##
##        if not filename:
##            filename='<{}>'.format(source[:-1])
##        sys=self.sys
##        sys.stdout=self.outFile
##        super().runsource(source,filename=filename,symbol=symbol,**kwargs)
##        sys.stdout=self.baseout

    def runcode(self,code,mode='eval',**kwargs):
        
        if mode=='eval':
            try:
                R=eval(code,self.locals,self.locals)
            except:
                super().runcode(code)
            else:
                if not R is None:
                    print(R,**kwargs)
        elif mode=='exec':
            super().runcode(code)

    def write(self,data):
        self.outTrip[2].append(str(data))
        
    def printout(self,*args,file=None,**kwargs):
        
        if not file:
            file=self.baseout
        print(*args,file=file,**kwargs)

    def EvalString(self,string):

        self.reciever.put(string)
        self.Evaluate()
        
    def Evaluate(self,waitTime='default'):

        T=self.reciever.get()
        L=T.splitlines()#self._formatString(T)
        if waitTime:
            if waitTime=='default':
                waitTime=len(L)+1
        T='\n'.join(L)+'\n'
        self.signal.alarm(waitTime)
        if self.mode=='str':
            self.outFile=open(self.filestr,'w+')
        try:
            self.push(T)
            self.signal.alarm(0)
        except:
            self.outTrip[2].append(tb.format_exc())
            raise
        finally:
            self.send()
            if self.mode=='str':
                self.outFile.close()

    def _formatString(self,string):
    
        avoid=['from','return','import','break','print(']
        L=string.splitlines()
    
        while L:
            line=L.pop(-1)
            S=line.strip()
            T=S.split()
            tests=[x not in T[0] for x in avoid]
            if all(tests):
                ws=self.re.match(r"\s*", line).group()
                L.append('{}print({})'.format(ws,S))
                break
            else:
                L.append(line)
                break
            
        return L
    
class ModuleText(ColoredText):

    import re,traceback as tb,signal
    
    def __init__(self,root=None,name=None,file=None,evalfile=None,
                 variables=None,NewlineSpaces=4,newThread=False,waitTime=2,**kwargs):
        if not 'wrap' in kwargs:
            kwargs['wrap']='none'
        
        super().__init__(root,name=name,NewlineSpaces=NewlineSpaces,**kwargs)
        for x in (('error','red'),('input','grey'),('output','blue3')):
            exec('self.tag_configure("{}",foreground="{}")'.format(*x))       
        self.file=file
        self.header=''
        self.outputNum=1
##        del x
        if not variables:
            variables={'self':self,'main':root}
            
        self.evaluator=TextEvaluator(parent=self,variables=variables,outputFile=evalfile,newThread=newThread)
        
        if newThread:
            self.evaluator.run()
        self.newThread=newThread
        if newThread==False:
            waitTime=200
        self.waitTime=waitTime
        self.localPat=REPattern('local',[k for k in locals()],value='blue',
                              avoid=('error','string','ignore',
                                     'output','input'),priority=0)
        self.AddPattern(self.localPat)
        self.bind('<Command-Return>',lambda*e:self.ExecuteAndWrite(self.getString()))
        self.bind('<Return>',lambda*e:self.NewLine())
        self.bind('<Command-s>',lambda*e:self.Save(file=self.file))
        self.bind('<Command-o>',lambda*e:self.importFrom())

        if not file is None and os.path.exists(file):
            with open(file) as f:
                self.Insert(f.read())
                self.after_idle(lambda s=self:s.after(100,s.ColorText))
    
    def getString(self,first='1.0',last='end'):

        return self.get(first,last)

    def Save(self,file=None,mode='name'):
        if not file:
            from tkinter.filedialog import asksaveasfilename as ask
            file=ask(parent=self)
            self.file=file
        if isinstance(file,str):
            if file:
                with open(file,'w+') as F:
                    F.write(self.getAll())
        else:
             file.write(self.getAll())           
        
    def close(self):

        self.evaluator.kill()
        
    def importFrom(self,file=None):

        if not file:
            from tkinter.filedialog import askopenfilename as ask
            file=ask(parent=self)
        if not self.file:
            self.file=file
        with open(file,'r') as F:
            self.Append(F.read())
            self.ColorText()
                
    def ExecuteAndWrite(self,string):

        if string:
            self.writeOutput(*self.Execute(string))

        return 'break'
            
    def Execute(self,string):
        
        if self.newThread:
            self.evaluator.put(string)
            try:
                self.signal.alarm(self.waitTime)
                O,V,E=self.evaluator.get()
                self.signal.alarm(0)
            except:
                self.evaluator.input.get(0)
                O=''
                E='Timeout Error'
                V={}
        else:
            try:
                O,V,E=self.evaluator.REP(string,mode='return')
            except:
                try:
                    self.signal.alarm(self.waitTime)
                    self.evaluator.get()
                    self.signal.alarm(0)
                except:
                    pass
                O,V=('',{})
                E=self.tb.format_exc()
            
        if E:
            tag='error'
            O=E
        elif O:
            tag='output'
        if len(O)==1:
            O=O[0].strip()
            
        self.localPat.update(V)                                
        return O,tag

    
    def writeOutput(self,outPut,t,on=None):

            if on is None:
                on=self
            i=self.index('insert')
            if t=='error':
                S=outPut.splitlines()
                outPut='\n#'.join(S)
                R='\n#'+outPut+'\n'
            elif t=='output':
                try:
                    if isinstance(outPut,str):
                        raise
                    outPut='\n\t'+'\n\t'.join([str(x) for x in outPut])
                except:
                    outPut='\n\t'+str(outPut)
                S=outPut.splitlines()
                outPut='\n#'.join(S)
                R='\n#--/Ouput {}:'.format(self.outputNum)+outPut+'\n'
                self.outputNum+=1
            else:
                R=outPut
            on.Insert(R,tag=t)
            self.ColorText(i)
##            return 'break'

class InterpreterText(ModuleText,LockText):

    def __init__(self,root=None,name=None,prompt='>> ',wrap='char',**kwargs):

        import code
        self._configured=False
        super().__init__(root,name=name,wrap='char',**kwargs)
        self.isp=str(prompt).replace('\n','>')
        self.activeLine='2.0'
        self.Append('Input:\n{}'.format(self.isp),tag='input')
        self.lock('1.0','end -1c')
##        self.bind('<Key>',self.Insert,add='+')
        self.bind('<Command-d>',lambda*e:self.Clear())
        self.unbind('<Command-s>')
        self.unbind('<Command-o>')
        self._configured=True
    
    def __setattr__(self,attr,val):
        super().__setattr__(attr,val)
        if attr!='_configured' and self._configured:
            self.evaluator.setVariable(attr,val)
        
    def Clear(self):

        self.unlock('0.0',self.activeLine+'linestart +1c')
        self.delete('0.0',self.activeLine+'linestart')
        self.activeLine='1.0'
        self.lock('0.0',self.activeLine+'+1c')

    def insert(self,*args,**kwargs):
        kwargs['call']=lambda ind,text,tag,s=self:s.ColorText('{} linestart'.format(ind),'{} lineend'.format(ind))
        ret=LockText.insert(self,*args,**kwargs)
        self.color_from_stack()
        return ret
    
    def delete(self,*args,**kwargs):
        kwargs['call']=lambda ind,last,s=self:s.ColorText('{} linestart'.format(ind),'{} lineend'.format(ind))
        ret=LockText.delete(self,*args,**kwargs)
        self.color_from_stack()
        return ret
        
    def getString(self):

        flag=False
        try:
            j=self.index('sel.first')
            k=self.index('sel.last')
            flag=True
        except:
            i=self.index('insert +-1c')
            if self.compare(i,'>=',
                            self.activeLine+'+{}c'.format(len(self.isp))):
                s=self.activeLine+'+{}c'.format(len(self.isp))
            else:
                flag=True
                Ns=self.tag_names(i)
                if not any([x in Ns for x in ('input','output','error')]):
                    n=0
                    test=i+'-{} lines linestart'.format(n)
                    j=test+'+{}c'.format(len(self.isp))
                    while not self.get(test,j)==self.isp:
                        n+=1
                        test=i+'-{} lines linestart'.format(n)
                        j=test+'+{}c'.format(len(self.isp))
                    n=1
                    k=i+'+{} lines linestart'.format(n)
                    Ns=self.tag_names(k)
                    while not any([x in Ns for x in ('input','output','error')]):
                        n+=1
                        k=i+'+{} lines linestart'.format(n)
                        Ns=self.tag_names(k)
                    k=k+' -1c'
                    t=self.get(j,k)
                        
                else:
                    t=''
        else:
            t=self.get(j,k)
        if flag:
            self.Append(t)
            self.see('end')
            s='end'
        R=self.get(s,'end')
        R=R.lstrip(self.isp).strip()
        return R
        
    def ExecuteAndWrite(self,string,post_script=None):
        n=max(len(string.splitlines())-1,0)
        self.activeLine=self.index(self.activeLine+' +{} lines linestart'.format(n))
        res = super().ExecuteAndWrite(string)
        if not post_script is None:
            prompt_ind='end -{}c'.format(len(self.isp))
            self.unlock(prompt_ind,'end')
            self.insert(prompt_ind,post_script+'\n')
            
            self.lock('all')
            self.unlock('end -{}c','end')
        return res
            
    
    def writeOutput(self,outPut,tag,on=None):        

        if on is None:
            on=self
        i=self.index('end')
        if tag=='output':
            try:
                if isinstance(outPut,str):
                    outPut=outPut.strip()
                    raise
                outPut='\n'+'\n'.join([str(x) for x in outPut])
            except:
                if outPut:
                    outPut='\n'+str(outPut)
            R='{}\n'.format(outPut)
            self.outputNum+=1
##            if outPut[0]==None:
##                R='\n'
##            else:
##                R=('\nOutput {}:\n'.format(self.outputNum)
##                +'\n'.join([str(x) for x in outPut])
##                   +'\n')
##            self.outputNum+=1
        elif tag=='error':
            if isinstance(outPut,str):
                outPut=[outPut]
            R='\n'+'\n'.join(outPut)+'\n'
        else:
            R='\n'
            self.outputNum+=1
        if R:
            n=len(R.splitlines())
            on.Append(R,tag=tag)
            t='input'
            self.Append(self.isp.format(self.outputNum),
                        tag=t)
            p=self.activeLine+'+{} lines linestart'.format(n)
            self.activeLine=self.index(p)
            j=self.index('end')
            self.see('end')
            self.lock('1.0',j+' -1c')
            self.ColorText(i)
##        return 'break'

def idlelib_ModuleText(root=None):

    from types import MethodType
    from idlelib import macosxSupport
    from idlelib.FileList import FileList
    from idlelib.EditorWindow import EditorWindow
    import idlelib.WindowList

    idlelib.WindowList.ListedTopLevel=tk.Frame
    
    if root is None:
        root=tk.Toplevel()
    macosxSupport._initializeTkVariantTests(root)
    fl=FileList(root)
    E=EditorWindow(flist=fl)
    TF=E.text_frame
##    TF.pack_forget()
##    TF._overwritten_old_pack=TF.pack
##    TF._overwritten_old_grid=TF.grid
##    TF._overwritten_old_place=TF.place
##    TF.pack=lambda in_=root,TF=TF,**k:TF._overwritten_old_pack(in_,**k)
##    TF.grid=lambda in_=root,TF=TF,**k:TF._overwritten_old_grid(in_,**k)
##    TF.place=lambda in_=root,TF=TF,**k:TF.old_store_place(in_,**k)

##    E.pack=TF.pack
##    E.grid=TF.grid
##    E.place=TF.place
    
    return E
    
    
