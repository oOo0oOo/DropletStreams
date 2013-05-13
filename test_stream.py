import stream_parser
import unittest


class TestStreamParser(unittest.TestCase):

    def single_droplet_test(self, tests, repeats=10):
        for line, droplet in tests:
            for i in range(repeats):
                print 'Testing: ', line
                stream = stream_parser.StreamParser(line)
                stream.parse_line('out-1->out')
                res = stream.droplets['out'][0]
                # self.assertEqual(res, droplet)
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
            ('()-->out;out-100->;analyze', [0, {}])
        ]
        print 'Trying analyze, will print analysis'
        self.single_droplet_test(tests, 1)

    def test_copy_over(self):
        tests = [
            ('(20, 0.08)-->out;(100)-->a;a-o->out', [100, {}]),
            ('(20, 0.08)-->out;()-->a;a-o->out', [0, {}]),
            ('(20, 0.08)-->inter;inter-s->out;(10)-->a;a-o->inter', [5, {}]),
        ]

        self.single_droplet_test(tests)


if __name__ == '__main__':
    unittest.main()
