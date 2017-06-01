#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$           
class ActionBuffer:
    #Set an undoPointer and a redoFlag
    #When things are appended, just change one spot above the undoPointer and
    #set the redoFlag
    #
    #When things are undone, deincrement the undoPointer and make redoPointer 
    #true. 
    def __init__(self,*initialactions,maxlen=5,
                 defaultUndo=lambda a:None,defaultRedo=lambda a:None):
        l=len(initialactions)
        initialactions=(initialactions+(None,)*(maxlen-l))[:maxlen]
        self.list=list(initialactions)
        self.defaultUndo=defaultUndo
        self.defaultRedo=defaultRedo
        self.maxlen=maxlen
        self.start=0
        self.count=l
        self.undoPointer=l-1

    def __getitem__(self,index):
        return self.list[index]
    def __setitem__(self,index,item):
        self.list[index]=item
    def index(self,integer):
        return (self.start+integer)%self.maxlen
    def last(self):
        return self[self.index(self.undoPointer)]
    def from_end(self,number):
        x=self.undoPointer-number
        if x>=0:
            return self[self.index(x)]
        else:
            raise IndexError("can't get {} from end with only {} actions".format(number,self.undoPointer))
    def undo(self):
        if self.undoPointer>=0:
            O=self.last()
            try:
                u=getattr(O,'undo')
            except AttributeError:
                self.defaultUndo(O)
            else:
                u()
            self.undoPointer+=-1
    def redo(self):
        if self.undoPointer<self.count-1:
            O=self[self.index(self.undoPointer+1)]
            try:
                r=getattr(O,'redo')
            except AttributeError:
                self.defaultRedo(O)
            else:
                r()
            self.undoPointer+=1
            if self.undoPointer==self.maxlen:
                self.redoFlag=False
                
    def append(self,item,undo=None,redo=None):
        # If the list is full, the 'start' element should be replaced
        # Else, the element should be added at the adjusted index right above
        # the undoPointer, which should be incremented
        # Redos should then be disabled
        if undo and redo:
            item=self.Action(item,undo,redo)
        if self.undoPointer+1==self.maxlen:
            self[self.start]=item
            self.start=(self.start+1)%self.maxlen
        else:
            self.undoPointer+=1
            self.count=self.undoPointer+1
            self[self.undoPointer]=item
        
    def resize(self,newsize):
        if newsize>self.maxlen:            
            self.list=self[self.start:self.maxlen]+self[:self.start]+[None]*self.maxlen-newsize
        else:
            if newsize<self.maxlen-self.start:                
                self.list=self[self.start:newsize+self.start]
            else:
                self.list=self[self.start:self.maxlen]+self[:maxlen-newsize]
        self.start=0
        self.maxlen=self.newsize
    
    class Action:
        def __init__(self,ob=None,undo=lambda a:None,redo=lambda b:None):
            self.ob=ob
            self.undo=lambda:undo(ob)
            self.redo=lambda:redo(ob)
