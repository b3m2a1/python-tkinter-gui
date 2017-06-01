#This provides access to various image files useful in graphics
import os,string
ls=os.listdir
osp=os.path

class shape_images:
    def __init__(self,file_root):
        self.dir=osp.join(osp.dirname(file_root),'Shape Images')

    def get_shape(self,name,size='medium'):
        name=name.lower().strip()
        size=size.lower().strip()
        return osp.join(self.dir,'{}_{}.png'.format(name,size))

class shape_class(shape_images):
    def __init__(self,file_root,base_shape):
        t=type(self)
        name=string.capwords(base_shape).replace(' ','_')
        self.__class__=type(name,(t,),self.__dict__)
        super().__init__(file_root)
        self.shape=base_shape.lower()
    def get_shape(self,size='medium'):
        return super().get_shape(self.shape,size=size)
    
ShapeImages=shape_images(__file__)
Sphere=shape_class(__file__,'sphere')
Tube=shape_class(__file__,'tube')

class animation_images:
    def __init__(self,file_root):
        self.dir=osp.join(file_root,'Animation Images')

    def get_image(self,image_name,source=None,default_ext='.png'):
        base,ext=osp.splitext(image_name)
        if ext=='':
            image_name=image_name+default_ext
        return osp.join(self.dir,image_name)
AnimationImages=animation_images(osp.dirname(__file__))

class button_images:
    def __init__(self,file_root,basic='standard'):
        self.dir=osp.join(osp.dirname(file_root),'Button Images')
        self.basic=basic
        self.raised=self.up(basic)
        self.depressed=self.down(basic)

    def get(self,*exts,key=''):
        last=exts[-1]+'{}.png'.format(key)
        path=[self.dir]+list(exts[:-1])+[last]
        return osp.join(*path)
    def up(self,*exts):
        return self.get(*exts,key='_up')
    def down(self,*exts):
        return self.get(*exts,key='_down')
    def __iter__(self):
        return iter(osp.join(self.dir,x) for x in ls(osself.dir))

ButtonImages=button_images(__file__)
    
