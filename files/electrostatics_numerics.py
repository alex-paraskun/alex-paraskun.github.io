"""Численные методы электростатики: программы к интерактивной странице.

Каждый раздел (#%% tNN) соответствует вкладке страницы. Нужен только NumPy.
Если не сказано иное, единицы такие, что 1/(4*pi*eps0) = 1.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss

EPS0 = 8.8541878128e-12
PI = np.pi


#%% t01 | Стержень: поле как сумма полей N точечных зарядов
def rod_field(l, lam, x, N):
    """Поле на продолжении стержня длины l на расстоянии x от ближайшего конца."""
    s = (np.arange(N) + 0.5) * l / N          # середины кусочков, стержень занимает [0, l]
    dq = lam * l / N                          # заряд одного кусочка
    return np.sum(dq / (x + l - s) ** 2)      # принцип суперпозиции


def rod_exact(l, lam, x):
    return lam * l / (x * (x + l))


#%% t02 | Кольцо: поле в произвольной точке (x, 0, z)
def ring_field(px, pz, N, R=1.0):
    """Кольцо радиуса R с зарядом 1 заменено N точечными зарядами 1/N."""
    phi = 2 * PI * np.arange(N) / N
    dx = px - R * np.cos(phi)
    dy = -R * np.sin(phi)
    dz = pz
    d3 = (dx**2 + dy**2 + dz**2) ** 1.5
    return np.array([np.sum(dx / d3), np.sum(dy / d3), dz * np.sum(1 / d3)]) / N


def ring_axis(h, N, R=1.0):
    """Поле на оси: все заряды дают одинаковый осевой вклад."""
    return h / (R**2 + h**2) ** 1.5


#%% t03 | Энергия поля: составная квадратура Гаусса
def gauss_integral(f, a, b, parts=40, n=20):
    """Интеграл f(r) dr по [a, b]: n-точечная формула Гаусса на каждом из parts отрезков."""
    x, w = leggauss(n)
    h = (b - a) / parts
    total = 0.0
    for k in range(parts):
        lo = a + k * h
        r = lo + 0.5 * h * (x + 1)            # узлы на отрезке [lo, lo + h]
        total += 0.5 * h * np.sum(w * f(r))
    return total


def sphere_and_ball_energy():
    """Энергия поля в единицах Q^2/(4 pi eps0 R) при Q = R = 1, eps0 = 1/(4 pi)."""
    eps0 = 1 / (4 * PI)
    w = lambda E: 0.5 * eps0 * E**2           # плотность энергии
    dV = lambda r: 4 * PI * r**2              # объём шарового слоя
    E_out = lambda r: 1 / r**2 / (4 * PI * eps0)
    E_in = lambda r: r / (4 * PI * eps0)      # внутри равномерно заряженного шара
    # внешняя часть: бесконечность убираем заменой r = 1/u
    W_out = gauss_integral(lambda u: w(E_out(1 / u)) * dV(1 / u) / u**2, 1e-9, 1, 60)
    W_in = gauss_integral(lambda r: w(E_in(r)) * dV(r), 0, 1, 10)
    return W_out, W_out + W_in                # сфера, шар (ответ: 1/2 и 3/5)


#%% t04 | Радиальные задачи: схема на цепочке узлов и прогонка
def solve_radial(m, a, b, N, eps_f, rho_f, flux_a, U_b, cell_integral=True):
    """(1/r^m) d/dr (r^m eps dU/dr) = -rho на [a, b].

    m = 0, 1, 2 -- плоская, цилиндрическая, сферическая симметрия;
    flux_a = r^m eps dU/dr при r = a;  U_b -- потенциал при r = b.
    """
    h = (b - a) / N
    r = a + h * np.arange(N + 1)
    rf = 0.5 * (r[:-1] + r[1:])                              # середины ячеек
    g = rf**m * np.array([eps_f(x) for x in rf]) / h         # «проводимости» между узлами
    xg, wg = leggauss(6)
    rhs = np.zeros(N + 1)
    for i in range(N + 1):
        if cell_integral:                                    # заряд ячейки -- точный интеграл плотности
            for lo0, hi0 in ((-0.5, 0.0), (0.0, 0.5)):
                lo = min(max(r[i] + lo0 * h, a), b)
                hi = min(max(r[i] + hi0 * h, a), b)
                rq = 0.5 * (hi + lo) + 0.5 * (hi - lo) * xg
                rhs[i] += 0.5 * (hi - lo) * np.sum(wg * np.array([rho_f(x) for x in rq]) * rq**m)
        else:                                                # «плотность в узле» (наивный вариант)
            rl, rr = max(r[i] - h / 2, a), min(r[i] + h / 2, b)
            rhs[i] = (rr ** (m + 1) - rl ** (m + 1)) / (m + 1) * rho_f(r[i])
    rhs[0] += -flux_a
    # трёхдиагональная система lo*U[i-1] + di*U[i] + up*U[i+1] = rhs
    lo, di, up = np.zeros(N + 1), np.zeros(N + 1), np.zeros(N + 1)
    di[1:] += g;  lo[1:] = -g
    di[:-1] += g; up[:-1] = -g
    di[N], lo[N], up[N], rhs[N] = 1.0, 0.0, 0.0, U_b         # условие U(b) = U_b
    for i in range(1, N + 1):                                # прямой ход прогонки
        f = lo[i] / di[i - 1]
        di[i] -= f * up[i - 1]
        rhs[i] -= f * rhs[i - 1]
    U = np.zeros(N + 1)
    U[N] = rhs[N] / di[N]
    for i in range(N - 1, -1, -1):                           # обратный ход
        U[i] = (rhs[i] - up[i] * U[i + 1]) / di[i]
    return r, U


def gradient1d(r, U):
    """E = -dU/dr: центральные разности, на концах односторонние формулы 2-го порядка."""
    E = np.zeros_like(U)
    E[1:-1] = -(U[2:] - U[:-2]) / (r[2:] - r[:-2])
    E[0] = -(-3 * U[0] + 4 * U[1] - U[2]) / (2 * (r[1] - r[0]))
    E[-1] = -(3 * U[-1] - 4 * U[-2] + U[-3]) / (2 * (r[-1] - r[-2]))
    return E


#%% t07 | Концентрические проводники: система линейных уравнений
def shells(r, Q_ball, Q_layer):
    """Шар (радиус r[0]) внутри металлического слоя (радиусы r[1], r[2]).

    Неизвестные: заряды трёх поверхностей q0, q1, q2 и потенциалы шара V0 и слоя V1.
    Потенциал сферы i от сферы j равен k*q_j/max(r_i, r_j).
    """
    k = 1 / (4 * PI * EPS0)
    r = np.asarray(r, float)
    P = k / np.maximum.outer(r, r)
    A, b = np.zeros((5, 5)), np.zeros(5)
    A[0, 0], b[0] = 1, Q_ball                  # заряд шара
    A[1, 1], A[1, 2], b[1] = 1, 1, Q_layer     # суммарный заряд слоя
    A[2, :3], A[3, :3], A[4, :3] = P[0], P[1], P[2]
    A[2, 3], A[3, 4], A[4, 4] = -1, -1, -1     # потенциалы поверхностей: шар = V0, слой = V1
    q0, q1, q2, V0, V1 = np.linalg.solve(A, b)
    return (q0, q1, q2), V0, V1


#%% t08 | Сетка «крест»: метод сопряжённых градиентов (используется в задачах 8-14)
def solve_cg(fixed, U_fix, h, rho=None, eps=None, tol=1e-11, maxit=6000):
    """Уравнение Пуассона на сетке «крест». Массивы индексируются как [j, i] = [y, x].

    fixed -- булева маска узлов с заданным потенциалом U_fix (проводники, рамка).
    Крайние узлы сетки должны быть фиксированными. Матрица не строится:
    произведение A·p считается через сдвиги массива.
    """
    free = ~fixed
    one = np.ones(fixed.shape)
    if eps is None:
        wE = wW = wN = wS = one
    else:                                                    # гармоническое среднее eps на связях
        hm = lambda a, b: 2 * a * b / (a + b)
        wE, wW = hm(eps, np.roll(eps, -1, 1)), hm(eps, np.roll(eps, 1, 1))
        wN, wS = hm(eps, np.roll(eps, -1, 0)), hm(eps, np.roll(eps, 1, 0))
    wE, wW, wN, wS = (free * w for w in (wE, wW, wN, wS))
    diag = wE + wW + wN + wS
    nb = lambda p: wE * np.roll(p, -1, 1) + wW * np.roll(p, 1, 1) + wN * np.roll(p, -1, 0) + wS * np.roll(p, 1, 0)
    U = np.where(fixed, U_fix, 0.0)
    b = free * (h * h * (0 if rho is None else rho))
    r = b - free * (diag * U - nb(U))                        # начальная невязка
    bn = np.linalg.norm(r) or 1.0
    z = np.where(free, r / np.where(free, diag, 1), 0.0)     # предобуславливатель: диагональ
    p, rz, it = z.copy(), np.sum(r * z), 0
    while it < maxit:
        Ap = free * (diag * p - nb(p))
        pAp = np.sum(p * Ap)
        if pAp == 0:
            break
        alpha = rz / pAp
        U += alpha * p
        r -= alpha * Ap
        it += 1
        if np.linalg.norm(r) / bn < tol:
            break
        z = np.where(free, r / np.where(free, diag, 1), 0.0)
        rz_new = np.sum(r * z)
        p = z + (rz_new / rz) * p
        rz = rz_new
    return U, it


def field2d(U, h):
    """E = -grad U: центральные разности во внутренних узлах."""
    Ex, Ey = np.zeros_like(U), np.zeros_like(U)
    Ex[:, 1:-1] = -(U[:, 2:] - U[:, :-2]) / (2 * h)
    Ey[1:-1, :] = -(U[2:, :] - U[:-2, :]) / (2 * h)
    return Ex, Ey


def energy2d(U):
    """Энергия поля на единицу длины: 1/2 * сумма (dU)^2 по связям сетки (eps = 1)."""
    return 0.5 * (np.sum(np.diff(U, axis=1) ** 2) + np.sum(np.diff(U, axis=0) ** 2))


def coax(R1, R2, h, U0=1.0):
    """Ёмкость на единицу длины коаксиала; проводники -- «замороженные» узлы."""
    L = 1.1 * R2
    n = int(round(2 * L / h)) + 1
    x = -L + h * np.arange(n)
    X, Y = np.meshgrid(x, x)                                 # X[j, i], Y[j, i]
    rr = np.hypot(X, Y)
    inner, outer = rr <= R1, rr >= R2
    U, it = solve_cg(inner | outer, np.where(inner, U0, 0.0), h)
    C = 2 * energy2d(U) / U0**2                              # C = 2W/U^2
    return C, 2 * PI / np.log(R2 / R1), it                   # модель, формула, число итераций


#%% t09 | Цилиндр в однородном поле: граничное условие на рамке
def cyl_in_field(R, Lfac, h, correct=True, E0=1.0):
    """Незаряженный проводящий цилиндр в поле E0 вдоль x. Область -- квадрат [-L, L]^2.

    correct=True: на рамке задан точный потенциал -E0*x*(1 - R^2/r^2) (с поправкой от цилиндра);
    correct=False: наивное условие -E0*x, которое даёт систематическую ошибку.
    """
    L = Lfac * R
    n = int(round(2 * L / h)) + 1
    x = -L + h * np.arange(n)
    X, Y = np.meshgrid(x, x)
    r2 = X**2 + Y**2
    frame = np.zeros((n, n), bool)
    frame[0, :] = frame[-1, :] = frame[:, 0] = frame[:, -1] = True
    Uframe = -E0 * X * (1 - R**2 / np.maximum(r2, 1e-12)) if correct else -E0 * X
    fixed = frame | (r2 <= R**2)                             # рамка и тело цилиндра
    U, it = solve_cg(fixed, np.where(frame, Uframe, 0.0), h)
    Ex, Ey = field2d(U, h)
    return U, Ex, Ey, it


#%% t10 | Нить у прямого угла: вычитание особенности
def corner_force(n, a, lam, Lbox):
    """Сила на единицу длины на нить в прямом металлическом угле.

    U = U_нити + psi: логарифмическую особенность выделяем аналитически,
    а сетка считает гладкую часть psi (на рамке psi = -U_нити).
    """
    h = Lbox / n
    k = int(round(a / h))
    ax = k * h                                               # положение нити кратно шагу сетки
    x = h * np.arange(n + 1)
    X, Y = np.meshgrid(x, x)
    U_line = -lam / (2 * PI) * np.log(np.maximum(np.hypot(X - ax, Y - ax), 1e-12))
    frame = np.zeros((n + 1, n + 1), bool)
    frame[0, :] = frame[-1, :] = frame[:, 0] = frame[:, -1] = True
    psi, it = solve_cg(frame, -U_line, h)
    Ex = -(psi[k, k + 1] - psi[k, k - 1]) / (2 * h)          # сила = lam * (-grad psi) в точке нити
    Ey = -(psi[k + 1, k] - psi[k - 1, k]) / (2 * h)
    return lam * Ex, lam * Ey, -lam**2 / (8 * PI * ax)       # Fx, Fy, формула (три изображения)


#%% t11 | Метод фиктивных зарядов: заряд и заземлённый шар
def fibonacci_sphere(n, R):
    """n почти равномерно распределённых точек на сфере радиуса R."""
    k = np.arange(n) + 0.5
    z = 1 - 2 * k / n
    rho = np.sqrt(1 - z * z)
    phi = PI * (3 - np.sqrt(5)) * k
    return R * np.column_stack([rho * np.cos(phi), rho * np.sin(phi), z])


def lstsq_qr(A, b):
    """Метод наименьших квадратов через QR-разложение: A = QR, R x = Q^T b."""
    Q, R = np.linalg.qr(A)
    return np.linalg.solve(R, Q.T @ b)


def csm_sphere(q, L, R, n_src, n_col, rf):
    """Заряд q на расстоянии L от центра заземлённого шара радиуса R.

    Внутри шара на сфере радиуса rf*R расположено n_src фиктивных зарядов; их величины
    подбираются так, чтобы потенциал на шаре был нулевым в n_col контрольных точках.
    """
    src = fibonacci_sphere(n_src, rf * R)
    col = fibonacci_sphere(n_col, R)
    pos = np.array([0.0, 0.0, L])
    G = 1 / np.linalg.norm(col[:, None, :] - src[None, :, :], axis=2)   # потенциал источника j в точке i
    rhs = -q / np.linalg.norm(col - pos, axis=1)                        # потенциал самого заряда q
    Q = lstsq_qr(G, rhs)
    d = pos - src                                                       # сила на q от фиктивных зарядов
    F = q * np.sum(Q * d[:, 2] / np.linalg.norm(d, axis=1) ** 3)
    return Q, src, np.sum(Q), F, -q**2 * R * L / (L**2 - R**2) ** 2    # заряды, их сумма, сила, формула


#%% t12 | Плоский конденсатор: краевые поля
def plate_capacitor(w, d, U0, L, h):
    """Две пластины шириной w, зазор d, напряжение U0, заземлённая рамка [-L, L]^2."""
    n = int(round(2 * L / h)) + 1
    fixed = np.zeros((n, n), bool)
    fixed[0, :] = fixed[-1, :] = fixed[:, 0] = fixed[:, -1] = True
    Uf = np.zeros((n, n))
    jt, jb = round((d / 2 + L) / h), round((-d / 2 + L) / h)            # строки пластин
    i0, i1 = round((-w / 2 + L) / h), round((w / 2 + L) / h)
    fixed[jt, i0:i1 + 1], Uf[jt, i0:i1 + 1] = True, U0 / 2
    fixed[jb, i0:i1 + 1], Uf[jb, i0:i1 + 1] = True, -U0 / 2
    U, it = solve_cg(fixed, Uf, h)
    Ex, Ey = field2d(U, h)
    Q_in = np.sum(Uf[jt, i0:i1 + 1] - U[jt - 1, i0:i1 + 1])             # заряд по теореме Гаусса
    return U, -Ey[n // 2, n // 2], Q_in


#%% t13 | Несколько точечных зарядов: суперпозиция и нули поля
def charges_field(ch, X, Y, soft=0.0):
    """Потенциал и поле зарядов ch = [(q, x, y), ...] в точках (X, Y) (k = 1)."""
    U, Ex, Ey = 0.0, 0.0, 0.0
    for q, cx, cy in ch:
        dx, dy = X - cx, Y - cy
        r2 = dx * dx + dy * dy + soft**2
        r = np.sqrt(r2)
        U = U + q / r                                        # потенциалы складываются как числа
        Ex = Ex + q * dx / (r2 * r)                          # поля -- как векторы
        Ey = Ey + q * dy / (r2 * r)
    return U, Ex, Ey


def find_nulls(ch, box, tol=1e-11):
    """Нули поля: метод Ньютона из сетки 13x13 стартовых точек; box = (x0, x1, y0, y1)."""
    E = lambda x, y: np.array(charges_field(ch, x, y)[1:])
    nulls = []
    for sx in np.linspace(box[0], box[1], 13):
        for sy in np.linspace(box[2], box[3], 13):
            x, y = sx, sy
            for _ in range(60):
                e, dh = E(x, y), 1e-6
                J = np.column_stack([(E(x + dh, y) - e) / dh, (E(x, y + dh) - e) / dh])   # якобиан
                if abs(np.linalg.det(J)) < 1e-14:
                    break
                step = -np.linalg.solve(J, e)
                x, y = x + step[0], y + step[1]
                if np.hypot(*step) < tol:
                    if (np.hypot(*E(x, y)) < 1e-8 and not any(np.hypot(x - c[1], y - c[2]) < 1e-3 for c in ch)
                            and not any(np.hypot(x - a, y - b) < 1e-4 for a, b in nulls)):
                        nulls.append((x, y))
                    break
    return nulls


#%% t14 | Суперпозиция на сетке: проверка линейности
def super_grid(hh, sources, L=4.0):
    """Решаем для трёх источников сразу, по отдельности (сумма) и для удвоенных зарядов.

    sources = [(q, x, y), ...]; заряд узла: rho = q / h^2 (нить в одном узле).
    """
    n = int(round(2 * L / hh)) + 1
    fixed = np.zeros((n, n), bool)
    fixed[0, :] = fixed[-1, :] = fixed[:, 0] = fixed[:, -1] = True
    zero = np.zeros((n, n))

    def solve(lst, scale):
        rho = np.zeros((n, n))
        for q, x, y in lst:
            rho[round((y + L) / hh), round((x + L) / hh)] += scale * q / hh**2
        return solve_cg(fixed, zero, hh, rho=rho, tol=1e-14, maxit=12000)[0]

    U_all = solve(sources, 1)
    U_sum = sum(solve([s], 1) for s in sources)
    U_dbl = solve(sources, 2)
    mx = np.max(np.abs(U_all))
    return np.max(np.abs(U_all - U_sum)) / mx, np.max(np.abs(U_dbl - 2 * U_all)) / mx


#%% t15 | Заряд у плоскости: метод граничных элементов
def quad_int(X, Y):
    """Интеграл от 1/r по прямоугольнику [0, X] x [0, Y] (знаки X, Y произвольны)."""
    ax, ay = np.abs(X), np.abs(Y)
    with np.errstate(divide="ignore", invalid="ignore"):
        v = ax * np.arcsinh(ay / ax) + ay * np.arcsinh(ax / ay)
    return np.where((ax == 0) | (ay == 0), 0.0, np.sign(X) * np.sign(Y) * v)


def image_plane(L, N, q=1.0, d=1.0):
    """Заряд q на высоте d над заземлённой плоскостью; плоскость -- квадрат 2L x 2L из N x N клеток.

    Неизвестны поверхностные плотности sigma клеток; условие phi = 0 на плоскости даёт
    симметричную положительно определённую систему A sigma = -phi_q, решаем разложением Холецкого.
    Метод изображений здесь не используется.
    """
    s = 2 * L / N
    c = -L + s * (np.arange(N) + 0.5)
    X, Y = [a.ravel() for a in np.meshgrid(c, c)]            # центры клеток
    dx1, dx2 = X[None, :] - s / 2 - X[:, None], X[None, :] + s / 2 - X[:, None]
    dy1, dy2 = Y[None, :] - s / 2 - Y[:, None], Y[None, :] + s / 2 - Y[:, None]
    A = quad_int(dx2, dy2) - quad_int(dx1, dy2) - quad_int(dx2, dy1) + quad_int(dx1, dy1)
    phi_q = q / np.sqrt(X**2 + Y**2 + d**2)                  # потенциал заряда q на плоскости
    Lc = np.linalg.cholesky(A)                               # A = Lc Lc^T
    sigma = np.linalg.solve(Lc.T, np.linalg.solve(Lc, -phi_q))
    Q_ind = np.sum(sigma) * s * s
    F = q * np.sum(sigma * s * s * d / (X**2 + Y**2 + d**2) ** 1.5)
    return sigma, Q_ind, F, -q**2 / (2 * d) ** 2             # плотности, заряд, сила, формула


#%% t16 | Релаксация: Якоби, Гаусс-Зейдель, SOR
def relax(n, method, K, snap_at=None):
    """Квадрат 1x1: U = 1 на верхней стороне, U = 0 на остальных; n + 1 узлов по стороне.

    method: "jacobi", "gs" (Гаусс-Зейдель) или "sor". Возвращает U, историю невязки и снимок U при k = snap_at.
    """
    U = np.zeros((n + 1, n + 1))
    U[n, :] = 1.0                                            # верхняя сторона (j = n)
    omega = 2 / (1 + np.sin(PI / n)) if method == "sor" else 1.0   # оптимальное omega для SOR
    resid = lambda: np.linalg.norm(U[1:-1, 2:] + U[1:-1, :-2] + U[2:, 1:-1] + U[:-2, 1:-1] - 4 * U[1:-1, 1:-1]) / n
    hist, snap = [resid()], (U.copy() if snap_at == 0 else None)
    for k in range(1, K + 1):
        if method == "jacobi":                               # все новые значения -- по старым
            U[1:-1, 1:-1] = 0.25 * (U[1:-1, 2:] + U[1:-1, :-2] + U[2:, 1:-1] + U[:-2, 1:-1])
        else:                                                # Гаусс-Зейдель / SOR: сразу берём свежие значения
            for j in range(1, n):
                for i in range(1, n):
                    avg = 0.25 * (U[j, i + 1] + U[j, i - 1] + U[j + 1, i] + U[j - 1, i])
                    U[j, i] += omega * (avg - U[j, i])
        hist.append(resid())
        if k == snap_at:
            snap = U.copy()
    return U, np.array(hist), snap
