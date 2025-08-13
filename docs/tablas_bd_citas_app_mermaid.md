erDiagram
    NEGOCIOS {
        INT id PK
        VARCHAR nombre
        TEXT descripcion
        VARCHAR direccion
        VARCHAR telefono
        VARCHAR email
        VARCHAR tipo_negocio
        VARCHAR zona_horaria
        BOOLEAN activo
        TIMESTAMP fecha_creacion
        TIMESTAMP fecha_modificacion
    }

    SERVICIOS {
        INT id PK
        INT negocio_id FK
        VARCHAR nombre
        TEXT descripcion
        INT duracion_minutos
        DECIMAL precio
        INT capacidad_maxima
        VARCHAR color_hex
        BOOLEAN activo
        TIMESTAMP fecha_creacion
        TIMESTAMP fecha_modificacion
    }

    RECURSOS {
        INT id PK
        INT negocio_id FK
        VARCHAR nombre
        VARCHAR tipo
        TEXT descripcion
        BOOLEAN activo
        TIMESTAMP fecha_creacion
        TIMESTAMP fecha_modificacion
    }

    SERVICIO_RECURSOS {
        INT id PK
        INT servicio_id FK
        INT recurso_id FK
        INT cantidad_necesaria
        %% UNIQUE(servicio_id, recurso_id)
        TIMESTAMP fecha_registro
        TIMESTAMP fecha_modificacion
    }

    HORARIOS_NEGOCIO {
        INT id PK
        INT negocio_id FK
        INT dia_semana
        TIME hora_inicio
        TIME hora_fin
        BOOLEAN activo
        TIMESTAMP fecha_registro
        TIMESTAMP fecha_modificacion
    }

    HORARIOS_SERVICIO {
        INT id PK
        INT servicio_id FK
        INT dia_semana
        TIME hora_inicio
        TIME hora_fin
        BOOLEAN activo
        TIMESTAMP fecha_registro
        TIMESTAMP fecha_modificacion
    }

    CLIENTES {
        INT id PK
        VARCHAR nombre
        VARCHAR apellido
        VARCHAR telefono
        VARCHAR email
        DATE fecha_nacimiento
        TEXT notas
        BOOLEAN activo
        TIMESTAMP fecha_registro
        TIMESTAMP fecha_modificacion
    }

    CITAS {
        INT id PK
        INT negocio_id FK
        INT servicio_id FK
        INT cliente_id FK
        TIMESTAMP fecha_hora_inicio
        TIMESTAMP fecha_hora_fin
        VARCHAR estado
        TEXT notas
        DECIMAL precio_final
        VARCHAR metodo_reserva
        TIMESTAMP fecha_creacion
        TIMESTAMP fecha_modificacion
    }

    CITA_RECURSOS {
        INT id PK
        INT cita_id FK
        INT recurso_id FK
        TIMESTAMP fecha_hora_inicio
        TIMESTAMP fecha_hora_fin
        TIMESTAMP fecha_creacion
        TIMESTAMP fecha_modificacion
    }

    BLOQUEOS_RECURSOS {
        INT id PK
        INT recurso_id FK
        TIMESTAMP fecha_hora_inicio
        TIMESTAMP fecha_hora_fin
        VARCHAR motivo
        BOOLEAN activo
        TIMESTAMP fecha_creacion
        TIMESTAMP fecha_creacion
        TIMESTAMP fecha_modificacion
    }

    CONFIGURACION_AGENDA {
        INT id PK
        INT negocio_id FK
        INT intervalo_citas
        INT tiempo_buffer
        INT anticipacion_maxima_dias
        INT cancelacion_limite_horas
        BOOLEAN overbooking_permitido
        TIMESTAMP fecha_creacion
        TIMESTAMP fecha_modificacion
    }

    %% Relaciones 1:N y 1:1 principales
    NEGOCIOS ||--o{ SERVICIOS : "1:N"
    NEGOCIOS ||--o{ RECURSOS : "1:N"
    NEGOCIOS ||--o{ CITAS : "1:N"
    NEGOCIOS ||--o{ HORARIOS_NEGOCIO : "1:N"
    SERVICIOS ||--o{ HORARIOS_SERVICIO : "1:N"
    SERVICIOS ||--o{ CITAS : "1:N"
    CLIENTES  ||--o{ CITAS : "1:N"
    RECURSOS  ||--o{ BLOQUEOS_RECURSOS : "1:N"
    NEGOCIOS  ||--|| CONFIGURACION_AGENDA : "1:1"

    %% Relaciones N:M mediante tablas puente
    SERVICIOS  ||--o{ SERVICIO_RECURSOS : "1:N"
    RECURSOS   ||--o{ SERVICIO_RECURSOS : "1:N"

    CITAS      ||--o{ CITA_RECURSOS : "1:N"
    RECURSOS   ||--o{ CITA_RECURSOS : "1:N"
