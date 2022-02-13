import os
import sys

sys.path.append('../')
from Nicks_framework.filetypes import file_types
from Nicks_framework.templator import render

static_name = 'static'

STATIC_DIR = f'{os.getcwd()}/{static_name}'


class PageNotFound404:
    def __call__(self, request):
        return '404 WHAT', render('404.html', date=request.get('date', None))


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
                    data = f.read()
                content_type = ''

                for file_type in file_types:
                    if file_type in path:
                        content_type = file_types[file_type]
            print(content_type)

            response_headers = [('Content-type', content_type),
                                ('Content-Length', str(len(data)))]
            start_response(status, response_headers)

            return [data]

        # добавление закрывающего слеша
        if not path.endswith('/'):
            path = f'{path}/'

        # находим нужный контроллер
        # отработка паттерна page controller
        if path in self.routes_lst:
            view = self.routes_lst[path]
        else:
            view = PageNotFound404()
        request = {}
        # наполняем словарь request элементами
        # этот словарь получат все контроллеры
        # отработка паттерна front controller
        for front in self.fronts_lst:
            front(request)
        # запуск контроллера с передачей объекта request
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]
