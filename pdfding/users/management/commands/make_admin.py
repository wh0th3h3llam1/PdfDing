from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument('-e', '--email', type=str, help='The email of the user who should be admin')

    def handle(self, *args, **kwargs):
        email = kwargs['email']
        user = User.objects.get(email=email)
        user.is_staff = True
        user.is_superuser = True
        user.save()
