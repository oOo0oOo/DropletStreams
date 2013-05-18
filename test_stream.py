import stream_parser
import unittest

class TestDroplets(unittest.TestCase):
    def single_droplet_test(self, tests):
        for line, droplet, amount in tests:
            # print 'Testing Line', line
            stream = stream_parser.StreamParser(line)
            res = stream.droplets['out']
            self.assertEqual(res[0], droplet)
            self.assertEqual(len(res), amount)

    def test_droplet_collection(self):

        tests = [
            ('()-->out;out-10->out', [0, {}], 10),
            ('(100)-->out;{red, 10}-->out;out-5->out', [100, {'red': 10}], 5),
            ('(10)-->out;{green, 10}-->out;out-10000->out', [10, {'green': 10}], 10000)
        ]
        self.single_droplet_test(tests)

    def test_droplet_deletion(self):

        tests = [
            ('()-->out;out-10->out;out-0->out;out-10->out', [0, {}], 10),
            ('()-->out;out-10->out;out-0->out;out-1->out', [0, {}], 1),
            ('()-->out;out-0->out;out-1->out', [0, {}], 1),
            ('()-->out;out-0->out;out-0->out;out-1->out', [0, {}], 1)
        ]
        self.single_droplet_test(tests)

    def test_droplet_append(self):
        tests = [
            ('()-->out;out-+10->out', [0, {}], 10),
            ('()-->out;out-+15->out;out-+30->out;out-+14->out', [0, {}], 59),
            ('()-->out;out-10->out;(100)-->a;a-+100->out', [0, {}], 110)
        ]
        self.single_droplet_test(tests)

class TestStreamParser(unittest.TestCase):

    def single_droplet_test(self, tests, repeats=25):
        for line, droplet in tests:
            for i in range(repeats):
                # print 'Testing: ', line
                stream = stream_parser.StreamParser(line)
                stream.parse_line('out-1->out')
                res = stream.droplets['out'][0]
                self.assertEqual(res, droplet)
                assert res, droplet

    def test_creation(self):
        tests = [
            ('()-->out', [0, {}]),
            ('(11)-->out', [11, {}]),
            ('(11.11)-->out', [11.11, {}]),
            ('(5)-->out;{red, 5.5}-->out', [5, {'red': 5.5}]),
            ('(10.101)-->out;{_1_2_3_, 33.33}-->out', [10.101, {'_1_2_3_': 33.33}])
        ]

        self.single_droplet_test(tests)

    def test_splitting(self):
        tests = [
            ('(100)-->out;out-s->out', [50, {}]),
            ('(22.22)-->out;out-s->out', [11.11, {}]),
            ('(11)-->out;{red, 5}-->out;out-s->out', [5.5, {'red': 2.5}]),
        ]

        self.single_droplet_test(tests)

    def test_merging(self):
        tests = [
            ('()-->out;()-->b;out,b-m->out', [0, {}]),
            ('(5)-->out;(10.3)-->b;out,b-m->out', [15.3, {}]),
            ('(2)-->out;(5)-->b;{red,10}-->b;out,b-m->out', [7, {'red': 10}]),
            ('(10.01)-->out;(1.01)-->b;{red,10.01}-->b;out,b-m->out', [11.02, {'red': 10.01}])
        ]

        self.single_droplet_test(tests)

    def test_combine_and_filter(self):
        tests = [
            ('()-->out;(10)-->b;{red, 10}-->b;out,b-c->out;out-(+red)->out', [10, {'red': 10}]),
            ('(10.01)-->out;(10)-->b;{red, 10}-->b;out,b-c->out;out-(-red)->out', [10.01, {}])
        ]

        self.single_droplet_test(tests)

    def test_analyze(self):
        tests = [
            ('(10)-->out;(25)-->alt;out,alt-c->out;out-100->;analyze', [10, {}])
        ]
        print 'Testing analyze, will print one analysis...'
        self.single_droplet_test(tests, 1)

    def test_copy_over(self):
        tests = [
            ('(20, 0.08)-->out;(100)-->a;a-o->out', [100, {}]),
            ('(20, 0.08)-->out;()-->a;a-o->out', [0, {}]),
            ('(20, 0.08)-->inter;inter-s->out;(10)-->a;a-o->inter', [5, {}]),
            ('()-->out;(100)-->inter;inter-o->out', [100, {}]),
            #Remove copy over tests...
            ('()-->out;(100)-->inter;inter-o->out;-!o->out', [0, {}]),
            ('(10)-->out;-!o->out', [10, {}])
        ]

        self.single_droplet_test(tests)


if __name__ == '__main__':
    unittest.main()
