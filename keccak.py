''' SHA-3 implementation based on the NIST standard FIPS 202
http://csrc.nist.gov/publications/drafts/fips-202/fips_202_draft.pdf
'''

import math

class Keccak:
    width_values = [25, 50, 100, 200, 400, 800, 1600]

    def __init__(self, b=1600):
        if b in width_values:
            self.b = b
            self.w = b // 25
            self.l = int(math.log(self.w, 2))

    def string_to_array(self, string):
        a = [][][]
        
        for x in range(5):
            for y in range(5):
                for z in range(w):
                    a[x][y][z] = string[w*(5*y+x)+z]

        return a

    def array_to_string(self, array):
        s = ''



