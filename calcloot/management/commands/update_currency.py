from django.core.management.base import NoArgsCommand
from calcloot.currency import *

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        update_currencies()