"""Regression: flat intros and sparse palettes must encode without losing colors."""
import struct,unittest
import numpy as np
from PIL import Image
from encode import palette_for,quantize,unplanar
from quality import perceptual_palette

class SparsePaletteTests(unittest.TestCase):
    def test_solid_frames_round_trip(self):
        for color in [(0,0,0),(255,255,255),(255,0,0),(0,255,0),(0,0,255)]:
            with self.subTest(color=color):
                frame=Image.new('RGB',(320,200),color)
                for optimized in [False,True]:
                    palette=palette_for([frame])
                    if optimized:palette=perceptual_palette([frame],palette)
                    self.assertEqual(palette[1].shape,(16,3))
                    self.assertEqual(len(palette[2]),32)
                    for dither in ['none','ordered','floyd','adaptive']:
                        bitmap,preview=quantize(frame,*palette[:2],dither,
                            'perceptual' if optimized else 'classic')
                        self.assertEqual(len(bitmap),32000)
                        np.testing.assert_array_equal(palette[1][unplanar(bitmap)],np.asarray(preview))
                        if dither in ['none','adaptive']:
                            self.assertTrue(np.all(np.asarray(preview)==np.array(color)))

    def test_sparse_color_counts(self):
        for n in [2,3,7,15,16]:
            with self.subTest(colors=n):
                a=np.zeros((200,320,3),dtype=np.uint8)
                for i in range(n):
                    a[:,i*320//n:(i+1)*320//n]=[(i*37)%256,(i*83)%256,(i*127)%256]
                palette=palette_for([Image.fromarray(a)])
                self.assertEqual(palette[1].shape,(16,3))
                self.assertEqual(len(struct.unpack('>16H',palette[2])),16)

if __name__=='__main__':unittest.main()
