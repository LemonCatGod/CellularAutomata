from math import erfc, pow, exp, pi, fabs, factorial, sqrt, gamma, cos, log2, sin, log
import numpy
import time

P_CONST = 0.01

def read_file(path):
    f = open(path, "r")
    str = f.read()
    f.close()
    return str

def rect_integral(f, xmin, xmax, n=10000):
    dx = (xmax - xmin) / n
    area = 0
    x = xmin
    for i in range(n):
        area += dx * f(x)
        x += dx
    return area


def tr_integral(f, xmin, xmax, n=10000):
    dx = (xmax - xmin) / n
    area = 0
    x = xmin
    for i in range(n):
        area += dx * (f(x) + f(x + dx)) / 2
        x += dx
    return area


def sign(x):
    return 1 if x >= 0 else -1


def erfc_sys(x):
    return erfc(x)


def erf(x):
    a1 =  0.254829592
    a2 = -0.284496736
    a3 =  1.421413741
    a4 = -1.453152027
    a5 =  1.061405429
    p  =  0.3275911

    sign = 1
    if x < 0:
        sign = -1
    x = fabs(x)

    t = 1.0/(1.0 + p*x)
    y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*exp(-x*x)

    return sign*y


def erfc_mine(x):
    return 1 - erf(x)


def erfc_asymp(x):
    a = sum([(((-1) ** i) * factorial(2 * i)) / (factorial(i) * pow(2 * x, 2 * i)) for i in range(0, 60)])
    return exp(-1 * pow(x, 2)) / (x * sqrt(pi)) * a


def test_1(str):
    total_value = 0
    for i in str:
        a = int(i)
        total_value += 1 if a == 1 else -1
    n = len(str)
    S_obs = abs(total_value) / sqrt(n)
    print("1 test")
    p_value = erfc_mine(S_obs / sqrt(2))
    print(f"total_value: {total_value} S_obs: {S_obs} p_value: {p_value}")
    return p_value >= P_CONST


def lower_gamma(s, x):
    lower_gamma = tr_integral(lambda t: pow(t, s - 1) + exp(-t), 0, x)
    return lower_gamma

def lower_gamma_2(s, x, q=10):
    lower_gamma = 0
    for i in range(q):
        lower_gamma += pow(x, i) / (gamma(s+i+1))
    return pow(x, s)*gamma(s)*exp(-x)*lower_gamma


def upper_gamma(s, x):
    return (gamma(s) - lower_gamma_2(s, x))/gamma(s)


def hi_quadro(arr, M):
    return 4 * M * sum(map(lambda x: pow(x - 0.5, 2), arr))


def test_2(str):
    print("2 test")
    PP = []
    M = 200
    counter = 0
    number = 0
    for i in str:
        counter += 1
        a = int(i)
        number += a
        if counter % M == 0:
            PP.append(number / M)
            number = 0
    hi = hi_quadro(PP, M)
    p_value = upper_gamma(len(PP) / 2, hi / 2)
    print(f"hi: {hi} p_value: {p_value}")
    return p_value >= P_CONST

def test_3(str):
    print("3 test")
    b = 2
    one_value = 0
    n = 0
    V_value = 0
    for i in str:
        n += 1
        a = int(i)
        V_value += 1 if b != a else 0
        one_value += a
        b = a
    one_value /= n
    if abs(one_value - 0.5) < 2 / sqrt(n):
        res = abs(V_value - 2*n*one_value*(1-one_value))/(2*sqrt(2*n)*one_value*(1-one_value))
        p_value = erfc_mine(res)
        print(one_value)
        print(f"V_value: {V_value} p_value: {p_value}")
        return p_value >= P_CONST
    else:
        print("Error")
        print(one_value)
        return False

def test_4(str):
    print("4 test")
    prev_value = 0
    one_value = 0
    n = 0
    M = 128
    values = []
    for i in str:
        n += 1
        a = int(i)
        one_value = one_value + 1 if a == 1 else 0
        prev_value = max(one_value, prev_value)
        if n % M == 0:
            values.append(prev_value)
            one_value = 0
            prev_value = 0
    v = [0]*6
    for i in values:
        if i <= 4:
            v[0] += 1
        elif i < 9:
            v[i - 4] += 1
        else:
            v[5] += 1
    p = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
    R = 49
    hi = 0
    for i in range(6):
        hi += pow(v[i] - R*p[i], 2)/(R*p[i])
    p_value = upper_gamma(3/2, hi/2)
    print(f"v: {v} hi: {hi} p_value: {p_value}")
    return p_value > P_CONST


def probability_5(Q, M):
    prob_res = []
    for i in range(min(Q, M)+1):
        p = 1
        for j in range(i):
            p *= (1 - pow(2, j - Q)) * (1 - pow(2, j - M)) / (1 - pow(2, j - i))
        prob_res.append(pow(2, i*(Q+M-i) - M*Q) * p)

    return prob_res


def test_5(str):
    M = 10
    Q = 10
    N = 100
    n = 0
    arrays = []
    arr = []
    for i in str:
        arr.append(int(i))
        n += 1
    ranks = [0]*11
    N = n // M // Q
    for i in range(N):
        arrays.append(numpy.array(arr[i*M*Q:(i+1)*M*Q]).reshape((M, Q)))
        ranks[numpy.linalg.matrix_rank(arrays[i], tol=None)] += 1
    pp = probability_5(Q, M)
    hi_2 = 0
    for i in range(min(Q, M)+1):
        hi_2 += (ranks[i] - N*pp[i])**2 / (N*pp[i])
    p_value = upper_gamma(1, hi_2 / 2)
    print("5 test")
    print(f"ranks: {ranks} hi: {hi_2} p_value: {p_value}")
    return p_value > P_CONST


def furie(arr):
    res = []
    n = len(arr)
    arr_x = []
    arr_y = []
    for i in range(n):
        arr_x.append(cos((2 * pi * i) / n))
        arr_y.append(sin((2 * pi * i) / n))
    for i in range(n):
        x = 0
        y = 0
        for j in range(n):
            x += arr[j] * arr_x[(i*j) % n]
            y += arr[j] * arr_y[(i*j) % n]
        res.append(sqrt(x**2 + y**2))
    return res

def test_6(str):
    print("6 test")
    arr_numbers = list(map(lambda x: int(x) if int(x) == 1 else -1, list(str)))
    X = numpy.abs(numpy.fft.fft(arr_numbers))
    n = len(str)
    T = sqrt(log(1 / 0.05) * n)
    N_0 = 0.95 * n / 2
    N_1 = 0
    check_arr = []
    for i in range(1, (n - 1) // 2):
        N_1 += 1 if X[i] < T else 0
    print(N_1, N_0)
    d = (N_1 - N_0) / (sqrt(n * 0.95 * 0.05 / 4))
    p_value = erfc_mine(abs(d) / sqrt(2))
    print(f"d: {d} p_value: {p_value}")
    return p_value > P_CONST

def test_7(str):
    m = 10
    M = 200
    N = 50
    arr_str = []
    arr_w = [0]*N
    for i in range(N):
        arr_str.append(str[i * M:(i+1) * M])
    test_str = "0000000001"
    for i in range(N):
        a = arr_str[i].find(test_str)
        while a != -1:
            arr_w[i] += 1
            arr_str[i] = arr_str[i][a+m:]
            a = arr_str[i].find(test_str)

    E = (M - m + 1) / (2 ** m)
    s_2 = M * (1 / (2 ** m) - (2 * m - 1) / (2 ** (2*m)))
    hi_2 = 0
    for i in arr_w:
        hi_2 += (i - E) ** 2
    hi_2 /= s_2
    p_value = upper_gamma(N / 2, hi_2 / 2)
    print("7 test")
    print(f"hi: {hi_2} p_value: {p_value}")
    return p_value > P_CONST

def test_8(str):
    m = 10
    M = 2000
    N = 5
    arr_str = []
    arr_w = [0] * 6
    for i in range(N):
        arr_str.append(str[i * M:(i + 1) * M])
    test_str = "0000000001"
    for i in range(N):
        k = 0
        a = arr_str[i].find(test_str)
        while a != -1:
            k += 1
            arr_str[i] = arr_str[i][a + 1:]
            a = arr_str[i].find(test_str)
        arr_w[k if k < 5 else 5] += 1

    E = (M - m + 1) / (2 ** m)
    hi_2 = 0
    pi_arr = [0.324652, 0.182617, 0.142670, 0.106645, 0.077147, 0.166269]
    for i in range(6):
        hi_2 += (arr_w[i] - N * pi_arr[i]) ** 2 / (N * pi_arr[i])
    p_value = upper_gamma(N / 2, hi_2 / 2)
    print("8 test")
    print(f"hi: {hi_2} p_value: {p_value}")
    return p_value > P_CONST

def test_9(str):
    L = 6
    Q = 640
    K = 1026
    possible_L = [0]*64
    sum = 0
    arr = []
    for i in range(Q+K):
        arr.append(int(str[i*L:(i+1)*L], 2))
    for i in range(Q):
        possible_L[arr[i]] = i + 1
    for i in range(Q, Q+K):
        sum += log2(i + 1 -possible_L[arr[i]])
        possible_L[arr[i]] = i + 1
    sum /= K
    c = (0.7 - 0.8 / L + (4 + 32 / L) * pow(K, -3 / L) / 15) * sqrt(2.954 / L)
    p_value = erfc_mine(abs((sum - 5.2177052)/ (sqrt(2) * c)))
    print("9 test")
    print(f"fn: {sum} p_value: {p_value}")
    return p_value >= P_CONST

def berlekamp_massey(s):
    n = len(s)
    b = [0]*n
    t = [0]*n
    c = [0]*n
    b[0] = 1
    c[0] = 1
    N = 0
    L = 0
    m = -1
    while N < n:
        d = 0
        for i in range(L+1):
            d += c[i]*s[N-i]
        d = d % 2
        if d != 0:
            t = c.copy()
            for j in range(n+m-N):
                c[N - m + j] = (c[N - m + j] + b[j]) % 2
            if (2*L) <= N:
                L = N + 1 - L
                m = N
                b = t.copy()
        N = N + 1
    return L

def test_10(str):
    M = 500
    N = 20
    E = M / 2 + (9 + (-1)**(M + 1)) / 36 - (M / 3 + 2 / 9) / (2 ** M)
    arr = []
    for i in range(N):
        arr.append([int(i) for i in str[i*M:(i+1)*M]])
    arr_T = []
    for i in arr:
        arr_T.append((-1)**M *(berlekamp_massey(i) - E) + 2/9)
    v = [0]*7
    for i in arr_T:
        if i <= -2.5:
            v[0] += 1
        elif -2.5 < i <= -1.5:
            v[1] += 1
        elif -1.5 < i <= -0.5:
            v[2] += 1
        elif -0.5 < i <= 0.5:
            v[3] += 1
        elif 0.5 < i <= 1.5:
            v[4] += 1
        elif 1.5 < i <= 2.5:
            v[5] += 1
        else:
            v[6] += 1

    print(v)
    hi_2 = 0
    p = [0.010417, 0.03125, 0.125, 0.5, 0.25, 0.0625, 0.020833]
    for i in range(7):
        hi_2 += (v[i] - N * p[i]) ** 2 / (N * p[i])

    p_value = upper_gamma(3, hi_2 / 2)
    print("10 test")
    print(f"hi: {hi_2} p_value: {p_value}")
    return p_value >= P_CONST

def test_11(str):
    m = 3
    #pattern = [["0", "1"], ["00", "01", "10", "11"], ["000", "001", "010", "011", "100", "101", "110", "111"]]
    frequency = [[0]*2, [0]*4, [0]*8]
    n = len(str)
    for i in str:
        frequency[0][int(i)] += 1
    str = str + str[0]
    for i in range(n):
        frequency[1][int(str[i:(i+2)], 2)] += 1
    str = str + str[1]
    for i in range(n):
        frequency[2][int(str[i:(i+3)], 2)] += 1

    stat_m = (2**m) / n * sum(map(lambda x: x**2, frequency[2]))
    stat_m1 = (2**(m-1)) / n * sum(map(lambda x: x**2, frequency[1]))
    stat_m2 = (2**(m-2)) / n * sum(map(lambda x: x**2, frequency[0]))

    delta_m = stat_m - stat_m1
    delta_m_2 = stat_m - 2 * stat_m1 + stat_m2

    p_value1 = upper_gamma(2**(m-2), delta_m)
    p_value2 = upper_gamma(2**(m-3), delta_m_2)
    print("11 test")
    print(f"p_value1: {p_value1} p_value2: {p_value2}")
    return p_value1 > P_CONST and p_value2 > P_CONST

def test_12(str):
    m = 3
    #pattern = [["000", "001", "010", "011", "100", "101", "110", "111"], [""]]
    frequency = [[0] * 8, [0]*16]
    c_values = [[0]*8, [0]*16]
    n = len(str)
    str += str[0] + str[1]
    for i in range(n):
        frequency[0][int(str[i:(i+3)], 2)] += 1
    str += str[2]
    for i in range(n):
        frequency[1][int(str[i:(i + 4)], 2)] += 1

    phi_m = sum(map(lambda x: x / n * log(x / n), frequency[0]))
    phi_m1 = sum(map(lambda x: x / n * log(x / n), frequency[1]))
    hi_2 = 2*n * (log(2) - (phi_m - phi_m1))
    p_value = upper_gamma(2**(m-1), hi_2 / 2)
    print("12 test")
    print(f"hi: {hi_2} p_value: {p_value}")
    return p_value > P_CONST

def f_normal_2(x):
    g = 1
    b = 8 / (3 * pi) * (3 - pi) / (pi - 4)
    r = -1 * pow(x / g, 2) * (4 / pi + b * pow(x / g, 2)) / (1 + b * pow(x / g, 2))
    res = 0.5 * (1 + sign(x) * sqrt(1 - exp(r)))
    return res

def f_normal(x):
    return (1 / 2) * (1 + erf(x / sqrt(2)))

def test_13(str):
    n = len(str)
    s = [0] * n
    s[0] = 1 if str[0] == "1" else -1
    for i in range(1, n):
        a = 1 if str[i] == "1" else -1
        s[i] = s[i-1] + a
    z = max(s)

    r_1 = 0
    r_2 = 0
    if z == 0:
        z = 1
    for k in range(4 * (-n // z + 1), 4 * (n // z - 1)):
        r_1 += f_normal((4*k + 1) * z/sqrt(n)) - f_normal((4*k - 1) * z/sqrt(n))
    for k in range(4 * (-n // z - 3), 4 * (n // z - 1)):
        r_2 += f_normal((4*k + 3) * z/sqrt(n)) - f_normal((4*k + 1) * z/sqrt(n))

    p_value = 1 - r_1 + r_2
    print("13 test")
    print(f"r: {r_1, r_2} p_value: {p_value}")
    return p_value > P_CONST


def test_14(str):
    n = len(str)
    s = [0] * (n+2)
    for i in range(n):
        a = 1 if str[i] == "1" else -1
        s[i+1] = s[i] + a
    check = 0
    arr = []
    b = []
    for i in s:
        if i == 0:
            check += 1
            if check % 2 == 0:
                check += 1
                arr.append(b)
                b = []
                continue
        else:
            b.append(i)
    arr_length = len(arr)
    states = [[0]*arr_length for i in range(8)]
    for i in range(arr_length):
        for j in arr[i]:
            if -4 <= j <= -1:
                states[j+4][i] += 1
            elif 1 <= j <= 4:
                states[j+3][i] += 1
    new_states = [[0]*6 for i in range(8)]
    for i in range(8):
        for j in range(arr_length):
            new_states[i][states[i][j] if states[i][j] <= 5 else 5] += 1
    arr_hi_2 = []
    pi_con = [[0.8750, 0.0156, 0.0137, 0.0120, 0.0105, 0.0733], [0.8333, 0.0278, 0.0231, 0.0193, 0.0161, 0.0804], [0.7500, 0.0625, 0.0469, 0.0352, 0.0264, 0.0791], [0.5000, 0.2500, 0.1250, 0.0625, 0.0312, 0.0312], [0.5000, 0.2500, 0.1250, 0.0625, 0.0312, 0.0312], [0.7500, 0.0625, 0.0469, 0.0352, 0.0264, 0.0791], [0.8333, 0.0278, 0.0231, 0.0193, 0.0161, 0.0804], [0.8750, 0.0156, 0.0137, 0.0120, 0.0105, 0.0733]]
    for i in range(8):
        s = 0
        for j in range(6):
            s += (new_states[i][j] - arr_length*pi_con[i][j]) ** 2 / (arr_length * pi_con[i][j])
        arr_hi_2.append(s)
    p_values = []
    for i in arr_hi_2:
        p_values.append(upper_gamma(5 / 2, i / 2))
    print("14 test")
    print(f"p_values: {p_values}")
    res = [i > P_CONST for i in p_values]
    return all(res)

def test_15(str):
    n = len(str)
    s = [0] * (n + 2)
    for i in range(n):
        a = 1 if str[i] == "1" else -1
        s[i + 1] = s[i] + a
    check = 0
    arr = []
    b = []
    for i in s:
        if i == 0:
            check += 1
            if check % 2 == 0:
                check += 1
                arr.append(b)
                b = []
                continue
        else:
            b.append(i)
    arr_length = len(arr)
    states = [0]*18
    for i in range(arr_length):
        for j in arr[i]:
            if -9 <= j <= -1:
                states[j + 9] += 1
            elif 1 <= j <= 9:
                states[j + 8] += 1
    p_values = []
    for i in range(-9, 0):
        p_values.append(erfc_mine(abs(states[i+9] - arr_length) / sqrt(2*arr_length * (4 * abs(i) - 2))))
    for i in range(1, 10):
        p_values.append(erfc_mine(abs(states[i + 8] - arr_length) / sqrt(2 * arr_length * (4 * i - 2))))
    print("15 test")
    print(f"p_values: {p_values}")
    res = [i > P_CONST for i in p_values]
    return all(res)


def run_all_tests():
    strings = []
    f = open("list.txt", "r")
    for i in f.read().split("\n"):
        strings.append(read_file(i))
    f.close()
    n = len(strings)
    res_percent = [0]*15
    for i in strings:
        print(f"FILE: {i}")
        print("RUNNING TESTS")
        res_percent[0] += 1 if test_1(i) else 0
        res_percent[1] += 1 if test_2(i) else 0
        res_percent[2] += 1 if test_3(i) else 0
        res_percent[3] += 1 if test_4(i) else 0
        res_percent[4] += 1 if test_5(i) else 0
        res_percent[5] += 1 if test_6(i) else 0
        res_percent[6] += 1 if test_7(i) else 0
        res_percent[7] += 1 if test_8(i) else 0
        res_percent[8] += 1 if test_9(i) else 0
        res_percent[9] += 1 if test_10(i) else 0
        res_percent[10] += 1 if test_11(i) else 0
        res_percent[11] += 1 if test_12(i) else 0
        res_percent[12] += 1 if test_13(i) else 0
        res_percent[13] += 1 if test_14(i) else 0
        res_percent[14] += 1 if test_15(i) else 0
    res = list(map(lambda x: 100 * x / n, res_percent))
    f = open("results.txt", "a")
    f.write("\nTest 1: " + str(res[0]) + "%")
    f.write("\nTest 2: " + str(res[1]) + "%")
    f.write("\nTest 3: " + str(res[2]) + "%")
    f.write("\nTest 4: " + str(res[3]) + "%")
    f.write("\nTest 5: " + str(res[4]) + "%")
    f.write("\nTest 6: " + str(res[5]) + "%")
    f.write("\nTest 7: " + str(res[6]) + "%")
    f.write("\nTest 8: " + str(res[7]) + "%")
    f.write("\nTest 9: " + str(res[8]) + "%")
    f.write("\nTest 10: " + str(res[9]) + "%")
    f.write("\nTest 11: " + str(res[10]) + "%")
    f.write("\nTest 12: " + str(res[11]) + "%")
    f.write("\nTest 13: " + str(res[12]) + "%")
    f.write("\nTest 14: " + str(res[13]) + "%")
    f.write("\nTest 15: " + str(res[14]) + "%")
    f.close()


run_all_tests()
