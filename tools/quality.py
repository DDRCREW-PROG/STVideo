"""Offline quality tools: hardware-constrained palettes and single-write YM DAC.

CIELAB distances are an optimization criterion, not a claim of a globally
optimal palette. All expensive work is done on the PC.
"""
from pathlib import Path
import re,struct
import numpy as np
from PIL import Image

def lab(rgb):
    c=np.asarray(rgb,dtype=np.float32)/255
    c=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
    xyz=c @ np.array([[.4124564,.2126729,.0193339],[.3575761,.7151522,.1191920],[.1804375,.0721750,.9503041]],dtype=np.float32)
    xyz/=np.array([.95047,1,1.08883],dtype=np.float32)
    f=np.where(xyz>216/24389,np.cbrt(xyz),xyz*(24389/27)/116+16/116)
    return np.stack((116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])),axis=-1)

GRID_LEVELS=np.array([(r,g,b) for r in range(8) for g in range(8) for b in range(8)],dtype=np.uint16)
GRID_RGB=np.rint(GRID_LEVELS*255/7).astype(np.uint8)
GRID_LAB=lab(GRID_RGB)
WEIGHT=np.array([1.15,1,1],dtype=np.float32)

def distances(a,b):
    return np.sum(((a[:,None,:]-b[None,:,:])*WEIGHT)**2,axis=2)

def make_palette(ids):
    rgb=GRID_RGB[np.asarray(ids)]
    rgb=rgb[np.argsort(lab(rgb)[:,0],kind='stable')]
    levels=np.rint(rgb.astype(float)*7/255).astype(int)
    words=(levels[:,0]<<8)|(levels[:,1]<<4)|levels[:,2]
    p=Image.new('P',(1,1));p.putpalette(rgb.flatten().tolist()+rgb[0].tolist()*240)
    return p,rgb,struct.pack('>16H',*words)

def perceptual_palette(frames,baseline):
    pixels=np.concatenate([np.asarray(f)[::2,::2].reshape(-1,3) for f in frames]).astype(np.uint16)
    keys=((pixels[:,0]>>3)<<10)|((pixels[:,1]>>3)<<5)|(pixels[:,2]>>3)
    counts=np.bincount(keys,minlength=32768);active=counts>0;w=counts[active].astype(np.float32)
    rgb=np.stack([np.bincount(keys,weights=pixels[:,c],minlength=32768)[active]/w for c in range(3)],axis=1)
    x=lab(rgb);grid=GRID_LAB
    mapped=np.rint(rgb*7/255).astype(int)
    ids=(mapped[:,0]<<6)|(mapped[:,1]<<3)|mapped[:,2]
    hw_weights=np.bincount(ids,weights=w,minlength=512)
    seeds=[int(hw_weights.argmax())]
    for _ in range(15):
        error=distances(grid,grid[seeds]).min(axis=1)*hw_weights
        error[seeds]=-1
        seeds.append(int(error.argmax()))
    original=np.rint(baseline[1].astype(float)*7/255).astype(int)
    original=(original[:,0]<<6)|(original[:,1]<<3)|original[:,2]
    original=list(dict.fromkeys(map(int,original)))
    while len(original)<16:
        error=distances(grid,grid[original]).min(axis=1)*hw_weights;error[original]=-1
        original.append(int(error.argmax()))
    best_ids=original;best_score=float((distances(x,grid[original]).min(axis=1)*w).sum())
    for initial in [original,seeds]:
        palette=list(initial)
        for _ in range(18):
            d=distances(x,grid[palette]);assignment=d.argmin(axis=1)
            score=float((d.min(axis=1)*w).sum())
            if score<best_score:best_ids=palette.copy();best_score=score
            new=[]
            for k in range(16):
                mask=assignment==k
                if mask.any():
                    centroid=np.average(x[mask],axis=0,weights=w[mask])
                    costs=distances(centroid[None,:],grid)[0]
                    costs[new]=np.inf
                    new.append(int(costs.argmin()))
                else:
                    residual=distances(grid,grid[new or palette]).min(axis=1)*hw_weights
                    residual[new]=-1;new.append(int(residual.argmax()))
            if new==palette:break
            palette=new
        score=float((distances(x,grid[palette]).min(axis=1)*w).sum())
        if score<best_score:best_ids=palette;best_score=score
    return make_palette(best_ids)

BAYER=np.array([[0,48,12,60,3,51,15,63],[32,16,44,28,35,19,47,31],
 [8,56,4,52,11,59,7,55],[40,24,36,20,43,27,39,23],
 [2,50,14,62,1,49,13,61],[34,18,46,30,33,17,45,29],
 [10,58,6,54,9,57,5,53],[42,26,38,22,41,25,37,21]],dtype=np.float32)

def perceptual_indices(frame,rgb,adaptive=False,strength=.7):
    source=np.asarray(frame);x=lab(source.reshape(-1,3));p=lab(rgb)
    d=distances(x,p);nearest=d.argmin(axis=1)
    if not adaptive:return nearest.astype(np.uint8).reshape(200,320)
    pairs=np.argpartition(d,3,axis=1)[:,:4]
    best=d[np.arange(len(x)),nearest].copy()
    pa=nearest.copy();pb=nearest.copy();mix=np.zeros(len(x),dtype=np.float32)
    # Fit two-color mixtures in Lab, then use a fixed spatial threshold.
    # A separation penalty discourages noisy complementary-color speckles.
    for i in range(4):
        for j in range(i+1,4):
            a=pairs[:,i];b=pairs[:,j];delta=p[b]-p[a]
            length=np.sum((delta*WEIGHT)**2,axis=1)
            t=np.clip(np.sum((x-p[a])*delta*WEIGHT**2,axis=1)/np.maximum(length,1e-6),0,1)
            candidate=p[a]+t[:,None]*delta
            cost=np.sum(((x-candidate)*WEIGHT)**2,axis=1)+.018*length*np.sqrt(t*(1-t))
            mask=(cost<best)&(t>=.075)&(t<=.925)&(x[:,0]>5)
            best[mask]=cost[mask];pa[mask]=a[mask];pb[mask]=b[mask];mix[mask]=t[mask]
    threshold=np.tile((BAYER+.5)/64,(25,40)).reshape(-1)
    result=np.where(threshold<mix,pb,pa)
    strength_threshold=np.tile(((BAYER*37+17)%64+.5)/64,(25,40)).reshape(-1)
    result=np.where(strength_threshold<strength,result,nearest)
    return result.astype(np.uint8).reshape(200,320)

def scene_groups(frames,enabled=True):
    start=0
    for i in range(1,len(frames)):
        before=np.asarray(frames[i-1])[::8,::8].astype(np.float32)
        after=np.asarray(frames[i])[::8,::8].astype(np.float32)
        if enabled and np.mean(np.abs(after-before))>32:
            yield frames[start:i];start=i
    yield frames[start:]

def ym_levels(root):
    p=Path(root)/'data/ym2149_fixed_vol.h'
    if not p.exists():p=Path(root)/'vendor/ym2149_fixed_vol.h'
    if not p.exists():p=Path(root).parent/'atari-slingshot/vendor/hatari-reference/ym2149_fixed_vol.h'
    text=re.sub(r'/\*.*?\*/','',p.read_text(),flags=re.S)
    a=np.array([int(x) for x in re.findall(r'\d+',text)],dtype=np.float64)
    if len(a)!=4096:raise ValueError('Invalid YM level table')
    return a/a.max()

class SingleWriteYM:
    """One volume change per sample. Each frame carries an exact restart state."""
    def __init__(self,root):
        self.levels=ym_levels(root)
        states=np.arange(4096,dtype=np.uint16)
        self.neighbors=np.empty((4096,48),dtype=np.uint16)
        for channel in range(3):
            for volume in range(16):
                self.neighbors[:,channel*16+volume]=(states&~np.uint16(15<<(channel*4)))|np.uint16(volume<<(channel*4))
        self.lookup=np.empty((4096,256),dtype=np.uint8)
        targets=np.arange(256)/255
        for state in range(4096):
            error=abs(targets[:,None]-self.levels[self.neighbors[state]][None,:])
            # Prefer an unchanged register when two commands reproduce the same level.
            self.lookup[state]=error.argmin(axis=1)
        self.state=int(abs(self.levels-.5).argmin())
        self.feedback=0.

    def commands(self,state):
        return struct.pack('>III',0x08000000|((state&15)<<8),
            0x09000000|(((state>>4)&15)<<8),0x0a000000|(((state>>8)&15)<<8))

    def table(self):
        data=bytearray(3072)
        for code in range(48):
            command=struct.pack('>I',((8+code//16)<<24)|((code&15)<<8))
            data[code*12:code*12+12]=command*3
        return bytes(data)

    def encode(self,pcm):
        initial=self.commands(self.state);data=bytearray(len(pcm))
        state=self.state;feedback=self.feedback
        for i,value in enumerate(pcm):
            target=max(0,min(255,round(int(value)+feedback*.5)))
            code=int(self.lookup[state,target]);state=int(self.neighbors[state,code]);data[i]=code
            feedback=max(-5,min(5,float(value)-self.levels[state]*255))
        self.state=state;self.feedback=feedback
        return bytes(data),initial

class LookaheadYM(SingleWriteYM):
    """Minimum squared level error over a frame, with one YM write per sample.

    The 4096 states are the three 4-bit volumes. A transition changes at most
    one channel. Minima along each axis of the 16x16x16 cost cube enumerate
    all legal predecessors without building a 4096x4096 transition matrix.
    Backtracking preserves the exact previous-frame state at each boundary.
    """
    def __init__(self,root):
        self.levels=ym_levels(root)
        self.state=int(abs(self.levels-.5).argmin())
        self.states=np.arange(4096,dtype=np.uint16)

    def encode(self,pcm):
        initial=self.commands(self.state)
        if not len(pcm):return b'',initial
        target=np.frombuffer(pcm,dtype=np.uint8).astype(np.float64)/255
        costs=np.full(4096,np.inf);costs[self.state]=0
        predecessors=np.empty((len(target),4096),dtype=np.uint16)
        shape=(16,16,16);states=self.states
        for i,value in enumerate(target):
            cube=costs.reshape(shape)
            a=cube.argmin(axis=2)
            b=cube.argmin(axis=1)
            c=cube.argmin(axis=0)
            pa=(states&0xff0)|np.broadcast_to(a[:,:,None],shape).ravel()
            pb=(states&0xf0f)|(np.broadcast_to(b[:,None,:],shape).ravel()<<4)
            pc=(states&0x0ff)|(np.broadcast_to(c[None,:,:],shape).ravel()<<8)
            best=pa.astype(np.uint16)
            minimum=costs[best]
            for candidate in (pb,pc):
                candidate=candidate.astype(np.uint16)
                values=costs[candidate];better=values<minimum
                best[better]=candidate[better];minimum=np.minimum(minimum,values)
            predecessors[i]=best
            costs=minimum+(self.levels-value)**2
        state=int(costs.argmin());self.state=state
        path=np.empty(len(target),dtype=np.uint16)
        for i in range(len(target)-1,-1,-1):
            path[i]=state;state=int(predecessors[i,state])
        previous=np.concatenate(([state],path[:-1])).astype(np.uint16)
        delta=previous^path
        channel=np.where(delta&15,0,np.where(delta&240,1,np.where(delta&3840,2,0)))
        codes=(channel*16+((path>>(channel*4))&15)).astype(np.uint8)
        return codes.tobytes(),initial
