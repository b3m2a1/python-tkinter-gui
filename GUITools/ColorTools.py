
import tkinter as tk

class TkColorOperations(tk.Frame):
    def __init__(self,root):
##        super().__init__(root)
        self.root_obj=root
    def pack(self):
        pass
    def grid(self):
        pass
    def place(self):
        pass
    
    @staticmethod
    def rgb2hex(*color_tuple):
        return '#{:02x}{:02x}{:02x}'.format(*color_tuple[:3])
    
    def name2rgb(self,name):
##        try:
        trip=self.root_obj.winfo_rgb(name)
##        except:
##            print(name)
        return [x//256 for x in trip]

    def rgb_tuple(self,rgb_id):
        if isinstance(rgb_id,str):
            rgb_id=self.name2rgb(rgb_id)
        return tuple(rgb_id)
    def rgb_hex(self,rgb_id):
        tup=None
        if isinstance(rgb_id,str):
            if not '#'==rgb_id[0]:
                tup=self.rgb_tuple(rgb_id)
        else:
            tup=rgb_id
        if not tup is None:
            rgb_id=self.rgb2hex(*tup)
        return rgb_id        
    @staticmethod
    def rgb_lighter(color_tuple,decimal_percentage):
        color=color_tuple
        color=list(color)
        r=color[0];g=color[1];b=color[2]
        l_factor=int(255*decimal_percentage)
        r,g,b=map(lambda a:min(int(a+l_factor),255),(r,g,b))
        color[0]=r;color[1]=g;color[2]=b
        return tuple(color)
    @staticmethod
    def rgb_darker(color_tuple,decimal_percentage):
        color=color_tuple
        color=list(color)
        r=color[0];g=color[1];b=color[2]
        d_factor=int(255*decimal_percentage)
        r,g,b=map(lambda a:max(int(a-d_factor),0),(r,g,b))
        color[0]=r;color[1]=g;color[2]=b
        return tuple(color)

    @staticmethod
    def rgb_fade(color1,color2,decimal_percentage):#fades one color linearly into another
        color_map=map(lambda c1,c2:(c1*(1-decimal_percentage)+c2*decimal_percentage),
                                    color1,color2)
        return tuple([min(max(int(x),0),255) for x in color_map])
    @staticmethod
    def increase_contrast(color,decimal_percentage):
        m=max(color)
        new=[]
        for x in color:
            if x<m:
                x=max(x*decimal_percentage,0)
            else:
                x=min(x*(1+decimal_percentage),255)
            new.append(int(x))
        return tuple(new)
    @staticmethod
    def invert_color(color):
##        r,g,b=color
        return tuple(((x+255)%256 for x in color))
        
        
    def tint_color(self,color,r,g,b):
        bg=list(self.rgb_tuple(color))
        sub=(r,g,b)
        for i in range(3):
            sub_1=sub[(i+1)%3]
            sub_2=sub[(i+2)%3]
            bg[i]=bg[i]-(sub_1+sub_2)
        new=map(lambda a:max(0,a),bg)
        new=map(lambda a,b:min(a+b,255),(r,g,b),new)
        return new
