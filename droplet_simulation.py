import random
import math
import csv
import itertools as it
from collections import defaultdict, Counter

class Stream(object):
    '''A Stream acts as a source for droplets.'''

    def __init__(self, volume, volume_sigma, content, content_sigma):
        self.content = content
        self.volume = volume
        self.volume_sigma = volume_sigma
        self.content_sigma = content_sigma
        self.copied = False
        self.stream = False

    def __iter__(self):
        return self

    def next(self):
        '''
        When the next method is called, a new droplet is generated and returned where
        
        droplet = [volume, content]
        content = {'molecule_name1': amount, 'molecule_name2': amount2, ...}

        1 > *_sigma > 0; If > 0 droplets will have a variation according to a normal distribution:

        E.g. droplet_volume = NormalDistribution(u = volume, sigma = volume * volume_sigma)

        content_sigma is global for all contents in a droplet.
        '''
        if not self.copied:
            vol = random.gauss(self.volume, self.volume_sigma * self.volume)
            if self.content_sigma == 0:
                cont = self.content.copy()
            else:
                cont = {}
                for mol, amount in self.content.items():
                    cont[mol] = random.gauss(amount, self.content_sigma * amount)
            return list([vol, cont])
        else:
            return self.stream.next()

    def add_content(self, molecule, amount):
        '''Add content to the stream. All requested droplets will contain this content.'''
        if molecule in self.content.keys():
            self.content[molecule] += amount
        else:
            self.content[molecule] = amount

    def copy_over(self, target_stream=False):
        '''
        Copy over with another stream.
        Stream will ignore its preset parameters and each time the next
        method is called it will instead request a droplet from the provided target_stream. 
        '''
        if not target_stream:
            self.copied = False
            self.stream = False
        else:
            self.copied = True
            self.stream = target_stream


### A SET OF FUNCTIONS (MOST OF THEM ARE GENERATORS) TO WORK WITH STREAMS

def combine(*streams):
    '''samples alternatingly from n streams'''
    num = len(streams)
    cur = 0
    while 1:
        yield streams[cur].next()
        cur = (cur + 1)%num 


def combine_ratio(stream1, stream2, ratio):
    '''Chooses randomly from two streams according to ratio.'''
    if not 0 <= ratio <= 1:
        raise RuntimeError('Ratio has to be between 0 and 1!')
    while 1:
        if random.random() >= ratio:
            yield stream1.next()
        else:
            yield stream2.next()


def merge(*streams):
    '''Merge one droplet from each stream into a single (bigger) droplet'''
    while 1:
        droplets = [s.next() for s in streams]
        volume = reduce(lambda x, y: x+y, [d[0] for d in droplets])
        content = defaultdict(int)
        for c in [d[1] for d in droplets]:
            for m, a in c.items():
                content[m] += a

        yield [volume, dict(content)]


def split(stream, num_progenitors = 2):
    '''Split droplets of stream in n equal droplets (volume & content)'''
    while 1:
        droplet = stream.next()
        new_volume = float(droplet[0]) / num_progenitors
        content = {}
        for c_id in droplet[1].keys():
            new_amount = float(droplet[1][c_id]) / num_progenitors
            content[c_id] = new_amount

        # a split always leads to only one droplet
        for i in range(2):
            yield [new_volume, content.copy()]


def reduce_stream(stream, discart_ratio=0.5):
    '''randomly discarts percentage of droplets'''
    while 1:
        while random.random < discart_ratio:
            stream.next()
        yield stream.next()


def stream_buffer(stream, capacity=10):
    '''Set up a buffer from which droplets are randomly sampled.'''

    # picks a random droplet from the buffered droplets
    # Fill buffer
    buff = []
    for i in range(capacity):
        buff.append(stream.next())

    while 1:
        droplet = random.choice(buff)
        yield droplet
        buff.remove(droplet)
        buff.append(stream.next())


def copy_stream(stream):
    '''Copy a stream'''
    while 1:
        yield stream.next()


def sample(stream, num_samples=100):
    '''Sample a number of droplets from the stream.'''
    sampled = []
    for i in range(num_samples):
        sampled.append(stream.next())

    return sampled


def save_droplets(droplets, filename='droplets.csv'):
    # Get all involved contents (dyes)
    list_dyes = [content.keys() for v, content in droplets]
    list_dyes = it.chain.from_iterable(list_dyes)
    list_dyes = list(set(list_dyes))

    # Save to csv
    f = open(filename, 'wt')
    try:
        writer = csv.writer(f, delimiter='\t')
        # set titles of columns
        row = ['Volume'] + list_dyes
        writer.writerow(tuple(row))

        for volume, content in droplets:
            templ = [volume] + [0] * len(list_dyes)
            # write data in column
            for mol, am in content.items():
                ind = list_dyes.index(mol)
                templ[ind+1] = am

            writer.writerow(tuple(templ))

    finally:
        f.close()


def filter_stream(stream, func, tries=500):
    '''filter stream using a filter function (returns True if passes filter).'''
    while 1:
        found = False
        for i in range(tries):
            droplet = stream.next()
            if func(droplet):
                found = True
                yield droplet
                break

        if not found:
            raise RuntimeError("Filter couldn't find droplet after {0} tries.".format(tries))

        yield droplet

def multi_buffer(streams, capacity):
    '''buffer from multiple input streams with a set capacity'''
    # Combine all streams
    combined = combine(*streams)

    #Prefill buffer
    buff = []
    while len(buff) < capacity:
        buff.append(combined.next())
    
    #Normal operation
    while 1:
        droplet = random.choice(buff)
        yield droplet
        buff.remove(droplet)
        buff.append(combined.next())


def droplet_monitor(stream, name=''):
    header = 'Monitor'
    if name:
        header += ' ' + name
    header += ':\n'

    while 1:
        droplet = stream.next()
        volume, content = droplet
        disp = 'Volume: {}, '.format(round(volume, 3))
        if content:
            c = map(lambda cont: '{}: {}'.format(cont[0], round(cont[1], 3)), content.items())
            disp += ', '.join(c)
        else:
            disp += 'no content'

        print header + disp
        yield droplet


def hashify(droplets):
    d = []
    for vol, content in droplets:
        c = []
        for mol, am in content.items():
            c.append((mol, am))
        d.append((vol, tuple(c)))
    return d


def unique_droplets(droplets):
    d = hashify(droplets)
    unique = len(set(d))
    d_len = len(droplets)
    print '{}% unique droplets ({}/{})'.format(round(100.0*unique/d_len, 3), unique, d_len)


def calculate_stdev(q):
    '''Simple stdev...'''
    avg = float(sum(q))/len(q)
    sqr = [dev ** 2 for dev in [x-avg for x in q]]
    standard_dev = math.sqrt(sum(sqr)/(len(sqr)-1))
    return standard_dev


def extract_data(droplets, plot=False):
    '''Create n-dimensional vectors, returned as a list
    of lists; n = number unique of dyes in all droplets'''

    # Get all involved contents (dyes)
    dyes = it.chain.from_iterable([c.keys() for _, c in droplets])
    dyes = list(set(dyes))

    ret = defaultdict(list)
    for v, cont in droplets:
        for dye in dyes:
            try:
                d = cont[dye]/float(v)
            except KeyError:
                d = 0

            ret[dye].append(d)

    data = dict(ret)
    if plot:
        while len(data) < 3:
            new_key = random.random()
            data[new_key] = [0] * len(droplets)

        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        # Plot in scatterplot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        plt.title('Scatter plot of {0} droplets'.format(len(droplets)))
        k = data.keys()[:3]
        ax.scatter(data[k[0]], data[k[1]], data[k[2]],
                   c='b', s=1, marker='.')
        plt.show()

    return data


def analyze(droplets, print_stuff = True):
    dyes = it.chain.from_iterable([c.keys() for _, c in droplets])
    dyes = list(set(dyes))
    all_print = ['All dyes in droplets:', ', '.join(dyes)]

    total_droplets = len(droplets)

    d = hashify(droplets)
    c = Counter(d)
    num = 10
    if len(c) < 10:
        num = len(c)
    else:
        all_print.append('Showing 10 most common droplets')

    for drop, occ in c.items()[:num]:
        perc = round(100.0 * occ / total_droplets, 2)
        all_print.append('{} times ({}%): {}'.format(occ, perc, drop))

    if print_stuff:
        print '\n'.join(all_print)


def histogram(droplets, bins=5):
    '''Plot histogram of each droplet type.'''
    import matplotlib.pyplot as plt

    data = extract_data(droplets, False)
    if data:
        for k, v in data.items():
            fig = plt.figure()
            plt.title('Histogram for %s' % (k))
            plt.hist(v, bins)

        plt.show()


# Some general filters for use with filter_stream (as second argument)

def presence_filter(molecules):
    '''Use this filter to extract all droplets containing all mentioned molecules.'''
    def func(droplet):
        k = droplet[1].keys()
        if all([mol in k for mol in molecules]):
            return True
        else:
            return False

    return func


def absence_filter(molecules):
    '''Use this filter to extract all droplets not containing all mentioned molecules.'''

    def func(droplet):
        if any(mol in droplet[1].keys() for mol in molecules):
            return False
        else:
            return True

    return func
