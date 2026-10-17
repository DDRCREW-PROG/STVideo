"""Profile-to-encoder integration: verify the settings actually sent to the worker."""
import sys,unittest,tkinter as tk
from pathlib import Path
from encoder_ui import EncoderApp
from translations import EN

class Profiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved=sys.argv[:];sys.argv=[sys.argv[0]]
        cls.root=tk.Tk();cls.root.withdraw();cls.ui=EncoderApp(cls.root)
        cls.ui.source.set('clip.mp4')

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy();sys.argv=cls.saved

    def options(self,preview=False):
        args=self.ui.arguments(preview)
        return {a:args[i+1] for i,a in enumerate(args[:-1]) if a.startswith('--') and not args[i+1].startswith('--')}

    def test_stf_profile_sends_verified_settings(self):
        self.ui.preset('stf');options=self.options()
        self.assertEqual(options['--stf-fps'],'12.5')
        self.assertEqual(options['--dither'],'ordered')
        self.assertEqual(options['--quality'],'perceptual')
        self.assertEqual(options['--audio-codec'],'optimal')

    def test_ste_profile_preserves_dma_format(self):
        self.ui.preset('ste');options=self.options()
        self.assertEqual(options['--audio-codec'],'classic')
        self.assertEqual(options['--stf-fps'],'25')

    def test_preview_is_separate_and_five_seconds(self):
        self.ui.preset('stf');self.ui.duration.set('90')
        options=self.options(True)
        self.assertEqual(options['--duration'],'5')
        self.assertEqual(self.ui.active_output.name,'APERCU')
        self.ui.duration.set('')

    def test_invalid_time_does_not_start_worker(self):
        self.ui.start.set('-1')
        with self.assertRaises(ValueError):self.ui.arguments(False)
        self.ui.start.set('0')

    def test_language_switch_preserves_encoding_settings(self):
        self.ui.set_language('fr',persist=False);self.ui.preset('stf')
        self.ui.clip_name.set('ESSAI');self.ui.fps.set('25')
        before=self.ui.arguments(False)
        self.ui.set_language('en',persist=False)
        after=self.ui.arguments(False)
        expected=before[:];expected[expected.index('--language')+1]='en'
        self.assertEqual(after,expected)
        self.assertEqual(self.ui.clip_name.get(),'ESSAI')
        self.assertEqual(self.ui.book.tab(0,'text').strip(),'Encoding')
        self.assertIn('David Ascenso',self.ui.about_view.get('1.0','end'))
        self.assertIn('GETTING STARTED',self.ui.guide_view.get('1.0','end'))
        self.ui.set_language('fr',persist=False)

    def test_english_preset_sends_same_codec(self):
        self.ui.set_language('en',persist=False);self.ui.preset('stf')
        self.assertEqual(self.options()['--audio-codec'],'optimal')
        self.assertEqual(self.ui.audio_codec.get(),'Optimised STF audio (slower encoding)')
        self.ui.set_language('fr',persist=False)

    def test_all_static_labels_have_english_translation(self):
        for _,original in self.ui.static_texts:
            if original not in ('ST Vidéo','Langue / Language'):
                self.assertIn(original,EN)

if __name__=='__main__':unittest.main()
