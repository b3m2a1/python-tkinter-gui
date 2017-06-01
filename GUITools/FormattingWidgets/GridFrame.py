from ._shared import *
    
class GridFrame(tk.Frame):
    '''Intended to be a grid upon which one can place frames

It will use a FormattingElement-like construction as done in FormattingGrid to make CellFrames which will maintain their place formatting and positioning

By default it will have non-zero width and height'''
    def __init__(self,root,rows=5,columns=5,row_weights=1,column_weights=1,**kw):
        kwargs={'height':250,'width':250};kwargs.update(kw)
        super().__init__(**kwargs)
        
        self.__rows=rows
        self.__columns=columns
        self.__row_weights=[1]*rows if isinstance(row_weights,(int,float,str)) else list(row_weights)*rows[:rows]
        self.__column_weights=[1]*rows if isinstance(row_weights,(int,float,str)) else list(row_weights)*rows[:rows]
        
        self.__refresh_lock=False
        self.pack_propagate(False)
        self.grid_propagate(False)
    
    #-------------------- THE GRID CHUNK ------------#  
    @property
    def rows(self):
        return self.__rows
    @rows.setter
    def rows(self,val):
        if isinstance(val,int):
            r=self.__rows
            self.__rows=val
            if r>val:
                self.__row_weights=self.__row_weights[:val]
            elif val>r:
                self.__row_weights.extend([1]*(val-r))
            self.refresh()
    @property
    def dimensions(self):
        return (self.rows,self.columns)
    @dimensions.setter
    def dimensions(self,ij):
        i,j=ij
        self.rows=i
        self.columns=j
    @property
    def row_weights(self):
        return tuple(self.__row_weights)
    @row_weights.setter
    def row_weights(self,val):
        if isinstance(val,(int,float,str)):
            val=[1]*rows
        for i,v in enumerate(vals):
            if not v is None:
                self.__row_weights[i]=v
        self.refresh()
    @property
    def columns(self):
        return self.__rows
    @rows.setter
    def columns(self,val):
        if isinstance(val,int):
            c=self.__columns
            self.__columns=val
            if c>val:
                self.__column_weights=self.__column_weights[:val]
            elif val>c:
                self.__column_weights.extend([1]*(val-c))
            self.refresh()
    @property
    def column_weights(self):
        return tuple(self.__column_weights)
    @column_weights.setter
    def column_weights(self,val):
        if isinstance(val,(int,float,str)):
            val=[1]*columns
        for i,v in enumerate(vals):
            if not v is None:
                self.__column_weights[i]=v
        self.refresh()
    def column_weight(self,i):
        return self.__column_weights[i]
    def set_column_weight(self,i,v):
        if isinstance(v,int):
            self.__column_weights[i]=v
            self.refresh()
    def row_weight(self,i):
        return self.__row_weights[i]
    def set_row_weight(self,i,v):
        if isinstance(v,int):
            self.__row_weights[i]=v
            self.refresh()
            
     #-------------------- FORMATTING CHUNK ------------#
     
    def add(self,widget,i=0,j=0,rowspan=1,columnspan=1,**kw):
        if type(widget) is type:
            widget=widget(self,**kw)
            kw={}
        widget.grid_position=[i,j]
        widget.grid_spans=[rowspan,columnspan]
        widget.grid_place_formatting=kw
        widget.grid_hidden=False
        self.refresh()
        return widget
    def hide(self,widgets):
        if widgets=='all':
            widgets=self.children.values()
        elif isinstance(widgets,tk.Widget):
            widgets=(widgets,)
        for widget in widgets:
            widget.grid_hidden=True
        self.refresh()
    def unhide(self,widgets):
        if widgets=='all':
            widgets=self.children.values()
        elif isinstance(widgets,tk.Widget):
            widgets=(widgets,)
        for widget in widgets:
            widget.grid_hidden=False
        self.refresh()
    def span(self,widget,rowspan=None,columnspan=None):
        if not rowspan is None:
            widget.grid_spans[0]=rowspan
        if not columnspan is None:
            widget.grid_spans[1]=columnspan
        self.refresh()
    def shift(self,widgets,i=0,j=0):
        if isinstance(widgets,(int,float)):
            j=i
            i=widgets
            widgets=='all'
        elif isinstance(widgets,tk.Widget):
            widgets=(widgets,)
        if widgets=='all':
            widgets=self.children.values()
        for widget in widgets:
            widget.grid_position[0]+=i
            widget.grid_position[1]+=j
        self.refresh()
    
    def refresh(self,event=None):
        if not self.__refresh_lock:
            self.__refresh_lock=True
            self.after_idle(self._refresh)
    
    def _refresh(self):
        for w in self.children.values():
            if w.winfo_viewable():
                w.pack_forget()
                w.grid_forget()
            if hasattr(w,'grid_hidden'):
                hide=w.grid_hidden
            else:
                hide=False
            if (not hide) and hasattr(w,'grid_position'):
                p=w.grid_position
                i,j=p[:2]
                r,c=self.dimensions
                if hasattr(w,'grid_place_formatting'):
                    kw=w.grid_place_formatting
                else:
                    kw={}
                if hasattr(w,'grid_spans'):
                    rs,cs=w.grid_spans
                else:
                    rs=cs=1
                
                if 0<i+rs and i<r and 0<j+cs and j<c:
                    kw.update(rely=i/r,relx=j/c,relheight=rs/r,relwidth=cs/c)
                    w.place(**kw)
                    
        self.__refresh_lock=False
                
class TextGrid(GridFrame):
    text_widget=tk.Text
    def add(self,string='',i=0,j=0,rowspan=1,columnspan=1,text_widget=None,**kw):
        if text_widget is None:
            text_widget=self.text_widget
        tw=super().add(text_widget,i=i,j=j,rowspan=rowspan,columnspan=columnspan,**kw)
        tw.insert('end',string)
    