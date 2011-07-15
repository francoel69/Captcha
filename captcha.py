# -*- coding: utf-8 -*-
import Image
import ImageFilter
import random
import math
import os


class InCaptcha():
    """ Clase para tratar captchas. """

    def __init__(self, name):
        self.incap = Image.open(name)
        self.nx, self.ny = self.incap.size
        self.limites = []
        self.letras = []

    def quitarRuido(self):
        self.incap = self.incap.filter(ImageFilter.ModeFilter())
        colors = self.incap.getcolors()
        colors.sort(reverse=True)
        colors = map(lambda (x, y): y, colors[:6])
        for x in range(self.nx):
            for y in range(self.ny):
                t = self.incap.getpixel((x, y))
                if not t in colors:
                    self.incap.putpixel((x, y), (255, 255, 255))
        self.dividir()

    def __proxcolumnacolor(self, desde):
        x, cond = desde, True
        while (x < self.nx) and cond:
            y = 0
            while (y < self.ny) and cond:
                r, g, b = self.incap.getpixel((x, y))
                if(r + g + b != (255 * 3)):
                    cond, ret = False, x
                y += 1
            x += 1
        if x == self.nx and cond:
            raise Warning("Imagen complicada.")
        return ret

    def __ultimacolumnacolor(self, desde):
        x, cond = desde, True
        while (x < self.nx) and cond:
            y, cond2 = 0, True
            while (y < self.ny) and cond2:
                r, g, b = self.incap.getpixel((x, y))
                if(r + g + b != (255 * 3)):
                    cond2 = False
                y += 1
            if(y == self.ny):
                cond, ret = False, x - 1
            x += 1
        if (x == self.nx):
            ret = x - 1
        return ret

    def __primerfilacolor(self, xdesde, xhasta):
        y, cond = 0, True
        while (y < self.ny) and cond:
            x = xdesde
            while (x < xhasta) and cond:
                r, g, b = self.incap.getpixel((x, y))
                if(r + g + b != (255 * 3)):
                    cond, ret = False, y
                x += 1
            y += 1
        return ret

    def __ultimafilacolor(self, xdesde, xhasta, ydesde):
        y, cond = ydesde, True
        while(y < self.ny) and cond:
            x, cond2 = xdesde, True
            while(x <= xhasta) and cond2:
                r, g, b = self.incap.getpixel((x, y))
                if(r + g + b != (255 * 3)):
                    cond2 = False
                else:
                    x += 1
            if(cond2):
                cond, ret = False, y - 1
            y += 1
        if (y == self.ny):
            ret = y - 1
        return ret

    def dividir(self, cant=5):
        left, right = 0, -1
        for i in range(cant):
            left = self.__proxcolumnacolor(right + 1)
            right = self.__ultimacolumnacolor(left)
            upper = self.__primerfilacolor(left, right)
            lower = self.__ultimafilacolor(left, right, upper)
            self.limites.append((left, upper, right, lower))

    def separar(self):
        for i in range(5):
            self.letras.append(Letra(self.incap, self.limites[i]))

    def save(self, filename, *args, **kwds):
        self.incap.save(filename, *args, **kwds)

    def show(self):
        self.incap.show()


class Letra():
    """ Clase para tratar las letras por separado. """

    xmax, ymax = 16, 16

    def __init__(self, im, box):
        self.region = im.crop(box)

    def resize(self, (x, y)=(xmax, ymax)):
        self.region = self.region.resize((x, y))

    def rellenarvector(self):
        self.matriz = []
        for x in range(0, self.xmax):
            for y in range(0, self.ymax):
                r, g, b = self.region.getpixel((x, y))
                if(r + g + b != (255 * 3)):
                    self.matriz.append(int(1))
                else:
                    self.matriz.append(int(0))


inputs = 256
c_ocultas = 1
n_ocultas = 24
outputs = 36
eta = 0.2
error_t = 0.1


def inicializar_inputs(im):
    xi = []
    cap = InCaptcha(im)
    cap.quitarRuido()
    cap.separar()
    for i in range(5):
        cap.letras[i].resize()
        cap.letras[i].rellenarvector()
        xi.append(cap.letras[i].matriz)
    return xi


def inicializar_pesos(filas, columnas, file):
    w = []
    try:
        f = open(file, "r")
    except IOError:
        for i in range(filas):
            fila = []
            for j in range(columnas):
                fila.append(random.uniform(-0.05, 0.05))
            w.append(fila)
    else:
        l = f.readlines()
        f.close()
        for i in range(filas):
            w.append(map(lambda x: float(x), l[i].split()))
    return w


def obtener_output(l):
    out = ord(l)
    if (48 <= out <= 57):
        pos = out - 48
    elif (65 <= out <= 90):
        pos = out - 55
    letra = [0 for x in range(outputs)]
    letra[pos] = 1
    return letra


def output_correcto(im):
    hash = open("./samples/captcha_samples_lib_03/hash.txt", "r")
    dic = dict(map(lambda l: l.split('\t'), hash.readlines()))
    hash.close()
    z = []
    for l in dic.get(im).strip():
        z.append(obtener_output(l))
    return z


def calcular_h1(w, xi, n):
    h1 = []
    for i in range(n_ocultas):
        sum = 0.0
        for j in range(inputs):
            sum += xi[n][j] * w[i][j]
        h1.append(sum)
    return h1


def calcular_h2(h1, w2):
    h2 = []
    for i in range(outputs):
        sum = 0.0
        for j in range(n_ocultas):
            sum += g(h1[j]) * w2[i][j]
        h2.append(sum)
    return h2


def computar_delta2(h2, z):
    d2 = []
    for i in range(outputs):
        d2.append(gp(h2[i]) * (z[i] - g(h2[i])))
    return d2


def computar_delta1(h1, w2, d2):
    d1 = []
    for i in range(n_ocultas):
        sum = 0.0
        for j in range(outputs):
            sum += w2[j][i] * d2[j]
        d1.append(gp(h1[i]) * sum)
    return d1


def actualizar_w1(w1, d1, xi, n):
    for i in range(n_ocultas):
        for j in range(inputs):
            w1[i][j] += eta * d1[i] * xi[n][j]


def actualizar_w2(w2, d2, h1):
    for i in range(outputs):
        for j in range(n_ocultas):
            w2[i][j] += eta * d2[i] * g(h1[j])


def actualizar_archivo(w, file):
    filas = len(w)
    f = open(file, "w")
    for i in range(filas):
            f.writelines(map(lambda a: repr(a) + " ", w[i]))
            f.write("\n")
    f.close()


def g(x):
    return (1.0 / (1.0 + math.exp(-x)))


def gp(x):
    return (g(x) * (1.0 - g(x)))


def error_ok(h2, z):
    lista = []
    for i in range(outputs):
        lista.append(abs(g(h2[i]) - z[i]))
    return any(map(lambda x: x>error_t, lista))


def representante(gh2):
    pmax = gh2.index(max(gh2))
    if 0<= pmax <= 9:
        ret = repr(pmax)
    else:
        ret = chr(pmax + 55)
    return ret


def process(im):
    w = inicializar_pesos(n_ocultas, inputs, "../pesos.txt")
    w2 = inicializar_pesos(outputs, n_ocultas, "../pesos2.txt")
    ret = []
    xi = inicializar_inputs(im)
    for i in range(5):
        first = False
        h1 = calcular_h1(w, xi, i)
        h2 = calcular_h2(h1, w2)
        ret.append(representante(map(g, h2)))
    return ret


def modify(im, out):
    w = inicializar_pesos(n_ocultas, inputs, "../pesos.txt")
    w2 = inicializar_pesos(outputs, n_ocultas, "../pesos2.txt")
    xi = inicializar_inputs(im)
    for i in range(5):
        zi = obtener_output(out[i])
        h1 = calcular_h1(w, xi, i)
        h2 = calcular_h2(h1, w2)
        d2 = computar_delta2(h2, zi)
        d1 = computar_delta1(h1, w2, d2)
        actualizar_w1(w, d1, xi, i)
        actualizar_w2(w2, d2, h1)
    actualizar_archivo(w, "../pesos.txt")
    actualizar_archivo(w2, "../pesos2.txt")
    return process(im)


def train(folder):
    w = inicializar_pesos(n_ocultas, inputs, "./pesos.txt")
    w2 = inicializar_pesos(outputs, n_ocultas, "./pesos2.txt")

    files = os.walk(folder).next()[2]
    if '.directory' in files:
        files.remove('.directory')
    if 'hash.txt' in files:
        files.remove('hash.txt')
    count = 0
    for im in files:
        count += 1
        try:
            xi = inicializar_inputs(folder + im)
            z = output_correcto(im)
        except (Warning, AttributeError) as detail:
            print im, count, detail
        else:
            print im, count
            for i in range(5):
                first = True
                while first or error_ok(h2, z[i]):
                    first = False
                    h1 = calcular_h1(w, xi, i)
                    h2 = calcular_h2(h1, w2)
                    d2 = computar_delta2(h2, z[i])
                    d1 = computar_delta1(h1, w2, d2)
                    actualizar_w1(w, d1, xi, i)
                    actualizar_w2(w2, d2, h1)
    actualizar_archivo(w, "./pesos.txt")
    actualizar_archivo(w2, "./pesos2.txt")

#def main():
#    w = inicializar_pesos(n_ocultas, inputs, "./pesos.txt")
#    w2 = inicializar_pesos(outputs, n_ocultas, "./pesos2.txt")
#
#    files = os.walk("./samples/captcha_samples_lib_03").next()[2]
#    if '.directory' in files:
#        files.remove('.directory')
#    files.remove('hash.txt')
#    count = 0
#    for im in files:
#        print im, count
#        count += 1
#        try:
#            xi = inicializar_inputs("./samples/captcha_samples_lib_03/" + im)
#            z = output_correcto(im)
#        except (Warning, AttributeError) as detail:
#            print "Imagen ", im, ": ", detail
#        else:
#            for i in range(5):
#                print im, i
#                first = True
#                while first or error_ok(h2, z[i]):
#                    first = False
#                    h1 = calcular_h1(w, xi, i)
#                    h2 = calcular_h2(h1, w2)
#                    d2 = computar_delta2(h2, z[i])
#                    d1 = computar_delta1(h1, w2, d2)
#                    actualizar_w1(w, d1, xi, i)
#                    actualizar_w2(w2, d2, h1)
#                print representante(map(g, h2))
#            actualizar_archivo(w, "./pesos.txt")
#            actualizar_archivo(w2, "./pesos2.txt")
#    xi = inicializar_inputs("./images/simples/pocas/conocido_01.bmp")
#    for i in range(5):
#        h1 = calcular_h1(w, xi, i)
#        h2 = calcular_h2(h1, w2)
#        print "conocido_01: ", i
#        print representante(map(g, h2))
