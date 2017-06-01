from ..Shared import *

class Walker:
    '''An implicit instance of whatever widget it's derived from, which will be some form of GridPrimitive

It's intended to move along a walker canvas'''
    def __init__(self,parent,widget=GridCircle,classname='Circle',
                 initialcell=None,facing=0,speed=1,**kwargs):
        t=type(self)
        self.__class__=type(t)(classname+t.__name__,(t,widget),{})
        super().__init__(parent=parent,cell=initialcell,**kwargs)
        self.setfacing(facing)
        self.speed=speed
        self.base_position=(0,0)
        self.followers=set()

    def delete(self):
        '''Removes the walker from its current cell'''
        self.ahead(0).remove(self,triggers=())
    
    def _move(self,old,new,triggers=True,override=False,ignore_walls=False,
        return_position=None,return_cell=None):
        '''Uses the canvas's MoveOb method to move the instance between two cells positions, to and here'''
        if return_position is None:
            return_position=tuple(self.position)
        if return_cell is None:
            return_cell=tuple(old)
        def reset_position(p=return_position,c=return_cell,self=self):
            self.position[:]=p
            self.cell[:]=c
            try:
                self.parent.AddObject(self)
            except self.parent.FullException:
                pass
            return (0,0)
        
        if old!=new:
            res=self.parent.MoveOb(self,old,new, triggers=triggers,override=override,ignore_fail=ignore_walls)
            if res is False:
                reset_position()
            else:
                if 'exit_window' in res:
                    reset_position()
                for t in res:
                    c=self.parent.cellget(new)
                    c.call(t,self)
                    
    def move(self,amt=None,triggers=True,override=False,ignore_walls=False):
        '''Calls Shift to set the position and cell. Calls _move after.'''
        
        p=tuple(self.position)
#         c=tuple(self.cell)
        
        if amt is None:
            amt=self.speed
        x=math.cos(self.facing)*amt
        y=-math.sin(self.facing)*amt
        old,new=self.Shift(x,y)
        self._move(old,new,return_position=p, triggers=triggers,override=override,ignore_walls=ignore_walls)
        
        return (x,y)
                
    def move_to(self,cellORcharORtuple,triggers=True,override=False,ignore_walls=False):
        '''Simply moves the instance to a new cell. Calls _move after.'''
        old=tuple(self.cell)
        cct=cellORcharORtuple
        new=(cct.cell if isinstance(cct,Walker) else 
            cct.pos if isinstance(cct,type(self.ahead(0))) else 
            cct)
        diff=tuple((a-b for a,b in zip(new,old)))
        
        self.cell[:]=new
        self._move(old,new,triggers=triggers,override=override,ignore_walls=ignore_walls)
                    
        return diff
        
    def move_behind(self,char,behind=1,triggers=True,override=False,ignore_walls=False):
        cell=char.ahead(-behind)
        old=tuple(self.cell)
        new=tuple(cell.pos)
        diff=tuple((a-b for a,b in zip(new,old)))
        self.cell[:]=new
        self._move(old,new,triggers=triggers,override=override,ignore_walls=ignore_walls)
        return diff
        
    def ahead(self,n=1):
        f=float(self.facing)
        x=math.cos(f)*n
        y=-math.sin(f)*n
        i,j=self.cell
        return self.parent.cellget((int(y)+i,int(x)+j))

    def objects_ahead(self,n=0):
        c=self.ahead(n)
        return c.obs
    
    def in_sight(self,n):
        f=float(self.facing)
        c=math.cos(f)
        s=-math.sin(f)
        i,j=self.cell
        ret=[]
        for k in range(n):
            x=c*k
            y=s*k
            test=self.parent.cellget((int(y+i),int(x+j)))
            if not test in ret:
                ret.append(test)
        return ret
    
    def center_view(self):
        i,j=self.cell
        P=self.parent
        x=P.base_x
        y=P.base_y
        cx=P.cols//2
        cy=P.rows//2
        move=[0,0]
        move[1]=i-y-cy
        move[0]=j-x-cx
        P.MoveView(*move)
        self.position[:]=self.base_position
        
    def turn(self,theta,mode='degrees'):
        if mode=='degrees':
            theta=math.radians(theta)
        self.facing=(self.facing+theta)%(2*math.pi)
        yield 'done'

    def setfacing(self,theta,mode='degrees'):
        if mode=='degrees':
            theta=math.radians(theta)
        self.facing=theta%(2*math.pi)
        yield 'done'
