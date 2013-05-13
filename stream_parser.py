'''Parses a .streams file and returns a stream'''

import droplet_simulation as dr
import re


class StreamParser(object):

    def __init__(self, line=''):
        # Streams is a dictionary of streams saved under a value (using ->)
        # Droplets is a dictionary of lists of droplets saved under a value (using e.g. -1000->)
        self.streams = {}
        self.droplets = {}
        self.snippets = {}

        self.patterns = [
            (r'\(([\d,.]*)\)\-\->(\w*)', 'CREATE_STREAM'),
            (r'{([\w,.]+)}\-\->(\w*)', 'ADD_CONTENT'),
            (r'(\w*)\-\->(\w*)', 'COPY'),

            (r'(\w*)\-(\d+)\->(\w*)', 'SAMPLE'),
            (r'(\w*)\-\+(\d+)\->(\w*)', 'APPEND'),
            (r'(\w*)\-s\->(\w*)', 'SPLIT'),
            (r'(\w*)\-o\->(\w*)', 'COPY_OVER'),
            (r'\-!o\->(\w*)', 'RESTORE_COPY'),

            (r'(\w*),(\w+)\-m\->(\w*)', 'MERGE'),
            (r'(\w*),(\w+)\-c\->(\w*)', 'COMBINE'),

            (r'(\w*)\-\(\+([\w,]+)\)\->(\w*)', 'PRESENCE_FILTER'),
            (r'(\w*)\-\(\-([\w,]+)\)\->(\w*)', 'ABSENCE_FILTER'),

            (r'([\w,]*)\-b(\d*)\->(\w*)', 'MULTI_BUFFER'),
            (r'(\w*)\-\((\w*)\)\->(\w*)', 'MONITOR'),

            # These commands are more intended for interactive use
            (r'plot(\w*)', 'PLOT'),
            (r'show(\w*)', 'SHOW'),
            (r'unique(\w*)', 'UNIQUE'),
            (r'analyze(\w*)', 'ANALYZE'),
            (r'hist(\d+),(\w*)', 'HISTOGRAM'),

            # Repeated snippet execution with combinations of streams copied on streams
            #(r'>>(\w+):([\w,]*)\-\->([\w,]*)', 'COMBINATIONS'),

            #!! Save is to save droplets while load is to load scripts
            (r'csv(\w*),(\w+)', 'SAVE'),
            # Load (if second argument is given: load into snippet)
            (r'(\w+)>(\w*)', 'LOAD'),

            # Snippets have lowest precedence
            (r'(\w+)', 'SNIPPET')

        ]

        if line:
            self.parse_line(line)

    def read_parse_loop(self, prompt='Stream> '):
        "A prompt-read-parse_line loop."
        print 'DropletStreams Interactive Session\nEnd session using quit or exit.\n'
        while True:
            inp = raw_input(prompt)
            if inp == 'clear':
                del self.streams
                del self.droplets
                self.streams = {}
                self.droplets = {}

            elif inp not in ('quit', 'exit'):
                self.parse_line(inp)
                '''
                try:
                    self.parse_line(inp)
                except Exception, e:
                    print 'Encountered Error:\n', repr(e)
                '''
            else:
                break

    def load_file(self, filename):
        f = open(filename, 'rb')

        # Each line
        print 'Executing script ' + filename

        try:
            for l in f.readlines():
                self.parse_line(l)
        finally:
            f.close()

    def parse_line(self, orig_line):
        # Remove whitespace
        lines = orig_line.replace(' ', '')

        # Comment whole line
        # if orig_line[0] == '#':
        #    print 'comment'
        #    return

        # Split line into seperate lines marked by ;
        lines = lines.split(';')

        # Check first statement of line for special actions
        start_patterns = [
            (r'loop(\d+)', 'LOOP'),
            (r'>(\w+)', 'SNIPPET')
        ]

        loop = 1
        for pattern, tag in start_patterns:
            regex = re.compile(pattern)
            match = regex.match(lines[0])

            if match:
                lines.pop(0)
                found = match.groups(0)[0]
                if tag == 'LOOP':
                    loop = int(found)
                elif tag == 'SNIPPET':
                    loop = 0
                    self.snippets[found] = ';'.join(lines)
                break

        for i in range(loop):
            for line in lines:
                if len(line) == 0:
                    continue
                elif line[0] == '#':
                    break

                for pattern, tag in self.patterns:
                    regex = re.compile(pattern)
                    match = regex.match(line)
                    if match:
                        found = match.groups(0)
                        if tag == 'CREATE_STREAM':
                            print 'found', found
                            origin, target = found
                            params = origin.strip().split(',')

                            if params == ['']:
                                volume = 0
                            else:
                                volume = float(params[0])

                            if len(params) == 2:
                                volume_sigma = float(params[1])
                            else:
                                volume_sigma = 0.0

                            if target == '':
                                target = 'current'

                            print tag, volume, volume_sigma, target
                            self.streams[target] = dr.Stream(volume=volume, volume_sigma=volume_sigma)

                        elif tag == 'ADD_CONTENT':
                            params, target = found
                            params = params.strip().split(',')
                            if len(params) == 3:
                                content, value, sigma = params
                                sigma = float(sigma)
                            else:
                                content, value = params
                                sigma = 0.0

                            if target == '':
                                target = 'current'
                            
                            print tag, content, value, target
                            self.streams[target].add_content(content, float(value))
                            #original_stream = self.streams[target]
                            #new_stream = dr.stream({content: float(value)}, 0, content_sigma=sigma)

                            #self.streams[target] = dr.merge(original_stream, new_stream)

                        elif tag in ('SAMPLE', 'APPEND'):
                            orig, num, target = found

                            if not target:
                                target = 'current'
                            if not orig:
                                orig = 'current'

                            droplets = dr.sample(self.streams[orig], int(num))
                            if tag == 'SAMPLE':
                                self.droplets[target] = droplets
                            elif tag == 'APPEND':
                                self.droplets[target] += droplets

                        elif tag in ('SPLIT', 'COPY_OVER'):
                            orig, target = found

                            if target == '':
                                target = 'current'
                            if orig == '':
                                orig = 'current'

                            if tag == 'SPLIT':
                                self.streams[target] = dr.split(self.streams[orig])
                            else:
                                try:
                                    self.streams[target].copy_over(self.streams[orig])
                                except AttributeError:
                                    print 'Only stream sources can be overwritten.'

                        elif tag in ('MERGE', 'COMBINE'):
                            orig1, orig2, target = found

                            if target == '':
                                target = 'current'
                            if orig1 == '':
                                orig1 = 'current'

                            if tag == 'MERGE':
                                self.streams[target] = dr.merge(self.streams[orig1], self.streams[orig2])

                            elif tag == 'COMBINE':
                                self.streams[target] = dr.combine(self.streams[orig1], self.streams[orig2])

                        elif tag in ('PRESENCE_FILTER', 'ABSENCE_FILTER'):
                            orig, contents, target = found
                            contents = contents.split(',')

                            if target == '':
                                target = 'current'
                            if orig == '':
                                orig = 'current'

                            if tag == 'PRESENCE_FILTER':
                                func = dr.presence_filter(contents)
                            else:
                                func = dr.absence_filter(contents)

                            self.streams[target] = dr.filter_stream(self.streams[orig], func)

                        elif tag == 'MULTI_BUFFER':
                            orig, capacity, target = found

                            if capacity == '':
                                capacity = 0
                            else:
                                capacity = int(capacity)

                            # assemble streams
                            streams = []
                            for o in orig.split(','):
                                if o == '':
                                    o = 'current'
                                streams.append(self.streams[o])

                            if target == '':
                                target = 'current'

                            self.streams[target] = dr.multi_buffer(streams, capacity)

                        elif tag == 'COMBINATIONS':
                            snippet, orig, target = found

                            origs = orig.split(',')
                            targets = target.split(',')

                            for i, name in enumerate(origs):
                                if name == '': origs[i] = 'current'

                            for i, name in enumerate(targets):
                                if name == '': targets[i] = 'current'


                        elif tag == 'MONITOR':
                            orig, name, target = found

                            if not orig:
                                orig = 'current'
                            if not target:
                                target = 'current'

                            self.streams[target] = dr.droplet_monitor(self.streams[orig], name)

                        elif tag == 'RESTORE_COPY':
                            orig = found[0]
                            if not orig:
                                orig = 'current'

                            self.streams[orig].copy_over()

                        elif tag == 'PLOT':
                            orig = found[0]
                            if orig == '':
                                orig = 'current'

                            try:
                                dr.extract_data(self.droplets[orig], plot=True)
                            except KeyError:
                                raise RuntimeError('Could not find droplets: ' + orig)

                        elif tag == 'ANALYZE':
                            orig = found[0]
                            if not orig:
                                orig = 'current'

                            dr.analyze(self.droplets[orig])

                        elif tag == 'SAVE':
                            orig, filename = found
                            if not orig:
                                orig = 'current'
                            filename += '.csv'

                            dr.save_droplets(self.droplets[orig], filename)

                        elif tag == 'LOAD':
                            filename, snippet = found
                            try:
                                filename.index('.streams')
                            except ValueError:
                                filename += '.streams'

                            if not snippet:
                                # Execute file
                                self.load_file(filename)
                            else:
                                # Save file as snippet
                                f = open(filename, 'rb')
                                try:
                                    script = ''.join([l for l in f.read()])
                                    self.snippets[snippet] = script
                                finally:
                                    f.close()

                        elif tag == 'COPY':
                            orig, target = found

                            if not orig:
                                orig = 'current'
                            if not target:
                                target = 'current'

                            if not orig == target:
                                self.streams[target] = dr.copy_stream(self.streams[orig])

                        elif tag == 'SHOW':
                            orig = found[0]

                            if not orig:
                                orig = 'current'

                            repl = []

                            if orig in self.streams.keys():
                                repl.append('Stream {}: {}'.format(orig, self.streams[orig]))

                            if orig in self.droplets.keys():
                                d = self.droplets[orig]
                                disp = '\n'.join(map(lambda x: 'Vol: {}, Cont: {}'.format(x[0], x[1]), d))

                                repl.append('Droplets {}, amount: {}\n{}'.format(orig, len(d), disp))

                            if orig in self.snippets.keys():
                                repl.append('Snippet {}:\n{}'.format(orig, self.snippets[orig]))

                            if not repl:
                                repl.append('Could not find {} in streams or droplets.'.format(orig))

                            print '\n\n'.join(repl)

                        elif tag == 'UNIQUE':
                            orig = found[0]
                            if not orig:
                                orig = 'current'

                            dr.unique_droplets(self.droplets[orig])

                        elif tag == 'HISTOGRAM':
                            bins, orig = found

                            if not orig:
                                orig = 'current'

                            if orig in self.droplets.keys():
                                dr.histogram(self.droplets[orig], int(bins))

                        elif tag == 'SNIPPET':
                            snip = found[0]
                            try:
                                snippet = self.snippets[snip]
                                for l in snippet.split('\n'):
                                    self.parse_line(l)
                            except KeyError:
                                pass

                        # end pattern search after first match
                        break


if __name__ == '__main__':
    s = StreamParser()
    s.read_parse_loop()
