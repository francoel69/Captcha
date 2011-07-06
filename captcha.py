# -*- coding: utf-8 -*-
import Image
import ImageFilter


class InCaptcha(Image.Image):
    """ Clase para tratar captchas. """

    def __init__(self, name):
        self.incap = Image.open(name)
        self.nx, self.ny = self.incap.size
        self.letras = []
        self.letra0, self.letra1, self.letra2 = [], [], []
        self.letra5, self.letra4 = [], []

    def quitarRuido(self):
        self.incap = self.incap.filter(ImageFilter.ModeFilter())

    def proxcolumnacolor(self, desde):
        x, cond = desde, True
        while (x < self.nx) and cond:
            y = 0
            while (y < self.ny) and cond:
                r, g, b = self.incap.getpixel((x, y))
                if(r + g + b != (255 * 3)):
                    cond, ret = False, x
                y += 1
            x += 1
        return ret

    def ultimacolumnacolor(self, desde):
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

    def primerfilacolor(self, xdesde, xhasta):
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

    def ultimafilacolor(self, xdesde, xhasta, ydesde):
        y, cond = ydesde, True
        while(y < self.ny) and cond:
            x, cond2 = xdesde, True
            while(x < xhasta) and cond2:
                r, g, b = self.incap.getpixel((x, y))
                if(r + g + b != (255 * 3)):
                    cond2 = False
                x += 1
            if(x == xhasta):
                cond, ret = False, y - 1
            y += 1
        if (y == self.ny):
            ret = y - 1
        return ret

    def dividir(self, cant=5):
        left, right = 0, -1
        for i in range(cant):
            left = self.proxcolumnacolor(right + 1)
            right = self.ultimacolumnacolor(left)
            upper = self.primerfilacolor(left, right)
            lower = self.ultimafilacolor(left, right, upper)
            self.letras.append((left, upper, right, lower))

    def armarmatriz(self, letra):
        matriz = []
        for y in range(letra[1], letra[3] + 1):
            fila = []
            for x in range(letra[0], letra[2] + 1):
                r, g, b = self.incap.getpixel((x, y))
                if(r + g + b != (255 * 3)):
                    fila.append(int(1))
                else:
                    fila.append(int(0))
            matriz.append(fila)
        return matriz

    def rellenarmatriz(self):
        self.letra0 = self.armarmatriz(self.letras[0])
        self.letra1 = self.armarmatriz(self.letras[1])
        self.letra2 = self.armarmatriz(self.letras[2])
        self.letra3 = self.armarmatriz(self.letras[3])
        self.letra4 = self.armarmatriz(self.letras[4])

    def save(self, filename, *args, **kwds):
        self.incap.save(filename, *args, **kwds)

    def show(self):
        self.incap.show()


class Letra(Image.Image):
    """ Clase para tratar las letras por separado. """

    def blancoynegro(self):
        for i in range(self.nx):
            for j in range(self.ny):
                r, g, b = self.incap.getpixel((i, j))
                if(r + g + b != (255 * 3)):
                    self.incap.putpixel((i, j), 0)

    def matriximag(self):
        matriz = []
        for i in range(self.nx):
            for j in range(self.ny):
                r, g, b = self.incap.getpixel((i, j))
                if(r + g + b != (255 * 3)):
                    matriz.append(int(1))
                else:
                    matriz.append(int(0))
        return matriz
