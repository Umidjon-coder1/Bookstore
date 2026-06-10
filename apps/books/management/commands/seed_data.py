from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.books.models import Category, Author, Publisher, Book
from faker import Faker
import random
import decimal

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Categories
        categories_data = [
            ('Fiction', None), ('Non-Fiction', None), ('Science Fiction', 'Fiction'),
            ('Fantasy', 'Fiction'), ('Mystery', 'Fiction'), ('Biography', 'Non-Fiction'),
            ('History', 'Non-Fiction'), ('Self-Help', 'Non-Fiction'),
            ('Children', None), ('Technology', None),
        ]
        categories = {}
        for name, parent_name in categories_data:
            from django.utils.text import slugify
            slug = slugify(name)
            parent = categories.get(parent_name)
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'parent': parent, 'is_active': True}
            )
            categories[name] = cat
        self.stdout.write(f'  Created {len(categories)} categories')

        # Authors
        authors = []
        author_names = [
            'J.K. Rowling', 'Stephen King', 'George R.R. Martin', 'Agatha Christie',
            'Leo Tolstoy', 'Ernest Hemingway', 'Mark Twain', 'Jane Austen',
            'Isaac Asimov', 'Arthur C. Clarke',
        ]
        for name in author_names:
            from django.utils.text import slugify
            slug = slugify(name)
            author, _ = Author.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'bio': fake.paragraph(nb_sentences=3)}
            )
            authors.append(author)
        self.stdout.write(f'  Created {len(authors)} authors')

        # Publishers
        publishers = []
        publisher_names = ['Penguin Books', 'HarperCollins', 'Random House', 'Oxford University Press', 'Bloomsbury']
        for name in publisher_names:
            pub, _ = Publisher.objects.get_or_create(
                name=name,
                defaults={'website': f'https://www.{name.lower().replace(" ", "")}.com'}
            )
            publishers.append(pub)
        self.stdout.write(f'  Created {len(publishers)} publishers')

        # Books
        book_titles = [
            'The Great Adventure', 'Midnight Shadows', 'Lost in Time', 'The Last Chapter',
            'Beyond the Horizon', 'Whispers in the Dark', 'The Hidden Truth',
            'Echoes of Tomorrow', 'The Silent Storm', 'Forgotten Worlds',
            'Stars and Stones', 'The Infinite Road', 'Bound by Fate',
            'The Crystal Eye', 'Fire and Ice', 'The Iron Gate',
            'Shadow of the Moon', 'The Golden Key', 'Into the Void',
            'The Silver Compass',
        ]
        leaf_categories = [c for name, c in categories.items() if name not in ['Fiction', 'Non-Fiction']]
        for i, title in enumerate(book_titles):
            from django.utils.text import slugify
            isbn = str(fake.isbn13()).replace('-', '')[:13]
            slug = slugify(title)
            price = decimal.Decimal(str(round(random.uniform(9.99, 49.99), 2)))
            has_discount = random.random() > 0.6
            discount_price = decimal.Decimal(str(round(float(price) * 0.8, 2))) if has_discount else None
            Book.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'isbn': isbn[:13],
                    'author': random.choice(authors),
                    'publisher': random.choice(publishers),
                    'category': random.choice(leaf_categories),
                    'description': fake.paragraphs(nb=3, ext_word_list=None).__str__(),
                    'price': price,
                    'discount_price': discount_price,
                    'quantity': random.randint(0, 50),
                    'language': random.choice(['English', 'Russian', 'Uzbek']),
                    'publication_date': fake.date_between(start_date='-10y', end_date='today'),
                    'pages': random.randint(150, 800),
                    'is_active': True,
                    'is_featured': random.random() > 0.7,
                }
            )
        self.stdout.write(f'  Created {len(book_titles)} books')

        # Users
        roles = ['customer', 'customer', 'customer', 'store_manager']
        for i in range(5):
            email = f'user{i+1}@example.com'
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    username=f'user{i+1}',
                    email=email,
                    password='TestPass123!',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role=roles[i % len(roles)],
                )

        # Admin user
        if not User.objects.filter(email='admin@bookstore.com').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@bookstore.com',
                password='Admin123!',
                role='super_admin',
            )

        self.stdout.write(self.style.SUCCESS('Data seeded successfully!'))
        self.stdout.write('  Admin: admin@bookstore.com / Admin123!')
        self.stdout.write('  Users: user1@example.com to user5@example.com / TestPass123!')
