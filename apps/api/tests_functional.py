"""
Test funcional completo del sistema PQRSD Medellín.
Cubre: Auth, Submit ciudadano, Pipeline IA, Staff CRUD,
Clasificación, Síntesis, Stats, Mapa de Calor, Inbox, Demo.
"""
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.pqrsd.models import PQRSD
from apps.conocimiento.models import Dependencia
from apps.clasificacion.models import ClasificacionIA


BASE = '/api/v1'


def post(client, path, data, content_type='application/json', **kw):
    return client.post(BASE + path, data, content_type=content_type, **kw)


def get(client, path, **kw):
    return client.get(BASE + path, **kw)


class T01_Auth(TestCase):
    """Autenticación: CSRF, login, logout, me."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.user = User.objects.create_user('test_admin', password='pass1234', is_staff=True)

    def test_csrf_endpoint(self):
        r = get(self.client, '/auth/csrf/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('csrfToken', r.json())

    def test_login_ok(self):
        r = post(self.client, '/auth/login/', {'username': 'test_admin', 'password': 'pass1234'})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data['username'], 'test_admin')
        self.assertTrue(data['isStaff'])

    def test_login_wrong_password(self):
        r = post(self.client, '/auth/login/', {'username': 'test_admin', 'password': 'wrong'})
        self.assertEqual(r.status_code, 401)

    def test_me_unauthenticated(self):
        r = get(self.client, '/auth/me/')
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()['authenticated'])

    def test_me_authenticated(self):
        self.client.force_login(self.user)
        r = get(self.client, '/auth/me/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()['authenticated'])

    def test_logout(self):
        self.client.force_login(self.user)
        r = post(self.client, '/auth/logout/', {})
        self.assertEqual(r.status_code, 200)


class T02_PublicEndpoints(TestCase):
    """Endpoints públicos: choices, dependencias."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        Dependencia.objects.create(nombre='Secretaría de Obras', sigla='SOBJ', activa=True)

    def test_choices(self):
        r = get(self.client, '/choices/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertIn('tipo', d)
        self.assertIn('canal', d)
        self.assertIn('estado', d)
        self.assertTrue(len(d['tipo']) >= 6)

    def test_dependencias(self):
        r = get(self.client, '/dependencias/')
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()), 1)

    def test_api_root(self):
        r = get(self.client, '/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('routes', r.json())


class T03_PqrsdCreate(TestCase):
    """Ciudadano: crear PQRSD vía API."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def _payload(self, **overrides):
        base = {
            'tipo': 'peticion',
            'canal_entrada': 'web',
            'anonimo': False,
            'nombre_ciudadano': 'Juan García',
            'email_ciudadano': 'juan@example.com',
            'asunto': 'Solicitud de arreglo de vía pública deteriorada',
            'descripcion': 'El pavimento de la Carrera 70 con Calle 44 está muy deteriorado '
                           'y representa un riesgo para los peatones y vehículos.',
            'barrio': 'Estadio',
            'comuna': 'Laureles',
        }
        base.update(overrides)
        return base

    def test_create_named(self):
        r = post(self.client, '/pqrsd/submit/', self._payload())
        self.assertEqual(r.status_code, 201)
        d = r.json()
        self.assertIn('radicado', d)
        self.assertTrue(d['radicado'].startswith('MDE-'))
        self.assertEqual(d['estado'], 'radicada')

    def test_create_anonymous(self):
        r = post(self.client, '/pqrsd/submit/',
                 self._payload(anonimo=True, nombre_ciudadano='', email_ciudadano=''))
        self.assertEqual(r.status_code, 201)

    def test_create_with_address_in_description(self):
        r = post(self.client, '/pqrsd/submit/', self._payload(
            descripcion='Hueco frente a la Calle 53 #45-23 esquina con la Avenida El Poblado, zona comercial.'
        ))
        self.assertEqual(r.status_code, 201)

    def test_missing_nombre_when_not_anonimo(self):
        r = post(self.client, '/pqrsd/submit/', self._payload(nombre_ciudadano=''))
        self.assertEqual(r.status_code, 400)

    def test_missing_required_fields(self):
        r = post(self.client, '/pqrsd/submit/', {'tipo': 'peticion'})
        self.assertEqual(r.status_code, 400)

    def test_multiple_types(self):
        for tipo in ['queja', 'reclamo', 'sugerencia', 'denuncia']:
            r = post(self.client, '/pqrsd/submit/', self._payload(tipo=tipo))
            self.assertEqual(r.status_code, 201, f"Falló con tipo={tipo}")

    def test_status_check(self):
        r = post(self.client, '/pqrsd/submit/', self._payload())
        radicado = r.json()['radicado']
        r2 = get(self.client, f'/pqrsd/status/{radicado}/')
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()['radicado'], radicado)

    def test_status_not_found(self):
        r = get(self.client, '/pqrsd/status/MDE-FAKE-99999/')
        self.assertEqual(r.status_code, 404)


class T04_StaffPqrsdManagement(TestCase):
    """Staff: listado, detalle, cambio de estado."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.staff = User.objects.create_user('staff1', password='pass', is_staff=True)
        self.client.force_login(self.staff)
        self.dep = Dependencia.objects.create(nombre='Obras Públicas', sigla='OBP', activa=True)
        self.pqrsd = PQRSD.objects.create(
            tipo='queja', canal_entrada='web',
            nombre_ciudadano='Ana López',
            asunto='Queja por demora en respuesta oficial',
            descripcion='Han pasado 20 días y no he recibido respuesta a mi petición anterior.',
            barrio='El Poblado', comuna='El Poblado',
        )

    def test_list_requires_auth(self):
        c = Client(enforce_csrf_checks=False)
        r = get(c, '/pqrsd/')
        self.assertEqual(r.status_code, 403)

    def test_list_staff(self):
        r = get(self.client, '/pqrsd/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('results', data)
        self.assertGreaterEqual(data['count'], 1)

    def test_detail(self):
        r = get(self.client, f'/pqrsd/{self.pqrsd.pk}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['id'], self.pqrsd.pk)

    def test_update_estado(self):
        r = self.client.patch(
            f'{BASE}/pqrsd/{self.pqrsd.pk}/estado/',
            json.dumps({'estado': 'en_tramite'}),
            content_type='application/json'
        )
        self.assertEqual(r.status_code, 200)
        self.pqrsd.refresh_from_db()
        self.assertEqual(self.pqrsd.estado, 'en_tramite')

    def test_filter_by_estado(self):
        r = get(self.client, '/pqrsd/?estado=radicada')
        self.assertEqual(r.status_code, 200)

    def test_filter_by_tipo(self):
        r = get(self.client, '/pqrsd/?tipo=queja')
        self.assertEqual(r.status_code, 200)
        for item in r.json()['results']:
            self.assertEqual(item['tipo'], 'queja')

    def test_search(self):
        r = get(self.client, '/pqrsd/?q=López')
        self.assertEqual(r.status_code, 200)


class T05_Classification(TestCase):
    """Clasificación IA y validación por funcionario."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.staff = User.objects.create_user('staff2', password='pass', is_staff=True)
        self.client.force_login(self.staff)
        self.dep = Dependencia.objects.create(nombre='Movilidad', sigla='MOV', activa=True)
        self.pqrsd = PQRSD.objects.create(
            tipo='reclamo', canal_entrada='email',
            nombre_ciudadano='Carlos Ríos',
            asunto='Semáforo dañado en intersección principal',
            descripcion='El semáforo de la Avenida Oriental con Calle 44 lleva 3 días dañado.',
            barrio='Prado', comuna='Villahermosa',
        )

    def test_classify_endpoint(self):
        r = post(self.client, f'/pqrsd/{self.pqrsd.pk}/classify/', {})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('clasificacion', data)

    def test_validate_classification(self):
        # Primero clasificar
        post(self.client, f'/pqrsd/{self.pqrsd.pk}/classify/', {})
        # Luego validar
        r = post(self.client, f'/pqrsd/{self.pqrsd.pk}/validate/', {
            'aceptada': True,
            'dependencia_id': self.dep.pk,
        })
        self.assertEqual(r.status_code, 200)
        self.pqrsd.refresh_from_db()
        self.assertTrue(self.pqrsd.clasificacion_validada)

    def test_validate_rejected(self):
        post(self.client, f'/pqrsd/{self.pqrsd.pk}/classify/', {})
        r = post(self.client, f'/pqrsd/{self.pqrsd.pk}/validate/', {
            'aceptada': False,
            'dependencia_id': self.dep.pk,
            'comentario': 'No corresponde a Movilidad',
        })
        self.assertEqual(r.status_code, 200)


class T06_Synthesis(TestCase):
    """Síntesis IA de PQRSD."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.staff = User.objects.create_user('staff3', password='pass', is_staff=True)
        self.client.force_login(self.staff)
        self.pqrsd = PQRSD.objects.create(
            tipo='peticion', canal_entrada='web',
            nombre_ciudadano='María Gómez',
            asunto='Solicitud de alumbrado público en el parque',
            descripcion='El parque del barrio no tiene alumbrado desde hace un mes, '
                        'lo que genera inseguridad para los residentes del sector.',
            barrio='Belén', comuna='Belén',
        )

    def test_get_synthesis_not_found(self):
        r = get(self.client, f'/pqrsd/{self.pqrsd.pk}/synthesis/')
        self.assertIn(r.status_code, [200, 404])

    def test_generate_synthesis(self):
        r = post(self.client, f'/pqrsd/{self.pqrsd.pk}/synthesis/', {})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('resumen_ejecutivo', data)


class T07_Stats(TestCase):
    """Dashboard: stats generales y mapa de calor."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.staff = User.objects.create_user('staff4', password='pass', is_staff=True)
        self.client.force_login(self.staff)
        dep = Dependencia.objects.create(nombre='Planeación', sigla='PLA', activa=True)
        for i, (barrio, comuna) in enumerate([
            ('Estadio', 'Laureles'),
            ('Estadio', 'Laureles'),
            ('El Poblado', 'El Poblado'),
            ('Belén', 'Belén'),
            ('Prado', 'Villahermosa'),
        ]):
            PQRSD.objects.create(
                tipo='peticion', canal_entrada='web',
                nombre_ciudadano=f'Ciudadano {i}',
                asunto=f'Solicitud {i} de prueba funcional',
                descripcion=f'Descripción detallada de la solicitud número {i} para prueba.',
                barrio=barrio, comuna=comuna,
            )

    def test_stats(self):
        r = get(self.client, '/stats/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('total', data)
        self.assertIn('radicadas', data)
        self.assertIn('alertas', data)
        self.assertGreaterEqual(data['total'], 5)

    def test_stats_requires_auth(self):
        c = Client(enforce_csrf_checks=False)
        r = get(c, '/stats/')
        self.assertEqual(r.status_code, 403)

    def test_mapa_calor(self):
        r = get(self.client, '/stats/mapa-calor/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('por_comuna', data)
        self.assertIn('por_barrio', data)
        self.assertIn('total', data)
        self.assertGreaterEqual(data['total'], 5)
        comunas = [c['nombre'] for c in data['por_comuna']]
        self.assertIn('Laureles', comunas)
        laureles = next(c for c in data['por_comuna'] if c['nombre'] == 'Laureles')
        self.assertEqual(laureles['count'], 2)

    def test_mapa_calor_requires_auth(self):
        c = Client(enforce_csrf_checks=False)
        r = get(c, '/stats/mapa-calor/')
        self.assertEqual(r.status_code, 403)


class T08_Inbox(TestCase):
    """Bandeja de entrada staff."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.staff = User.objects.create_user('staff5', password='pass', is_staff=True)
        self.client.force_login(self.staff)
        for i in range(3):
            PQRSD.objects.create(
                tipo='queja', canal_entrada='whatsapp',
                nombre_ciudadano=f'Quejoso {i}',
                asunto=f'Queja urgente número {i} sobre servicio',
                descripcion=f'Descripción completa de la queja {i} con detalles del problema.',
            )

    def test_inbox(self):
        r = get(self.client, '/inbox/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('results', data)
        self.assertGreaterEqual(data['count'], 3)

    def test_inbox_requires_auth(self):
        c = Client(enforce_csrf_checks=False)
        r = get(c, '/inbox/')
        self.assertEqual(r.status_code, 403)

    def test_inbox_filter_by_canal(self):
        r = get(self.client, '/inbox/?canal=whatsapp')
        self.assertEqual(r.status_code, 200)


class T09_PipelineSubmit(TestCase):
    """Submit con pipeline de agentes (sin API key → fallback estándar)."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        Dependencia.objects.create(nombre='Infraestructura', sigla='INF', activa=True)

    def test_pipeline_fallback_no_key(self):
        """Sin ANTHROPIC_API_KEY → delega a pqrsd_create estándar."""
        from django.conf import settings
        original = settings.ANTHROPIC_API_KEY
        settings.ANTHROPIC_API_KEY = ''
        try:
            r = post(self.client, '/pqrsd/submit-pipeline/', {
                'tipo': 'peticion',
                'canal_entrada': 'web',
                'canal': 'web',
                'anonimo': False,
                'nombre_ciudadano': 'Pedro Salcedo',
                'email_ciudadano': 'pedro@test.com',
                'asunto': 'Solicitud de arreglo de tubería rota en la vía pública',
                'descripcion': 'Hay una tubería rota frente al colegio de la Calle 50 con Carrera 42.',
                'descripcion_raw': 'Hay una tubería rota frente al colegio de la Calle 50 con Carrera 42.',
                'barrio': 'Manrique',
                'comuna': 'Manrique',
            })
            self.assertEqual(r.status_code, 201)
            self.assertIn('radicado', r.json())
        finally:
            settings.ANTHROPIC_API_KEY = original


class T10_Demo(TestCase):
    """Inyección demo multicanal."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.staff = User.objects.create_user('staff6', password='pass', is_staff=True)
        self.client.force_login(self.staff)

    def test_demo_inject(self):
        r = post(self.client, '/demo/inject/', {'canal': 'web'})
        self.assertIn(r.status_code, [200, 201])

    def test_demo_inject_whatsapp(self):
        r = post(self.client, '/demo/inject/', {'canal': 'whatsapp'})
        self.assertIn(r.status_code, [200, 201])

    def test_demo_requires_auth(self):
        c = Client(enforce_csrf_checks=False)
        r = post(c, '/demo/inject/', {'canal': 'web'})
        self.assertEqual(r.status_code, 403)


class T11_PqrsdDataIntegrity(TestCase):
    """Integridad de datos: radicado único, fecha límite calculada, SLA."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def _create(self, asunto_suffix=''):
        return post(self.client, '/pqrsd/submit/', {
            'tipo': 'peticion',
            'canal_entrada': 'web',
            'anonimo': False,
            'nombre_ciudadano': 'Test Integridad',
            'email_ciudadano': 'integridad@test.com',
            'asunto': f'Solicitud de prueba de integridad {asunto_suffix}',
            'descripcion': 'Verificación de integridad del radicado y fecha límite calculada.',
            'barrio': 'Centro', 'comuna': 'La Candelaria',
        })

    def test_unique_radicado(self):
        r1 = self._create('A')
        r2 = self._create('B')
        self.assertNotEqual(r1.json()['radicado'], r2.json()['radicado'])

    def test_fecha_limite_set(self):
        r = self._create('C')
        self.assertIsNotNone(r.json()['fecha_limite'])

    def test_estado_inicial_radicada(self):
        r = self._create('D')
        self.assertEqual(r.json()['estado'], 'radicada')

    def test_barrio_comuna_persisted(self):
        r = self._create('E')
        pk = r.json()['id']
        pqrsd = PQRSD.objects.get(pk=pk)
        self.assertEqual(pqrsd.barrio, 'Centro')
        self.assertEqual(pqrsd.comuna, 'La Candelaria')


class T12_RejectionReactivation(TestCase):
    """Rechazo automático por filtro y reactivación por staff."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.staff = User.objects.create_user('staff_react', password='pass', is_staff=True)
        self.pqrsd = PQRSD.objects.create(
            tipo='queja', canal_entrada='web',
            nombre_ciudadano='Test Rechazo',
            asunto='Queja con lenguaje inadmisible',
            descripcion='Contenido con insultos inaceptables.',
            estado='rechazada',
            observaciones_internas='Filtro automático: lenguaje_inadmisible — Su solicitud contiene lenguaje inapropiado.',
        )

    def test_detail_api_exposes_observaciones_internas(self):
        """El endpoint de detalle expone observaciones_internas al staff."""
        self.client.force_login(self.staff)
        r = get(self.client, f'/pqrsd/{self.pqrsd.pk}/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('observaciones_internas', data)
        self.assertIn('lenguaje_inadmisible', data['observaciones_internas'])

    def test_detail_api_hidden_from_anon(self):
        """Anónimo no puede ver el detalle staff."""
        c = Client(enforce_csrf_checks=False)
        r = get(c, f'/pqrsd/{self.pqrsd.pk}/')
        self.assertEqual(r.status_code, 403)

    def test_reactivar_via_cambiar_estado(self):
        """Staff puede reactivar una PQRSD rechazada volviendo a 'radicada'."""
        self.client.force_login(self.staff)
        r = self.client.post(
            f'/funcionarios/pqrsd/{self.pqrsd.pk}/estado/',
            {'estado': 'radicada', 'observaciones': 'Reactivada manualmente'},
        )
        self.assertIn(r.status_code, [200, 302])
        self.pqrsd.refresh_from_db()
        self.assertEqual(self.pqrsd.estado, 'radicada')
        self.assertEqual(self.pqrsd.observaciones_funcionario, 'Reactivada manualmente')
        # observaciones_internas preservadas como auditoría
        self.assertIn('lenguaje_inadmisible', self.pqrsd.observaciones_internas)

    def test_observaciones_internas_preserved_after_reactivation(self):
        """observaciones_internas no se borra al reactivar — queda como auditoría."""
        self.pqrsd.estado = 'radicada'
        self.pqrsd.save()
        self.pqrsd.refresh_from_db()
        self.assertIn('Filtro automático', self.pqrsd.observaciones_internas)
