from datetime import date
# from views import Index, About, Contacts, CategoryList, Collections, CreateCategory, StyleList, CreateStyle, CopyStyle


# front controller
def secret_front(request):
    request['date'] = date.today()


def other_front(request):
    request['key'] = 'key'


fronts = [secret_front, other_front]

# routes = {
#     '/': Index(),
#     '/about/': About(),
#     '/contacts/': Contacts(),
#     '/category-list/': CategoryList(),
#     '/create-category/': CreateCategory(),
#     '/style-list/': StyleList(),
#     '/create-style/': CreateStyle(),
#     '/copy-style/': CopyStyle(),
#     '/collections/': Collections(),
# }
