"""
manage.py sync_medata

Downloads real PQRSD records from Medata (Alcaldía de Medellín open data portal),
upserts Dependencias, imports the 500 most complete records into PQRSD, and writes a SyncLog.

Usage:
    docker compose exec web python manage.py sync_medata
    docker compose exec web python manage.py sync_medata --limit 200
    docker compose exec web python manage.py sync_medata --dry-run
"""
import csv
import io
import logging
import urllib.request
from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.conocimiento.models import Dependencia, SyncLog
from apps.pqrsd.models import PQRSD, _calcular_fecha_limite

logger = logging.getLogger(__name__)

MEDATA_CSV_URL = (
    'https://medata.gov.co/sites/default/files/distribution/'
    '1-013-13-000112/Registro_publico_PQRS.csv'
)

TEMA_TO_TIPO = {
    'peticion': 'peticion',
    'petición': 'peticion',
    'queja': 'queja',
    'reclamo': 'reclamo',
    'sugerencia': 'sugerencia',
    'denuncia': 'denuncia',
    'correspondencia': 'correspondencia',
    'derecho de petición': 'peticion',
    'derecho de peticion': 'peticion',
    'solicitud de información': 'peticion',
    'solicitud de informacion': 'peticion',
    'felicitacion': 'sugerencia',
    'felicitación': 'sugerencia',
}

VALID_TIPOS = {t for t, _ in PQRSD.TIPO_CHOICES}


def _map_tipo(tema: str) -> str:
    t = tema.lower().strip()
    for key, val in TEMA_TO_TIPO.items():
        if key in t:
            return val
    return 'correspondencia'


def _completeness(row: dict) -> int:
    """Count non-empty fields — used to rank records for the representative sample."""
    return sum(1 for v in row.values() if v and v.strip())


def _parse_date(val: str) -> date | None:
    if not val or not val.strip():
        return None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(val.strip(), fmt).date()
        except ValueError:
            pass
    return None


class Command(BaseCommand):
    help = 'Sync real PQRSD data from Medata open data portal'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=500, help='Max PQRSD records to import (default 500)')
        parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
        parser.add_argument('--timeout', type=int, default=60, help='HTTP timeout in seconds')

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        timeout = options['timeout']

        self.stdout.write(f'Descargando CSV desde Medata (timeout={timeout}s)...')
        try:
            req = urllib.request.Request(
                MEDATA_CSV_URL,
                headers={'User-Agent': 'PQRSD-Medellin-OmegaHack/1.0'},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode('utf-8-sig', errors='replace')
        except Exception as exc:
            msg = f'Error descargando CSV: {exc}'
            self.stderr.write(self.style.ERROR(msg))
            if not dry_run:
                SyncLog.objects.create(fuente='medata', exitoso=False, error_msg=msg)
            return

        self.stdout.write('CSV descargado. Procesando...')
        reader = csv.DictReader(io.StringIO(raw))
        rows = list(reader)
        self.stdout.write(f'  Total registros en CSV: {len(rows)}')

        # Rank by completeness, take top N
        rows.sort(key=_completeness, reverse=True)
        rows = rows[:limit]

        # Collect unique dependencias from data
        dep_names = {r.get('dependencia_responsable', '').strip() for r in rows if r.get('dependencia_responsable', '').strip()}
        self.stdout.write(f'  Dependencias únicas en muestra: {len(dep_names)}')

        dep_map: dict[str, Dependencia] = {}
        deps_created = 0
        if not dry_run:
            for name in sorted(dep_names):
                if not name:
                    continue
                sigla = ''.join(w[0].upper() for w in name.split()[:4] if w)[:10]
                dep, created = Dependencia.objects.get_or_create(
                    nombre=name,
                    defaults={
                        'sigla': sigla or name[:10],
                        'descripcion': f'Dependencia importada desde Medata: {name}',
                        'competencias': name,
                        'keywords': name.lower(),
                        'activa': True,
                    }
                )
                dep_map[name] = dep
                if created:
                    deps_created += 1

        self.stdout.write(f'  Dependencias creadas: {deps_created} / actualizadas: {len(dep_names) - deps_created}')

        # Import PQRSD records
        created_count = 0
        skipped = 0
        for row in rows:
            numero = (row.get('record_number') or row.get('numero') or '').strip()
            tema = (row.get('tema') or '').strip()
            dependencia_nombre = (row.get('dependencia_responsable') or '').strip()
            fecha_ingreso_str = (row.get('fecha_de_ingreso') or row.get('fecha_ingreso') or '').strip()
            fecha_respuesta_str = (row.get('fecha_de_respuesta') or row.get('fecha_respuesta') or '').strip()

            if not tema:
                skipped += 1
                continue

            tipo = _map_tipo(tema)
            radicado = f'MDE-MEDATA-{numero}' if numero else None
            if radicado and PQRSD.objects.filter(radicado=radicado).exists():
                skipped += 1
                continue

            fecha_ingreso = _parse_date(fecha_ingreso_str)
            fecha_respuesta_dt = _parse_date(fecha_respuesta_str)

            dep = dep_map.get(dependencia_nombre) if not dry_run else None

            if not dry_run:
                p = PQRSD(
                    tipo=tipo,
                    estado='respondida' if fecha_respuesta_dt else 'cerrada',
                    canal_entrada='web',
                    anonimo=True,
                    prioridad='media',
                    nombre_ciudadano='',
                    asunto=f'{tema} — {dependencia_nombre}'[:300] if dependencia_nombre else tema[:300],
                    descripcion=f'Registro histórico importado desde Medata. Tema: {tema}. Dependencia: {dependencia_nombre}.',
                    dependencia_asignada=dep,
                    clasificacion_validada=True,
                    omnicanal_meta={'origen': 'medata', 'numero_original': numero, 'tema': tema},
                )
                if radicado:
                    p.radicado = radicado
                if fecha_ingreso:
                    p.fecha_radicacion = timezone.make_aware(datetime.combine(fecha_ingreso, datetime.min.time()))
                p.fecha_limite = _calcular_fecha_limite(tipo)
                if fecha_respuesta_dt:
                    p.fecha_respuesta = timezone.make_aware(datetime.combine(fecha_respuesta_dt, datetime.min.time()))
                p.save()
                created_count += 1
            else:
                created_count += 1

        summary = (
            f'{"[DRY-RUN] " if dry_run else ""}'
            f'Sync Medata completado: {created_count} PQRSDs importadas, '
            f'{skipped} omitidas, {deps_created} dependencias creadas.'
        )
        self.stdout.write(self.style.SUCCESS(summary))

        if not dry_run:
            SyncLog.objects.create(
                fuente='medata',
                registros_importados=created_count,
                exitoso=True,
            )
