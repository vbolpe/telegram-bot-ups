flowchart TD
    A[Inicio] --> B[Contenedor Docker activo]
    B --> C[Ejecutar monitor_ups.sh cada 30s]
    C --> D[SNMP GET a UPS Eaton 93E]

    D -->|Timeout / Error| E[Log error y esperar siguiente ciclo]
    E --> C

    D -->|Respuesta OK| F[Leer upsBasicBatteryStatus]
    F --> G{¿Estado cambió?}

    G -->|No| H[No hacer nada]
    H --> C

    G -->|Sí| I[Guardar nuevo estado]
    I --> J{Estado UPS}

    J -->|En línea| K[Evento: Energía restaurada]
    J -->|En batería| L[Evento: Corte eléctrico]
    J -->|Otro| M[Evento: Estado desconocido]

    K --> N[Log evento]
    L --> N
    M --> N

    N --> O{¿Telegram habilitado?}
    O -->|No| C
    O -->|Sí| P[Enviar mensaje al Bot Telegram]
    P --> C
