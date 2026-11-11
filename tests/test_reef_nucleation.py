"""Fast regression tests; no expedition rerun. unittest or pytest compatible."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

spec=importlib.util.spec_from_file_location('nucleation',Path(__file__).resolve().parents[1] / 'research/experiments/REEF-nucleation/run.py')
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)

class NucleationTests(unittest.TestCase):
    def test_historical_pairs_exact(self):
        s,_=m.initial('ring')
        for dose,old in [('0.5','X11'),('0.75','X12'),('1','X9')]:
            a,_=m.initial('A'+dose); e,_=m.initial('contact'+dose)
            original,meta=m.seed('BLOB-'+old)
            shift=128-np.rint(meta['construction']['centre_yx']).astype(int)
            np.testing.assert_array_equal(a,np.roll(original,shift,(0,1)))
            np.testing.assert_array_equal(e,a+s)
            self.assertLessEqual(e.max(),1)
    def test_no_clipping_and_dose_span(self):
        for name in m.conditions():
            a,_=m.initial(name)
            self.assertGreaterEqual(a.min(),0); self.assertLessEqual(a.max(),1)
            self.assertFalse(m.guarded(a))
        a,_=m.initial('B16'); self.assertGreater(a.sum()/169,7.7)
        self.assertLess(a.sum()/169,7.9)
    def test_padding_preserves_input(self):
        for name in ['A0.75','B16','contact0.75']:
            a,c=m.initial(name); b,d=m.initial(name,512)
            np.testing.assert_array_equal(a,b[128:384,128:384])
            np.testing.assert_array_equal(c+128,d)
            self.assertEqual(a.sum(),b.sum())
    def test_boundary_guard(self):
        a=np.zeros((256,256)); a[12,128]=1e-11
        self.assertTrue(m.guarded(a)); a[12,128]=1e-13
        self.assertFalse(m.guarded(a))
    def rows(self,mass=1,radius=1,bodies=1):
        return [dict(time=t,mass=mass,radius=radius,bodies=bodies) for t in range(26)]
    def test_evaporation(self):
        self.assertEqual(m.classify(self.rows(0,0,0)),'EVAPORATION')
    def test_stable(self):
        self.assertEqual(m.classify(self.rows()),'STABLE_LOCALIZED')
    def test_colony_requires_spread_and_topology(self):
        rows=self.rows()
        for r in rows[1:]: r.update(mass=4+r['time'],radius=1+r['time']*.2,bodies=5)
        self.assertEqual(m.classify(rows),'EXPANDING_COLONY')
        for r in rows:r['bodies']=1
        self.assertEqual(m.classify(rows),'SUSTAINED_GROWTH')
    def test_transients_and_short_windows_unresolved(self):
        rows=self.rows(); rows[-1]['mass']=5
        self.assertEqual(m.classify(rows),'UNRESOLVED')
        self.assertEqual(m.classify(self.rows()[:10]),'UNRESOLVED')
    def test_blank_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            result=m.run_one('blank',Path(d)/'blank',256,10,'alm',10)
            self.assertEqual(result['outcome'],'EVAPORATION')
            self.assertEqual(result['initial_sha256'],result['final_sha256'])
            self.assertEqual(result['scored_through'],10)
    def test_arithmetic_small_step(self):
        from alm.lenia import Lenia, Rule
        from alm_check.lenia import World, Rule as CR
        a=np.zeros((64,64)); a[25:35,25:35]=.6
        x=Lenia(Rule(mu=.155,sigma=.020),a)
        y=World(a.copy(),CR(mu=.155,sigma=.020),path='direct')
        for _ in range(3):x.step();y.step()
        np.testing.assert_allclose(x.A,y.A,atol=1e-13,rtol=0)

if __name__=='__main__':unittest.main()
