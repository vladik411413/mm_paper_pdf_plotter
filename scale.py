from math import *
import numpy as np

class Scale:
    def __init__(self, n, m, multiplier=0):
        self.n = n
        self.m = m
        self.mul = multiplier

    # Получить масштаб s из разложения в виде числа 
    # n - колво 2 в разложении
    # m - колво 5 в разложении
    @property
    def l(self):
        return (2 ** (self.n+self.mul))*(5 ** (self.m+self.mul))
    
    def __repr__(self):
        return f'{self.l}'
    
    # Получить следующий близжайший по возрастанию масштаб s
    # Получает близжайшее по length число подбором разложения 
    # Очевидно что максимум в два раза отличается след масштаб от предыдущего
    # Но на деле, в среднем гораздо меньше чем в два раза
    def next(self):    
        
        snew = Scale(self.n+1,self.m)
        
        for p in range(-self.m,floor((self.n+1)/log(5,2))+1):
            q = ceil(p*log(5,2))-1
            
            proposed_s = Scale(self.n-q,self.m+p)
            
            if (proposed_s.l < snew.l):
                snew = proposed_s
        
        return snew
        
class Axis:
    # lmax больше 1!!!
    def __init__(self, x, lmax):
        self.range = x
        self.lmax = lmax
        self.s_array = None
        self.s = None
        
    @property
    def power(self):
        return 10 ** floor(log10(self.range))
    @property 
    def alpha(self):
        return self.range / self.power
    @property
    def scale(self):
        return self.power/self.s.l
    @property
    def length(self):
        return self.alpha*self.s.l
    @property 
    def percentage(self):
        return self.length/self.lmax

    def __repr__(self):
        if not self.s:
            self.find_s()

        return f'Class Axis(\n\
                Range = {self.range:.6f},\n\
                L = {self.length:.1f},\n\
                S = {self.s},\n\
                Sarr = {self.s_array},\n\
                Scale = {self.scale} [units/mm] = {1/self.scale} [mm/unit],\n\
                Power = {self.power},\n\
                Q = {100*self.percentage:.0f}%)'

    # Получить все масштабы для данной длины оси (в mm) 
    def gen_s_array(self):
        self.s_array = [Scale(0,0)]
        s_last = self.s_array[-1]
        
        while(s_last.l/self.lmax < 1):
            s_last = s_last.next()
            # десятичный вид записи 1/s должен быть 1,2,4,5,25
            if (abs(s_last.m - s_last.n) > 2) :
                # фильтруем числа с плохой записью
                # print(f'bad s={s_last}')
                continue 
            # хорошие числа идут сюда
            self.s_array.append(s_last)
        self.s_array.pop()

    # Получить лучший масштаб для данной длины оси (в mm)
    # И для заданного диапазона физ.величины (xmax-xmin=x)
    def find_s(self):
        if not self.s_array:
            self.gen_s_array()
        
        for i in range(1,len(self.s_array)):

            percent = self.alpha*self.s_array[i].l/self.lmax
 
            if (percent >= 1):
                self.s = self.s_array[i-1]
                return self.s
        
        # Если мы здесь то percent не разу не был больше 1
        # Поэтому просто выбираем самый старший s
        self.s = self.s_array[-1]
        return self.s

class Graph:
    def __init__(self,range1,lmax1,range2,lmax2):
        self.ox = Axis(range1,lmax1)
        self.oy = Axis(range2,lmax2)
        self.ox.find_s()
        self.oy.find_s()

    def swap_axes(self):
        self.ox.range, self.oy.range = self.oy.range, self.ox.range
        self.ox.find_s()
        self.oy.find_s()

    @property 
    def area(self):
        return self.ox.length*self.oy.length

    @property 
    def percentage(self):
        return self.area / (self.ox.lmax*self.oy.lmax)

    def __repr__(self):
        return f'Class Graph(\n\
            Ox = {self.ox},\n\
            Oy = {self.oy},\n\
            Area = {self.area},\n\
            Q = {100*self.percentage:.2f}%)'
        

