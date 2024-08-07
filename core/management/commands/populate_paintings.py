import random
from django.core.management.base import BaseCommand
from faker import Faker
from core.models import Artist, Category, Tag, Painting
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Populate the database with a large amount of diverse paintings.'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create Artists
        artists = []
        for _ in range(10):  # Create 10 artists
            artist = Artist.objects.create(
                name=fake.name(),
                bio=fake.text(),
                birth_date=fake.date_of_birth(),
                profile=fake.image_url()
            )
            artists.append(artist)

        # Create Categories
        categories = []
        for _ in range(5):  # Create 5 categories
            category = Category.objects.create(
                name=fake.word(),
                slug=fake.slug()
            )
            categories.append(category)

        # Create Tags
        tags = []
        for _ in range(20):  # Create 20 tags
            tag = Tag.objects.create(
                name=fake.word(),
                slug=fake.slug()
            )
            tags.append(tag)

        # Create Paintings
        for _ in range(100):  # Create 100 paintings
            painting = Painting.objects.create(
                title=fake.sentence(nb_words=4),
                description=fake.text(),
                price=fake.random_number(digits=5) / 100,
                artist=random.choice(artists),
                category=random.choice(categories),
                image=fake.image_url(),
                slug=fake.slug()
            )

            # Add tags to the painting
            for _ in range(random.randint(1, 5)):  # Each painting can have 1 to 5 tags
                painting.tags.add(random.choice(tags))

            painting.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with paintings.'))
