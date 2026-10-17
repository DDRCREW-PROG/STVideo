"""Regression: a new encode must never reuse an existing clip's outputs."""
from pathlib import Path
import tempfile,unittest
from encode import reserve_name

class OutputNamesTests(unittest.TestCase):
    def test_existing_video_and_audio_are_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            (folder/'VIDEO.STV').write_bytes(b'keep original')
            (folder/'VIDEO001-AUDIO12288.WAV').write_bytes(b'keep partial encode')
            name,lock=reserve_name(folder,'VIDEO')
            self.assertEqual(name,'VIDEO002')
            self.assertEqual((folder/'VIDEO.STV').read_bytes(),b'keep original')
            lock.unlink()

    def test_custom_names_and_active_encodes(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            first,l1=reserve_name(folder,'monclip')
            second,l2=reserve_name(folder,'monclip')
            self.assertEqual((first,second),('MONCLIP','MONCL001'))
            self.assertLessEqual(len(second),8)
            l1.unlink();l2.unlink()

    def test_invalid_name_does_not_create_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            for name in ['../bad','TOO_LONG_NAME','CON']:
                with self.assertRaises(ValueError):reserve_name(folder,name)
            self.assertEqual(list(folder.iterdir()),[])

if __name__=='__main__':unittest.main()
