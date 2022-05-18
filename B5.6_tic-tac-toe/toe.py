
from IPython.display import clear_output

# Матрица ходов (state[0] - крестики, state[1] - нулики)
state = [[0 for i in range(9)] for i in range(2)]
# Общая картина игры
field = [i for i in range(1,10)]
# Максимальный результат для всех выигрышных срезов 
out   = [0 for i in range(2)]
# Идентификатов игрока (0 - крестик, 1 - нулик)
person = [0,1]
# Обозначения игроков при выводе результатов на общую картину игры
output = ['+','-']
# Максимальные результаты игроков
rezult = [0,0]

# Выигрышные срезы (три горизонтальных, три вертикальных и два диагональных)
tmp = ((0,3,1),(3,6,1),(6,9,1),       (0,9,3),(1,9,3),(2,9,3),       (0,9,4),(2,8,2))

# Начальная инициализация переменных
state  = [[0 for i in range(9)] for i in range(2)]
field  = [str(i) for i in range(1,10)]
out    = [0 for i in range(2)]
person = [0,1]
rezult = [0,0]
output = ['x','o']

# Ход игры
while True:
    p = person[0]       

    # Вывод текущего поля игры на экран
    while True:
        for i in range(3):
            k = i*3
            print('{0} {1} {2}'.format(field[k],field[k+1],field[k+2]))
        
        clear_output(wait=True)            

        # Поочередные ходы игроков
        k = input("Ход '" + str(output[p]) + "': ")
        if (k in field) and (k!='x') and (k!='o'):
            k = int(k) - 1
            break
        else:
            print('\nНеправильный ввод')

    # Выполнение хода игрока
    state[p][k] = 1
    field[k]    = str(output[p])
    rezult[p]   = max(list(map(sum,[state[p][i:j:k] for i,j,k in tmp])))
    person      = person[::-1]
    print()

    # Анализ результата хода игрока
    if (rezult[0] == 3) or (rezult[1] == 3):
        print('Конец игры, выиграл ', "'"+output[p]+"'")
        break
    steps = sum([state[0][i] + state[1][i] for i in range(9)])
    if steps == 9:
        print('Конец игры, ничья')
        break

# Вывод финальной картины игры на экран
for i in range(3):
    k = i*3
    print('{0} {1} {2}'.format(field[k],field[k+1],field[k+2]))
