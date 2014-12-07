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

        a = [[[string[self.w * (5 * y + x) + z] for z in range(self.w)] 
                                                for y in range(5)]
                                                for x in range(5)]
        '''
        a = [][][]
        
        for x in range(5):
            for y in range(5):
                for z in range(w):
                    a[x][y][z] = string[w*(5*y+x)+z]
        '''

        return a

    def array_to_string(self, array):
        lanes = [[''.join([array[i][j][x] for x in range(self.w)])
                                          for j in range(5)]
                                          for i in range(5)]

        planes = [''.join([lanes[i][j] for i in range(5)])
                                       for j in range(5)]

        s = ''.join([planes[i] for i in range(5)])
        
        return s

    def step_theta(self, state_array):
        C = [[reduce(lambda i, j: i^j, [state_array[x][y][z] for y in range(5)])
                                                             for x in range(5)]
                                                             for z in range(self.w)]

        D = [[C[(x-1) % 5][z] ^ C[(x+1) % 5][(z-1) % self.w] for x in range(5)]
                                                             for z in range(self.w)]

        A = [[[state_array[x][y][z] ^ D[x][z] for x in range(5)]
                                              for y in range(5)]
                                              for z in range(self.w)]

        return A

