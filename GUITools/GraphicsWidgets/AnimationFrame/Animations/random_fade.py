fade_factor=5
def start(animation,frame):
    animation.pass_ob=frame.add_file(0,0,'Spinner.png')

def fade_move(animation,frame):
    frame.fade_ob(animation.pass_ob,1/fade_factor)
    frame.move(animation.pass_ob,1/fade_factor,1/fade_factor,mode='frac')

def end(animation,frame):
    frame.delete(animation.pass_ob)
    animation.pass_ob=None

animation=(start,)+(fade_move,)*fade_factor+(end,)

