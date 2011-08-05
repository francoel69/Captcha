# -*- coding: utf-8 -*-
import random
import math
import imagein

inputs = 256
c_ocultas = 1
n_ocultas = 24
outputs = 36
eta = 0.2
error_t = 0.1

def g(x):
    return (1.0 / (1.0 + math.exp(-x)))


def gp(x):
    return (g(x) * (1.0 - g(x)))

# Make a matrix IxJ.
def makeMatrix(I, J, fill=0.0):
    m = []
    for i in range(I):
        m.append([fill]*J)
    return m


class Net:
    """ Clase contenedora de las redes neuronales. """

    def __init__(self):
        # Number of input, hidden, and output nodes.
        self.ni = inputs
        self.nh = n_ocultas
        self.no = outputs

        # Activations for nodes.
        self.hi = [1.0]*self.ni
        self.hh = [1.0]*self.nh
        self.ho = [1.0]*self.no

        # Set weights.
        self.wi = setWeights(self.nh, self.ni, "../pesos.txt")
        self.wo = setWeights(self.no, self.nh, "../pesos2.txt")

        # Last change in weights for momentum.
        self.ci = makeMatrix(self.nh, self.ni)
        self.co = makeMatrix(self.no, self.nh)

    def update(self, inputs):
        if len(inputs) != self.ni:
            raise ValueError('Wrong number of inputs.')

        # Input activations.
        for i in range(self.ni):
            self.hi[i] = inputs[i]

        # Hidden activations.
        for j in range(self.nh):
            sum = 0.0
            for i in range(self.ni):
                sum = sum + self.hi[i] * self.wi[j][i]
            self.hh[j] = sum

        # Output activations.
        for k in range(self.no):
            sum = 0.0
            for j in range(self.nh):
                sum = sum + g(self.hh[j]) * self.wo[k][j]
            self.ho[k] = sum

        return maxout(map(g, self.ho))

    def backPropagate(self, targets, N, M):
        if len(targets) != self.no:
            raise ValueError('Wrong number of target values.')

        # calculate error terms for output
        output_deltas = [0.0] * self.no
        for k in range(self.no):
            error = targets[k]-g(self.ho[k])
            output_deltas[k] = gp(self.ho[k]) * error

        # calculate error terms for hidden
        hidden_deltas = [0.0] * self.nh
        for j in range(self.nh):
            error = 0.0
            for k in range(self.no):
                error = error + output_deltas[k]*self.wo[k][j]
            hidden_deltas[j] = gp(self.hh[j]) * error

        # update output weights
        for j in range(self.nh):
            for k in range(self.no):
                change = output_deltas[k]*g(self.hh[j])
                self.wo[k][j] = self.wo[k][j] + N*change + M*self.co[k][j]
                self.co[k][j] = change
                #print N*change, M*self.co[j][k]

        # update input weights
        for i in range(self.ni):
            for j in range(self.nh):
                change = hidden_deltas[j]*self.hi[i]
                self.wi[j][i] = self.wi[j][i] + N*change + M*self.ci[j][i]
                self.ci[j][i] = change

        # calculate error
        error = 0.0
        for k in range(len(targets)):
            error = error + 0.5*(targets[k]-g(self.ho[k]))**2
        return error

    def test(self, patterns):
        for p in patterns:
            print p[0], '->', self.update(p[0])

    def weights(self):
        print('Input weights:')
        for i in range(self.ni):
            print(self.wi[i])
        print()
        print('Output weights:')
        for j in range(self.nh):
            print(self.wo[j])

    def error_ok(self, targets):
        lista = []
        for i in range(self.no):
            lista.append(abs(g(self.ho[i]) - targets[i]))
        return any(map(lambda x: x>error_t, lista))

    def train(self, files, folder, iterations=50, N=0.5, M=0.9):
        # N: learning rate
        # M: momentum factor
        dic = targetDic(folder)
        k = 0
        cant = len(files)
        error = 0.05*cant + 1.0
        while error/cant > 0.05:
            k += 1
            error = 0.0
            for im in files:
                if dic.has_key(im):
                    xi = getInputs(folder + "/" + im)
                    for i in range(5):
                        targets = getTarget(dic.get(im)[i])
                    #first = True
                    #while first or self.error_ok(targets):
                        #first = False
                        self.update(xi[i])
                        error = error + self.backPropagate(targets, N, M)
            print k, '\t', error/cant
        print u"Terminó de entrenar"


def getInputs(im):
    xi = []
    cap = imagein.InCaptcha(im)
    cap.quitarRuido()
    cap.separar()
    for i in range(5):
        cap.letras[i].resize()
        cap.letras[i].rellenarvector()
        xi.append(cap.letras[i].matriz)
    return xi


def setWeights(nrows, ncols, file):
    w = []
    try:
        f = open(file, "r")
    except IOError:
        for i in range(nrows):
            row = []
            for j in range(ncols):
                row.append(random.uniform(-0.1, 0.1))
            w.append(row)
    else:
        l = f.readlines()
        f.close()
        for i in range(nrows):
            w.append(map(lambda x: float(x), l[i].split()))
    return w


def getTarget(l):
    out = ord(l)
    if (48 <= out <= 57):
        pos = out - 48
    elif (65 <= out <= 90):
        pos = out - 55
    letra = [0 for x in range(outputs)]
    letra[pos] = 1
    return letra


def targetDic(folder):
    hash = open(folder + "/hash.txt", "r")
    dic = dict(map(lambda l: l.split('\t'), hash.readlines()))
    hash.close()
    return dic


def updateFile(w, file):
    filas = len(w)
    f = open(file, "w")
    for i in range(filas):
            f.writelines(map(lambda a: repr(a) + " ", w[i]))
            f.write("\n")
    f.close()


def maxout(gh2):
    pmax = gh2.index(max(gh2))
    if 0<= pmax <= 9:
        ret = repr(pmax)
    else:
        ret = chr(pmax + 55)
    return ret


#def process(im):
    #w = inicializar_pesos(n_ocultas, inputs, "../pesos.txt")
    #w2 = inicializar_pesos(outputs, n_ocultas, "../pesos2.txt")
    #ret = []
    #xi = inicializar_inputs(im)
    #for i in range(5):
        #h1 = calcular_h1(w, xi, i)
        #h2 = calcular_h2(h1, w2)
        #ret.append(representante(map(g, h2)))
    #return ret


#def modify(im, out):
    #w = inicializar_pesos(n_ocultas, inputs, "../pesos.txt")
    #w2 = inicializar_pesos(outputs, n_ocultas, "../pesos2.txt")
    #xi = inicializar_inputs(im)
    #for i in range(5):
        #zi = obtener_output(out[i])
        #h1 = calcular_h1(w, xi, i)
        #h2 = calcular_h2(h1, w2)
        #d2 = computar_delta2(h2, zi)
        #d1 = computar_delta1(h1, w2, d2)
        #actualizar_w1(w, d1, xi, i)
        #actualizar_w2(w2, d2, h1)
    #actualizar_archivo(w, "../pesos.txt")
    #actualizar_archivo(w2, "../pesos2.txt")
