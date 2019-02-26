import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage

# Define Constant Values
up = np.complex(0,1)
down = np.complex(0,-1)
left = np.complex(-1,0)
right = np.complex(1,0)

turnl = np.complex(0,1)
turnr = np.complex(0,-1)
reverse = np.complex(-1,0)

white = 0
blue = 1
red = 2
black = 3

quadcmap = ListedColormap(['w','b','r','k'])

RL = {white:(turnr,black), black:(turnl,white)}
LR = {white:(turnl,black), black:(turnr,white)}
RRLL = {white:(turnr,blue), blue:(turnr,red),
        red:(turnl,black), black:(turnl,white)}
RLLL = {white:(turnr,blue), blue:(turnl,red),
        red:(turnl,black), black:(turnl,white)}
RLRL = {white:(turnr,blue), blue:(turnl,red),
        red:(turnr,black), black:(turnl,white)}

# Default settings for an open (i.e. expandable) world
# For which we need a set (instead of an array)
bset = set()

# Then a function would be necessary to transform it into an array when plotting it
def into_array(bset):
    getrange = lambda l: (min(min(l,default=0),-3), max(max(l,default=0),3))
    xrange = getrange([pos[0] for pos in bset])
    yrange = getrange([pos[1] for pos in bset])
    grid = np.zeros([yrange[1]-yrange[0]+1,xrange[1]-xrange[0]+1], int)
    new_pos = [(yrange[1]-pos[1],pos[0]-xrange[0]) for pos in bset]
    grid[[pos[0] for pos in new_pos], [pos[1] for pos in new_pos]]=1
    return(grid)

# The following functions could be implemented in a different way if the colors are stored in an array
def check_clr(pos):
    if pos in bset:
        return(black)
    else:
        return(white)
    
def recolor(pos, color):
    if color == black:
        bset.add(pos)
    if color == white:
        bset.discard(pos)
        
default = (check_clr, recolor)

class ant:
    
    def __init__(self, pos, dir2d, check_clr=check_clr, rule=RL):
        self.pos = np.complex(*pos)
        self.dir = dir2d
        self.rule = rule
        self.check_clr = check_clr
        
    def loc(self):
        return((int(self.pos.real),int(self.pos.imag)))
    
    def color(self):
        return(self.check_clr(self.loc()))
    
    def turn_and_forward(self, toturn):
        self.dir = self.dir*toturn
        self.pos = self.pos+self.dir
        
    def step(self):
        toturn, tocolor = self.rule[self.color()]
        loc = self.loc()
        self.turn_and_forward(toturn)
        return((loc, tocolor))
        
    def wrapped(self, xrange, yrange):
        self.pos = np.complex(self.pos.real%xrange, self.pos.imag%yrange)
        
    def fixed(self, xrange, yrange):
        x,y = self.pos.real,self.pos.imag
        x -= (x<0)*x + (x>xrange-1)*(x-xrange+1)
        y -= (y<0)*y + (y>yrange-1)*(y-yrange+1)
        self.pos = np.complex(x,y)

class OpenWorld:
    
    def __init__(self, setting=default):
        self.antlist = []
        self.check_clr, self.recolor = setting
    
    def add_ant(self, pos, dir2d, rule=RL):
        self.antlist.append(ant(pos, dir2d, self.check_clr, rule))
        
    def step(self):
        changes = [a.step() for a in self.antlist]
        [self.recolor(*change) for change in changes]
        
    def steps(self, times=1):
        [self.step() for _ in range(times)]
        
    def ani_gen(self, path, title="", cmap='binary', duration=3e2):
        bset.clear()
        fig, ax = plt.subplots(1, figsize=(4, 4), facecolor=(1,1,1))
        def make_frame(t):
            ax.clear()
            ax.axis('off')
            ax.set_title(title, fontsize=16)
            self.step()
            ax.imshow(into_array(bset),cmap=cmap,animated=True)
            return(mplfig_to_npimage(fig))
        ani = VideoClip(make_frame, duration = duration)
        ani.write_videofile(path, fps=50)
        return

class ClosedWorld:
    
    def __init__(self, xrange, yrange, boundary='wrapped'):
        self.ranges = (xrange, yrange)
        self.grid = np.zeros((yrange, xrange))
        self.boundary = boundary
        self.check_clr = lambda pos:self.grid[pos]
        self.antlist = []
    
    def add_ant(self, pos, dir2d, rule=RL):
        self.antlist.append(ant(pos, turnl*dir2d, self.check_clr, rule))
        
    def recolor(self, pos, color):
        self.grid[pos]=color
        
    def step(self):
        changes = [a.step() for a in self.antlist]
        [self.recolor(*change) for change in changes]
        if self.boundary == 'wrapped':
            [a.wrapped(*self.ranges) for a in self.antlist]
        if self.boundary == 'fixed':
            [a.fixed(*self.ranges) for a in self.antlist]
            
    def steps(self, times=1):
        [self.step() for _ in range(times)]
    
    def plot(self, ax, cmap):
        ax.imshow(self.grid,cmap=cmap,animated=True)
        
    def ani_gen(self, path, title="", cmap='binary', duration=3e2):
        bset.clear()
        fig, ax = plt.subplots(1, figsize=(4, 4), facecolor=(1,1,1))
        def make_frame(t):
            ax.clear()
            ax.axis('off')
            ax.set_title(title, fontsize=16)
            self.step()
            self.plot(ax,cmap)
            return(mplfig_to_npimage(fig))
        ani = VideoClip(make_frame, duration = duration)
        ani.write_videofile(path, fps=50)
        return