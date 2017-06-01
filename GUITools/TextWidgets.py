#A collection of text related GUITools
from .Shared import *
##import tkinter as tk
##import string,sys,re

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class RichText(tk.Text):

    arrow_keys={'Up','Right','Down','Left'}
    
    def __init__(self,root=None,name=None,file=None,
                 NewlineSpaces=None,ReturnChar='\n',
                 track_inserts=None,track_deletes=None,**kwargs):
        self.track_inserts=track_inserts
        self.track_deletes=track_deletes
        if not 'wrap' in kwargs:
            kwargs['wrap']='word'
        if not 'tabs' in kwargs:
            kwargs['tabs']='1c'
        super().__init__(root,**kwargs)
        self.file=None
        self.defaultext=''
        self.edits_tracking=False
        self._last_text_len=0
        if NewlineSpaces is None:
            nl='\t'
        else:
            nl=' '*NewlineSpaces
        self.newspaces=nl
        self.keymap={'Tab':nl,'Return':ReturnChar,#'Up':'','Right':'','Left':'','Down':'',
                     '??':'',#'quoteleft':'`','asciitilde':'~','minus':'-','underscore':'_',
                     
                     #'equal':'=','space':' ','slash':'/','question':'?',
                     'BackSpace':''}
        if not name:
            name=type(self).__name__
        self.bind('<Control-Tab>',lambda:self.Indent)
        self.bind('<Key>',self.Insert)
        self.bind('<Command-Key>',lambda e:None)
        self.bind('<Command-a>',lambda e:self.SelectAll())
        self.bind('<BackSpace>',lambda e:self.delete(self.index('insert')))
#         self.bind('<Command-s>'),self.Save)
#         self.bind('<Command-S>'),lambda e:self.Save(True))
        self.sb=tk.Scrollbar(self.master,command=self.yview)
        self['yscrollcommand']=self.sb.set
        self.name=name
        self.undolen=0
        self.config(undo=True)
    
    def save_bind(self,defaultext=None):
        if not defaultext==None:
            self.defaultext=defaultext
        self.bind('<Command-s>',self.Save)
        self.bind('<Command-S>',lambda e:self.Save(True))
    def track_edits_bind(self):
        self.edits_tracking=True
        self.bind('<KeyPress>',self.track_edits)
    def track_edits(self,event=None):
        if self.edits_tracking and hasattr(self.master,'title'):
            l=len(self.get('all'))
            if l<self._last_text_len:
                t=self.master.title()
                t.strip('* ')
                self.master.title('* {} *'.format(t))
                
    def Save(self,event=None):
        if event is True or not self.file:
            from tkinter.filedialog import asksaveasfilename as ask
            f=ask(parent=self,title='Save as...',defaultextension=self.defaultext)
            if f:
                self.file=f
        if self.file:
            with open(self.file,'w+') as F:
                F.write(self.get('all'))
            if self.edits_tracking and hasattr(self.master,'title'):
                self.master.title(self.file)

    def get(self,index,end=None,replace_returns=False):
        if index=='all':
            index='1.0'
            end='end'
        ret=super().get(index,end)
        if replace_returns:
            ret=ret.replace(self.keymap['Return'],'\n')
        return ret

    def getAll(self):
        return self.get('all')

    
    @property
    def insertion_marker(self):
        return self.index('insert')
    @property
    def selection_indices(self):
        try:
            pair=(self.index('sel.first'),self.index('sel.last'))
        except:
            pair=None
        return pair
    
    #-------------------------------------------------------------------------
    def Clear(self):
        
        self.delete(0.0,'end')
    #--
    def SelectAll(self):
        self.tag_add('sel', "1.0", 'end')
        self.mark_set('insert', "1.0")
        self.see('insert')
        return 'break'
    #--
    def DeselectAll(self):
        self.tag_remove('sel','1.0','end')
        return 'break'
    #-------------------------------------------------------------------------
    def Append(self,text,tag=None,replace_sequences=None):
        
        return self.Insert(text,tag=tag,index='end',replace_sequences=replace_sequences)
        
    #
    def insert(self,first,text,tag=(),call=lambda fir,tex,tg:None):
        if text:
            sels=self.selection_indices
            if not sels is None:
                first,last=sels
                if text:
                    self.delete(first,last)                  
            resp=super().insert(first,text,tag)
            call(first,text,tag)
            if self.track_inserts is not None:
                for k in self.track_inserts:
                    indices=[]
                    call=self.track_inserts[k]
                    i=-1
                    if isinstance(k,str):
                        try:
                            for j in range(len(text)):
                                i=text.index(k,i+1)
                                indices.append(i)
                        except ValueError:
                            pass
                        for i in indices:
                            if isinstance(call,tuple):
                                for c in call:
                                    c(self,k,self.index('{}+{}c'.format(first,i)))
                            else:
                                call(self,k,self.index('{}+{}c'.format(first,i)))
                    else:
                        total=''.join(k)
                        try:
                            for j in range(len(text)):
                                i=text.index(total,i+1)
                                indices.append(i)
                        except ValueError:
                            pass
                        if indices==[]:
                            alt_test=self.index('{}-{}c'.format(first,len(k)-1))
##                            print(self.get(alt_test,first),total[:-1])
                            if self.get(alt_test,first)+text==total:
                                if isinstance(call,tuple):
                                    for c in call:
                                        c(self,k,alt_test)
                                else:
                                    call(self,k,alt_test)
                        else:
                            for i in indices:
                                if isinstance(call,tuple):
                                    for c in call:
                                        c(self,k,self.index('{}+{}c'.format(first,i)))
                                else:
                                    call(self,k,self.index('{}+{}c'.format(first,i)))
            return resp
    #
    def delete(self,first,last=None,call=lambda fir,las:None):

        if last is None:
            l=len(self.newspaces)
            last=first+'-{} c'.format(l)
            if self.get(last,first)!=self.keymap['Tab']:
                last=first#+'-1c'
            first,last=(last,first)
                

        text=self.get(first,last)
        resp=super().delete(first,last)
        call(first,last)
        if self.track_deletes is not None:
            
            for k in self.track_deletes:
                indices=[]
                call=self.track_deletes[k]
                
                i=-1
                if isinstance(k,str):
                    try:
                        for j in range(len(text)):
                            i=text.index(k,i+1)
                            indices.append(i)
                    except ValueError:
                        pass
                    for i in indices:
                        if isinstance(call,tuple):
                            for c in call:
                                c(self,k,self.index('{}+{}c'.format(first,i)))
                        else:
                            call(self,k,self.index('{}+{}c'.format(first,i)))
                else:
                    total=''.join(k)
                    try:
                        for j in range(len(text)):
                            i=text.index(total,i+1)
                            indices.append(i)
                    except ValueError:
                        pass
                    if indices==[]:
                        alt_test=self.index('{}-{}c'.format(first,len(k)-1))
                        if self.get(alt_test,first+'-1c')==total[:-1]:
                            if isinstance(call,tuple):
                                for c in call:
                                    c(self,k,alt_test)
                            else:
                                call(self,k,alt_test)
                    else:
                        for i in indices:
                            if isinstance(call,tuple):
                                for c in call:
                                    c(self,k,self.index('{}+{}c'.format(first,i)))
                            else:
                                call(self,k,self.index('{}+{}c'.format(first,i)))                    
        return resp
        
       # return 'break'
    #-------------------------------------------------------------------------
    def Insert(self,text,tag=(),index='insert',replace_sequences=None):

        if isinstance(text,tk.Event):
            e=text
            K=e.keysym
            C=e.char
            if K in self.keymap:
                text=self.keymap[K]
            elif C in string.printable:
                text=C
            else:
                return ''

        if text:
            if isinstance(replace_sequences,dict):
                for k,v in replace_sequences.items():
                    try:
                        v=self.keymap[v]
                    except KeyError:
                        pass
                    text=text.replace(k,v)
                    
            elif replace_sequences is not None:
                for k in replace_sequences:
                    if k=='Return':
                        text=text.replace('\n',self.keymap['Return'])
                    elif k=='Tab':
                        text=text.replace('\t',self.keymap['Tab'])
                    else:
                        text=text.replace(k[0],k[1])
                        
            i=self.index(index)
            self.insert(i,text,tag)
        return 'break'
    #-------------------------------------------------------------------------
    def NewLine(self):

        tabs=0
        current=self.index('insert')
        last=self.get(current+'-1c')
        word=self.get(current+' linestart',current+' lineend')
        tabs+=word.count(self.newspaces)
        if last in (':','(','{','['):
            tabs+=1
        self.Insert('\n'+self.newspaces*tabs)
        return 'break'
    #-
    @property
    def line_spread(self):
        sels=self.selection_indices
        if sels is None:
            s=self.insertion_marker
            sels=(s,s)
        first,last=sels
        i=int(first.split('.')[0])
        j=int(last.split('.')[0])
        lines=['{}.0 linestart'.format(k) for k in range(i,j+1)]
        self.tag_add('sel',lines[0],lines[-1]+'lineend')
        return lines
    #-
    def Indent(self,lines=None,num=1):
        if lines is None:
            lines=self.line_spread
        for x in lines:
            self.insert(x+' linestart',self.newspaces*num)
        
    #-------------------------------------------------------------------------
    def undo(self):
        try:
            self.edit_undo()
        except:
            pass
    #-------------------------------------------------------------------------
    def setundo(self):
        try:
            self.undolen=len(self.get('selection'))
        except:
            self.undolen+=1
        self.config(maxundo=self.undolen)

class LockText(RichText):

    import string

    def __init__(self,root,name=None,**kwargs):

        string=self.string
        super().__init__(root,name=name,**kwargs)
##        self.lockRanges=[]
        
        self.bind('<Command-l>',lambda*e:self.ToggleSelection(lock=True))
        self.bind('<Command-u>',lambda*e:self.ToggleSelection(lock=False))
##        self.bind'<Command-v>'
        

    def ToggleSelection(self,lock=True):
        try:
            i=self.index('sel.first')
            j=self.index('sel.last')
        except:
            pass
        else:
            if lock:
                self.lock(i,j)
            else:
                self.unlock(i,j)

##    def Insert(self,text,tag=None):
##
##        try:
##            first=self.index('sel.first')
##            last=self.index('sel.last')
##        except tk.TclError:
##            first=self.index('insert')
##            last=first
##        else:
##            self.delete(first,last)
##
##        return super().Insert(text,tag)
            
            
    def checkIndex(self,*indices):

        names=[]
        for i in indices:
            names.extend(self.tag_names(i))
        if 'lock' in names:
            return False
        else:
            return True
        
    def insert(self,first,text,*tags,**kwargs):

        if self.checkIndex(first):
            return super().insert(first,text,*tags,**kwargs)
        return 'break'

    def delete(self,first,last=None,**kwargs):

        if last is None:
            try:
                first=self.index('sel.first')
                last=self.index('sel.last')
            except:
                last=first
                first+='-1c'
        
        if self.checkIndex(first,last):
            super().delete(first,last,**kwargs)
        return 'break'

    def lock(self,start,end=None):
        if start=='all':
            start='0.0'
            end='end'
        self.tag_add('lock',start,end)

    def unlock(self,start,end=None):
        if start=='all':
            start='0.0'
            end='end'
        self.tag_remove('lock',start,end)

    def LockAll(self):
        self.lock('0.0','end')
    def UnlockAll(self):
        self.unlock('0.0','end')
            
            
        
class ColoredText(RichText):

    pattern_breaks=string.ascii_letters+string.digits+'_'
    spanning_characters=(
        (('"','"','"'),('"','"','"')),
        (("'","'","'"),("'","'","'")),
        ('(',')'),
        ('[',']'),
        ('{','}')
        )
    
    def __init__(self,root=None,name=None,patterns=None,spanning_characters=None,**kwargs):

##        self.outputFile=tf.TemporaryFile()
        
        #might make sense to do these as priority queues
        self.unmatched_span_starts=[]
        self.unmatched_span_ends=[]
        self.color_stack=[]
        
        
        if not 'font' in kwargs:
            kwargs['font']='Arial'

        if spanning_characters is None:
            spanning_characters=self.spanning_characters
            
        ins_dic={k[0]:self.insert_span_start for k in spanning_characters}
        for k in spanning_characters:
            if k[1] in ins_dic:
                ins_dic[k[1]]=(ins_dic[k[1]],self.insert_span_end)
            else:
                ins_dic[k[1]]=self.insert_span_end
        del_dic={k[0]:self.delete_span_start for k in spanning_characters}
        for k in spanning_characters:
            if k[1] in del_dic:
                del_dic[k[1]]=(del_dic[k[1]],self.delete_span_end)
            else:
                del_dic[k[1]]=self.delete_span_end
                
        if not 'track_inserts' in kwargs:
            kwargs['track_inserts']={}
        if not 'track_deletes' in kwargs:
            kwargs['track_deletes']={}
        kwargs['track_inserts'].update(ins_dic)
        kwargs['track_deletes'].update(del_dic)
        super().__init__(root,name=name,**kwargs)
        self.update_flag=tk.BooleanVar(value=True)
        if not patterns:
            self.PyConfig()
        else:
            self.patterns=patterns
        self.patterns=sorted(self.patterns,key=lambda p:p.priority)
        for P in self.patterns:
            exec('self.tag_configure("{}",{}="{}")'.format(P.tag,P.option,P.value))

    def insert_span_start(self,inst,char,index):
        pair=[k[1] for k in self.spanning_characters if k[0]==char][0]
        choices=[s for s in self.unmatched_span_ends if s[1]==pair and float(s[0])>float(index)]
        if choices:
            choices=sorted(choices,key=lambda s:s[0])
            match=choices[0]
            self.unmatched_span_ends.remove(match)
            if pair==char:
                self.unmatched_span_starts.remove(match)
            self.color_stack.append((index,match[0]))
        else:
            self.unmatched_span_starts.append((index,char))
            
    def insert_span_end(self,inst,char,index):
        pair=[k[0] for k in self.spanning_characters if k[1]==char][0]
        choices=[s for s in self.unmatched_span_starts if s[1]==pair and float(s[0])<float(index)]
        if choices:
            choices=sorted(choices,key=lambda s:s[0])
            match=choices[-1]
            self.unmatched_span_starts.remove(match)
            if pair==char:
                self.unmatched_span_starts.remove((index,char))
            self.color_stack.append((match[0],index))
        else:
            self.unmatched_span_ends.append((index,char))
            
    def delete_span_start(self,inst,char,index):
        if (char,index) in self.unmatched_span_starts:
            self.unmatched_span_starts.remove((char_index))
##        else:
##            pair=[k[1] for k in self.spanning_characters if k[0]==char][0]
##            text=self.get(index+'+1c','end')
##            count=0
##            i=1
##            for t in text:
##                if t==pair:
##                    count+=-1
##                    if count<0:
##                        self.unmatched_span_ends.append((self.index('{}+{}c'.format(index,i)),char))
##                        break
##                elif t==k:
##                    count+=1
##                i+=1
                
    def delete_span_end(self,inst,char,index):
        if (char,index) in self.unmatched_span_ends:
            self.unmatched_span_ends.remove((char_index))

    def color_from_stack(self,event=None):
        def color_proc(self=self):
            match_list=[]
            segments=self.color_stack
            while segments:
                start,end=segments.pop()
                test_start=float(start)
                test_end=float(end)
                remove=[]
                for i in range(len(segments)):
                    s,e=segments[i]
                    test_s=float(s)
                    test_e=float(e)
                    if test_s<test_start and test_end<test_e:
                        break
                    elif test_s<test_start:
                        segments[i]=(s,end)
                    elif test_end<test_e:
                        segments[i]=(start,e)
                    else:
                        remove.append(i)
                else:
                    match_list.append((start,end))
                    
                new_segs=[]
                for i in range(len(segments)):
                    if i not in remove:
                        new_segs.append(segments[i])
                segments=new_segs
            self.color_stack.clear()
            for s,e in match_list:
                self.ColorText(s+' linestart',e+' lineend')
        if not self.update_flag.get():
            self.wait_variable(self.update_flag)
        self.after_idle(color_proc)
                          
    def insert(self,*args,**kwargs):
        kwargs['call']=lambda ind,text,tag,s=self:s.ColorText('{} linestart'.format(ind),'{} lineend'.format(ind))
        ret=super().insert(*args,**kwargs)
        self.color_from_stack()
        return ret
        
    def delete(self,*args,**kwargs):
        kwargs['call']=lambda ind,last,s=self:s.ColorText('{} linestart'.format(ind),'{} lineend'.format(ind))
        ret=super().delete(*args,**kwargs)
        self.color_from_stack()
        return ret
    
    def AddPattern(self,P):
        self.patterns.append(P)
        self.patterns=sorted(self.patterns,key=lambda p:p.priority,reverse=True)
        for P in self.patterns:
            self.tag_configure(P.tag,*{P.option:P.value})
            self.tag_lower(P.tag)
        self.patterns.reverse()

    def PyConfig(self,colorMap=None):
        coloring={'command':'orange',
                  'punctuation':'black',
                  'function':'purple',
                  'string':'green4',
                  'numeric':'#005f9f',
                  'call':'purple3',
                  'bracketed':'maroon',
                  'ignore':'red3',
                  'def':'blue2'}
        if colorMap:
            coloring.update(colorMap)
    
        key='command'
        comPat=PyParse.CommandPattern(key,value=coloring[key])#Pattern(key,comnames,value=coloring[key])

        key='function'
        funPat=PyParse.FunctionPattern(key,value=coloring[key])#Pattern(key,fnames,value=coloring[key])

        key='punctuation'
        punPat=PyParse.PunctuationPattern(key,value=coloring[key])#Pattern(key,punc,value=coloring[key])

        key='numeric'
        numbPat=PyParse.NumericPattern(key,value=coloring[key])

        key='bracketed'
        bracPat=PyParse.BracketPattern(key,value=coloring[key])
        
        key='string'
        strPat=PyParse.StringPattern(key,value=coloring[key])
##        Pattern(key,(("'","'"),('"','"')),mode='span',spanMatch=True,spanLines=False,value=coloring[key],priority=3,avoid=('ignore',))
        txtPat=PyParse.TextPattern(key,value=coloring[key])
##        Pattern(key,(('"""','"""'),),mode='span',spanMatch=True,priority=3,value=coloring[key],avoid=('ignore',))
        
        key='call'
        callPat=PyParse.CallPattern(key,value=coloring[key])
        #Pattern(key,(('(',')'),('[',']'),('{','}')),mode='span',value=coloring[key],priority=0)
        
        key='ignore'
        ignorePat=PyParse.IgnorePattern(key,value=coloring[key])
        #Pattern(key,(('#',None),),mode='span',spanMatch=True,spanLines=False,value=coloring[key],avoid=('string',),priority=3)
        
        key='def'
        defPat=PyParse.DefPattern(key,value=coloring[key])
        #Pattern(key,(('def','(')),mode='span',spanLines=False,value=coloring[key],priority=2)
        
        self.patterns=[comPat,funPat,punPat,numbPat,bracPat,txtPat,strPat,callPat,ignorePat,defPat]

    def ColorText(self,*args,**kwargs):
        if self.update_flag.get():
            self.update_flag.set(False)
            self.after_idle(lambda:(self.color_function(*args,**kwargs),self.update_flag.set(True)))

    def color_function(self,first='1.0',last='end'):

##        output=self.outputFile
        
        def shiftind(ind,Num):
            return (ind+'+{}c'.format(Num))

        def tag_segment(pattern,pattern_start,length,remove_tags,i):
            pattern_end='{}+{}c'.format(pattern_start,length)
            tags_here=self.tag_names(pattern_start)
            tests=(p not in tags_here for p in pattern.avoid)
            if all(tests):
                for t in remove_tags[i:]:
                    self.tag_remove(t,pattern_start,pattern_end)
                self.tag_add(tag,pattern_start,pattern_end)
        
        letters=self.pattern_breaks
        start=first
        end=last
        count=tk.IntVar()
        tagset=[x.tag for x in self.patterns]
        for V in tagset:
            self.tag_remove(V,start,end)
        
        for i in range(len(self.patterns)):
            P=self.patterns[i]
            tag=P.tag

            if isinstance(P,Pattern):
                if P.mode=='match':
                    for pattern in P:
                        s1=len(pattern)
                        index=self.search(pattern,start,end,count=count)
                        if count.get()==0:
                            continue
                        while index:
                            textend=shiftind(index,s1)
                            if index=='1.0':
                                tests=(self.get(textend) not in letters,)
                            else:
                                tests=(self.get(textend) not in letters,
                                       self.get(index+'-1c') not in letters)
                            if all(tests):
                                ind=shiftind(index,s1)
                                Ns=self.tag_names(index)
                                tests=(p not in Ns for p in P.avoid)
                                if all(tests):
                                    for t in tagset[:i]:
                                        self.tag_remove(t,index,textend)
                                    self.tag_add(tag, index, textend)
                            index=self.search(pattern,textend+'+1c',end,count=count)
                            if count.get()==0:
                                break
                
                if P.mode=='span':
                    for pattern in P:
                        pat1,pat2=pattern
                        if not P.spanMatch:
                            s1=len(pat1)
                            s2=len(pat2)
                        else:
                            s1=0
                            s2=len(str(s2))
                        if pat2==None:
                            s2=0
                            pat2='\KKBB'
                        #tries to find the pattern
                        index=self.search(pat1,start,end)
                        while index:
                            #if the spanLines flag is off
                            if not P.spanLines:
                                #the line end is as normally defined
                                lineend='{}.end'.format(index.split('.')[0])
                            else:
                                #else it foes until the end of the text
                                lineend=self.index('end')
                            #tries to find the second pattern element starting
                            #one character after the first pattern index
                            p2=self.search(pat2,shiftind(index,1),lineend)
                            #if this is found
                            if p2:
                                #if the second element is found a tag index which is
                                #the length of the second pattern plus the second
                                #element index is used
                                sh=shiftind(p2,s2)
                                ind=shiftind(index,s1)
                                Ns=self.tag_names(index+' -1c')
                                tests=[p not in Ns for p in P.avoid]
                                if all(tests):
                                    for t in tagset[:i]:
                                        self.tag_remove(t,ind,sh)
                                    self.tag_add(tag,ind,sh)
                            else:
                                #if it isn't, the tag is applied to whatever is in
                                #the scope of the line end and the new search index
                                #is set one character before the newlien starts
                                Ns=self.tag_names(index+' -1c')
                                tests=[p not in Ns for p in P.avoid]
                                ind=shiftind(index,s1)
                                sh=lineend
                                if all(tests):
                                    for t in tagset[i:]:
                                        self.tag_remove(t,ind,sh)
                                    self.tag_add(tag,ind,sh)
                                p2='{}.0 -1c'.format(int(index.split('.')[0])+1)
##                            try:
                                #tries to find the first pattern element starting
                                #one place after the last second element index
                            index=self.search(pat1,shiftind(p2,1),end)
##                            except:
##                                    raise
            elif isinstance(P,REPattern):

                if P.pattern is None:
                    P.compile()
##                if P.recursive:
                text=self.get(start,end)
                matches=P.apply(text)
##                if P.flags!=():
##                    print(text,start,end)
                for m in matches:
                    m_start=self.index(shiftind(start,m.start()))
                    tag_segment(P,m_start,m.end()-m.start(),tagset,i)
##                else:
##                    index=self.search(P.pattern,start,end,regexp=True,count=count)
##                    if count.get()==0:
##                        continue
##                    while index:
##                        tag_segment(P,index,count.get(),tagset,i)
##                        index=self.search(P.pattern,pattern_end+'+1c',end,regexp=True,count=count)
##                        if count.get()==0:
##                            break
                
                
                
                

class REPattern(list):

    import re
    
    class REPattern_Match:
        def __init__(self,chunk,start,end):
            self.chunk=chunk
            self.start=lambda s=start:s
            self.end=lambda e=end:e
        def group(self,num=0):
            return self.chunk

    def __init__(self,tag,re_chunks,option='foreground',value='purple',
                 avoid=(),join=None,mode='or',recursive=False,apply_first=(),
                 flags=(),recursive_sub=' ',priority=1):
        super().__init__(re_chunks)
        self.tag=tag
        self.priority=priority
        self.avoid=avoid
        self.option=option
        self.value=value
        self.flags=flags
        
        self.pattern=None
        self.compiled=None
        self.recursive=recursive
        self.apply_first=apply_first
        if recursive_sub=='':
            recursive_sub=' '
        self.recursive_sub=str(recursive_sub)[0]
        if join is None:
            if mode=='or':
                join='|'
        self.joiner=join

    def compile(self,re_compile=False):
        self.pattern='({}({}))'.format(''.join(self.flags),
            self.joiner.join((s if isinstance(s,str) else '({})'.format('|'.join(s)) for s in self))
            )
        if re_compile:
            self.compiled=self.re.compile(self.pattern)
            
    def update(self,bits):
        self.extend(bits)
        self.compile()
        
    def apply(self,chunk,mode='match'):
        ret=None
        if self.recursive:
            if mode=='match':
                ret=self.find_recursive(chunk,apply_first=self.apply_first)
            elif mode=='remove':
                ret=self.remove_recursive(chunk,apply_first=self.apply_first)
        else:
            ret=list(self.finditer(chunk))
            if mode=='remove':
                segments=[]
                for f in ret:
                    start=f.start();end=f.end()
                    segments.append((start,end))
                    chunk=chunk[:start]+self.recursive_sub*(end-start)+chunk[end:]
                ret=(chunk,segments)
        return ret
    
    def match(self,string):
        if self.compiled is None:
            if self.pattern is None:
                self.compile()
            ret=self.re.match(self.pattern,string)
        else:
            ret=self.compiled.match(string)
        return ret
    
    def findall(self,string):
        if self.compiled is None:
            if self.pattern is None:
                self.compile()
            ret=self.re.findall(self.pattern,string)
        else:
            ret=self.compiled.findall(string)
        return ret
    
    def finditer(self,string):
        if self.compiled is None:
            if self.pattern is None:
                self.compile()
            ret=self.re.finditer(self.pattern,string)
        else:
            ret=self.compiled.finditer(string)
        return ret

    def remove_recursive(self,chunk,apply_first=()):
        
        if self.compiled is None:
            self.compile(re_compile=True)
        segments=[]

        for pattern in apply_first:
            chunk,junk=pattern.apply(chunk,mode='remove')
            
        found=list(self.compiled.finditer(chunk))
        
        while len(found)>0:
            for f in found:
                start=f.start();end=f.end()
                segments.append((start,end))
                chunk=chunk[:start]+self.recursive_sub*(end-start)+chunk[end:]
            found=list(self.compiled.finditer(chunk))

##        print(chunk)
        
        return (chunk,segments)
    
    def find_recursive(self,chunk,apply_first=()):
        
        base_chunk=chunk
        match_list=[]
        
        (chunk,segments)=self.remove_recursive(chunk,apply_first=apply_first)
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
                match_list.append((start,end))
                
            new_segs=[]
            for i in range(len(segments)):
                if i not in remove:
                    new_segs.append(segments[i])
            segments=new_segs
            
        return [self.REPattern_Match(base_chunk[s:e],s,e) for s,e in match_list]

class PyParse:
    
    import string,sys
    
    command_pattern=('(?<!\w)',('while','from','return','for','as','if','else','elif','and','or',
                      'in','is','try','except','raise','break','not',
                      'import','del','def','class','pass','yield','with','finally',
                  'continue','lambda','False','True','None'),'(?!\w)')
    try:
        bkeys=[key for key in __builtins__]
    except:
        bkeys=[key for key in vars(__builtins__)]
    function_pattern=('(?<!\w)',([key for key in sys.modules]+
            [key for key in sys.builtin_module_names]+bkeys),'(?!\w)')
    del bkeys

    punctuation_pattern=('['+string.punctuation+r'\[\](){}'+']',)
    
    string_pattern=(r"'.*?'((?!')|(?=''))",r'".*?"((?!")|(?=""))')
    
    text_pattern=(r'"""(.|\n)*?"""',r"'''(.|\n)*?'''")

    numeric_pattern=(r'((?<![\w_.])(math.pi|math.e)(?=[^\w_.]))',r'((?<![\w_])\d+(\.\d*)*)')

    symbol_pat=r'(\w+(([_.]\w+)?)*)'
    symbol_pattern=(symbol_pat,)
    
    assignment_pat='({0}\s*=\s*)'.format(symbol_pat)
    assignment_pattern=(assignment_pat,)
    
    bracket_pattern=tuple((r'(?<!\w)\{0}\s*([^\{0}\{1}]*\s*,\s*)*[^\{0}\{1}]*\s*\{1}'.format(*(c.split('|'))) for c in ('(|)','[|]','{|}')))

    obj_pattern='({})'.format('|'.join(string_pattern+numeric_pattern+symbol_pattern))

    call_base='('+symbol_pat+r'\(\s*[^()\[\]\{\}]*\s*\))'
    call_pattern=(call_base,)

    ignore_pattern=('#.*',)
    def_pattern=('((?<=def)|(?<=class))\s*{0}'.format(symbol_pat),)

    @classmethod
    def CommandPattern(cls,tag='command',option='foreground',value='orange'):
        return REPattern(tag,cls.command_pattern,option=option,value=value,join='')
    @classmethod
    def PunctuationPattern(cls,tag='punctuation',option='foreground',value='black'):
        return REPattern(tag,cls.punctuation_pattern,option=option,value=value)
    @classmethod
    def FunctionPattern(cls,tag='function',option='foreground',value='purple'):
        return REPattern(tag,cls.function_pattern,option=option,value=value,join='')
    @classmethod
    def StringPattern(cls,tag='string',option='foreground',value='green4'):
        return REPattern(tag,cls.string_pattern,option=option,value=value,priority=3,avoid=('ignore',))
    @classmethod
    def TextPattern(cls,tag='string',option='foreground',value='green4'):
        return REPattern(tag,cls.text_pattern,flags=('(?m)',),option=option,value=value,priority=3,avoid=('ignore',))
    @classmethod
    def NumericPattern(cls,tag='numeric',option='foreground',value='#005f9f'):
        return REPattern(tag,cls.numeric_pattern,option=option,value=value)
    @classmethod
    def BracketPattern(cls,tag='brackted',option='foreground',value='maroon'):
        return REPattern(tag,cls.bracket_pattern,flags=('(?m)',),option=option,value=value,priority=0,recursive=True)
    @classmethod
    def CallPattern(cls,tag='call',option='foreground',value='maroon'):
        return REPattern(tag,cls.call_pattern,option=option,value=value,priority=0,recursive=True,apply_first=(cls.BracketPattern(),))
    @classmethod
    def IgnorePattern(cls,tag='ignore',option='foreground',value='red3'):
        return REPattern(tag,cls.ignore_pattern,option=option,value=value,priority=3,avoid=('string',))
    @classmethod
    def DefPattern(cls,tag='def',option='foreground',value='blue2'):
        return REPattern(tag,cls.def_pattern,option=option,value=value,priority=2)
    
class Pattern(set):
    
    def __init__(self,tag,characters=[],mode='match',spanMatch=False,
                 spanLines=True,option='foreground',value='purple',avoid=(),
                 priority=1):

        self.tag=tag
        self.spanLines=spanLines
        self.option=option
        self.avoid=avoid
        self.value=value
        self.spanMatch=spanMatch
        super().__init__(characters)
        if mode in ('span','match','re'):
            self.mode=mode
        else:
            if len(characters)>1:
                self.mode='span'
            else:
                self.mode='match'
        self.priority=priority
        
class PixelDimensionText(tk.Frame):
    except_attrs={'bind'}
    def __init__(self,root=None,text_type=RichText,**kwargs):
        window_stuff={}
        for k in ('width','height'):
            if k in kwargs:
                window_stuff[k]=kwargs[k]
                del kwargs[k]
        super().__init__(root,**window_stuff)
        self._text=text_type(self,**kwargs)
        self.pack_propagate(False)
        self._text.pack(fill='both',expand=True)
        self.__getattribute__=self.__attrredirect__

    def __attrredirect__(self,attr):
        print(attr)
        S=super()
        if attr in S.__getattribute__('except_attrs'):
            t=S.__getattribute__('_text')
            return S.__text.__getattribute(attr)
        else:
            return S.__getattribute__(attr)
            
    def __getattr__(self,attr):
        return self._text.__getattribute__(attr)
##        exclusions=super().__getattribute__('_property_exclusions')
##        print(attr)
##        if not attr in exclusions:
##            text=super().__getattribute__('_text')
##            try:
##                return text.__getattribute__(attr)
##            except AttributeError:
##                return super().__getattribute__(attr)
##        else:
##            return super().__getattribute__(attr)
