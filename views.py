from Nicks_framework.templator import render
from patterns.сreational_patterns import Engine, Logger
from patterns.structural_patterns import AppRoute, Debug
from patterns.behavioral_patterns import EmailNotifier, SmsNotifier, ListView, CreateView, BaseSerializer

site = Engine()
logger = Logger('main')
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()

routes = {}


# контроллер - главная страница
@AppRoute(routes=routes, url='/')
class Index:
    @Debug(name='Index')
    def __call__(self, request):
        return '200 OK', render('index.html')


# контроллер "О проекте"
@AppRoute(routes=routes, url='/about/')
class About:
    @Debug(name='About')
    def __call__(self, request):
        return '200 OK', render('about.html')


# контроллер - обратной связи
@AppRoute(routes=routes, url='/contacts/')
class Contacts:
    @Debug(name='Contacts')
    def __call__(self, request):
        return '200 OK', render('contact.html')


# контроллер - Коллекции
@AppRoute(routes=routes, url='/collections/')
class Collections:
    @Debug(name='Collections')
    def __call__(self, request):
        return '200 OK', render('collections.html')


# контроллер - стилей
@AppRoute(routes=routes, url='/style-list/')
class StyleList:
    @Debug(name='StyleList')
    def __call__(self, request):
        logger.log('Список Стилей')
        try:
            category = site.find_category_by_id(
                int(request['request_params']['id']))
            return '200 OK', render('styles_list.html',
                                    objects_list=category.styles,
                                    name=category.name, id=category.id)
        except KeyError:
            return '200 OK', 'No Style have been added yet'


# контроллер - создать стиль
@AppRoute(routes=routes, url='/create-style/')
class CreateStyle:
    category_id = -1

    @Debug(name='CreateStyle')
    def __call__(self, request):
        if request['method'] == 'POST':
            # метод пост
            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category = None
            if self.category_id != -1:
                category = site.find_category_by_id(int(self.category_id))

                style = site.create_style('modern', name, category)
                site.styles.append(style)

            return '200 OK', render('styles_list.html',
                                    objects_list=category.styles,
                                    name=category.name,
                                    id=category.id)

        else:
            try:
                self.category_id = int(request['request_params']['id'])
                category = site.find_category_by_id(int(self.category_id))

                return '200 OK', render('create_style.html',
                                        name=category.name,
                                        id=category.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


# контроллер - создать категорию
@AppRoute(routes=routes, url='/create-category/')
class CreateCategory:
    @Debug(name='CreateCategory')
    def __call__(self, request):

        if request['method'] == 'POST':
            # метод пост

            data = request['data']

            name = data['name']
            name = site.decode_value(name)

            category_id = data.get('category_id')

            category = None
            if category_id:
                category = site.find_category_by_id(int(category_id))

            new_category = site.create_category(name, category)

            site.categories.append(new_category)

            return '200 OK', render('category_list.html', objects_list=site.categories)
        else:
            categories = site.categories
            return '200 OK', render('create_category.html',
                                    categories=categories)


# контроллер - список категорий
@AppRoute(routes=routes, url='/category-list/')
class CategoryList:
    @Debug(name='CategoryList')
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html',
                                objects_list=site.categories)


# контроллер - копировать курс
@AppRoute(routes=routes, url='/copy-style/')
class CopyStyle:
    @Debug(name='CopyStyle')
    def __call__(self, request):
        request_params = request['request_params']

        try:
            name = request_params['name']

            old_course = site.get_style(name)
            if old_course:
                new_name = f'copy_{name}'
                new_style = old_course.clone()
                new_style.name = new_name
                site.styles.append(new_style)

            return '200 OK', render('styles_list.html',
                                    objects_list=site.styles,
                                    name=new_style.category.name)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


@AppRoute(routes=routes, url='/user-list/')
class UserListView(ListView):
    queryset = site.shopUsers
    template_name = 'user_list.html'


@AppRoute(routes=routes, url='/create-user/')
class StudentCreateView(CreateView):
    template_name = 'create_user.html'

    def create_obj(self, data: dict):
        name = data['name']
        name = site.decode_value(name)
        new_obj = site.create_user('shopUser', name)
        site.shopUsers.append(new_obj)


@AppRoute(routes=routes, url='/add-user/')
class AddUserByStyleCreateView(CreateView):
    template_name = 'add_user.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['styles'] = site.styles
        context['users'] = site.shopUsers
        return context

    def create_obj(self, data: dict):
        style_name = data['style_name']
        style_name = site.decode_value(style_name)
        style = site.get_style(style_name)
        user_name = data['user_name']
        user_name = site.decode_value(user_name)
        user = site.get_user(user_name)
        style.add_user(user)


@AppRoute(routes=routes, url='/api/')
class CourseApi:
    @Debug(name='styleApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(site.styles).save()
