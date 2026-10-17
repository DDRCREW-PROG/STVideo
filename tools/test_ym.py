"""Check the constrained optimizer against exhaustive short-sequence search."""
from pathlib import Path
import struct,unittest
import numpy as np
from quality import LookaheadYM,SingleWriteYM
ROOT=Path(__file__).resolve().parents[1]

def decode(codec,data,initial):
    state=sum(((value>>8)&15)<<(4*c) for c,value in enumerate(struct.unpack('>III',initial)))
    levels=[]
    for code in data:
        if code>=48:raise AssertionError('Illegal register command')
        channel=code//16;state=(state&~(15<<(4*channel)))|((code&15)<<(4*channel))
        levels.append(codec.levels[state])
    return np.array(levels),state

class YMTests(unittest.TestCase):
    def test_global_solution_matches_exhaustive_search(self):
        codec=LookaheadYM(ROOT);initial_state=codec.state
        pcm=bytes([129,146]);targets=np.frombuffer(pcm,dtype=np.uint8)/255
        def neighbors(state):
            return {(state&~(15<<(4*c)))|(v<<(4*c)) for c in range(3) for v in range(16)}
        exhaustive=min((codec.levels[a]-targets[0])**2+(codec.levels[b]-targets[1])**2
                       for a in neighbors(initial_state) for b in neighbors(a))
        data,initial=codec.encode(pcm);actual,end=decode(codec,data,initial)
        self.assertAlmostEqual(float(np.sum((actual-targets)**2)),float(exhaustive),places=14)
        self.assertEqual(end,codec.state)

    def test_boundaries_and_gain(self):
        codec=LookaheadYM(ROOT);previous=codec.state
        for size in [491,492,655,656]:
            pcm=np.rint(128+80*np.sin(np.arange(size)*2*np.pi*440/12288)).astype(np.uint8)
            data,initial=codec.encode(pcm.tobytes())
            self.assertEqual(initial,codec.commands(previous))
            actual,previous=decode(codec,data,initial)
            self.assertEqual(previous,codec.state);self.assertEqual(len(data),size)
            self.assertLess(np.sqrt(np.mean((actual*255-pcm)**2)),4)

    def test_improves_quiet_signal_over_greedy(self):
        pcm=np.rint(128+16*np.sin(np.arange(491)*2*np.pi*440/12288)).astype(np.uint8)
        errors=[]
        for cls in [SingleWriteYM,LookaheadYM]:
            codec=cls(ROOT);data,initial=codec.encode(pcm.tobytes())
            actual,_=decode(codec,data,initial)
            errors.append(np.mean((actual*255-pcm)**2))
        self.assertLess(errors[1],errors[0]*.65)

if __name__=='__main__':unittest.main()
