import os
import sys

from quopri import decodestring

sys.path.append('../')
from Nicks_framework.filetypes import file_types
from Nicks_framework.templator import render
from Nicks_framework.requests import GetRequests, PostRequests

static_name = 'static'

STATIC_DIR = f'{os.getcwd()}/{static_name}'


class PageNotFound404:
    def __call__(self, request):
        return '404 WHAT', render('404.html')


class Framework:
    """Класс Framework - основа фреймворка"""

    def __init__(self, routes_obj, fronts_obj):
        self.routes_lst = routes_obj
        self.fronts_lst = fronts_obj

    def __call__(self, environ, start_response):
        # получаем адрес, по которому выполнен переход
        path = environ['PATH_INFO']

        # подключение статики

        if "/static/" in path:
            file_path = STATIC_DIR + path.replace('/static', '')
            if path[-1] == '/':
                list_files = '<br>'.join(os.listdir(file_path))

                template = f'''directory: ${STATIC_DIR}
                {list_files}
                '''
                start_response('200 OK', [('Content-Type', 'text/html')])
                return [template.encode('UTF-8')]
            else:
                print(f'Отдаем файл: ${file_path}')
                status = '200 OK'

                with open(file_path, 'rb') as f:
                    static_data = f.read()
                content_type = ''

                for file_type in file_types:
                    if file_type in path:
                        content_type = file_types[file_type]
            print(content_type)

            response_headers = [('Content-type', content_type),
                                ('Content-Length', str(len(static_data)))]
            start_response(status, response_headers)

            return [static_data]

        # добавление закрывающего слеша
        if not path.endswith('/'):
            path = f'{path}/'

        request = {}
        # Получаем все данные запроса
        method = environ['REQUEST_METHOD']
        request['method'] = method

        if method == 'POST':
            data = PostRequests().get_request_params(environ)
            request['data'] = Framework.decode_value(data)
            print(f'Нам пришёл post-запрос: {Framework.decode_value(data)}')

        if method == 'GET':
            request_params = GetRequests().get_request_params(environ)
            request['request_params'] = Framework.decode_value(request_params)
            print(f'Нам пришли GET-параметры:'
                  f' {Framework.decode_value(request_params)}')


        # находим нужный контроллер
        # отработка паттерна page controller
        if path in self.routes_lst:
            view = self.routes_lst[path]
        else:
            view = PageNotFound404()

        # наполняем словарь request элементами
        # этот словарь получат все контроллеры
        # отработка паттерна front controller
        for front in self.fronts_lst:
            front(request)
        # запуск контроллера с передачей объекта request
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
            val_decode_str = decodestring(val).decode('UTF-8')
            new_data[k] = val_decode_str
        return new_data


# Новый вид WSGI-application.
# Первый — логирующий (такой же, как основной,
# только для каждого запроса выводит информацию
# (тип запроса и параметры) в консоль.
class DebugApplication(Framework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = Framework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        print('DEBUG MODE')
        print(env)
        return self.application(env, start_response)


# Новый вид WSGI-application.
# Второй — фейковый (на все запросы пользователя отвечает:
# 200 OK, Hello from Fake).
class FakeApplication(Framework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = Framework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Hello from Fake']