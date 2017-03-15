import math, os

K_H2SO4 = 1.2 * math.pow(10, -2)
K_W = math.pow(10, -14)
NEU = math.pow(10, -7)

def dens_aq(t):
    A = -6.16236 * math.pow(10, -10)
    B = 8.61137 * math.pow(10, -8)
    C = -8.93025 * math.pow(10, -6)
    D = 6.7176 * math.pow(10, -5)
    E = 0.999841509
    dens = 0
    j = 0
    for i in (E, D, C, B, A):
        dens += i * math.pow(t, j)
        j += 1
    return dens

def press_aq(t):
    coe = [6.26192078e-06,
          -5.39506438e-05,
           1.41365468e-02,
           4.06908949e-01,
           3.86911009e+00]
    pr = [(t ** (4 - i)) * coe[i] for i in range(5)]
    return sum(pr)

def calibration(mass_aq, mass, t):
    acc = 0.01
    def corr(mass_aq, acc):
        mean_mass_aq = math.fsum(mass_aq) / len(mass_aq)
        deleted = []
        for i in mass_aq:
            if abs(i - mean_mass_aq) > acc:
                deleted.append(i)
        return deleted
    while True:
        deleted = corr(mass_aq, acc)
        if len(deleted) > len(mass_aq) * 0.4:
            acc += 0.01
        else:
            print('remove', len(deleted), 'points from', len(mass_aq))
            print('final acc =', acc)
            break
    for i in deleted:
        mass_aq.remove(i)
    mean_mass_aq = math.fsum(mass_aq) / len(mass_aq)
    return round((mean_mass_aq - mass) / dens_aq(t), 3)

def square_eq(a, b, c):
#    print(a, b, c)
    p = b / a
    q = -1 * c / a
    try:
        return (math.sqrt(0.25 * p ** 2 + q) - 0.5 * p,             #отрицательный корень
                q / (0.5 * p + math.sqrt(0.25 * p ** 2 + q)))       #положительный корень
    except ValueError:
        print('Только мнимые корни')

def c(n, v):
    return n / v * 1000

def n(c, v):
    return c * v / 1000

def titration(nacid, nalkaly, v):
    '''
    basic equation:
    nalkaly < 2 * nacid:
        K_H2SO4 = (x - cacid - calkaly) * x / (2 * cacid - calkaly - K_H2SO4)
    nalkaly > 2 * nacid:
        K_W = x * (x + calkaly - 2 * cacid)
    calkaly: concentration of NaOH
    cacid: concentration of H2SO4
    '''
    cacid, calkaly = c(nacid, v), c(nalkaly, v)
    #print(cacid, calkaly)
    if 2 * nacid > nalkaly:
        ch = square_eq(1, calkaly - cacid + K_H2SO4,
                       K_H2SO4 * (calkaly - 2 * cacid))[1]
    else:
        ch = square_eq(1, calkaly - 2 * cacid, -1 * K_W)[1]
    return ch

def untitration(nacid, ch, v):
    print('start untitration:', nacid, ch, v)
    cacid = c(nacid, v)
    print(cacid)
    if ch > NEU:                                    #NEU = 10^-7
        print('pass')
    else:      
        calkaly = K_W / ch - ch + 2 * cacid
#        print(calkaly)
        return round(n(calkaly, v), 6)

def file_choose(name, test, longname = False):
    file_list = []
    for i in os.listdir():
        if test in i:
            file_list.append((i, os.getcwd() + os.sep + i))
    print('Список файлов:')
    for ind, (val, fval) in enumerate(file_list):
        print('{0:>3}: {1}'.format(ind, val))
    choose = int(input('Выберите файл для расчета: '))
    if longname:
        return file_list[choose][1]
    else:
        return file_list[choose][0]

def zero_func(x0, xn, func, errr):
    a = x0
    b = xn
    while abs(a - b) > errr:
        c = (a + b) / 2
        if func(a) * func(c) > 0:
            a = c
        else:
            b = c
    return (a + b)
    
if __name__ == '__main__':
    print(press_aq(298))
    test = [i for i in range(20, 32, 2)]
    for i in test:
        print(round(dens_aq(i), 6))
    print(
        calibration([139.767, 139.800, 139.830, 139.822], 42.007, 31.2)
          )
    print(
        calibration([142.14, 142.088, 142.108, 142.096, 142.124,
                     142.143, 142.081, 142.025, 142.073], 42.194, 21.4)
          )
'''
    test = [(1, -2, 1), (1, 2, -3), (1, -4, 4), (1, 1, 100500)]
    for i in test:
        print(square_eq(*i))
    print(titration(0.01, 0.02, 100))
    print(titration(n(0.1, 100), n(0.1, 100), 100))
    print(titration(n(0.1, 100), 0, 100))
    print(titration(0.01, 0.03, 100))
    print(untitration(0.01, titration(0.01, 0.03, 100), 100))
    print(zero_func(-5, 5, lambda x: 3 * x + 1, .001))
'''
