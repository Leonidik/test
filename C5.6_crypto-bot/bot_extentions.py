from bot_config import Config

import requests
import json
import telebot
import re

#====================================================== 
class APIException(Exception): 
    pass
#====================================================== 
class Function():   
    # Перевод латинских символов в кирилицу
    # (для случая набора русского текста на латинской раскладке клавиатуры)       
    @staticmethod
    def en2ru(chars):
        en_chars = u"~!@#$%^&qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?"
        ru_chars = u"ё!\"№;%:?йцукенгшщзхъфывапролджэячсмитьбю.ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"
        trans_table = dict(zip(en_chars, ru_chars))
        text = u''.join([trans_table.get(c, c) for c in chars])
        return text
    #-------------------------------------------------
    # Определение близости слов по метрике Левинштейна
    # Суммарное минимальное число вставок/удалений/замен символов в первом слове,
    # необходимых для того, чтобы оно превратилось во второе
    @staticmethod
    def ld(s1, s2):  # Levenshtein Distance
        len1 = len(s1)+1
        len2 = len(s2)+1
        lt = [[0 for i2 in range(len2)] for i1 in range(len1)]  # lt - levenshtein_table
        lt[0] = list(range(len2))
        i = 0
        for l in lt:
            l[0] = i
            i += 1
        for i1 in range(1, len1):
            for i2 in range(1, len2):
                if s1[i1-1] == s2[i2-1]:
                    v = 0
                else:
                    v = 1
                lt[i1][i2] = min(lt[i1][i2-1]+1, lt[i1-1][i2]+1, lt[i1-1][i2-1]+v)
        return lt[-1][-1]
    #--------------------------------------------------
    # Поиск в списке наименований валют валюту,
    # наиболее близкую к априори заданному слову (по метрике Левинштейна)
    @staticmethod
    def score(s, keys,fun=ld):
        keys_list = list(keys.keys())
        tmp = []
        for x in keys_list:
            tmp.append(fun(s,x))
        return keys_list[tmp.index(min(tmp))], min(tmp)
#======================================================  
class Intension(Function):
    # Предварительная обработка входной текстовой строки
    @staticmethod
    def prepare(text):
        text = text.lower().strip()
        text = Function.en2ru(text)
        
        text = text.replace(',','.')
        text = text.replace('..','.')
        text = text.replace('  ',' ')  
        text = re.sub('[^а-я0-9. _]+', '', text)      
        return text
    #--------------------------------------------------
    # Анализ правильности ввода (соответствия используемому шаблону) и
    # корректности ввода числа конвертируемой валюты
    @staticmethod
    def analyze(text):
        values = text.split( )
        try:
            if len(values) != 3:
                raise APIException('Неверное количество параметров!')       
        except APIException as e:
            answer = f'{e}\nЧисло слов в запросе должно быть равно 3-м\n\
(разделитель слов - пробел)'
            return False, answer
        
        # Для количества конвертируемой валюты перевод в русскую точку символов 'б' и 'ю',
        # которые возникли после первоначального перевода латинской точки и запятой в кирилицу
        amount = values[2]
        amount = amount.replace('б','.')
        amount = amount.replace('ю','.')
        
        try:
            amount = float(amount)
        except ValueError as e:
            e = f'Не удалось обработать количество валюты "{amount}" !'
            answer = f'{e}\nЭто должно быть целое или действительное число\n\
(разделитель для действительного числа - точка или запятая)'    
            return False, answer 
        
        values[2] = amount 
        return True, values
    #--------------------------------------------------
    # Исправление незначительный опечаток (не более двух символов)
    # во входных наименованиях валют
    # (при исправлении трех символов возможно, например, превращение 'aaa' в 'юань')
    @staticmethod
    def classify(values, keys):
        max_operations = 2
        base, quote, amount = values
        
        val, n = Function.score(base, keys, Function.ld)
        try:
            if n > max_operations:
                raise APIException(f'Неправильно задана 1-ая валюта ({base})')
            else: base = val
        except APIException as e:
            return False, e

        val, n = Function.score(quote, keys, Function.ld)
        try:
            if n > max_operations:
                raise APIException(f'Неправильно задана 2-ая валюта ({quote})')
            else: quote = val
        except APIException as e:
            return False, e
               
        values = [base, quote, amount]
        return True, values    
#======================================================  
class Main(Config, Intension):   
    @staticmethod
    def start(token, access, keys):
        bot = telebot.TeleBot(token)

        @bot.message_handler(commands=['start'])
        def welcome(message: telebot.types.Message):
            text = 'Доброго времени суток!\n'+\
            'Вас приветствует справочный бот по обмену валюты.\n'+\
            'Что бы начать введите /start\n'+\
            'Чтобы получить помощь, введите /help\n'+\
            'Чтобы увидеть список всех доступных валют, введите /values' 
            bot.send_message(message.chat.id, text)
        
        @bot.message_handler(commands=['help'])
        def welcome(message: telebot.types.Message):
            text = 'Бот воспринимает запросы в следующем формате:\n'+\
                   '<имя исходной валюты><пробел>'+\
                   '<имя конечной валюты><пробел>'+\
                   '<количество переводимой валюты>'
            bot.send_message(message.chat.id, text)
  
        @bot.message_handler(commands=['values'])
        def help(message: telebot.types.Message):
            text = 'Доступные валюты:'
            for key in keys.keys():
                text = '\n'.join((text,key))
            bot.reply_to(message, text)

        @bot.message_handler(content_types=['text'])
        def convert(message: telebot.types.Message):
            values = message.text                      
            values = Intension.prepare(values)
            
            # Обеспечение непрерывной работы программы при обработке исключений
            status, values = Intension.analyze(values)
            if status == False:
                bot.send_message(message.chat.id, values)
            else:
                status, values = Intension.classify(values, keys) 
                if status == False:
                    bot.send_message(message.chat.id, values)             
                else:
                    base, quote, amount = values
            
                    r = requests.get(
                        f'http://api.exchangeratesapi.io/v1/latest?access_key={access}')
                    resp = json.loads(r.content)
                    base_ticker  = keys[base]
                    quote_ticker = keys[quote]
                    rate = resp['rates'][quote_ticker] / resp['rates'][base_ticker]
                    total_amount = rate*float(amount)
    
                    text = f'Курс {base} / {quote}: {rate}\nВсего за {amount} {base}: {total_amount} {quote}'
                    bot.send_message(message.chat.id, text)
        
        bot.polling(none_stop=True)
