from ._shared import *

class FormattingElement:
    
    def __init__(self,widgetTypeORwidget,root=None,grid_height=1,grid_width=1,**kwargs):
            
        t=type(self)
        W=widgetTypeORwidget
        if isinstance(W,type):
            init=self.typeInit
            widgetType=W
        else:
            init=self.baseInit
            widgetType=type(W)

        self._widgetType=widgetType
        self._pack=self.pack
        self._grid=self.grid
        self._place=self.place
        self._hash=self.__hash__
        self._eq=self.__eq__
        
        self.__class__=type(t)('Formatable'+widgetType.__name__,(t,widgetType),{})
        self.root=root
        
        self.grid_height=grid_height
        self.grid_width=grid_width
        
        r=init(W,**kwargs)
        if r:
            self.post_init()
            
    def post_init(self):
        self.wType=self._widgetType
        self.pack=self._pack
        self.grid=self._grid
        self.place=self._place
        self.__hash__=self._hash
        self.__eq__=self._eq
        self.packKwargs={'in_':self.root}
        self.gridKwargs={'in_':self.root}
        self.placeKwargs={'in_':self.root}

    def __call__(self,root):
        if not hasattr(self,'master'):
            self.setParent(root)
            self.post_init()
        return self

    def setParent(self,root):
        self.root=root
        self.typeInit(root,**self._kw)
        
    def typeInit(self,wType,**kw):
        if self.root is None:
            self._kw=kw
            self.w=None
            r=False
        else:
            self.w=self
            super().__init__(self.root,**kw)
            self.w=self
            r=True
        return r
        
    def baseInit(self,W,**kw):
        try:
            W.config(**kw)
        except:
            for k,v in kw.items():
                try:
                    W.config(**{k:v})
                except:
                    pass
        self.w=W
        return True
    def __getattr__(self,attr):
        return self.w.__getattribute__(attr)
        
    def packConfig(self,**kwargs):
        self.packKwargs.update(kwargs)
    def gridConfig(self,**kwargs):
        self.gridKwargs.update(kwargs)
        if 'rowspan' in kwargs:
            self.grid_height=kwargs['rowspan']
        if 'columnspan' in kwargs:
            self.grid_width=kwargs['columnspan']
    grid_configure=grid_config=g_c=gridConfig
    def placeConfig(self,**kwargs):
        self.placeKwargs.update(kwargs)
    def pack(self,*args,**kwargs):
        use={};use.update(self.packKwargs)
        use.update(kwargs)
        if self.w is self:
            super().pack(*args,**use)
        else:
            self.w.pack(*args,**use)
    def grid(self,*args,**kwargs):
        use={};use.update(self.gridKwargs)
        use.update(kwargs)
        r,c=self.master.commands.dimensions
        if 'rowspan' in use:
            v=use['rowspan']
            if v=='all':
                use['rowspan']=r
        if 'columnspan' in use:
            v=use['columnspan']
            if v=='all':
                use['columnspan']=c
        if self.w is self:
            super().grid(*args,**use)
        else:
            self.w.grid(*args,**use)
    def place(self,*args,**kwargs):
        use={};use.update(self.placeKwargs)
        use.update(kwargs)
        if self.w is self:
            super().place(*args,**use)
        else:
            self.w.place(*args,**use)

##    def destroy(self):
##        if hasattr(self.master,'commands'):
##            self.master.commands.remove(self)
##        if self.w is self:
##            super().destroy()
##        else:
##            self.w.destroy()

    def __hash__(self):
        if self.w is self:
            h=super().__hash__()
        else:
            h=self.w.__hash__()
        return h
    def __eq__(self,other):
        if self.w is self:
            r=super().__eq__(other)
        else:
            r=self.w==other
        return r
        
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class FormattingGrid(tk.Frame):
    '''A grid of widgets
    
Stores commands in an Array2D

Can be configured however one would normally, by making a frame and then using grid as the geometry manager.

Bindings propagate to child widgets, by default and one can specify moving through the widgets via arrow_move. Different appearances can be obtained by passing active and inactive config dictionaries.'''
    #Need to make it easier to use FormattingElement.grid_height
    #and FormattingElement.grid_width when greater than 1
    #
    FormatElement=FormattingElement
    Empty=Array2D.Empty
    ItemFlattener=Flattener(endtype=tuple,dontExpand=(str,tk.Widget))
    
    class EmptyFrame(FormattingElement):
        __bool__=lambda:False
        Empty=Array2D.Empty
        
        def __init__(self,root):
            super().__init__(tk.Label,root=root,text=' ')
        
##        def __eq__(self,other):
##            r=super().__eq__(other)
##            u=other is self.Empty
##            return r or u
    active_config={}
    inactive_config={}
    def __init__(self,root=None, rows=1, columns=0,name=None, arrow_move=False, selectable=None, active=None, inactive=None, **kwargs):
        '''Builds the grid from the specified dimensions and sets the active and inactive configs'''
        super().__init__(root,**kwargs)
        self.root=self.master
        if active is None:
            active=self.active_config
        if inactive is None:
            inactive=self.inactive_config
        self.active_config=active
        self.inactive_config=inactive

        if columns==0:
            self.addmode='col'
        elif rows==0:
            self.addmode='row'
        else:
            self.addmode='col'
        if not name:
            self.name=type(self).__name__
        else:
            self.name=name
        self.display_rectangle=(0,0,None,None)
        self.commands=GeneralTools.Array2D(dim=(max(rows,1),max(columns,1)),bracketchar='')
        self.tracker_bindings=[Binding(key,self.pan,add='+')
                             for key in ('<Up>','<Down>','<Left>','<Right>')]
        self.select_bindings=[Binding('<FocusIn>',self.track_focus,add='+'),
                                 Binding('<FocusOut>',lambda e, s=self: e.widget.config(s.inactive_config), add='+'),
                                 Binding('<Button-1>',lambda e:e.widget.focus_set(),add='+')]
        self.bindings=set()
        self._pannable=False;self._selectable=False
        self.set_panning(arrow_move)
        self.set_selectable(arrow_move if selectable is None else selectable)
              
        self.focus_point=(0,0)
        self._initial_empties=self.commands.empty_count
        self.lengths=self.commands.lengths
        m=0
        j=0
        for l in self.lengths:
            m=max(0,l)
            self.columnconfigure(j,weight=1)
            j+=1
        for i in range(m):
            self.rowconfigure(i,weight=1)

        self.config_map={}
        
    #------------------------------------------------------------------------- 
    def FormattingElement(self,widget,**kwargs):
        w=self.FormatElement(widget,self,**kwargs)
        return w
    
    #
    def set_panning(self,flag=True):
        '''Specifies whether to have panning or not'''
        if flag and not self._pannable:
            self.bindings.update(self.tracker_bindings)
        elif self._pannable:
            self.bindings.difference_update(self.tracker_bindings)
            for b in self.tracker_bindings:
                for w in self.commands:
                    b.remove(w)
    #
    def set_selectable(self,flag=True):
        '''Specifies whether to be selectable or not'''
        if flag and not self._selectable:
            self.bindings.update(self.select_bindings)
        elif self._selectable:
            self.bindings.difference_update(self.select_bindings)
            for b in self.select_bindings:
                for w in self.commands:
                    b.remove(w)
    #
    def apply_bindings(self,*items):
        '''Applies stored bindings to the items specified'''
        if len(items)==0:
            items=('all',)
        if 'all' in items:
            items=iter(self.commands)
        for item in items:
            for b in self.bindings:
                b.apply(item)
    #
    def pan(self,event):
        '''Tries to pan through the grid, based on the current focus_point of the widget
    
Sets the focus to the panned-to widget and depends on the applied FocusIn and FocusOut bindings to configure the widgets and set the focus_point'''
        k=event.keysym
        q=None
        if k=='Up':
            q=(-1,0)
        elif k=='Down':
            q=(1,0)
        elif k=='Left':
            q=(0,-1)
        elif k=='Right':
            q=(0,1)
        if not q is None:
            new_pos=tuple(map(lambda a,b:max(a+b,0),self.focus_point,q))
            try:
                E=self.get(*new_pos)
            except IndexError:
                pass
            else:
                if not E is self.Empty:
                    E.focus_set()
    #
    def focus_on(self,i=None,j=None):
        '''Sets focus to the command specified by i,j if any, or the focal point'''
        if i is None or j is None:
            i,j=self.focus_point
        try:
            E=self.get(i,j)
        except IndexError:
            pass
        else:
            if not E is self.Empty:
                E.focus_set()
    #
    def track_focus(self,event):
        '''Sets the focal point of the formatting grid to the widget specified by event.widget
        
Applies the active_config of the widget if that exists'''
        w=event.widget
        w.config(self.active_config)
        self.focus_point=w.pos
    #------------------------------------------------------------------------- 
    def prep_item(self,item):
        '''Preps an item into a FormattingElement so that it can be configured normally'''
        if not isinstance(item,FormattingElement):
            item=self.FormattingElement(item)
##        if not item.master==self:
##            raise ValueError('can only add child widgets')
        self.apply_bindings(item)
        item.gridConfig(**self.config_map)
        return item
    #-------------------------------------------------------------------------                         
    def Insert(self,*items,x=-1,y=-1): 
        '''Inserts a widget at the specified position'''           
        wrap=len(self.commands.lengths)
        curx=x;cury=y
        flat=self.ItemFlattener.flatten(items)
        for item in flat:
            item=self.prep_item(item)
            if self._initial_empties>0:
                i,j=self.commands.get_index(y,x)
                try:
                    E=self.commands[i,j]
                except IndexError:
                    self.commands.insert((i,j),item)
                else:
                    if E is self.Empty:
                        self.commands[i,j]=item
            else:
                self.commands.insert((x,y),item)
        self.Refresh()
    #-------------------------------------------------------------------------
    def InsertFormat(self,i,j,wid_type,**kwargs):
        '''Insert but taking the arguments of a FormattingElement after the index'''
        FE=self.FormattingElement(wid_type,**kwargs)
        self.Insert(FE,x=j,y=i)
        return FE
    #-------------------------------------------------------------------------
    def AddFormat(self,wid_type,add_mode='row',**kwargs):
        '''Takes the arguments of a FormattingElement and adds a new FormattingElement to the grid'''
        FE=self.FormattingElement(wid_type,**kwargs)
        self.Add(FE,mode=add_mode)
        return FE
    #-
    def SetView(self,mx=0,my=0,MX=None,MY=None,
                rel_x='',REL_X='',rel_y='',REL_Y=''):
        '''Forces the grid display into the specified range. Useful for adding scrollbars and such.'''
        r,c=self.commands.dimensions
        if rel_x!='':
            mx=int(c*rel_x)
        if rel_y!='':
            my=int(r*rel_y)
        if REL_X!='':
            MX=int(c*REL_X)
        if REL_Y!='':
            MY=int(r*REL_Y)
        self.display_rectangle=(mx,my,MX,MY)
        self.Refresh()
    #-------------------------------------------------------------------------
    def AddTo(self,i,item,mode='row'):
        '''Adds the item to the row or column specified'''        
        item=self.prep_item(item)
        if mode=='row':
            if self._initial_empties<=0:
                self.commands.row_append(i,item)
            else:
                r=self.commands.row(i,include_empties=True)
                try:
                    j=r.index(self.Empty)
                except ValueError:
                    self.commands.row_append(i,item)
                else:
                    self.commands[i,j]=item
        else:
            if self._initial_empties<=0:
                self.commands.insert((-1,i),item)
            else:
                c=self.commands.column(i,include_empties=True)
                try:
                    j=c.index(self.Empty)
                except ValueError:
                    self.commands.insert((-1,i),item)
                else:
                    self.commands[j,i]=item
        self.Refresh()
    #-------------------------------------------------------------------------
    def AddItems(self,*items,mode=None):
        '''Adds items to the grid, adding so that it preserves the desired dimensions'''
        if not mode:
            mode=self.addmode
        l1=tuple(self.commands.lengths)
        for item in self.ItemFlattener.flatten(items):
            item=self.prep_item(item)
            if self._initial_empties>0:
                try:
                    i,j=self.commands.index(self.commands.Empty)
                except ValueError:
                    self._initial_empties=0
                    self.commands.append(item,mode=mode,dontExpand=(type(item),))
                else:
                    self.commands[i,j]=item
                    self._initial_empties+=-1
            else:
                self.commands.append(item,mode=mode,dontExpand=(type(item),))
        self.Refresh()
    Add=AddItems
    #------------------------------------------------------------------------
    def DeleteItem(self,indexPair):
        '''Removes an item at the index tuple specified'''
        for x in self.commands.pop(indexPair):
            if not x is self.Empty:
                x.grid_forget()
        self.Refresh()
    #------------------------------------------------------------------------- 
    def Blank(self,indexPair,reduce=True,collapse=False):
        '''Blanks the item at the index pair specified.
        
Can also be specified to reduce the grid down to a more compact version, if possible'''
        i,j=indexPair
        v=self.commands[i,j]
        if not v is self.Empty:
            v.grid_forget()
        self.commands[i,j]=self.Empty
        updateFlag=False
        if collapse=='col' or collapse is True:
            updateFlag=True
            self.commands.collapse_column(j)
        if collapse=='row' or collapse is True:
            updateFlag=True
            self.commands.collapse_row(i)
        if reduce:
            updateFlag=True
            v2=self.commands.column(j)
            for x in v2:
                if not x is self.Empty:
                    break
            else:
                self.commands.pop(j,mode='col')
            v1=self.commands.row(i)
            for x in v1:
                if not x is self.Empty:
                    break
            else:
                self.commands.pop(i,mode='row')
        if updateFlag:
            self.Refresh()
            
    #------------------------------------------------------------------------- 
    def SwapRows(self,i,j):
        '''Swaps rows'''
        self.commands.swaprows(i,j)
    #--
    def RemoveRow(self,i):
        '''Deletes a row'''
        self.commands.pop(i)
        self.ClearChildren()
        self.Refresh()
    #------------------------------------------------------------------------- 
    def Clear(self,purge_empties=True):
        '''Resets the grid'''
        self.commands=LinAlg.Array2D(dim=self.commands.dim())
        self._initial_empties=self.commands.empty_count      
    #------------------------------------------------------------------------- 
    def get(self,*indexPair):
        '''Returns the widget at the index pair'''
        if indexPair[0]=='current':
            i,j=self.focus_point
        else:
            i,j=indexPair
        return self.commands[i,j]
    #------------------------------------------------------------------------- 
    def set(self,*indexPairNew):
        '''Sets a widget at the index pair'''
        i,j,new=indexPairNew
        new=self.prep_item(new)
        self.commands[i,j]=new
    #------------------------------------------------------------------------- 
    def bind(self,*args,to=None,to_all=True,to_children=False,**kwargs):
        '''Applies bindings to the widget or its children or both (the default) bindings are remembered so that they can be applied again upon adding new elements'''
        if to is None:
            if to_children:
                to='children'
            if to_all:
                to='all'
        
        fid=None
        if to in ('all','self'):
            fid=super().bind(*args,**kwargs)
        if to in ('all','children'):
            seq=args[0]
            B=Binding(*args,**kwargs)
            self.bindings.add(B)
            for x in self.commands.items():
                B.apply(x)
        return fid
    #-------------------------------------------------------------------------         
    def elementbind(self,i,j,*args,**kwargs):
        '''Applies a binding to element i,j'''
        self.get(i,j).bind(*args,**kwargs)
    #------------------------------------------------------------------------- 
    def command_configure(self,*indexPair,**kwargs):
        '''Config, but on element i,j'''
        i,j=indexPair
        E=self.commands[i,j]
        E.config(**kwargs)
    #------------------------------------------------------------------------- 
    def gridConfig(self,which='all',mode='row',**kwargs):
        '''Configures the grid manager of the formatting grid 

Can apply to rows or columns, a specific row, or a specific column'''
        if which=='all':
            which=self.commands.items()
            self.config_map.update(kwargs)
        elif isinstance(which,int):
            if mode.lower() in ('row','rows','r'):
                which=self.commands.row(which)
            else:
                which=self.commands.row(which)
        else:
            which=[self.get(*w) for w in which]
        for x in which:
            x.gridConfig(**kwargs)
        self.Refresh()
    grid_configure=grid_config=g_c=gridConfig
    #------------------------------------------------------------------------- 
    def configure_all(self,**kwargs):
        '''Applies config to all elements'''
        for x in self.commands.items():
            x.config(**kwargs)
    #------------------------------------------------------------------------- 
    def configure_rows(self,**kwargs):
        '''Applies grid_rowconfigure to all rows'''
        l=max(self.commands.lengths)
        mx,my,MX,MY=self.display_rectangle
        for i in range(l):
            if my is None or MY is None or i<(MY-my):
                self.grid_rowconfigure(i,**kwargs)
            else:
                self.grid_rowconfigure(i,weight=1,minsize=0)#make it disappear
    #------------------------------------------------------------------------- 
    def configure_cols(self,**kwargs):
        '''Applies grid_columnconfigure to all columns'''
        l=len(self.commands.lengths)
        mx,my,MX,MY=self.display_rectangle
        for i in range(l):
            if mx is None or MX is None or i<(MX-mx):
                self.grid_columnconfigure(i,**kwargs)
            else:
                self.grid_columnconfigure(i,weight=1,minsize=0)#make it disappear
    #-
    def ClearChildren(self):
        for n,c in self.children.items:
            c.grid_forget()
    #------------------------------------------------------------------------- 
    def Refresh(self):
        '''Regrids all widgets'''

        #Redraw everything
        for n,w in self.children.items():
            w.grid_forget()
        mx,my,MX,MY=self.display_rectangle
        #Which elements to draw
        filled_spots=[]
        i=my
        y=0
        R=self.commands.rowiter(include_empties=True)

        if not MY is None:
            h=MY-my
            R=[r for n,r in zip(range(h),list(R)[my:MY])]
        for r in R:
            #R is the set of rows
            x=0
            j=mx
            I=r
            L=len(r)
            if not MX is None:
                w=MX-mx
                I=(E for m,E in zip(range(w),r))
            for E in I:
                if E is self.Empty:
                    x+=1
                    continue
                E.grid_forget()
                old_x=x;old_y=y
                while (y,x) in filled_spots:
                    x+=1
                    if x>=L:
                        y+=1
                        x=0
                E.grid(row=y,column=x,in_=self)
                for n in range(E.grid_width):
                    for m in range(E.grid_height):
                        filled=(y+m,x+n)
                        filled_spots.append(filled)
                E.pos=(i,j)
                E.spot=(y,x)
                x=old_x;y=old_y
                x+=1
                j+=1
            i+=1
                        
    def pack(self,**kwargs):
        self.Refresh()
        super().pack(**kwargs)
    def grid(self,**kwargs):
        self.Refresh()
        super().grid(**kwargs)
    def place(self,**kwargs):
        self.Refresh()
        super().place(**kwargs)
        
###############################
class SwapGrid(FormattingGrid):
    
    class SwapHook(FormattingElement):
        def __init__(self,root,index,label='   ',base='gray90',relief='ridge',cursor='plus'):
            super().__init__(tk.Label,root=root,bg=base,text=label,
                             relief=relief,cursor=cursor)
            self.root=root
            self.base=base
            self.swapIndex=index
            self.swapState=tk.BooleanVar(value=False)
            self.swapState.trace('w',lambda*e:(self.config(bg='light yellow') if self.swapState.get() else self.config(bg=self.base)))
            self.bind('<Button-1>',lambda*e:self.activate() if (not self.swapState.get()) else self.deactivate())
        def activate(self):
            self.swapState.set(True)
            s=self.root.swapTrace.get()
            self.root.swapTrace.set(s+';{}'.format(self.swapIndex))
        def deactivate(self):
            self.swapState.set(False)
            s=self.root.swapTrace.get()
            indString=';{}'.format(self.swapIndex)
            le=len(indString)
            if s[-le:]==indString:
                s=s[:-le]
            else:
                s.replace(indString+';','')
            self.root.swapTrace.set(s)
        def get(self):
            return self['text']
        def set(self,text):
            self['text']=text
            
    def __init__(self,root=None,rows=0,columns=1,name=None,callback=None,**kwargs):
        columns=columns+1
        if not callback:
            callback=lambda i,j:None
        self.callback=callback
        super().__init__(root=root,rows=rows,columns=columns,name=name,**kwargs)
        self.swapTrace=tk.StringVar(self,value='')
        self.swapTrace.trace('w',lambda*e:self.Swap() if len(self.swapTrace.get().split(';'))>2 else None)
        for i in range(max(self.commands.lengths)):
            self.set(i,0,self.SwapHook(self,i))
        self.Refresh()
    def Swap(self):
        string=self.swapTrace.get()
        self.swapTrace.set('')
        sp=string.split(';')
        sp.remove('')
        i,j=sp[:2]
        i=int(i);j=int(j)
        for x in sp:
            self.get(int(x),0).swapState.set(False)
        self.get(i,0).swapIndex=j
        self.get(j,0).swapIndex=i
        self.SwapRows(i,j)
        self.callback(i,j)
        self.Refresh()
    
    
#$$$$$$$$$$$$$$$$$$$$$$$
class EntryGrid(FormattingGrid):

    def __init__(self,root=None,rows=3,columns=3,swappable=False,**kwargs):
        sp=0
        if swappable:
            t=type(self)
            self.__class__=type(t)(t.__name__,(t,SwapGrid),{})
            sp=1
        self.swapFlag=swappable
        super().__init__(root,rows=rows,columns=columns,**kwargs)
        self._intial_empties=0
        for i in range(rows):
            for j in range(sp,columns+sp):
                com=FormattingElement(tk.Entry,self)
                self.commands[i,j]=com
                com.grid(row=i,column=j)
                
    def __setitem__(self,indexPair,val):
        i,j=indexPair
        def setProc(i,j):
            com=self.commands[i,j]
            s=com.cget('state')
            rdF=False
            if s=='disabled':
                com.config(state='normal')
            elif s=='readonly':
                rdF=True
            com.delete(0,'end')
            com.insert(0,str(val))
            if rdF:
                com.config(state='readonly')
        if self.swapFlag:
            if j==0:
                self.commands[i,j].config(text=str(val))
            else:
                setProc(i,j)
        else:
            setProc(i,j)
            
    def __getitem__(self,indexPair):
        e=self.commands[indexPair]
        if isinstance(e,Array2D.EmptyType):
            ret=''
        else:
            ret=e.get()
            
        return ret

    def RowIterator(self):
        n,m=self.commands.dimensions
        return iter(([self[i,j] for j in range(m)] for i in range(n)))

    def ColumnIterator(self):
        n,m=self.commands.dimensions
        return iter(([self[i,j] for j in range(n)] for i in range(m)))
    
    def AddRow(self):
        self.Add(*[FormattingElement(tk.Entry,self) for i in range(self.commands.dimensions[1])],mode='row')
        
    entryconfig=FormattingGrid.command_configure