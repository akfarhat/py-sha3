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

    def step_rho(self, state_array):
        A = state_array[:]
        x,y = 1,0

        for t in range(24):
            A[x][y][z] = state_array[x][y][(z-(t+1)(t+2)/2) % self.w]
            x,y = y, (2*x + 3*y) % 5

        return A

    def step_pi(self, state_array):
        A = [[[state_array[(x + 3*y) % 5][x][z] for x in range(5)]
                                                for y in range(5)]
                                                for z in range(self.w)]

        return A

    def step_chi(self, state_array):
        A = [[[state_array[x][y][z] ^ ((state_array[(x+1)%5][y][z] ^ 1)*state_array[(x+2)%5][y][z])
               for x in range(5)]
               for y in range(5)]
               for z in range(self.w)]

        return A

    def rc(self, t):j
        if t % 255 == 0:
            return 1

        R = bytearray('10000000')

        for i in range(1, t%255 + 1):
            R = 0 + R
            R[0] = (R[0] + R[8]) % 2
            R[4] = (R[4] + R[8]) % 2
            R[5] = (R[5] + R[8]) % 2
            R[6] = (R[6] + R[8]) % 2
            R = R[:8]

        return R[0]

    def step_iota(self, state_array, round_index):
        A = state_array[:]
        RC = bytearray('0'*self.w)

        for j in range(self.l):
            RC[2**j - 1] = rc(j+7*round_index)

        for z in range(self.w):
            A[0][0][z] = A[0][0][z] ^ RC[z]

        return A

    def Rnd(self, state_array, round_index):
        return step_iota(step_chi(step_pi(step_rho(step_theta(state_array)))), round_index)

    def keccak_p(self, s):
        A = string_to_array(s)

        for i in range(2*self.l + 12 - self.num_rounds, 2*self.l + 12):
            A = Rnd(A, i)

        S = array_to_string(A)

        return S

    def sponge(self, f, pad, r, M, d):
        P = M + pad(r, len(M))
        n = len(P)/r
        c = self.b - r
        P_blocks = [P[i:i+r] for i in range(0, len(P), r)]
        S = bytearray('0'*self.b)
        
        for i in range(n):
            tmp = bytearray(s^p for s,p in zip(S,bytearray(P_blocks[i] + '0'*c)))
            S = f(str(tmp))

        Z = ''

        while True:
            Z += S[:r]

            if d <= len(Z):
                return Z[:d]

            S = f(S)

    def pad10star1(self, x, m):
        j = (-m - 2) % x
        return '1' + '0'*j + '1'

    def keccak(self, c, M, d):
        return sponge(keccak_p, pad10star1, 1600-c, M, d)

    def SHA3_224(M):
        
        return keccak(448, M + 








