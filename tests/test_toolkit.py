import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import workflow
import prepare_demo

class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'study'
    def test_init_does_not_overwrite(self):
        workflow.initialize(self.path)
        with self.assertRaises(ValueError): workflow.initialize(self.path)
    def test_missing_evidence_blocks_approval(self):
        workflow.initialize(self.path)
        with self.assertRaises(ValueError): workflow.decide(self.path, 'approved', 'human', 'reviewed')
        self.assertEqual(workflow.current(workflow.load(self.path))['id'], 'question')
    def test_approval_advances_and_detects_changed_evidence(self):
        workflow.initialize(self.path)
        for name in ['brief.md','review.md']:
            (self.path/'question'/name).write_text('Test evidence with review observations')
        state = workflow.decide(self.path,'approved','human','checked')
        self.assertEqual(workflow.current(state)['id'],'literature')
        (self.path/'question'/'brief.md').write_text('changed')
        with self.assertRaises(ValueError): workflow.load(self.path)
    def test_revision_stays_and_rejection_stops(self):
        workflow.initialize(self.path)
        state = workflow.decide(self.path,'revision_required','human','clarify question')
        self.assertEqual(workflow.current(state)['id'],'question')
        workflow.decide(self.path,'rejected','human','unsupported design')
        with self.assertRaises(ValueError): workflow.decide(self.path,'approved','human','retry')
    def test_demo_is_deterministic(self):
        a = prepare_demo.generate(self.path)
        b = prepare_demo.generate(Path(self.tmp.name)/'second')
        self.assertEqual(a,b)
        manifest=json.loads((self.path/'manifest.json').read_text())
        self.assertTrue(manifest['synthetic'])
        self.assertEqual(manifest['flow_count'],4)
    def test_demo_preserves_existing_files(self):
        prepare_demo.generate(self.path)
        with self.assertRaises(ValueError): prepare_demo.generate(self.path)
    def test_unmatched_flow_rejected(self):
        with self.assertRaises(ValueError): prepare_demo.features(prepare_demo.CITIES,[('A','Z',1)])
    def test_invalid_coordinates_rejected(self):
        for lon in (181,float('nan')):
            with self.assertRaises(ValueError): prepare_demo.features([dict(id='A',lon=lon,lat=0)],[])
    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError): prepare_demo.features(prepare_demo.CITIES*2,[])
    def test_antimeridian_rejected(self):
        with self.assertRaises(ValueError):
            prepare_demo.features([dict(id='A',lon=179,lat=0),dict(id='B',lon=-179,lat=0)],[('A','B',1)])

if __name__ == '__main__': unittest.main()
