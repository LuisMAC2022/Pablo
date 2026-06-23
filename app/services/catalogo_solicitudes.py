"""Catálogo de áreas, subcategorías y opciones para solicitudes de servicios."""

CATALOGO_SERVICIOS = [
    {
        "nombre": "Mantenimiento y Protección Civil",
        "slug": "mantenimiento_proteccion_civil",
        "subcategorias": [
            {
                "id": "infraestructura",
                "nombre": "Infraestructura",
                "opciones": [
                    {"valor": "albanileria", "etiqueta": "Albañilería"},
                    {"valor": "carpinteria", "etiqueta": "Carpintería"},
                    {"valor": "electricidad", "etiqueta": "Electricidad"},
                    {"valor": "herreria", "etiqueta": "Herrería"},
                    {"valor": "pintura", "etiqueta": "Pintura"},
                    {"valor": "plomeria", "etiqueta": "Plomería"},
                    {"valor": "otro", "etiqueta": "Otro"},
                ],
            },
            {
                "id": "equipo_parque_vehicular",
                "nombre": "Equipo y parque vehicular",
                "opciones": [
                    {"valor": "mecanica", "etiqueta": "Mecánica"},
                    {"valor": "refrigeracion", "etiqueta": "Refrigeración"},
                    {"valor": "aire_acondicionado", "etiqueta": "Aire acondicionado"},
                    {"valor": "equipo_computo", "etiqueta": "Equipo de cómputo"},
                    {"valor": "reparacion_equipo", "etiqueta": "Reparación de equipo"},
                    {"valor": "planta_luz", "etiqueta": "Planta de luz"},
                    {"valor": "otro", "etiqueta": "Otro"},
                ],
            },
        ],
    },
    {
        "nombre": "Seguridad",
        "slug": "seguridad",
        "subcategorias": [
            {
                "id": "seguridad",
                "nombre": "Seguridad",
                "opciones": [
                    {"valor": "vigilancia_eventos", "etiqueta": "Vigilancia para eventos"},
                    {"valor": "control_accesos", "etiqueta": "Control de accesos"},
                    {"valor": "otro", "etiqueta": "Otro"},
                ],
            },
        ],
    },
    {
        "nombre": "Servicios de Apoyo",
        "slug": "servicios_apoyo",
        "subcategorias": [
            {
                "id": "transporte",
                "nombre": "Transporte",
                "opciones": [
                    {"valor": "local", "etiqueta": "Local"},
                    {"valor": "foraneo", "etiqueta": "Foráneo"},
                    {"valor": "pasajeros", "etiqueta": "Pasajeros"},
                    {"valor": "carga", "etiqueta": "Carga"},
                ],
            },
            {
                "id": "diversos_limpieza",
                "nombre": "Diversos y limpieza",
                "opciones": [
                    {"valor": "cafeteria", "etiqueta": "Cafetería"},
                    {"valor": "cerrajeria", "etiqueta": "Cerrajería"},
                    {"valor": "limpieza", "etiqueta": "Limpieza"},
                    {"valor": "otro", "etiqueta": "Otro"},
                ],
            },
            {
                "id": "prestamo_de",
                "nombre": "Préstamo de",
                "opciones": [
                    {"valor": "salas_aulas", "etiqueta": "Salas o aulas"},
                    {"valor": "auditorio", "etiqueta": "Auditorio"},
                    {"valor": "equipo_audiovisual", "etiqueta": "Equipo audiovisual"},
                ],
            },
            {
                "id": "correspondencia_paqueteria",
                "nombre": "Correspondencia y/o paquetería",
                "opciones": [
                    {"valor": "propio", "etiqueta": "Propio"},
                    {"valor": "correo_ordinario", "etiqueta": "C. ordinario"},
                    {"valor": "mensajeria_especializada", "etiqueta": "M. especializada"},
                ],
            },
            {
                "id": "reproduccion_engargolado",
                "nombre": "Reproducción y/o engargolado",
                "opciones": [
                    {"valor": "reproduccion", "etiqueta": "Reproducción"},
                    {"valor": "engargolado", "etiqueta": "Engargolado"},
                    {"valor": "otro", "etiqueta": "Otro"},
                ],
            },
        ],
    },
]

AREAS_SOLICITUD_ACTIVAS = [area["nombre"] for area in CATALOGO_SERVICIOS]

SUBCATEGORIAS_POR_AREA = {
    area["nombre"]: {subcategoria["id"]: subcategoria for subcategoria in area["subcategorias"]}
    for area in CATALOGO_SERVICIOS
}

SUBCATEGORIAS_SERVICIO = {
    subcategoria["id"]: subcategoria
    for area in CATALOGO_SERVICIOS
    for subcategoria in area["subcategorias"]
}

CAMPOS_OPCIONES_SERVICIO = tuple(SUBCATEGORIAS_SERVICIO.keys())
