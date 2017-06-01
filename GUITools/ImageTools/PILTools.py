import tkinter as tk
from PIL import Image,ImageTk,ImageColor,ImageChops,ImageOps

from GUITools.Shared import *

class TkWrapper(ImageTk.PhotoImage):
    
    ''''A secondary tk image wrapper on top of an image wrapper'''
    show_root=None
    def __init__(self,image_wrapper=None,
                 source=None,root=None,width=16,height=16,
                 mode='RGBA',color='white',undolen=5,name=None,
                 mark_flag=False):
        if image_wrapper is None:
            image_wrapper=ImageWrapper(source=source,root=root,
                                       width=width,height=height,
                                       mode=mode,color=color,
                                       undolen=undolen,name=name)
        self.image_wrapper=image_wrapper
        self.allow_kill=False
##        print('constructing image...')
        super().__init__(image_wrapper.image)
##        print('done')
        self.track_flag=mark_flag
        if mark_flag:
            print(' loading: {}'.format(repr(self)))

    def _load(self):
        '''Generates a Tk image on top of an image wrapper image'''
        super().__init__(self.image_wrapper.image)

    @property
    def TkImage(self):
        '''Generates a tk ready image'''
        self._load()
        P=self.new_tk()
        n=0
        for p,pos in self.image_wrapper:
            f=p[3]
            p=p[:3]
            if f<10:
                P.put('#{:0>2x}{:0>2x}{:0>2x}'.format(*p),pos)
        
        return P

    def new_tk(self):
        '''Makes a new PhotoImage with the appropriate dimensions'''
        P=tk.PhotoImage(width=self.width(),height=self.height())
        P.image_wrapper=self.image_wrapper
        self.lastTk=P
        return P
        
    def show_base(self):
        '''Calls show on the image wrapper'''
        self.image_wrapper.show()
            
    def show(self,hold=False): 
        '''Sticks the image into a formatting grid of all generated images'''
        from GUITools.FormattingWidgets import FormattingGrid
        t=type(self)
        S=t.show_root
        if S is None:
            t.show_root=T=tk.Toplevel()
            T.hooks=[]
            T.title('Tk Images')
            T.attributes('-topmost',True)
            T.protocol('WM_DELETE_WINDOW',
                       lambda s=t:(
                           t.show_root.destroy(),
                           setattr(s,'show_root',None)
                           ))
            T.fg=FormattingGrid(T,rows=5,columns=5)
            T.fg.pack(fill='both',expand=True)
        t.show_root.hooks.append(self)
        I=t.show_root.fg.AddFormat(tk.Label,text=str(self),image=self,
                                    compound='top',bd=2,
                                    relief='ridge')
        t.show_root.fg.Refresh()
        return I
        
    def show_tk(self):
        '''Shows the tk image'''
        I=self.show()
        ltk=self.TkImage
        I['image']=ltk
        
    def __repr__(self):
        s=super().__str__()
        s+=self.image_wrapper.name
        return s

    def __del__(self):
        if self.track_flag:
            print('deleteing: {}'.format(repr(self)))
##        self.image_wrapper.tk_hooks.remove(str(self))
        super().__del__()
        
class ImageWrapper:
    '''A powerful image wrapper class on the standard PIL.Image that tracks all edits to the image so that they can be cleanly restored, as well as providing many useful image editing functions 

Operations include:
    Rotations: rotate
    Color masking: 
    Color adjustment:
    Plus anything that a normal PIL image can do via

Also provides reasonably efficient iterators through the pixels themselves via:
    '''
    Flattener=GeneralTools.Flattener(endtype=list)
    flatten=Flattener.flatten
    transformation_map={'flip horizontal':Image.FLIP_LEFT_RIGHT,
             'flip vertical':Image.FLIP_TOP_BOTTOM,
             'rotate_right':Image.ROTATE_90
             }
    filters={'antialias':Image.ANTIALIAS,
             'bilinear':Image.BILINEAR,
             'bicubic':Image.BICUBIC,
             'nearest':Image.NEAREST}
    colormap=ImageColor.colormap
    
    def __init__(self,source=None,root=None,width=16,height=16,
                 mode='RGBA',color='white',undolen=10,name=None):

        from collections import deque

        ImageClass=Image.Image
        ImageWrapper=type(self)
        if source is None:
            image=Image.new(mode,(width,height),color)
            if name is None:
                name='{}x{}.{}'.format(width,height,mode)
        else:
            if isinstance(source,str):
                image=Image.open(source)
                if name is None:
                    name=source
                self.file=source
            elif isinstance(source,(ImageClass,ImageWrapper)):
                image=source
                if name is None:
                    name=str(image)
        self.rotation_angle=0
        self.lightness=0
        self.name=name
        self.last=deque(())
        self.temp_stack=deque(())
        self.image=self.original=image

    @property
    def dimensions(self):
        return (self.width,self.height)

    @property
    def width(self):
        try:
            w=self.image.width
        except AttributeError:
            w=self.image.size[0]
        return w
    @property
    def height(self):
        try:
            w=self.image.height
        except AttributeError:
            w=self.image.size[1]
        return w
    
    def copy(self):
        return type(self)(self.image.copy())

    def contant(self,color):
        '''Returns an image wrapper of the same size with constant color'''
        return type(self)(ImageChops.constant(self.dimensions,color),mode=self.mode)
#     constant=contant

    def scale(self,scaling,filter='nearest'):
        '''Scales the underlying image applying the provided filter'''
        w,h=self.dimensions
        to=(int(w*scaling),int(h*scaling))
        self.resize(to,filter=filter)

    def resize(self,x_y,filter='nearest'):
        '''Resizes the underlying image applying the provided filter'''
        self.last.append(self.image)
        if isinstance(filter,str):
            filter=self.filters[filter]
        self.image=self.image.resize(x_y,filter)

    def reload(self):
        '''Attempts to reload the image from the base file'''
        try:
            f=self.file
        except AttributeError:
            f=self.name
        if os.path.exists(f):
            type(self).__init__(self,f)
        else:
            raise ValueError('{}.reload: original link lost'.format(type(self).__name__))

    def save(self,file=None):
        '''Saves the image to a file'''
        if file is None:
            try:
                f=self.file
            except AttributeError:
                raise ValueError('{}.save: no file provided and original file lost'.format(type(self).__name__))
        self.image.save(file)
        
    def load_link(self,link):
        '''Reinitializes from the image link provided'''
        self.__init__(link)
        
    def getrow(self,i,start=None,end=None):
        '''Provides an iterator through the pixels of row i, starting at start and ending at end'''
        if end is None:
            end=self.width
        if start is None:
            start=0
        for x in range(start,end):
            yield (self.getpixel(x,i),(x,i))
            
    def getcol(self,j,start=None,end=None):
        '''Provides an iterator through the pixels of row j, starting at start and ending at end'''
        if end is None:
            end=self.height
        if start is None:
            start=0
        for y in range(start,end):
            yield (self.getpixel(j,y),(j,y))

    def row_iter(self,start=None,end=None,seg_start=None,seg_end=None,step=1):
        '''Provides an iterator of row iterators through the rows, starting at start and ending at end, with each row iterator spanning seg_start to seg_end'''
        if start is None:
            start=0
        if end is None:
            end=self.height
        for i in range(start,end,step):
            yield self.getrow(i,seg_start,seg_end)

    def col_iter(self,start=None,end=None,seg_start=None,seg_end=None,step=1):
        '''Provides an iterator of column iterators through the columns, starting at start and ending at end, with each column iterator spanning seg_start to seg_end'''
        if start is None:
            start=0
        if end is None:
            end=self.width
        for i in range(start,end,step):
            yield self.getcol(i,seg_start,seg_end)

    def getrectangle(self,xmin=0,ymin=0,xmax=None,ymax=None,
                     orient='row',positions=False):
        '''Returns an iterator through the rectangle of pixels specified

orient being row iterates row wise
orient being column iterates column

positions being true also returns the pixel position'''
        if positions:
            if orient=='row':
                for iterator in self.row_iter(ymin,ymax,xmin,xmax):
                    for p in iterator:
                        yield p
            elif orient=='col':
                for iterator in self.col_iter(xmin,xmax,ymin,ymax):
                    for p in iterator:
                        yield p
        else:
            if orient=='row':
                for iterator in self.row_iter(ymin,ymax,xmin,xmax):
                    for p,pos in iterator:
                        yield p
                    yield '\n'
            elif orient=='col':
                for iterator in self.col_iter(xmin,xmax,ymin,ymax):
                    for p,pos in iterator:
                        yield p
                    yield '\n'

    def copyrectangle(self,xmin=0,ymin=0,xmax=None,ymax=None,mode='RGBA',color='white'):
        '''Copies the specified rectangle to a new image

This is obviously slow, given that it's a large python copy process.
Could be sped up by operating at the pure PIL.Image level
'''
        if ymax is None:
            ymax=self.height
        if xmax is None:
            xmax=self.width
        w=xmax-xmin
        h=ymax-ymin
        new=ImageWrapper(width=w,height=h,mode=mode,color=color)
        x=0;y=0
        pix=new.image.im.putpixel
        for p in self.getrectangle(xmin,ymin,xmax,ymax):
            if not isinstance(p,str):
                pix((x,y),p)
                x+=1
                if x>=w:
                    x=0
                    y+=1
                    if y>=h:
                        break
        return new
    
    def getpixel(self,*tup):
        '''Gets the pixel specified by tup'''
        if not isinstance(tup[0],(int,str,float)):
            tup=self.flatten(tup)
        x,y=[int(x) for x in tup[:2]]
        if (x < 0) or (y < 0):
            w,h=self.dimensions
            if x<0:
                x=w-x
            if y<0:
                y=h-y
        return self.image.getpixel((x,y))

    def new_from_data(self,new):
        '''Creates a new PIL.Image with the same size and mode as the current image and returns it'''
        I=self.Image.new(size=self.size,mode=self.mode)
        I.putdata(new)
        return I
    
    def apply_cutoff(self,rmin=0,rmax=255,r_low=None,r_high=None,r_map=None,
                          bmin=0,bmax=255,b_low=None,b_high=None,b_map=None,
                          gmin=0,gmax=255,g_low=None,g_high=None,g_map=None,
                          amin=0,amax=255,a_low=None,a_high=None,a_map=None,
                          low_cut=0,high_cut=255,map_to=lambda p:p):
        '''Applies a cutoff by mapping the pixels above max to high and min to low

Specific color cutoffs override the base one

The maps define what should happen to pixels within the allowed range

One can define a simple color replacement by providing only maps
'''
        
        self.last.append(self.image)

        if r_low is None:
            r_low=low_cut
        if r_high is None:
            r_high=high_cut
        if r_map is None:
            r_map=map_to
        if g_low is None:
            g_low=low_cut
        if g_high is None:
            g_high=high_cut
        if g_map is None:
            g_map=map_to
        if b_low is None:
            b_low=low_cut
        if b_high is None:
            b_high=high_cut
        if b_map is None:
            b_map=map_to
        if a_low is None:
            a_low=low_cut
        if a_high is None:
            a_high=high_cut
        if a_map is None:
            a_map=map_to
        lut=(
            [r_low]*(rmin)+
                [r_map(x) for x in range(rmin,rmax+1)]+
                [r_high for x in range(rmax,255)]+#red band
            [g_low]*(gmin)+
                [g_map(x) for x in range(gmin,gmax+1)]+
                [g_high for x in range(gmax,255)]+#green band
            [b_low]*(bmin)+
                [b_map(x) for x in range(bmin,bmax+1)]+
                [b_high for x in range(bmax,255)]+#blue band
            [a_low]*(amin)+
                [a_map(x) for x in range(amin,amax+1)]+
                [a_high for x in range(amax,255)])#alpha band
            
        self.image=self.image.point(lut)

    def take_between(self,min=0,max=255,map_outside=255,**cutoffs):
        '''Reduces all pixels outside of the specified min and max to the cutoff value

cutoffs can be specified as in apply_cutoff'''
        if not 'low_cut' in cutoffs:
            cutoffs['low_cut']=map_outside
        if not 'high_cut' in cutoffs:
            cutoffs['high_cut']=map_outside
        self.apply_cutoff(rmin=min,rmax=max,
                          gmin=min,gmax=max,
                          bmin=min,bmax=max,
                          amin=min,amax=max,
                          **cutoffs)

    
    def create_mask(self,min_value,max_value,mode='outside',
                    bw=True,L=False):
        '''Generates a mask for colors either outside or inside min_value and max_value

if bw is true, it then inverts the generated mask'''
        if mode=='outside':
            outside=0;take=(0,5)
            invert=255
        elif mode=='inside':
            outside=255;take=(250,255)
            invert=0
        self.take_between(min_value,max_value,map_outside=outside,a_low=255,a_high=255)
        if bw:
            self.take_between(*take,map_outside=invert,a_low=255,a_high=255)
            self.last.pop()
        if L:
            self.black_and_white()
            self.last.pop()

    def color_ranges(self,*range_color_pairs,keep_shading=True):
        '''Colorizes base on the range, color pairs provided
        
if keep_shading is true, the colorized ranges keeps its shading
otherwise the ranes become simply the color provide'''
        I=self
        I.last.append(I.image)
        image_pairs=[(I.copy(),I.copy()) for x in range_color_pairs]
        for tup_pair,im_pair in zip(range_color_pairs,image_pairs):
            R,tup=tup_pair
            M,C=im_pair
            M.create_mask(*R,L=True)
            C.create_mask(*R,bw=False,mode='inside')

            if keep_shading:
                keep_shading=(255,255,255)
            else:
                keep_shading=tup
            C.colorize(tup,tup)
            I.image=I.image.copy()
            I.paste(C,mask=M)
            
    def use_bands(self,r=None,g=None,b=None,a=None):
        '''Inserts the bands into the image'''
        bands=list(self.image.split())
        N=len(bands)
        new_bands=[]
        if not r is None:
            new_bands=[r]
        if not g is None:
            if len(new_bands)==0:
                new_bands=[bands[0],g]
            else:
                new_bands.append(g)
        if not b is None:
            l=len(new_bands)
            if l==0:
                new_bands=[bands[0],bands[1],b]
            elif l==1:
                new_bands=new_bands+[bands[1],b]
            else:
                new_bands.append(b)
        if not a is None:
            l=len(new_bands)
            if l==0:
                new_bands=bands[:3]+[a]
            elif l==1:
                new_bands=new_bands+[bands[1],bands[2],a]
            elif l==2:
                new_bands=new_bands+[bands[2],a]
            else:
                new_bands.append(a)
        l=len(new_bands)
        if l>0:
            new_bands+=bands[l:]
            self.last.append(self.image)
            self.image=Image.merge('RGBA',new_bands)
            return True
        return False
    
    def black_and_white(self):
        '''Makes the image black and white'''
        self.last.append(self.image)
        self.image=ImageOps.grayscale(self.image)

    def paste(self,*args,**kwargs):
        '''Pastes the image into the base image'''
        self.last.append(self.image.copy())
        self.image.paste(*args,**kwargs)
        
    def colorize(self,black_tuples=(),white_tuples=(),from_bw=False):
        '''Colorizes, but can't remember how'''
        #allow for more band mixing via multiple black and white tuples
        #compute multiple times
        #blend all results
        
        self.last.append(self.image)
        b=self.image.split()
        self.black_and_white()
        self.last.pop()

        try:
            I=black_tuples[0]
        except IndexError:
            black_tuples=((),)
        else:
            if isinstance(I,int):
                black_tuples=(black_tuples,)
        try:
            I=white_tuples[0]
        except IndexError:
            white_tuples=((),)
        else:
            if isinstance(I,int):
                white_tuples=(white_tuples,)
        b_len=len(black_tuples)
        w_len=len(white_tuples)
        black_tuples=list(black_tuples)
        white_tuples=list(white_tuples)
        for i in range(b_len,w_len):
            black_tuples.append((0,0,0))
        for j in range(w_len,b_len):
            white_tuples.append((255,255,255))
        image=None
        for black,white in zip(black_tuples,white_tuples):
            new=ImageOps.colorize(self.image,black,white)
            if image is None:
                image=new
            else:
                image=Image.blend(image,new,.5)
        if not image is None:
            self.image=image
            if len(b)==4:
                if self.use_bands(a=b[3]):
                    self.last.pop()
    
    def rotate(self,theta,resample='nearest',expand=False,mode='degree'):
        '''Rotates the image based on the theta, resampling, expand and mode'''

        if isinstance(resample,str):
            resample=self.filters[resample]
        self.rotation_angle+=theta
        self.last.append(self.image)
        self.image=self.image.rotate(theta,resample=resample,expand=expand)
        
    def transpose(self,key):
        '''Transposes the image based on the theta, resampling, expand and mode'''
        op=self.transformation_map[key]
        im=self.image.transpose(op)
        self.last.append(self.image)
        self.image=im

    def invert(self):
        '''Inverts the image colors'''
        self.last.append(self.image)
        self.image=ImageChops.invert(self.image)

    def undo(self):
        '''Undoes the last command'''
        self.image=self.last.pop()

    def display_rectangle(self,rel_xmin=0,rel_ymin=0,rel_xmax=1,rel_ymax=1):
        '''Sets the rectangle to display'''
        w,h=self.dimensions
        x0=int(rel_xmin*w);x1=int((w)*rel_xmax)
        y0=int(rel_ymin*h);y1=int((h)*rel_ymax)
        img=self.constant((0,0,0,0)).image
        self.last.append(self.image)
        t=(x0,y0,x1,y1)
        cropped=self.image.crop(t)
        img.paste(cropped,t)
        self.image=img
            
    def set_base_image(self,im=None):
        '''Sets the base of the undo stack to the current image'''
        if im is None:
            im=self.image
        self.last.appendleft(im)
        self.original=im

    def temporary_set(self,im=None):
        '''Temporarily sets the base of the undo stack to the current image'''
        if im is None:
            im=self.image
        self.temp_stack.append(self.original)
        self.set_base_image(im)

    def temporary_reset(self):
        '''Resets the previous temporary_set'''
        original=self.temp_stack.pop()
        self.original=original
        self.last.popleft()
        self.last.appendleft(original)
        
    def reset(self):
        '''Resets to the base of the undo stack'''
        self.last.clear()
        self.rotation_angle=0
        self.image=self.original
        
    def tint(self,r=None,g=None,b=None,a=255):
        '''Applies a tint to the image'''
        ticks=0
        if r is None:
            r=0
            ticks+=1
        if g is None:
            g=0
            ticks+=1
        if b is None:
            b=0
            ticks+=1
        if ticks==3:
            r=g=b=255
        color=(r,g,b,a)

        w,h=self.dimensions
        self.last.append(self.image)
        test_im=self.constant(color)
        self.last.append(self.image)
        self.image=ImageChops.multiply(self.image,test_im)

    def constant(self,color):
        '''Sets returns a constant color copy'''
        w=self.width;h=self.height
        c=color
        return type(self)(width=w,height=h,mode=self.mode,color=c)
    
    def darken(self,decimal_percentage=.1):
        '''Darkens the image by a decimal percentage'''
        color=tuple([int(255*decimal_percentage) for x in range(3)]+[0])
        scl_im=self.constant(color)
        self.last.append(self.image)
        self.image=ImageChops.subtract(self.image,scl_im)

    def lighten(self,decimal_percentage=.1):
        '''Lightens the image by a decimal percentage'''
        color=tuple([int(255*decimal_percentage) for x in range(3)]+[0])
        scl_im=self.constant(color)
        self.last.append(self.image)
        self.image=ImageChops.add(self.image,scl_im)

    def fade_to(self,color,decimal_percentage=.1):
        '''Fades into a color by a decimal percentage'''
        if len(color)==3:
            scl_im=self.constant('white')
            r=self.getrectangle()
            def flam(t):
                l=list(t)
                l[:3]=color
                return tuple(l)
            scl_im.putdata([flam(x) for x in r if not x is '\n'])
##            scl_im.show()
        else:
            scl_im=self.constant(color)
        self.last.append(self.image)
        self.image=ImageChops.blend(self,scl_im,decimal_percentage)

    def fade_restore(self,decimal_percentage=.1):
        '''Restores from a the root image by a decimal percentage'''
        I=self.last.popleft()
        self.last.append(self.image)
        self.image=ImageChops.blend(self,I,decimal_percentage)
        self.last.appendleft(I)
    
    def solidify(self,color=None,decimal_percentage=.1):
        '''Restores alpha channel by a decimal percentage'''
        #color is there for use with animation frame.
        #May find use later, though, combining with fade
        fade=int(255*decimal_percentage)
        r=self.getrectangle()
        self.last.append(self.image)
        sub_im=self.constant((0,0,0,fade))
        self.image=ImageChops.add(self.image,sub_im)
        
    def disappear(self,color=None,decimal_percentage=.1):
        '''Reduces the alpha channel by a decimal percentage'''
        #color is there for use with animation frame.
        #May find use later, though, combining with fade
        fade=int(255*decimal_percentage)
        r=self.getrectangle()
        self.last.append(self.image)
        sub_im=self.constant((0,0,0,fade))
        self.image=ImageChops.subtract(self.image,sub_im)

    @property
    def Tk(self):
        '''Property version of toTk'''
        return self.toTk()
        
    def toTk(self,image=None):
        '''Generates a tk wrapper image from the current image'''
        
        self.lastTk=TkWrapper(self)#,True)
        return self.lastTk

    def getrgb(self,color):
        return ImageColor.getrgb(color,self.image.mode)

    def getcolor(self,color):
        return ImageColor.getcolor(color,self.image.mode)

    def __call__(self,name,*args,**kwargs):
        self.last.append(self.image)
        f=getattr(self.image,name)
        self.image=f(*args,**kwargs)
    
    def __getattr__(self,attr):
        ret=None
        try:
            ret=super().__getattribute__(attr)
        except AttributeError as E:
            try:
                ret=self.image.__getattribute__(attr)
            except AttributeError:
                raise E from E
        return ret

    def __iter__(self):
        '''Returns an iterator through all the pixels in the image'''
        return self.getrectangle(positions=True)

class ImageEditor(ImageWrapper):
    def replace(self,ctup1,rep_with=(255,255,255,255),tolerance=(0,0,0)):
        ctup2=rep_with
        try:
            t=iter(tolerance)
        except:
            tolerance=[int(tolerance)]*3
        else:
            tolerance=tuple(t)
            
        reps=0
        d=self.image.getdata()
        l=len(d)
        new=[None]*l
        for i in range(l):
            t=d[i]
            for j in range(3):
                c=t[j]
                c1=c-tolerance[j]
                c2=c+tolerance[j]
                test=ctup1[j]
                if test<c1 or test>c2:
                    new[i]=t
                    break
            else:
                new[i]=ctup2
                reps+=1
        I=self.Image.new(size=self.size,mode=self.mode)
        I.putdata(new)
        return (reps,type(self)(I))
    
    def recolored(self,r=1,g=1,b=1,a=1):
        d=self.image.getdata()
        l=len(d)
        new=[None]*l
        m=[max(x,0) for x in (r,g,b,a)]
        for i in range(l):
            t=d[i]
            new[i]=tuple(min(int(x*y),255) for x,y in zip(m,t))
        
        I=self.Image.new(size=self.size,mode=self.mode)
        I.putdata(new)
        return type(self)(I)

    def in_range(self,color,other=(255,255,255,255),tolerance=(0,0,0)):
        try:
            t=iter(tolerance)
        except:
            tolerance=[int(tolerance)]*3
        else:
            tolerance=tuple(t)
        t=other
        for j in range(3):
            c=t[j]
            c1=c-tolerance[j]
            c2=c+tolerance[j]
            test=color[j]
            if test<c1 or test>c2:
                return False
        return True

    def index_replace(self,tup,rep_with=(255,255,255,255),tolerance=(0,0,0)):
        c=self.getpixel(tup)
        return self.replace(c,rep_with=rep_with,tolerance=tolerance)
    
    def split_at(self,cutoff,low=(255,255,255,255),high=None):
        
        if len(cutoff)==2:
            cutoff=self.getpixel(cutoff)
            
        d=self.getdata()
        l=len(d)
        new=[None]*l
        for i in range(l):
            p=d[i]
            counts=0
            for j in range(3):
                if p[j]>cutoff[j]:
                    counts+=1
                    if counts>2:
                        new[i]=low
                        break
            else:
                if high is None:
                    put=p
                else:
                    put=high
                new[i]=put
                
        return self.new_from_data(new)
