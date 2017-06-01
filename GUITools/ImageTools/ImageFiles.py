from GUITools.SharedData.ImageFiles import *

class ImageLocator:
    search_path=('shape_image',
                 'button_image')
    def shape_image(self,shape,key=None):
        if key is None:
            key='medium'
        return ShapeImages.get_shape(shape,key)
    def button_image(self,*exts,key=None):
        if key is None:
            key='_up'
        return ButtonImages.get(*exts,key=key)
    def button_up(self,*exts):
        return ButtonImages.up(*exts)
    def button_down(self,*exts):
        return ButtonImages.down(*exts)
    def __getitem__(self,keys):
##        print(keys)
        if isinstance(keys,str):
            keys=(keys,None)
        for x in self.search_path:
            f=getattr(self,x)
            file=f(*keys[:-1],key=keys[-1])
            if os.path.exists(file):
                break
        else:
            raise FileNotFoundError
        return file
    
Locator=ImageLocator()
