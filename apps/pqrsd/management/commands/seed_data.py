"""
Carga datos de prueba realistas para OmegaHack 2026.
Idempotente: puede ejecutarse varias veces sin duplicar.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta


DEPENDENCIAS = [
    {
        "sigla": "SDEC",
        "nombre": "Secretaría de Desarrollo Económico",
        "descripcion": "Lidera la política de desarrollo económico, emprendimiento, empleo y competitividad de Medellín.",
        "competencias": "Fomento empresarial; Empleo y trabajo; Emprendimiento; Economía popular; Ferias y mercados; Clústeres productivos",
        "keywords": "empleo, trabajo, empresa, emprendimiento, negocio, comercio, feria, mercado, desempleo, contrato, economía",
        "email_contacto": "sdec@medellin.gov.co",
        "telefono": "604 385 5555",
    },
    {
        "sigla": "SDIS",
        "nombre": "Secretaría de Inclusión Social, Familia y Derechos Humanos",
        "descripcion": "Garantiza los derechos de personas en situación de vulnerabilidad, familias y comunidades.",
        "competencias": "Población vulnerable; Adultos mayores; Discapacidad; Infancia y adolescencia; Violencia intrafamiliar; Comedores comunitarios",
        "keywords": "pobreza, vulnerabilidad, discapacidad, adulto mayor, niñez, familia, violencia, comedor, subsidio social",
        "email_contacto": "sdis@medellin.gov.co",
        "telefono": "604 385 4444",
    },
    {
        "sigla": "SSPM",
        "nombre": "Secretaría de Seguridad y Convivencia",
        "descripcion": "Diseña e implementa políticas de seguridad ciudadana, convivencia y orden público.",
        "competencias": "Seguridad ciudadana; Convivencia; Policía Metropolitana; CCTV; Prevención del delito",
        "keywords": "robo, hurto, inseguridad, convivencia, pelea, ruido, pandilla, cámara, vigilancia, policía, delito",
        "email_contacto": "seguridad@medellin.gov.co",
        "telefono": "604 444 4100",
    },
    {
        "sigla": "SMOT",
        "nombre": "Secretaría de Movilidad",
        "descripcion": "Regula el tránsito, transporte público y movilidad sostenible en el municipio.",
        "competencias": "Tránsito; Señalización vial; Transporte público; Parqueaderos; Ciclovías; Fotomultas; Licencias de conducción",
        "keywords": "tránsito, multa, semáforo, señal, bus, metro, bicicleta, parqueo, accidente, comparendo, licencia, moto",
        "email_contacto": "movilidad@medellin.gov.co",
        "telefono": "604 444 2626",
    },
    {
        "sigla": "SOMA",
        "nombre": "Secretaría de Medio Ambiente",
        "descripcion": "Protege el patrimonio natural, gestiona residuos sólidos y controla la contaminación.",
        "competencias": "Calidad del aire; Ruido ambiental; Residuos sólidos; Árboles y zonas verdes; Quebradas; Fauna urbana",
        "keywords": "basura, reciclaje, árbol, ruido, contaminación, quebrada, animal, fauna, smog, humo, poda, tala, residuo",
        "email_contacto": "medioambiente@medellin.gov.co",
        "telefono": "604 385 6060",
    },
    {
        "sigla": "SSALUD",
        "nombre": "Secretaría de Salud",
        "descripcion": "Dirige la política de salud pública, vigilancia epidemiológica y atención primaria.",
        "competencias": "Salud pública; Vacunación; Epidemiología; IPS municipales; Salubridad de establecimientos; Licencias sanitarias",
        "keywords": "salud, hospital, médico, vacuna, EPS, IPS, consulta, urgencias, medicamento, epidemia, sanitario",
        "email_contacto": "salud@medellin.gov.co",
        "telefono": "604 385 9090",
    },
    {
        "sigla": "SEDU",
        "nombre": "Secretaría de Educación",
        "descripcion": "Garantiza el acceso a educación de calidad en las instituciones educativas oficiales.",
        "competencias": "Matrículas; Cobertura escolar; Infraestructura educativa; Docentes; Restaurantes escolares; Gratuidad",
        "keywords": "colegio, escuela, matrícula, estudiante, profesor, docente, educación, beca, restaurante escolar, cupo",
        "email_contacto": "educacion@medellin.gov.co",
        "telefono": "604 385 7070",
    },
    {
        "sigla": "SVIVIENDA",
        "nombre": "Secretaría de Vivienda",
        "descripcion": "Gestiona programas de vivienda digna, mejoramiento habitacional y legalización de predios.",
        "competencias": "Subsidios de vivienda; Mejoramiento habitacional; Reasentamientos; Legalización predial; Titulación",
        "keywords": "vivienda, casa, arriendo, subsidio habitacional, invasión, reasentamiento, predio, lote, escritura, titulación",
        "email_contacto": "vivienda@medellin.gov.co",
        "telefono": "604 385 8080",
    },
    {
        "sigla": "SOPUB",
        "nombre": "Secretaría de Obras Públicas",
        "descripcion": "Planifica y ejecuta la infraestructura vial, andenes, puentes y obras públicas municipales.",
        "competencias": "Vías; Andenes; Puentes; Alumbrado público; Infraestructura comunitaria; Mantenimiento vial",
        "keywords": "hueco, via, andén, puente, obra, calle, pavimento, alumbrado, luz, poste, derrumbe, grieta, zanja",
        "email_contacto": "obrapublica@medellin.gov.co",
        "telefono": "604 385 5151",
    },
    {
        "sigla": "DAGER",
        "nombre": "Departamento Administrativo de Gestión del Riesgo",
        "descripcion": "Previene y atiende emergencias por desastres naturales y eventos de origen antrópico.",
        "competencias": "Emergencias; Inundaciones; Deslizamientos; Atención a víctimas; Zonas de riesgo; Alertas tempranas",
        "keywords": "emergencia, inundación, deslizamiento, derrumbe, terremoto, riesgo, desastre, alerta, evacuación, desalojo",
        "email_contacto": "gestionriesgo@medellin.gov.co",
        "telefono": "604 444 0000",
    },
    {
        "sigla": "INDER",
        "nombre": "Instituto de Deportes y Recreación",
        "descripcion": "Promueve el deporte, la recreación y la actividad física en todos los estratos sociales.",
        "competencias": "Escuelas deportivas; Polideportivos; Eventos deportivos; Recreación comunitaria; Parques",
        "keywords": "deporte, fútbol, natación, parque, polideportivo, recreación, canchas, gimnasio, evento deportivo",
        "email_contacto": "inder@medellin.gov.co",
        "telefono": "604 385 1212",
    },
    {
        "sigla": "CULTM",
        "nombre": "Secretaría de Cultura Ciudadana",
        "descripcion": "Fomenta la cultura, el arte, las tradiciones y la convivencia ciudadana.",
        "competencias": "Cultura y arte; Patrimonio; Eventos culturales; Convivencia ciudadana; Espacio público",
        "keywords": "cultura, arte, música, teatro, patrimonio, festival, evento cultural, convivencia, espacio público",
        "email_contacto": "cultura@medellin.gov.co",
        "telefono": "604 385 1515",
    },
    {
        "sigla": "PLADES",
        "nombre": "Departamento Administrativo de Planeación",
        "descripcion": "Orienta el ordenamiento territorial y el desarrollo urbano sostenible.",
        "competencias": "POT; Licencias urbanísticas; Estratificación; Uso del suelo; Planes parciales; Catastro",
        "keywords": "licencia construcción, POT, estratificación, uso suelo, urbanismo, lote, construcción ilegal, planos",
        "email_contacto": "planeacion@medellin.gov.co",
        "telefono": "604 385 2020",
    },
    {
        "sigla": "HACIENDA",
        "nombre": "Secretaría de Hacienda",
        "descripcion": "Administra los recursos financieros del municipio, tributos y contratación pública.",
        "competencias": "Impuesto predial; ICA; Deudas tributarias; Contratación pública; Presupuesto municipal",
        "keywords": "impuesto, predial, ICA, deuda, tributario, factura, pago, embargo, multa tributaria, contribución",
        "email_contacto": "hacienda@medellin.gov.co",
        "telefono": "604 385 2525",
    },
    {
        "sigla": "CONTROL",
        "nombre": "Secretaría de Control y Gestión Territorial",
        "descripcion": "Ejerce control sobre el uso del espacio público, establecimientos comerciales y obras.",
        "competencias": "Espacio público; Establecimientos de comercio; Vendedores informales; Obras sin licencia",
        "keywords": "vendedor informal, espacio público, establecimiento, bar, discoteca, ruido nocturno, obra ilegal, cerramiento",
        "email_contacto": "control@medellin.gov.co",
        "telefono": "604 385 3030",
    },
    {
        "sigla": "JARDIMDE",
        "nombre": "Jardín Botánico de Medellín",
        "descripcion": "Centro de conservación de flora, biodiversidad y educación ambiental.",
        "competencias": "Flora urbana; Conservación; Educación ambiental; Investigación botánica",
        "keywords": "jardín botánico, plantas, flores, conservación, biodiversidad, árbol patrimonial, orquídeas",
        "email_contacto": "info@botanicomedellin.org",
        "telefono": "604 444 5500",
    },
    {
        "sigla": "ISVIMED",
        "nombre": "Instituto Social de Vivienda y Hábitat de Medellín",
        "descripcion": "Ejecuta proyectos de vivienda de interés social y mejoramiento de hábitat.",
        "competencias": "VIS; VIP; Subsidios habitacionales; Mejoramiento de vivienda; Reasentamiento",
        "keywords": "VIS, VIP, vivienda interés social, subsidio vivienda, postulación, listado espera, reasentamiento",
        "email_contacto": "isvimed@medellin.gov.co",
        "telefono": "604 385 4848",
    },
    {
        "sigla": "EDU",
        "nombre": "Empresa de Desarrollo Urbano",
        "descripcion": "Gestiona proyectos de renovación urbana, espacio público y equipamientos.",
        "competencias": "Renovación urbana; Macroproyectos; Espacio público; Equipamientos colectivos",
        "keywords": "renovación urbana, proyecto urbano, parque, espacio público, equipamiento, macroproyecto",
        "email_contacto": "edu@edu.gov.co",
        "telefono": "604 385 7474",
    },
    {
        "sigla": "EPM",
        "nombre": "Empresas Públicas de Medellín",
        "descripcion": "Presta servicios de agua, energía, gas y telecomunicaciones en Medellín.",
        "competencias": "Acueducto; Alcantarillado; Energía eléctrica; Gas natural; Internet; Facturación servicios",
        "keywords": "agua, luz, energía, gas, alcantarillado, tubería, fuga, corte servicio, factura EPM, internet",
        "email_contacto": "atencion@epm.com.co",
        "telefono": "604 444 2626",
    },
    {
        "sigla": "METRO",
        "nombre": "Metro de Medellín",
        "descripcion": "Opera el sistema masivo de transporte público metro, metrocable y tranvía.",
        "competencias": "Metro; Metrocable; Tranvía; Tarifa; Integración tarifaria; Infraestructura metro",
        "keywords": "metro, metrocable, tranvía, tarjeta cívica, tarifa, estación, retraso, accidente metro",
        "email_contacto": "servicio@metrodemedellin.gov.co",
        "telefono": "604 452 6300",
    },
    {
        "sigla": "DAGRD",
        "nombre": "Dagrd — Gestión del Riesgo de Desastres",
        "descripcion": "Coordina la respuesta a emergencias y la prevención de desastres en Medellín.",
        "competencias": "Prevención desastres; Atención emergencias; Zonas de alto riesgo no mitigable; Alertas",
        "keywords": "emergencia, deslizamiento, inundación, riesgo alto, zona riesgo, calamidad, desastre, evacuación",
        "email_contacto": "dagrd@medellin.gov.co",
        "telefono": "123",
    },
    {
        "sigla": "EMVARIAS",
        "nombre": "Empresas Varias de Medellín",
        "descripcion": "Gestiona el aseo, recolección de residuos y barrido de vías en el municipio.",
        "competencias": "Recolección basuras; Barrido calles; Escombros; Puntos críticos; Reciclaje",
        "keywords": "basura, aseo, recolección, escombros, reciclaje, limpieza, punto crítico, barrido, residuos",
        "email_contacto": "atencion@emvarias.gov.co",
        "telefono": "604 444 0022",
    },
    {
        "sigla": "ITSMAP",
        "nombre": "Instituto Tecnológico Metropolitano",
        "descripcion": "Institución de educación superior pública del municipio de Medellín.",
        "competencias": "Educación superior pública; Becas ITM; Acceso a programas técnicos y tecnológicos",
        "keywords": "ITM, educación superior, beca, tecnólogo, técnico, universidad pública, matrícula ITM",
        "email_contacto": "admisiones@itm.edu.co",
        "telefono": "604 440 5100",
    },
    {
        "sigla": "PERSONERIA",
        "nombre": "Personería de Medellín",
        "descripcion": "Defiende los derechos humanos, el ejercicio de las veedurías y el control de la administración.",
        "competencias": "Derechos humanos; Veedurías ciudadanas; Control disciplinario; Tutelas; Quejas contra funcionarios",
        "keywords": "tutela, derechos humanos, queja funcionario, corrupción, veeduría, discriminación, acoso, abuso autoridad",
        "email_contacto": "personeria@personeriamedellin.gov.co",
        "telefono": "604 516 0808",
    },
    {
        "sigla": "CONTRAL",
        "nombre": "Contraloría General de Medellín",
        "descripcion": "Ejerce control fiscal sobre los recursos públicos del municipio.",
        "competencias": "Control fiscal; Auditorías; Denuncias de corrupción; Uso indebido de recursos públicos",
        "keywords": "corrupción, malversación, recursos públicos, contrato irregular, soborno, auditoría, control fiscal",
        "email_contacto": "contraloriageneral@contraloriadem.gov.co",
        "telefono": "604 251 7474",
    },
    {
        "sigla": "ALCALDE",
        "nombre": "Despacho del Alcalde",
        "descripcion": "Oficina directa del Alcalde de Medellín para asuntos de alta dirección.",
        "competencias": "Peticiones directas al Alcalde; Asuntos de interés general; Correspondencia oficial",
        "keywords": "alcalde, alcaldía, dirección, carta alcalde, petición especial, urgente, grave",
        "email_contacto": "alcalde@medellin.gov.co",
        "telefono": "604 385 0000",
    },
]

PQRSDS_PRUEBA = [
    {
        "tipo": "queja",
        "canal_entrada": "web",
        "nombre_ciudadano": "María Fernanda Ospina",
        "email_ciudadano": "mf.ospina@gmail.com",
        "telefono_ciudadano": "3014567890",
        "documento_ciudadano": "43201567",
        "comuna": "Laureles-Estadio",
        "barrio": "Los Conquistadores",
        "asunto": "Hueco peligroso en la Cra 76 con Calle 35",
        "descripcion": "Buenos días, me dirijo a ustedes para reportar un hueco de gran tamaño en la carrera 76 con calle 35, barrio Los Conquistadores. Este daño lleva más de 3 meses sin ser atendido y ya ha causado dos accidentes de motociclistas. El hueco tiene aproximadamente 60 cm de diámetro y 20 cm de profundidad. Adjunto fotografías. Solicito reparación urgente antes de que ocurra una tragedia.",
        "prioridad": "alta",
        "estado": "radicada",
        "dep_sigla": "SOPUB",
        "dias_vencimiento": 10,
    },
    {
        "tipo": "peticion",
        "canal_entrada": "email",
        "nombre_ciudadano": "Carlos Andrés Restrepo",
        "email_ciudadano": "c.restrepo.med@hotmail.com",
        "telefono_ciudadano": "3127654321",
        "documento_ciudadano": "71345678",
        "comuna": "Villa Hermosa",
        "barrio": "Enciso",
        "asunto": "Solicitud de información sobre subsidio de vivienda VIS 2026",
        "descripcion": "Cordial saludo. Soy cabeza de familia con 4 hijos, vivo en arriendo en el barrio Enciso y quisiera saber los requisitos para aplicar al subsidio de vivienda de interés social convocado para el año 2026. Tengo ingresos de 2 SMLV. Agradezco información sobre fechas, documentos necesarios y cómo postularme.",
        "prioridad": "media",
        "estado": "clasificada",
        "dep_sigla": "ISVIMED",
        "clasificacion_validada": True,
        "dias_vencimiento": 8,
    },
    {
        "tipo": "denuncia",
        "canal_entrada": "whatsapp",
        "nombre_ciudadano": "Ana Lucía Gómez",
        "email_ciudadano": "ana.gomez.denuncia@gmail.com",
        "telefono_ciudadano": "3205551234",
        "documento_ciudadano": "52876543",
        "comuna": "Guayabal",
        "barrio": "La Colina",
        "asunto": "Establecimiento comercial vertiendo aguas residuales a la quebrada La Hueso",
        "descripcion": "Denuncio que la empresa de lavado de vehículos ubicada en la calle 12 sur #42-15 del barrio La Colina está vertiendo directamente sus aguas residuales con jabón y aceite a la quebrada La Hueso. Esto ocurre todos los días entre 8am y 5pm. Ya hablé con el dueño y me dijo que 'eso no le importa a nadie'. Solicito inspección urgente y sanción.",
        "prioridad": "urgente",
        "estado": "en_tramite",
        "dep_sigla": "SOMA",
        "clasificacion_validada": True,
        "dias_vencimiento": 2,
    },
    {
        "tipo": "reclamo",
        "canal_entrada": "presencial",
        "nombre_ciudadano": "Jorge Iván Martínez",
        "email_ciudadano": "jorge.martinez1975@yahoo.com",
        "telefono_ciudadano": "3004443322",
        "documento_ciudadano": "8901234",
        "comuna": "San Javier",
        "barrio": "Las Independencias",
        "asunto": "Cobro indebido en licencia de funcionamiento de tienda de barrio",
        "descripcion": "Presento reclamo formal por cobro excesivo en el trámite de renovación de mi licencia de funcionamiento para mi tienda de barrio. Según la norma vigente el costo es de 45.000 pesos pero me cobraron 180.000 pesos sin justificación. Hice el pago el 15 de marzo y solicito la devolución del excedente cobrado o la justificación escrita del cobro adicional.",
        "prioridad": "media",
        "estado": "en_tramite",
        "dep_sigla": "CONTROL",
        "clasificacion_validada": True,
        "dias_vencimiento": 5,
    },
    {
        "tipo": "sugerencia",
        "canal_entrada": "instagram",
        "nombre_ciudadano": "Valentina Torres",
        "email_ciudadano": "valen.torres.med@gmail.com",
        "telefono_ciudadano": "3157778899",
        "documento_ciudadano": "1037654321",
        "comuna": "El Poblado",
        "barrio": "Patio Bonito",
        "asunto": "Propuesta para ampliar ciclovía nocturna los fines de semana",
        "descripcion": "Hola, soy ciclista urbana y quiero sugerir que se amplíe el horario de la ciclovía nocturna los viernes y sábados hasta la medianoche, especialmente en el eje del Parque Lineal El Poblado. Actualmente cierra a las 10pm y muchos trabajadores nocturnos no pueden usarla. Además propongo instalar más iluminación LED en el tramo entre la Loma de Los Balsos y la Aguacatala.",
        "prioridad": "baja",
        "estado": "respondida",
        "dep_sigla": "SMOT",
        "clasificacion_validada": True,
        "dias_vencimiento": -3,
    },
    {
        "tipo": "peticion",
        "canal_entrada": "web",
        "anonimo": True,
        "nombre_ciudadano": "",
        "email_ciudadano": "",
        "telefono_ciudadano": "",
        "documento_ciudadano": "",
        "comuna": "Castilla",
        "barrio": "Tricentenario",
        "asunto": "Denuncia anónima: venta de alucinógenos en parque infantil",
        "descripcion": "De manera anónima denuncio que en el parque infantil del barrio Tricentenario, frente al bloque 4 de las Torres de Tricentenario, hay personas vendiendo sustancias alucinógenas todos los días desde las 6pm. Los niños no pueden jugar allí con seguridad. Por favor tomar medidas de seguridad urgentes.",
        "prioridad": "urgente",
        "estado": "en_clasificacion",
        "dep_sigla": "SSPM",
        "dias_vencimiento": 13,
    },
    {
        "tipo": "queja",
        "canal_entrada": "email",
        "nombre_ciudadano": "Rubén Darío Cano",
        "email_ciudadano": "ruben.cano.med@gmail.com",
        "telefono_ciudadano": "3213334455",
        "documento_ciudadano": "70123456",
        "comuna": "Aranjuez",
        "barrio": "San Isidro",
        "asunto": "Falta de recolección de basuras hace 10 días en el barrio San Isidro",
        "descripcion": "Señores Alcaldía, hace exactamente 10 días que en nuestro barrio San Isidro de la comuna Aranjuez no pasa el carro de la basura. Los residuos se están acumulando en las esquinas generando olores y plagas. Ya llamé a Emvarias al 4440022 y me dicen que el camión está en mantenimiento pero no dan fecha de solución. Esto es un problema de salud pública.",
        "prioridad": "alta",
        "estado": "radicada",
        "dep_sigla": "EMVARIAS",
        "dias_vencimiento": 14,
    },
    {
        "tipo": "reclamo",
        "canal_entrada": "web",
        "nombre_ciudadano": "Luisa Ángela Herrera",
        "email_ciudadano": "luisa.herrera.abg@gmail.com",
        "telefono_ciudadano": "3008887766",
        "documento_ciudadano": "42567890",
        "comuna": "La Candelaria",
        "barrio": "Centro",
        "asunto": "Funcionario de tránsito impuso comparendo sin fundamento legal",
        "descripcion": "Interpongo reclamo formal contra el agente de tránsito con placa 4521 que el día 10 de abril de 2026 me impuso un comparendo en la carrera 46 con avenida El Poblado por supuestamente transitar en contravía, cuando la señalización en ese punto no existe y el flujo vehicular es bidireccional. Tengo video del momento. Solicito nulidad del comparendo y investigación disciplinaria al agente.",
        "prioridad": "media",
        "estado": "clasificada",
        "dep_sigla": "SMOT",
        "clasificacion_validada": True,
        "dias_vencimiento": 7,
    },
    {
        "tipo": "peticion",
        "canal_entrada": "presencial",
        "nombre_ciudadano": "Doris Elena Zapata",
        "email_ciudadano": "doris.zapata.65@gmail.com",
        "telefono_ciudadano": "3146665544",
        "documento_ciudadano": "32112345",
        "comuna": "Manrique",
        "barrio": "La Cruz",
        "asunto": "Solicito cupo escolar urgente para mi hijo de 6 años",
        "descripcion": "Soy madre cabeza de hogar y llevo 3 meses intentando conseguir cupo escolar para mi hijo de 6 años en las instituciones educativas cercanas al barrio La Cruz. En la IE Marco Fidel Suárez me dicen que no hay cupos y en la IE Rodrigo Lara Bonilla tampoco. Mi hijo tiene derecho a la educación. Solicito intervención urgente de la Secretaría de Educación para garantizar este derecho fundamental.",
        "prioridad": "alta",
        "estado": "en_tramite",
        "dep_sigla": "SEDU",
        "clasificacion_validada": True,
        "dias_vencimiento": 1,
    },
    {
        "tipo": "denuncia",
        "canal_entrada": "web",
        "nombre_ciudadano": "Felipe Andrés Montoya",
        "email_ciudadano": "f.montoya.den@gmail.com",
        "telefono_ciudadano": "3182221133",
        "documento_ciudadano": "1017891234",
        "comuna": "Belén",
        "barrio": "Las Violetas",
        "asunto": "Construcción ilegal en zona de ladera sin licencia",
        "descripcion": "Denuncio que en el lote ubicado en la calle 31A sur #95-20 del barrio Las Violetas se está construyendo una edificación de 3 pisos sin licencia de construcción y en zona de ladera con pendiente superior al 40%, lo que representa riesgo geotécnico para las viviendas colindantes. La obra funciona 7 días a la semana incluso en festivos. Solicito suspensión inmediata y visita de Planeación y Dagrd.",
        "prioridad": "urgente",
        "estado": "radicada",
        "dep_sigla": "PLADES",
        "dias_vencimiento": 15,
    },
]

PRECEDENTES = [
    {
        "dep_sigla": "SOPUB",
        "tipo": "queja",
        "pregunta": "¿Qué hace la Secretaría de Obras Públicas ante un reporte de hueco en vía?",
        "respuesta": "La Secretaría de Obras Públicas programa visita técnica en un plazo máximo de 5 días hábiles para evaluar el daño. Según la gravedad, ordena la intervención de cuadrillas de mantenimiento vial en un plazo de 15 días hábiles adicionales. El ciudadano puede hacer seguimiento con el número de radicado.",
        "normativa": "Decreto 1228 de 2010; Resolución 1282 de 2012 (estándares vías municipales)",
        "veces": 47,
    },
    {
        "dep_sigla": "ISVIMED",
        "tipo": "peticion",
        "pregunta": "¿Cuáles son los requisitos para postularse al subsidio de vivienda VIS?",
        "respuesta": "Para aplicar al subsidio VIS debe: 1) No ser propietario de vivienda, 2) Ingresos familiares no superiores a 4 SMLV, 3) Conformar un hogar (mínimo 2 personas), 4) Contar con ahorro programado equivalente al 10% del valor de la vivienda. Documentos: cédulas, certificado de ingresos, extractos bancarios de 6 meses. Las convocatorias se abren 2 veces al año.",
        "normativa": "Ley 3 de 1991; Decreto 2190 de 2009; Decreto 1077 de 2015",
        "veces": 83,
    },
    {
        "dep_sigla": "SOMA",
        "tipo": "denuncia",
        "pregunta": "¿Cómo se tramita una denuncia por vertimiento ilegal a fuentes hídricas?",
        "respuesta": "La Secretaría de Medio Ambiente programa visita de inspección ambiental en un plazo máximo de 3 días hábiles. Si se confirma el vertimiento ilegal, se impone medida preventiva de suspensión de actividades y se inicia proceso sancionatorio ambiental. El denunciante puede reservar su identidad. La empresa puede ser multada hasta con 5.000 SMLMV.",
        "normativa": "Ley 99 de 1993; Decreto 3930 de 2010; Código Nacional de Recursos Naturales",
        "veces": 29,
    },
    {
        "dep_sigla": "SMOT",
        "tipo": "reclamo",
        "pregunta": "¿Cómo se puede impugnar un comparendo de tránsito?",
        "respuesta": "El infractor puede presentar descargos ante el funcionario de tránsito dentro de los 5 días hábiles siguientes a la imposición. Si no está de acuerdo con la decisión, puede interponer recurso de apelación ante el Director de Movilidad. El proceso es gratuito y no requiere abogado. Si tiene evidencia (video, testigos), debe aportarla con los descargos.",
        "normativa": "Ley 1843 de 2017 (fotomultas); Código Nacional de Tránsito art. 135; Resolución 3027 de 2010",
        "veces": 62,
    },
    {
        "dep_sigla": "SEDU",
        "tipo": "peticion",
        "pregunta": "¿Qué hacer cuando no hay cupo escolar disponible para un menor?",
        "respuesta": "La Secretaría de Educación tiene la obligación legal de garantizar cupo en institución oficial dentro del municipio. El padre/madre debe radicar la solicitud en la Secretaría con documentos del menor (registro civil, comprobante de residencia, carné de vacunación). En casos urgentes, la Secretaría puede ordenar directamente la matrícula en la institución más cercana con disponibilidad.",
        "normativa": "Constitución art. 67; Ley 115 de 1994; Decreto 1421 de 2017; Ley 1098 de 2006",
        "veces": 38,
    },
]


class Command(BaseCommand):
    help = "Carga datos de prueba para OmegaHack 2026 (idempotente)"

    def handle(self, *args, **kwargs):
        from apps.conocimiento.models import Dependencia, PrecedenteRespuesta
        from apps.pqrsd.models import PQRSD

        self.stdout.write("Cargando dependencias...")
        dep_map = {}
        for d in DEPENDENCIAS:
            obj, created = Dependencia.objects.get_or_create(
                sigla=d["sigla"],
                defaults={k: v for k, v in d.items() if k != "sigla"},
            )
            dep_map[d["sigla"]] = obj
            if created:
                self.stdout.write(f"  + {obj.sigla}")

        self.stdout.write("Cargando precedentes...")
        for p in PRECEDENTES:
            dep = dep_map.get(p["dep_sigla"])
            if not dep:
                continue
            PrecedenteRespuesta.objects.get_or_create(
                dependencia=dep,
                pregunta_frecuente=p["pregunta"],
                defaults={
                    "tipo_pqrsd": p["tipo"],
                    "respuesta_base": p["respuesta"],
                    "normativa_aplicable": p["normativa"],
                    "usado_veces": p["veces"],
                },
            )

        self.stdout.write("Cargando PQRSDs de prueba...")
        hoy = date.today()
        for idx, data in enumerate(PQRSDS_PRUEBA):
            dep_sigla = data.pop("dep_sigla", None)
            clasificacion_validada = data.pop("clasificacion_validada", False)
            dias = data.pop("dias_vencimiento", 15)

            if PQRSD.objects.filter(asunto=data["asunto"]).exists():
                continue

            p = PQRSD(**data)
            p.fecha_limite = hoy + timedelta(days=dias)
            p.save()

            if dep_sigla and dep_sigla in dep_map:
                dep = dep_map[dep_sigla]
                p.dependencia_asignada = dep
                p.dependencia_sugerida = dep
                p.clasificacion_validada = clasificacion_validada
                p.confianza_clasificacion = 87 if clasificacion_validada else None
                p.save()

        self.stdout.write("Creando usuarios de prueba...")
        if not User.objects.filter(username="enlace1").exists():
            User.objects.create_user(
                username="enlace1",
                password="pqrsd2026",
                first_name="Laura",
                last_name="Ríos",
                email="enlace1@medellin.gov.co",
                is_staff=True,
            )
            self.stdout.write("  + enlace1 / pqrsd2026")

        if not User.objects.filter(username="juridico1").exists():
            User.objects.create_user(
                username="juridico1",
                password="pqrsd2026",
                first_name="Hernán",
                last_name="Vélez",
                email="juridico1@medellin.gov.co",
                is_staff=True,
            )
            self.stdout.write("  + juridico1 / pqrsd2026")

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                password="admin1234",
                email="admin@medellin.gov.co",
            )
            self.stdout.write("  + admin / admin1234 (superuser)")

        self.stdout.write(self.style.SUCCESS("Datos de prueba cargados exitosamente."))
