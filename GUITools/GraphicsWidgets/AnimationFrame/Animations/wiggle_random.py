
def start(animation,frame):
    o=frame.make_random()[0]
    animation.pass_obj=o
def move_right(animation,frame):
    frame.move(animation.pass_obj,10,0)
def move_left(animation,frame):
    frame.move(animation.pass_obj,-10,0)
def end(animation,frame):
    frame.delete(animation.pass_obj)
animation=(
    start,
    move_right,
    move_left,
    move_left,
    move_right,
    end
    )
     
