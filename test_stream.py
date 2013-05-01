import stream_parser
import unittest


class TestStreamParser(unittest.TestCase):

    def test_creation(self):
        tests = [
            ('()-->out', [0, {}]),
            ('(11)-->out', [11, {}]),
            ('(11.11)-->out', [11.11, {}]),
            ('(5)-->out;{red, 5.5}-->out', [5, {'red': 5.5}]),
            ('(10.101)-->out;{_1_2_3_, 33.33}-->out', [10.101, {'_1_2_3_': 33.33}]),
        ]

        for line, droplet in tests:
            stream = stream_parser.StreamParser(line)
            stream.parse_line('out-1->out')
            res = stream.droplets['out'][0]
            self.assertEqual(res, droplet)

    def test_copy_over(self):
        tests = [
            ('(20, 0.08)-->out;(100)-->a;a-o->out', [100, {}]),
            ('(20, 0.08)-->out;()-->a;a-o->out', [0, {}]),
            ('(20, 0.08)-->inter;inter-s->out;(10)-->a;a-o->inter', [5, {}]),
        ]

        for line, droplet in tests:
            stream = stream_parser.StreamParser(line)
            stream.parse_line('out-1->out')
            res = stream.droplets['out'][0]
            self.assertEqual(res, droplet)


if __name__ == '__main__':
    unittest.main()
