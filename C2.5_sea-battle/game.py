get_ipython().run_cell_magic('javascript', '', 'IPython.OutputArea.prototype._should_scroll = function(lines) {return false;}')

from IPython.display import clear_output
from random import choice, shuffle

class Config():   
    def __init__(self, size = 6, ships_num = 7):
        self.size      = size
        self.ships_num = ships_num
        
        self.values   = [str(i) for i in range(1, size+1)]        
        self.all_dots = [i      for i in range(1, size**2+1)]
        p2c = {}  #Перевод номера элемента доски в его координаты
        c2p = {}  #Перевод координат элемента доски в ее номер
        for i in range(1, size+1):
            for j in range(1, size+1):
                tmp = (i-1)*size + j
                p2c[tmp] = (i,j)
                c2p[(i,j)] = tmp
        self.p2c = p2c
        self.c2p = c2p       

config = Config() 

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за доску!'

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Dot():                        # row - x
    def __init__(self, row, col):   # col - y             
        self.row = row
        self.col = col
    
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col     

    def __repr__(self):       
        return f'({self.row}, {self.col})'

class Ship():
    def __init__(self, bow, lenght, direct):  
        self.bow    = bow         # bow - точка носа корабля (объект класса Dot)                               
        self.lenght = lenght      # lenght - длина корабля (3,2,2,1,1,1,1)
        self.direct = direct      # direct - направление оси корабля от носа  
        self.lives  = lenght      # (0,1,2,3 = вправо, вниз, влево, вверх
 
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.lenght):
            bow_row = self.bow.row 
            bow_col = self.bow.col
            
            if self.direct   == 0: # вправо
                bow_col += i                
            elif self.direct == 1: # вниз
                bow_row += i
            elif self.direct == 2: # влево
                bow_col -= i           
            elif self.direct == 3: # вверх
                bow_row -= i            
            
            ship_dots.append(Dot(bow_row, bow_col))
        return ship_dots
    
class Board():
    def __init__(self, hid = False, size = config.size):
        self.size = size
        self.hid  = hid
        
        self.field = [ ["o"]*size for _ in range(size) ]  # Поле доски        
        self.count = 0  # Количество живых кораблей на доске
        
        self.busy  = []  # Список всех занятых позиций
        self.ships = []  # Список всех кораблей на доске
    #----------------------------------------------------    
    def add_ship(self, ship):
        near = [                            # Соседи заданной точки
            (-1, -1), (-1, 0) , (-1, 1),           
            ( 0, -1),           ( 0, 1),
            ( 1, -1), ( 1, 0) , ( 1, 1) ]        
              
        for d in ship.dots:               
            if self.out(d) or d in self.busy:
                return False
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()

        for d in ship.dots:          
            for dx, dy in near:
                cur = Dot(d.row + dx, d.col + dy)
                if (1 <= cur.row <= self.size) and (1 <= cur.col <= self.size):
                    if cur not in self.busy:
                        self.busy.append(cur)
                
        for d in ship.dots:
            self.field[d.row-1][d.col-1] = '■'
            if d not in self.busy:
                self.busy.append(d)            
    
        self.ships.append(ship)
        
        return True  
    #----------------------------------------------------            
    def contour(self, ship, verb = False):
        near = [                            # Соседи заданной точки
            (-1, -1), (-1, 0) , (-1, 1),           
            ( 0, -1),           ( 0, 1),
            ( 1, -1), ( 1, 0) , ( 1, 1) ]

        for d in ship.dots:          
            for dx, dy in near:
                cur = Dot(d.row + dx, d.col + dy)
                if not(self.out(cur)) and cur not in self.busy:                  
                    if verb:
                        self.field[cur.row-1][cur.col-1] = "."
    #----------------------------------------------------     
    def out(self, d):
        return not((1 <= d.row <= self.size) and (1 <= d.col <= self.size))
    #----------------------------------------------------    
    def shot(self, d):           
        if d in self.busy:
            raise BoardUsedException()
        
        self.busy.append(d)
        
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.row-1][d.col-1] = '+'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)                                    
                    print('Корабль уничтожен!')

                    for x in ship.dots:
                        self.field[x.row-1][x.col-1] = 'X'           
                    return True
                else:                  
                    print('Корабль ранен!')
                    return True

        self.field[d.row-1][d.col-1] = 'T'
        print('Мимо!')
        return False
    #----------------------------------------------------    
    def begin(self):
        self.busy = []
    #----------------------------------------------------
    def __str__(self):
        print('  ====================')       
        res = ''
        res +=   '  | 1  2  3  4  5  6 |'
        res += '\n--|------------------|'
        
        for i, row in enumerate(self.field):
            res += f'\n{i+1} | ' + '  '.join(row) + ' |'        
        if self.hid:
            res = res.replace('■', 'o')
        return res

class Players():
    def __init__(self, board, enemy):
        self.board  = board
        self.enemy  = enemy
    
    def ask(self):
        raise NotImplementedError()
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)              
                return repeat
            except BoardException as e:
                print(e)

class Enemy(Players):
    tmp = config.all_dots.copy()
    p2c = config.p2c
    c2p = config.c2p

    def ask(self, tmp=tmp, p2c=p2c, c2p=c2p):            
        rand_num = choice(tmp)
        tmp.remove(rand_num)
        rand_dot = p2c[rand_num]
        p = Dot(rand_dot[0],rand_dot[1])

        for x in self.enemy.busy:
            z = c2p[(x.row, x.col)]       
            if z in tmp: tmp.remove(z)

            if tmp == []:
                print('Противник израсходовал все ходы')
                break
        
        print('Противник пошел:', rand_dot[0], rand_dot[1])
        return p 

class User(Players):     
    values = config.values

    def ask(self, values=values):
        rezult = True
        while rezult:
            tmp = input('Ваш  ход: ')
            while True:
                if tmp[1] != ' ':
                    print('Ошибка ввода: Второй символ должен быть пробелом')
                    break
        
                if not (tmp[0] in values and tmp[2] in values):
                    print('Ошибка ввода: 1-ый и 3-ий символы должены быть цифрами'+'в диапазоне [1-6], у Вас:', tmp)
                    break
        
                rezult = False
                break
        
        row, col = tmp[:3].split()
        row = int(row)
        col = int(col)

        print('*'*22)
        print('Вы пошли:', row, col)        
            
        return Dot(row, col)

class Game():
    def __init__(self, mode, size = config.size):
        self.size = size
        us = self.random_board()
        en = self.random_board()
        en.hid = mode          # True  - содержимое доски противника скрыто
                               # False - содержимое доски противника открыто
        self.us = User( us, en)
        self.en = Enemy(en, us)
    #------------------------------------------------------------       
    def random_board(self):
        p2c = config.p2c
        c2p = config.c2p
        bow = [0,1,2,3]
        n = 0
        while True:
            n += 1 
            for ship_len in [3,2,2,1,1,1,1]:
                if ship_len == 3:
                    tmp = config.all_dots.copy()
                    b = Board()
                rand_num = choice(tmp)
                tmp.remove(rand_num)
                rand_dot = p2c[rand_num]
                row = rand_dot[0]
                col = rand_dot[1]
                p = Dot(row, col)   
       
                shuffle(bow)
                for i in bow:
                    ship = Ship(Dot(row,col), ship_len, i)
                    st = b.add_ship(ship)
                    if st == True: break
                if st == False: break
               
                for x in b.busy:
                    z = c2p[(x.row, x.col)]       
                    if z in tmp: tmp.remove(z)    
                if len(tmp) == 0: break  

            if len(b.ships) == config.ships_num: break
            if n == 100: break
        b.begin()
        return b
    #------------------------------------------------------------
    def greet(self):
        print(' '*3+'-------------------')
        print(' '*3+'  Приветсвуем вас  ')
        print(' '*3+'      в игре       ')
        print(' '*3+'    морской бой    ')
        print(' '*3+'-------------------')
        print(' '*3+' формат ввода: x y ')
        print(' '*3+' x - номер строки  ')
        print(' '*3+' y - номер столбца ')
        print(' '*3+'-------------------')
        print()
    #------------------------------------------------------------     
    def loop(self):
        num = 0
        while True:           
            if num % 2 == 0:
                print('='*22)
                print('Ходит пользователь')
                print(' '*3 + 'Доска противника:')
                print(self.en.board)
                print('='*22)               
                repeat = self.us.move()
#                clear_output(True)
                print('='*22)
                print(' '*3 + 'Доска противника:')
                print(self.en.board)
                print('='*22)
            else:
                print('='*22)
                print('Ходит противник')
                print(' '*3 + 'Доска пользователя:')
                print(self.us.board)
                print('='*22)               
                repeat = self.en.move()
                print('='*22)
                print(' '*3 + 'Доска пользователя:')
                print(self.us.board)
                print('='*22) 
                
            if repeat:
                num -= 1     

            if self.en.board.count == config.ships_num:
                print('-'*22)
                print('Пользователь выиграл!\n')
                print(' '*3  + 'Доска противника')
                print(self.en.board)
                print('='*22)
                print(' '*3  + 'Доска пользователя')
                print(self.us.board)
                print('='*22)
                break
            
            if self.us.board.count == config.ships_num:
                print('-'*22)
                print('Противник выиграл!\n')
                print(' '*3  + 'Доска пользователя')
                print(self.us.board)
                print('='*22)
                print(' '*3  + 'Доска противника')
                print(self.en.board)
                print('='*22)
                break
            num += 1
    #------------------------------------------------------------                  
    def start(self):
        self.greet()
        self.loop()

g = Game(mode=False) # True  - содержимое доски противника скрыто (рабочий вариант)
g.start()            # False - содержимое доски противника открыто (отладочный вариант)

