# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from dnet import Network, ConfigSet
import unittest

class TestNetwork(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_tutorial(self):
        nw = Network('data/test.yaml')
        self.assertTrue(isinstance(nw, Network))

        self.assertEqual(len(nw.nodes), 37)
        self.assertEqual(nw.nodes[0], ['section_-001', 'section_0302', 'section_0303'])
        self.assertEqual(len(nw.switches), 16)
        self.assertEqual(len(nw.sections), 25)
        self.assertEqual(len(nw.sections['section_1068']['load']), 3)
        self.assertAlmostEqual(nw.sections['section_1068']['load'][0], 23.87780659+4.33926456j, 3)
        self.assertEqual(len(nw.sections['section_1068']['impedance']), 3)
        self.assertAlmostEqual(nw.sections['section_1068']['impedance'][0], 0.1539000+0.4512584j, 3)
        self.assertFalse(nw.sections['section_1068']['substation'])

        self.assertEqual(len(nw._switch2edge), 16)
        self.assertEqual(nw._switch2edge['switch_0001'], (1, 2))
        self.assertEqual(len(nw._edge2switch), 16)
        self.assertEqual(nw._edge2switch[(1, 2)], 'switch_0001')
        self.assertEqual(nw._root_vertices, set([1, 10, 13]))

        configs = nw.enumerate()
        self.assertTrue(isinstance(configs, ConfigSet))
        self.assertEqual(len(configs), 111)
        self.assertEqual(configs.len(), 111)

        configs_w2_wo3 = configs.including('switch_0002').excluding('switch_0003')
        self.assertEqual(len(configs_w2_wo3), 15)

        for config in configs_w2_wo3:
            self.assertTrue(isinstance(config, list))

        i = 1
        sum = 0.0
        for config in configs_w2_wo3.rand_iter():
            sum += nw.loss(config)
            if i == 5:
                break
            i += 1
        self.assertAlmostEqual(sum / 5, 83014.1, 0)

        optimal_config = nw.optimize(configs)
        self.assertEqual(optimal_config,
                         ['switch_0001', 'switch_0002', 'switch_0003',
                          'switch_0005', 'switch_0006', 'switch_0008',
                          'switch_0009', 'switch_0010', 'switch_0011',
                          'switch_0013', 'switch_0014', 'switch_0016'])
        self.assertEqual(len(nw._search_space.edges()), 10)
        self.assertAlmostEqual(nw._search_space['38']['T']['weight'], 227.255, 3)

        results = nw.loss(optimal_config, details=True)
        self.assertAlmostEqual(results['loss'], 69734.3, 0)
        self.assertAlmostEqual(results['lower bound'], 67028.8, 0)
#        self.assertAlmostEqual(results['root sections'], 23605.8, 0)
        self.assertEqual(results['open switches'],
                         ['switch_0004', 'switch_0007', 'switch_0012',
                          'switch_0015'])

    def test_fukui_tepco(self):
        nw = Network('data/test-fukui-tepco', format='fukui-tepco')

        configs = nw.enumerate()
        self.assertEqual(len(configs), 111)        

        config = nw.optimize(configs)
        self.assertEqual(config,
                         ['switch_0003', 'switch_0007', 'switch_0295',
                          'switch_0297', 'switch_0301', 'switch_0304',
                          'switch_0308', 'switch_1056', 'switch_1060',
                          'switch_1064', 'switch_1065', 'switch_1067'])

        results = nw.loss(config, details=True)
        self.assertAlmostEqual(results['loss'], 69734.3, 0)
        self.assertEqual(results['open switches'],
                         ['switch_0005', 'switch_0306', 'switch_1058',
                          'switch_1069'])


if __name__ == '__main__':
    unittest.main()
