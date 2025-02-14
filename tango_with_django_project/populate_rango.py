import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')
django.setup()

from rango.models import Category, Page

def populate():
    categories = {
        'Python': {
            'pages': [
                {'title': 'Official Python Tutorial', 'url': 'http://docs.python.org/3/tutorial/'},
                {'title': 'How to Think like a Computer Scientist', 'url': 'http://www.greenteapress.com/thinkpython/'},
                {'title': 'Learn Python in 10 Minutes', 'url': 'http://www.korokithakis.net/tutorials/python/'}
            ],
            'views': 128,
            'likes': 64
        },
        'Django': {
            'pages': [
                {'title': 'Official Django Tutorial', 'url': 'https://docs.djangoproject.com/en/2.1/intro/tutorial01/'},
                {'title': 'Django Rocks', 'url': 'http://www.djangorocks.com/'},
                {'title': 'How to Tango with Django', 'url': 'http://www.tangowithdjango.com/'}
            ],
            'views': 64,
            'likes': 32
        },
        'Other Frameworks': {
            'pages': [
                {'title': 'Bottle', 'url': 'http://bottlepy.org/docs/dev/'},
                {'title': 'Flask', 'url': 'http://flask.pocoo.org'}
            ],
            'views': 32,
            'likes': 16
        }
    }

    for category_name, category_data in categories.items():
        category = add_category(category_name, category_data['views'], category_data['likes'])
        for i, page in enumerate(category_data['pages']):
            add_page(category, page['title'], page['url'], views=random.randint(50, 500) + i * 10)

    for category in Category.objects.all():
        for page in Page.objects.filter(category=category):
            print(f'- {category.name}: {page.title} ({page.views} views)')

def add_category(name, views=0, likes=0):
    category, created = Category.objects.get_or_create(name=name, defaults={'views': views, 'likes': likes})
    if not created:
        category.views = views
        category.likes = likes
        category.save()
    return category

def add_page(category, title, url, views=0):
    page, _ = Page.objects.get_or_create(category=category, title=title)
    page.url = url
    page.views = views  # Assigns a random view count
    page.save()
    return page

if __name__ == '__main__':
    print('Starting Rango population script...')
    populate()
