''' SHA-3 implementation based on the NIST standard FIPS 202
http://csrc.nist.gov/publications/drafts/fips-202/fips_202_draft.pdf
'''

import math
from bitstring import BitArray

class Keccak:
    width_values = [25, 50, 100, 200, 400, 800, 1600]

    def __init__(self, b=1600, num_rounds=24):
        if b in Keccak.width_values:
            self.b = b
            self.w = b // 25
            self.l = int(math.log(self.w, 2))

        self.num_rounds = num_rounds

    def string_to_array(self, s):
        A = [[[s[self.w * (5 * y + x) + z] for z in range(self.w)] 
                                                for y in range(5)]
                                                for x in range(5)]
        
        return A

    def array_to_string(self, array):
        lanes = [[''.join(['1' if array[i][j][x] else '0' 
                                   for x in range(self.w)])
                                   for j in range(5)]
                                   for i in range(5)]

        planes = [''.join([lanes[i][j] for i in range(5)])
                                       for j in range(5)]

        s = ''.join([planes[i] for i in range(5)])

        return s

    def step_theta(self, state_array):
        C = [[reduce(lambda i, j: i^j, [state_array[x][y][z] for y in range(5)])
                                                             for z in range(self.w)]
                                                             for x in range(5)]

        D = [[C[(x-1) % 5][z] ^ C[(x+1) % 5][(z-1) % self.w] for z in range(self.w)]
                                                             for x in range(5)]

        A = [[[state_array[x][y][z] ^ D[x][z] for z in range(self.w)]
                                              for y in range(5)]
                                              for x in range(5)]

        return A

    def step_rho(self, state_array):
        A = state_array[:]
        x,y = 1,0

        for t in range(24):
            for z in range(self.w):
                A[x][y][z] = state_array[x][y][(z-(t+1)*(t+2)/2) % self.w]
            x,y = y, (2*x + 3*y) % 5

        return A

    def step_pi(self, state_array):
        A = [[[state_array[(x + 3*y) % 5][x][z] for z in range(self.w)]
                                                for y in range(5)]
                                                for x in range(5)]

        return A

    def step_chi(self, state_array):
        A = [[[state_array[x][y][z] ^ ((state_array[(x+1)%5][y][z] ^ 1)*state_array[(x+2)%5][y][z])
               for z in range(self.w)]
               for y in range(5)]
               for x in range(5)]

        return A

    def rc(self, t):
        if t % 255 == 0:
            return 1

        R = BitArray(bin='10000000')

        for i in range(1, t%255 + 1):
            R.prepend('0b0')
            R[0] = (R[0] + R[8]) % 2
            R[4] = (R[4] + R[8]) % 2
            R[5] = (R[5] + R[8]) % 2
            R[6] = (R[6] + R[8]) % 2
            R = R[:8]

        return R[0]

    def step_iota(self, state_array, round_index):
        A = state_array[:]
        RC = BitArray(bin='0'*self.w)

        for j in range(self.l):
            RC[2**j - 1] = self.rc(j+7*round_index)

        for z in range(self.w):
            A[0][0][z] = A[0][0][z] ^ RC[z]

        return A

    def Rnd(self, state_array, round_index):
        return self.step_iota(
                self.step_chi(
                 self.step_pi(
                  self.step_rho(
                   self.step_theta(state_array)))), 
                round_index)

    def keccak_p(self, s):
        A = self.string_to_array(s)

        for i in range(2*self.l + 12 - self.num_rounds, 2*self.l + 12):
            A = self.Rnd(A, i)

        S = self.array_to_string(A)

        return S

    def sponge(self, f, pad, r, M, d):
        P = M + pad(r, len(M))
        n = len(P)/r
        c = self.b - r
        P_blocks = [P[i:i+r] for i in range(0, len(P), r)]
        S = BitArray(bin='0'*self.b)
        
        for i in range(n):
            tmp = P_blocks[i] + BitArray(bin='0'*c)
            S = f(S ^ tmp)

        Z = ''

        while True:
            Z += S[:r]

            if d <= len(Z):
                return Z[:d]

            S = f(S)

    def pad10star1(self, x, m):
        j = (-m - 2) % x
        return '0b1' + '0'*j + '1'

    def keccak(self, c, M, d):
        return self.sponge(self.keccak_p, self.pad10star1, 1600-c, M, d)

    def SHA3_224(self, M):
        b = BitArray(bytes=M)
        b.append('0b01')
        bitstr = self.keccak(448, b, 224)
        return BitArray(bin=bitstr).bytes

    def SHA3_256(self, M):
        b = BitArray(bytes=M)
        b.append('0b01')
        bitstr = self.keccak(512, b, 256)
        return BitArray(bin=bitstr).bytes

    def SHA3_384(self, M):
        b = BitArray(bytes=M)
        b.append('0b01')
        bitstr = self.keccak(768, b, 384)
        return BitArray(bin=bitstr).bytes

    def SHA3_512(self, M):
        b = BitArray(bytes=M)
        b.append('0b01')
        bitstr = self.keccak(1024, b, 512)
        return BitArray(bin=bitstr).bytes

    def SHAKE_128(self, M, d):
        b = BitArray(bytes=M)
        b.append('0b1111')
        bitstr = self.keccak(256, b, d) 
        return BitArray(bin=bitstr).bytes

    def SHAKE_256(self, M, d):
        b = BitArray(bytes=M)
        b.append('0b1111')
        bitstr = self.keccak(512, b, d) 
        return BitArray(bin=bitstr).bytes
