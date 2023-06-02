import json
import hmac
import numpy as np
import random
from hashlib import sha512

'''
Computational Fuzzy Extractors - https://github.com/benjaminfuller/CompFE
Copyright 2018 Benjamin Fuller and Sailesh Simhadri
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

class FuzzyExtractor:

    def __init__(self, hash=sha512):
        self.hash = hash

    def gen_config(self, real, bits, config):
        with open(config, "r") as f:
            c = json.load(f)
        c['confidence']['reals'] = real
        return self.gen(bits, c['locker_size'], c['lockers'], c['confidence'])

    def parse_config(self, config, real):
        with open(config, "r") as f:
            c = json.load(f)
        c['confidence']['reals'] = real
        return c['confidence']

    def gen(self, bits, locker_size=43, lockers=1000000, confidence=None):
        length = self.hash().digest_size

        rand_len = int(length/2)
        pad_len = length-rand_len
        r = self.generate_sample(size=rand_len)
        zeros = bytearray([0 for x in range(pad_len)])
        check = zeros + r
        seeds = self.generate_sample(length=lockers, size=16)
        if confidence is None:
            pick_range = range(0, len(bits)-1)
        else:
            pick_range = self.confidence_range(
                confidence, list(range(0, len(bits)-1)))
            print(len(pick_range))
            if(len(pick_range) < 1024):
                return "Confidence range too small"
        positions = np.array([random.SystemRandom().sample(
            pick_range, locker_size) for x in range(lockers)])
        p = []
        for x in range(lockers):
            v_i = np.array([bits[y] for y in positions[x]])
            seed = seeds[x]
            h = bytearray(hmac.new(seed, v_i, self.hash).digest())
            c_i = self.xor(check, h)
            p.append((c_i, positions[x], seed))
        return r, p


    def confidence_range(self, confidence, bits):
        indices = []
        for x in range(len(confidence['reals'])):
            r = confidence['reals'][x]
            if not (confidence['positive_start'] < r < confidence['positive_end']) or (
                    confidence['negative_start'] > r > confidence['negative_end']):
                indices.append(x)
        return np.delete(bits, indices)

    def rep(self, bits, p):
        for c_i, positions, seed in p:
            v_i = np.array([bits[x] for x in positions])
            h = bytearray(hmac.new(seed, v_i, self.hash).digest())
            res = self.xor(c_i, h)
            if self.check_result(res):
                key_len = int(len(res)/2)
                return res[key_len:]
        return None


    def check_result(self, res):
        pad_len = int(len(res)-len(res)/2)
        return all(v == 0 for v in res[:pad_len])


    def xor(self, b1, b2):
        return bytearray([x ^ y for x, y in zip(b1, b2)])


    def generate_sample(self, length=0, size=32):
        rand_gen = random.SystemRandom()
        if length == 0:
            return bytearray([rand_gen.randint(0, 255) for _ in range(int(size))])
        else:
            samples = []
            for x in range(length):
                samples.append(
                    bytearray([rand_gen.randint(0, 255) for _ in range(int(size))]))
            return samples