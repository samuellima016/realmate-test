from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time

class Command(BaseCommand):
    """Comando customizado para aguardar o banco de dados antes de executar migrações."""
    help = "Espera o banco de dados estar disponível."

    def handle(self, *args, **options):
        self.stdout.write("⏳ Aguardando o banco de dados estar disponível...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.cursor()
            except OperationalError:
                self.stdout.write("Banco de dados indisponível, tentando novamente em 1s...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("✅ Banco de dados disponível!"))
