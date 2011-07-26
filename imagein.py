# -*- coding: utf-8 -*-
import Image
import ImageFilter

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
        colors.remove((255, 255, 255))
        self.dividir(colors)

    def __proxcolumnacolor(self, desde, colors):
        x, cond = desde, True
        while (x < self.nx) and cond:
            y = 0
            while (y < self.ny) and cond:
                t = self.incap.getpixel((x, y))
                if t in colors:
                    cond, ret = False, x
                y += 1
            x += 1
#        if x == self.nx and cond:
#            raise Warning("Imagen complicada.")
        return (ret, t)

    def __ultimacolumnacolor(self, desde, color):
        x, cond = desde, True
        while (x < self.nx) and cond:
            y, cond2 = 0, True
            while (y < self.ny) and cond2:
                t = self.incap.getpixel((x, y))
                if(t == color):
                    cond2 = False
                y += 1
            if(y == self.ny):
                cond, ret = False, x - 1
            x += 1
        if (x == self.nx):
            ret = x - 1
        return ret

    def __primerfilacolor(self, xdesde, xhasta, color):
        y, cond = 0, True
        while (y < self.ny) and cond:
            x = xdesde
            while (x <= xhasta) and cond:
                t = self.incap.getpixel((x, y))
                if(t == color):
                    cond, ret = False, y
                x += 1
            y += 1
        return ret

    def __ultimafilacolor(self, xdesde, xhasta, ydesde, color):
        y, cond = ydesde, True
        while(y < self.ny) and cond:
            x, cond2 = xdesde, True
            while(x <= xhasta) and cond2:
                t = self.incap.getpixel((x, y))
                if(t == color):
                    cond2 = False
                else:
                    x += 1
            if(cond2):
                cond, ret = False, y - 1
            y += 1
        if (y == self.ny):
            ret = y - 1
        return ret

    def dividir(self, colors):
        left = 0
        for i in range(5):
            left, color = self.__proxcolumnacolor(left, colors)
            colors.remove(color)
            right = self.__ultimacolumnacolor(left, color)
            upper = self.__primerfilacolor(left, right, color)
            lower = self.__ultimafilacolor(left, right, upper, color)
            self.limites.append((left, upper, right + 1, lower + 1))

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
        colors = self.region.getcolors()
        colors.sort(reverse=True)
        color = colors[0][1]
        if color == (255, 255, 255):
            color = colors[1][1]
        self.color = color

    def resize(self, (x, y)=(xmax, ymax)):
        self.region = self.region.resize((x, y))

    def rellenarvector(self):
        self.matriz = []
        for x in range(0, self.xmax):
            for y in range(0, self.ymax):
                t = self.region.getpixel((x, y))
                if(t == self.color):
                    self.matriz.append(int(1))
                else:
                    self.matriz.append(int(0))

