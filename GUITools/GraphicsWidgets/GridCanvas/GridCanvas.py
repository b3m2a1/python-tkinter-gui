from ..Shared import *
from ..RichCanvas import RichCanvas as RichCanvas


import random


#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class GridCanvas(RichCanvas):
    """The widget works by making constructing an indexing system on the available
window space, dividing it into a grid.
Then each cell gets an index and draws objects in the alloted window space by the
grid.
Future improvements:

    Also make it so that partial grid elements can be drawn. That is, half of a
    cell can be on the screen at the edge. Apply the same sort of partition in
    this case, but substract the fraction that will not be on the screen
    (at the left and top) and just draw the cells normally from there.
    Tkinter will do the chopping appropriately.    
    
"""
    gridsep='|'
    gridbracket=''    

    selectionBorder=GridRectangle(width=1,height=1,size=0,outline='blue')

    from GUITools.GraphicsWidgets.GridCanvas import Event,EventQueue,Cell

    FullException=Cell.FullException
    Full=Cell.Full
    InactiveException=EventQueue.InactiveException
    NotProcessing=EventQueue.NotProcessing
    
    def __init__(self,root,visible_rows,visible_cols,bounded=False,basefill=None,name=None,**kwargs):
        from random import choice
        from string import ascii_letters
        self.bind_key=''.join((choice(ascii_letters) for i in range(9)))
        
        initKwargs={'bd':0}
        initKwargs.update(kwargs)
        super().__init__(root,**initKwargs)
        self.cellconfig={'space':basefill}
        self.rows=visible_rows
        self.cols=visible_cols
        self.base_x=0
        self.base_y=0
        self.bounds=(self.base_y,self.base_x,self.rows-1,self.cols-1)
        self.borders=True
        self.basearray=LinAlg.FullArray(dim=(visible_rows,visible_cols),
                                        bracketchar=self.gridbracket,joinchar=self.gridsep)
        self.backgroundFlag=True
        self.bounded=bounded
        rflag=False

        self.currently_visible=self.bounds
        #use this to just move those cells which just need to be moved when
        #redrawing, allowing for decreased computation time.
        #basic idea is to figure out the overall shift for a given cell (need
        # only be calculated once) and then shift the *backgrounds* of those
        #cells which will remain visible
        self.event_queue=self.EventQueue(self)
    
        for i in range(visible_rows):
            for j in range(visible_cols):
                self.basearray[i,j]=self.NewCell(i,j)
                    
        self.bind('<Button-1>',lambda e:self.focus_set())
        self.bind('<Command-i>',lambda e:self.Interactor(self))
        self.bind('<Configure>',lambda e:self.ClearDraw())
        
        def config(cell):
            try:
                v=cell.cget('fill')
            except:
                v='white'
            if v=='blue':
                cell.space=1
                cell.config(fill='white')
            else:
                cell.space=0
                cell.config(fill='blue')
            
##        self.bind('<Double-Button-1>',lambda e:(config(self.ClickGet(e)),self.Draw()))
    def step(self,lock=False,raise_exc=(),queue_lock=False):
        self.event_queue.empty_queue(lock=queue_lock)
        if lock:
            self._queue_lock=tk.BooleanVar(self,value=False)
            def hold_query(self=self):
                if not self.event_queue.processing:
                    self._queue_lock.set(True)
                else:
                    self.event_queue.empty_queue()
#                     print(self.event_queue.processing)
                    self.after(10,hold_query)                    
            self.after(10,hold_query)
            if not self._queue_lock.get():
                self.wait_variable(self._queue_lock)
        for E,m in self.event_queue.processing_errors:
            if isinstance(E,raise_exc):
                raise E
            else:
                print(m)
        
    def cancel_queue(self,event=None):
        self.event_queue.cancel_flag=True
        
    def MoveView(self,x=0,y=0):
        curx=self.base_x
        cury=self.base_y
        self.base_x+=x
        self.base_y+=y
        if self.base_x<0:
            self.base_x=0
        if self.base_y<0:
            self.base_y=0
        my,mx,My,Mx=self.CalculateBounds()
        if not self.bounded:
            self.CalculateArray()
        else:
            r,c=self.basearray.dim()
            self.base_y=int(self.base_y + min(r-My-1,0))
            self.base_x=int(self.base_x + min(c-Mx-1,0))
            self.CalculateBounds()
##        if self.base_x!=curx or self.base_y!=cury:
##            self.backgroundFlag=True
        
    def SetSize(self,y=0,x=0):
        curx=self.cols
        cury=self.rows
        if x>0:
            self.cols=x
        if y>0:
            self.rows=y
        if self.cols!=curx or cury!=self.rows:
            self.CalculateBounds()
            if not self.bounded:
                self.CalculateArray()
            else:
                r,c=self.basearray.dimensions
##                if self.cols>c:
##                    self.cols=c
##                if self.rows>r:
##                    self.rows=r
##                if self.base_x<0:
##                    self.base_x=0
##                if self.base_y<0:
##                    self.base_y=0
##                self.CalculateBounds()
                xMove=self.cols+self.base_x-c
                yMove=self.rows+self.base_y-r
                self.MoveView(xMove,yMove)
                self.CalculateBounds()
            self.backgroundFlag=True
        
    def CalculateBounds(self):
        y=int(self.base_y)
        x=int(self.base_x)
        t=(y,x,y+self.rows-1,x+self.cols-1)
        self.bounds=t
##        self.currently_visible=self.bounds
        return t

    def NewCell(self,i,j):
        return self.Cell(self,i,j,**self.cellconfig)

    def ExtendArray(self,*indices,mode='row',relative=False):
        
        r,c=self.basearray.dimensions
        if mode=='row':
            ob=(1,)*c
            base=self.base_y
        else:
            ob=(1,)*r
            base=self.base_x        
            
        for k in indices:
            if relative:
                k+=base
            self.basearray.insert(k,ob,mode=mode)            

        if mode=='row':
            for i in indices:
                if relative:
                    i+=base
                for j in range(c):
                    i,j=self.basearray.get_index(i,j)
                    self.basearray[i,j]=self.NewCell(i,j)
        elif mode=='col':
            for j in indices:
                if relative:
                    j+=base
                for i in range(r):
                    i,j=self.basearray.get_index(i,j)
                    self.basearray[i,j]=self.NewCell(i,j)
        self.ReassignIndices()
    def ShortenArray(self,*indices,mode='row',relative=False):
        if mode=='row':
            base=self.base_y
        else:
            base=self.base_x
        if not relative:
            base=0
        for i in indices:
            self.basearray.pop(i+base,mode=mode)
        self.ReassignIndices()

    def ReassignIndices(self,row=0,column=0):
        #Make it so that the assignment can from just one row or column on
        r,c=self.basearray.dimensions
        for i in range(row,r):
            for j in range(column,c):
                cell=self.basearray[i,j]
                cell.pos=[i,j]
                for o in cell.obs:
                    o.cell=[i,j]

##    def Refresh(self):
##        self.backgroungFlag=True
##        self.re
    def CalculateArray(self):
        my,mx,My,Mx=self.bounds
        r,c=self.basearray.dim()
        for i in range(r,My+1):
            self.basearray.append([1]*c,mode='row')
            for x in range(c):
                self.basearray[i,x]=self.NewCell(i,x)            
        
        for j in range(c,Mx+1):
            self.basearray.append([1]*(My+1),mode='col')
            for x in range(My+1):
                self.basearray[x,j]=self.NewCell(x,j)
        
    def Increments_Start(self):
        w,h=self.WindowDimensions()
        
        dx=int(w/self.cols)#2/self.cols
        dy=int(h/self.rows)#2/self.rows
        self.config(scrollregion=(0,0,w,h))
        excessx=w-dx*self.cols-2
        excessy=h-dy*self.rows-2
        x=max(0,excessx//3)
        y=max(0,excessy//3)
        
        return (dx,dy,x,y)
    
    def BBox(self,i,j,incs=None):
        if incs is None:
            incs=self.Increments_Start()
        dx,dy,x,y=incs
        m=j-self.base_x
        n=i-self.base_y
        x=m*dx+x
        y=n*dy+y
        return (x,y,x+dx,y+dy)

    def MouseCell(self,event):
        x,y=(event.x,event.y)
        dx,dy,ex,ey=self.Increments_Start()
        i=int((x-ex)/dx)+self.base_x
        j=int((y-ey)/dy)+self.base_y
        return (j,i)
    def ClickGet(self,event):
        j,i=self.MouseCell(event)
        return self.basearray.element(j,i)
    
    def cellget(self,cellID):
        
        if isinstance(cellID,self.Cell):
            c=cellID
        else:
            i,j=cellID
            c=self[i,j]
        return c
    
    def CellConfigure(self,cellID,**kwargs):
        C=self.cellget(cellID)
        C.config(**kwargs)
        C.Background()
##        self.backgroundFlag=True

    def CellSet(self,cellID,**kwargs):
        c=self.cellget(cellID)        
        for x,y in kwargs.items():
            setattr(c,x,y)
        c.Background()
##        self.backgroundFlag=True

    def CellBind(self,cellID,callback,frequency=1,trigger='enter'):
        c=self.cellget(cellID)
        c.bind(callback,frequency=1,trigger='enter')
            
    def MoveOb(self,ob,cellID1,cellID2,triggers=True,override=False,ignore_fail=False):
        ret=False
        try:
            cell1=self.cellget(cellID1);cell2=self.cellget(cellID2)
        except IndexError:
            ret=('exit_window',)
##            pass
        else:
            kw={}
            a,b=cell1.pos
            c,d=cell2.pos            
            if abs(a-c)>abs(b-d):
                if a>c:
                    op='up'
                else:
                    op='down'
            else:
                if b>d:
                    op='left'
                else:
                    op='right'
                    
            if not triggers:
                appTrigs=rmvTrigs=()
            else:
                appTrigs=(op+'_enter','enter')
                rmvTrigs=(op+'_exit','exit')

            try:
                cell1.remove(ob,triggers=())
            except ValueError:
                ret=rmvTrigs
            else:
##                if not cell1.space is None:
##                    cell1.space+=ob.size                       
                try:
                    cell2.append(ob,override=override,triggers=appTrigs)
                except self.FullException:
                    ret=False
                    
                    if ignore_fail:
                        trigs=(op+'_enter',)
                    else:
                        trigs=(op+'_enter','fail')
                        
                    if triggers:
                        for t in trigs:
                            cell2.call(t,ob)
##                            if 'moved' in vals:
##                                ret=()
                                
                else:
                    ret=rmvTrigs
##                    if not cell2.space is None:
##                        cell2.space+=-ob.size
                

        return ret

    def ClearDraw(self,tags=None):
        self.backgroundFlag=True
        self.Draw(tags=tags)
        
    def DrawNow(self,tags=None):
        self.Draw(tags=tags)
        self.update_idletasks()
#         self.hold_update(5,minimum=0)
        
    def Draw(self,tags=None):
    
        if tags is None:
            tags=self.bind_key
        incs=self.Increments_Start()
        rows,cols=self.basearray.dim()
        my,mx,My,Mx=self.bounds
        Y=My+1
        X=Mx+1
        
        if self.backgroundFlag:
            self.delete('background')
            for i in range(my,Y):
                for j in range(mx,X):
                    try:
                        c=self[i,j]
                    except IndexError:
                        break
                    c.Background(border=self.borders,incs=incs)
            self.background=True

        else:
            oy,ox,OY,OX=old_bounds=self.currently_visible
            col_shift,row_shift=cell_shift=(ox-mx,oy-my)
            row_move=row_shift*incs[1];col_move=col_shift*incs[0]
            cell_move=(col_move,row_move)
            
            # POSITIVE IS MOVING LEFT
            # NEGATIVE IS MOVING RIGHT
            col_sign=col_shift/abs(col_shift) if col_shift != 0 else 0
            col_base=OX if col_sign > 0 else ox
#             print(oy,ox,OY,OX)
            for i in range(abs(col_shift)):
                if col_sign > 0:
                    #RIGHTMOST
                    cell_it=(((j,col_base-i),self[j,col_base-i]) for j in range(oy,OY+1))
                else:
                    #LEFTMOST
                    cell_it=(((j,col_base+i),self[j,col_base+i]) for j in range(oy,OY+1))
                    
                for p,c in cell_it:
                    self.delete(c.drawn[0])
                    c.drawn[0]=None
                    
            
            # POSITIVE IS MOVING UP
            # NEGATIVE IS MOVING DOWN
            row_sign=row_shift/abs(row_shift) if row_shift != 0 else 0
            row_base=OY if row_sign > 0 else oy
            for i in range(abs(row_shift)):
                
                if row_sign > 0:
                    #DELETE THE BOTTOMMOST ROWS
                    cell_it=(((row_base-i,j),self[row_base-i,j]) for j in range(ox,OX+1))
                else:
                    #DELETE THE TOPMOST ROWS
                    cell_it=(((row_base+i,j),self[row_base+i,j]) for j in range(ox,OX+1))
                    
                for p,c in cell_it:
                    self.delete(c.drawn[0])
                    c.drawn[0]=None
                
        self.delete('objects')
##        to_clear=[]
        for i in range(my,Y):
            for j in range(mx,X):
                #Need to make it so that old backgrounds move, if still in frame
                #"if still in frame" means that the index is in the old bounds
                try:
                    c=self[i,j]
                except IndexError:
                    break
                
                if not self.backgroundFlag:
                    if (oy<=i<=OY and ox<=j<=OX):
                        I=c.drawn[0]
                        if not I is None:
                            self.move(I,cell_move[0],cell_move[1])
                            self.tag_raise(I)
                            
                    else:
##                        if not c.drawn[0] is None:
##                            self.delete(c.drawn[0])
                        c.Background(border=self.borders,incs=incs)
                        
                c.Draw(incs=incs,tags=tags)
                    
        self.currently_visible=self.bounds
        self.backgroundFlag=False

        #place in requisite tagging
    def AddObject(self,ob,triggers=(),where=None,override=False):
        if isinstance(ob,GridGraphic):
            if where is None:
                where=ob.cell
            else:
                ob.cell=list(where)
            ob.parent=self
            C=self.cellget(where)
            C.append(ob,triggers=triggers,override=override)
        else:
            raise TypeError('Can only add GridGraphic-type objects')

    def __iter__(self):
        return self.basearray.items()
    
    def __getitem__(self,tup):
        #can customize for something like center-based or
        #lhc based, etc.
        i,j=tup
        if i<0 or j<0:
            raise IndexError('Negative indexing not allowed')
        return self.basearray.__getitem__(tup)
