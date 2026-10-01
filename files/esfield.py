# -*- coding: utf-8 -*-
"""esfield.py -- маленькая библиотека для расчёта электростатических полей.
Единицы: если не сказано иное, eps0 = 1 (потенциал в единицах Q/eps0/длина и т.п.)."""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
EPS0 = 8.8541878128e-12          # электрическая постоянная, Ф/м

# ---------------------------------------------------------------- 2D: схема «крест»
def solve_poisson_2d(fixed, U_fixed, h, eps=None, rho=None):
    """Уравнение div(eps grad U) = -rho на квадратной сетке с шагом h (схема «крест»).
    fixed   -- булев массив: True там, где потенциал задан (проводники, рамка);
    U_fixed -- массив с этими значениями (в остальных узлах игнорируется);
    eps     -- массив проницаемости в узлах (по умолчанию 1);
    rho     -- массив плотности заряда (по умолчанию 0).
    Внешний слой узлов должен быть в fixed. Возвращает массив U."""
    if eps is None:
        eps = np.ones(fixed.shape)
    free = ~fixed
    number = -np.ones(fixed.shape, dtype=int)
    number[free] = np.arange(free.sum())            # номер неизвестной в системе
    J, I = np.nonzero(free)                         # индексы неизвестных узлов
    n = len(J)
    diag = np.zeros(n)
    rhs = np.zeros(n) if rho is None else h * h * rho[free]
    rows, cols, vals = [], [], []
    for dj, di in ((0, 1), (0, -1), (1, 0), (-1, 0)):        # четыре соседа
        e1, e2 = eps[J, I], eps[J + dj, I + di]
        w = 2 * e1 * e2 / (e1 + e2)                 # вес соседа (среднее гармоническое)
        diag += w
        # номер соседа (или -1, если он задан)
        k = number[J + dj, I + di]
        unknown = k >= 0
        rows.append(np.nonzero(unknown)[0])
        cols.append(k[unknown]); vals.append(-w[unknown])
        rhs[~unknown] += w[~unknown] * U_fixed[(J + dj)[~unknown], (I + di)[~unknown]]
    rows.append(np.arange(n)); cols.append(np.arange(n)); vals.append(diag)
    A = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows),
    np.concatenate(cols))), shape=(n, n))
    U = np.where(fixed, U_fixed, 0.0)
    U[free] = spla.spsolve(A.tocsc(), rhs)
    return U

def field_2d(U, h):
    """Поле E = -grad U по центральным разностям (в граничных узлах ноль)."""
    Ex = np.zeros_like(U); Ey = np.zeros_like(U)
    Ex[:, 1:-1] = -(U[:, 2:] - U[:, :-2]) / (2 * h)
    Ey[1:-1, :] = -(U[2:, :] - U[:-2, :]) / (2 * h)
    return Ex, Ey

def energy_2d(U, h, eps=None):
    """Энергия поля на единицу длины: W = 1/2 * sum eps * (dU)^2 по рёбрам сетки
    (eps0=1)."""
    if eps is None:
        eps = np.ones(U.shape)
    ex = 0.5 * (eps[:, 1:] + eps[:, :-1]); ey = 0.5 * (eps[1:, :] + eps[:-1, :])
    return 0.5 * (np.sum(ex * np.diff(U, axis=1) ** 2)
                  + np.sum(ey * np.diff(U, axis=0) ** 2))

def grid(L, h):
    """Квадратная сетка [-L, L]^2 с шагом h: возвращает X, Y (индексы: [строка y,
    столбец x])."""
    n = int(round(2 * L / h))
    x = -L + h * np.arange(n + 1)
    return np.meshgrid(x, x)

# ---------------------------------------------------------------- 1D: радиальные и
# слоистые задачи
def solve_radial(m, a, b, N, eps, rho, flux_a, U_b):
    """Одномерная задача (1/r^m) d/dr (r^m eps dU/dr) = -rho на отрезке [a, b], N ячеек.
    m = 0 плоская, 1 цилиндрическая, 2 сферическая симметрия.
    eps(r), rho(r) -- функции; flux_a = r^m eps dU/dr при r = a (для оси или центра =
    0);
    U_b -- потенциал при r = b. Возвращает узлы r и потенциал U (схема «взвешенного
    среднего»)."""
    r = np.linspace(a, b, N + 1); h = (b - a) / N
    rf = 0.5 * (r[1:] + r[:-1])                      # грани между узлами
    g = rf ** m * eps(rf) / h                        # «проводимость» грани
    main = np.zeros(N + 1); main[:-1] += g; main[1:] += g
    A = sp.diags([-g, main, -g], [-1, 0, 1], format="lil")
    # заряд ячейки: интеграл rho * r^m dr по ячейке (две половины, квадратура Гаусса).
    # Считать заряд как «rho в узле * объём» нельзя: если граница заряженной области
    # лежит
    # внутри ячейки, порядок точности упадёт с 2 до 1.
    xg, wg = np.polynomial.legendre.leggauss(6)
    rhs = np.zeros(N + 1)
    for lo_off, hi_off in ((-0.5, 0.0), (0.0, 0.5)):
        lo = np.clip(r + lo_off * h, a, b); hi = np.clip(r + hi_off * h, a, b)
        for xq, wq in zip(xg, wg):
            rq = 0.5 * (hi + lo) + 0.5 * (hi - lo) * xq
            rhs += 0.5 * (hi - lo) * wq * rho(rq) * rq ** m
    rhs[0] += -flux_a                                # заданный поток на левом конце
    A[-1, :] = 0; A[-1, -1] = 1; rhs[-1] = U_b       # потенциал на правом конце
    return r, spla.spsolve(A.tocsc(), rhs)

def gradient_1d(r, U):
    """E = -dU/dr по центральным разностям."""
    return -np.gradient(U, r, edge_order=2)

# ---------------------------------------------------------------- метод фиктивных
# зарядов
def fibonacci_sphere(n, R):
    """n почти равномерно распределённых точек на сфере радиуса R (спираль
    Фибоначчи)."""
    k = np.arange(n) + 0.5
    z = 1 - 2 * k / n
    r = np.sqrt(1 - z * z); phi = np.pi * (3 - 5 ** 0.5) * k
    return R * np.c_[r * np.cos(phi), r * np.sin(phi), z]
# ---------------------------------------------------------------- печать сравнения
def report(title, rows):
    """rows: список (что сравниваем, аналитика, модель). Печатает таблицу с
    отклонением."""
    print(title)
    print("%-38s %14s %14s %10s" % ("величина", "аналитика", "модель", "откл., %"))
    for name, a, m in rows:
        dev = 100 * abs(m - a) / abs(a) if a != 0 else abs(m)
        print("%-38s %14.6g %14.6g %10.4f" % (name, a, m, dev))
