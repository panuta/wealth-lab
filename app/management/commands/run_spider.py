from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #     parser.add_argument('spider', nargs='+', type=int)

    def handle(self, *args, **options):
        print('SUCCESS')
