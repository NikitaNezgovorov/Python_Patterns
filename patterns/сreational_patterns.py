from copy import deepcopy
from quopri import decodestring
from patterns.behavioral_patterns import FileWriter, Subject


# абстрактный пользователь
class User:
    def __init__(self, name):
        self.name = name


# Админ
class Admin(User):
    pass


# студент
class ShopUser(User):
    def __init__(self, name):
        self.styles = []
        super().__init__(name)


class UserFactory:
    types = {
        'admin': Admin,
        'shopUser': ShopUser,
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name):
        return cls.types[type_](name)


# порождающий паттерн Прототип
class TypesPrototype:
    # прототип курсов обучения

    def clone(self):
        return deepcopy(self)


class Styles(TypesPrototype, Subject):

    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.category.styles.append(self)
        self.users = []
        super().__init__()

    def __getitem__(self, item):
        return self.users[item]

    def add_user(self, user: ShopUser):
        self.users.append(user)
        user.styles.append(self)
        self.notify()


# Тип Модерн
class ModernCategory(Styles):
    pass


# Категория Ретро
class RetroCategory(Styles):
    pass


class StylesFactory:
    types = {
        'modern': ModernCategory,
        'retro': RetroCategory,
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, category):
        return cls.types[type_](name, category)


# категория
class Category:
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.category = category
        self.styles = []

    def styles_count(self):
        result = len(self.styles)
        if self.category:
            result += self.category.styles_count()
        return result


# основной интерфейс проекта
class Engine:
    def __init__(self):
        self.admins = []
        self.shopUsers = []
        self.styles = []
        self.categories = []

    @staticmethod
    def create_user(type_, name):
        return UserFactory.create(type_, name)

    @staticmethod
    def create_category(name, category=None):
        return Category(name, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    @staticmethod
    def create_style(type_, name, category):
        return StylesFactory.create(type_, name, category)

    def get_style(self, name):
        for item in self.styles:
            if item.name == name:
                return item
        return None

    def get_user(self, name) -> ShopUser:
        for item in self.shopUsers:
            if item.name == name:
                return item

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')


# порождающий паттерн Синглтон
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name, writer=FileWriter()):
        self.name = name
        self.writer = writer

    def log(self, text):
        text = f'log---> {text}'
        self.writer.write(text)
