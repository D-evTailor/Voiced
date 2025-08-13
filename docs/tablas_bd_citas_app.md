# Base de Datos - Sistema de Reserva de Citas

## 1. TABLAS PRINCIPALES

### **NEGOCIOS**
```sql
CREATE TABLE negocios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    direccion VARCHAR(200),
    telefono VARCHAR(20),
    email VARCHAR(100),
    tipo_negocio VARCHAR(50), -- 'restaurante', 'peluqueria', 'clinica', etc.
    zona_horaria VARCHAR(50) DEFAULT 'Europe/Madrid',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Propósito**: Almacena información básica de cada negocio registrado
**Relaciones**: 1:N con servicios, recursos, horarios, citas

### **SERVICIOS**
```sql
CREATE TABLE servicios (
    id SERIAL PRIMARY KEY,
    negocio_id INTEGER NOT NULL REFERENCES negocios(id),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    duracion_minutos INTEGER NOT NULL, -- Duración del servicio
    precio DECIMAL(10,2),
    capacidad_maxima INTEGER DEFAULT 1, -- Cuántas personas pueden recibir el servicio simultáneamente
    color_hex VARCHAR(7) DEFAULT '#3B82F6', -- Para visualización en calendario
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Propósito**: Define los servicios que ofrece cada negocio
**Relaciones**: N:1 con negocios, 1:N con citas, N:M con recursos

### **RECURSOS**
```sql
CREATE TABLE recursos (
    id SERIAL PRIMARY KEY,
    negocio_id INTEGER NOT NULL REFERENCES negocios(id),
    nombre VARCHAR(100) NOT NULL, -- 'Dr. García', 'Sala 1', 'Mesa Terraza 4'
    tipo VARCHAR(50), -- 'persona', 'espacio', 'equipo'
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Propósito**: Representa elementos limitantes (personas, espacios, equipos)
**Relaciones**: N:1 con negocios, N:M con servicios, 1:N con asignaciones de citas

### **SERVICIO_RECURSOS**
```sql
CREATE TABLE servicio_recursos (
    id SERIAL PRIMARY KEY,
    servicio_id INTEGER NOT NULL REFERENCES servicios(id),
    recurso_id INTEGER NOT NULL REFERENCES recursos(id),
    cantidad_necesaria INTEGER DEFAULT 1,
    UNIQUE(servicio_id, recurso_id)
);
```
**Propósito**: Define qué recursos necesita cada servicio
**Ejemplo**: El servicio "Consulta Cardiología" necesita 1 "Dr. Cardiólogo" + 1 "Consultorio"

## 2. TABLAS DE CONFIGURACIÓN DE HORARIOS

### **HORARIOS_NEGOCIO**
```sql
CREATE TABLE horarios_negocio (
    id SERIAL PRIMARY KEY,
    negocio_id INTEGER NOT NULL REFERENCES negocios(id),
    dia_semana INTEGER NOT NULL, -- 0=Domingo, 1=Lunes, ..., 6=Sábado
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);
```
**Propósito**: Define los horarios de operación generales del negocio

### **HORARIOS_SERVICIO**
```sql
CREATE TABLE horarios_servicio (
    id SERIAL PRIMARY KEY,
    servicio_id INTEGER NOT NULL REFERENCES servicios(id),
    dia_semana INTEGER NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);
```
**Propósito**: Horarios específicos por servicio (opcional)
**Ejemplo**: "Masajes relajantes" solo de 14:00 a 20:00

## 3. GESTIÓN DE CLIENTES Y CITAS

### **CLIENTES**
```sql
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    fecha_nacimiento DATE,
    notas TEXT, -- Alergias, preferencias, etc.
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Propósito**: Información de los clientes
**Relaciones**: 1:N con citas

### **CITAS**
```sql
CREATE TABLE citas (
    id SERIAL PRIMARY KEY,
    negocio_id INTEGER NOT NULL REFERENCES negocios(id),
    servicio_id INTEGER NOT NULL REFERENCES servicios(id),
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    fecha_hora_inicio TIMESTAMP NOT NULL,
    fecha_hora_fin TIMESTAMP NOT NULL,
    estado VARCHAR(20) DEFAULT 'confirmada', -- 'confirmada', 'cancelada', 'completada', 'no_asistio'
    notas TEXT,
    precio_final DECIMAL(10,2),
    metodo_reserva VARCHAR(20) DEFAULT 'web', -- 'web', 'telefono', 'presencial'
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Propósito**: Tabla central de todas las reservas
**Relaciones**: N:1 con negocios, servicios y clientes, 1:N con asignaciones de recursos

### **CITA_RECURSOS**
```sql
CREATE TABLE cita_recursos (
    id SERIAL PRIMARY KEY,
    cita_id INTEGER NOT NULL REFERENCES citas(id),
    recurso_id INTEGER NOT NULL REFERENCES recursos(id),
    fecha_hora_inicio TIMESTAMP NOT NULL,
    fecha_hora_fin TIMESTAMP NOT NULL
);
```
**Propósito**: Asigna recursos específicos a cada cita
**Ejemplo**: La cita 123 usa el recurso "Dr. Pérez" de 10:00 a 10:30

## 4. TABLAS DE DISPONIBILIDAD Y BLOQUEOS

### **BLOQUEOS_RECURSOS**
```sql
CREATE TABLE bloqueos_recursos (
    id SERIAL PRIMARY KEY,
    recurso_id INTEGER NOT NULL REFERENCES recursos(id),
    fecha_hora_inicio TIMESTAMP NOT NULL,
    fecha_hora_fin TIMESTAMP NOT NULL,
    motivo VARCHAR(200), -- 'Vacaciones', 'Mantenimiento', 'Curso', etc.
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Propósito**: Bloquea recursos en fechas específicas
**Ejemplo**: "Dr. García" no disponible del 15/03 al 22/03 por vacaciones

### **CONFIGURACION_AGENDA**
```sql
CREATE TABLE configuracion_agenda (
    id SERIAL PRIMARY KEY,
    negocio_id INTEGER NOT NULL REFERENCES negocios(id),
    intervalo_citas INTEGER DEFAULT 15, -- Cada cuántos minutos pueden empezar las citas
    tiempo_buffer INTEGER DEFAULT 5, -- Tiempo entre citas para limpieza/preparación
    anticipacion_maxima_dias INTEGER DEFAULT 30, -- Cuántos días adelante se puede reservar
    cancelacion_limite_horas INTEGER DEFAULT 24, -- Horas mínimas para cancelar
    overbooking_permitido BOOLEAN DEFAULT FALSE,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Propósito**: Configuraciones específicas de cada negocio para el manejo de la agenda

## 5. ÍNDICES RECOMENDADOS

```sql
-- Índices para optimizar consultas de disponibilidad
CREATE INDEX idx_citas_negocio_fecha ON citas(negocio_id, fecha_hora_inicio);
CREATE INDEX idx_citas_servicio_fecha ON citas(servicio_id, fecha_hora_inicio);
CREATE INDEX idx_cita_recursos_recurso_fecha ON cita_recursos(recurso_id, fecha_hora_inicio);
CREATE INDEX idx_bloqueos_recurso_fecha ON bloqueos_recursos(recurso_id, fecha_hora_inicio);

-- Índices para búsquedas frecuentes
CREATE INDEX idx_servicios_negocio ON servicios(negocio_id) WHERE activo = TRUE;
CREATE INDEX idx_recursos_negocio ON recursos(negocio_id) WHERE activo = TRUE;
CREATE INDEX idx_clientes_telefono ON clientes(telefono);
CREATE INDEX idx_clientes_email ON clientes(email);
```

## 6. RELACIONES CLAVE

### **1:N (Uno a Muchos)**
- **negocios** → **servicios**: Un negocio tiene múltiples servicios
- **negocios** → **recursos**: Un negocio tiene múltiples recursos  
- **negocios** → **citas**: Un negocio recibe múltiples citas
- **servicios** → **citas**: Un servicio puede tener múltiples citas
- **clientes** → **citas**: Un cliente puede tener múltiples citas
- **recursos** → **bloqueos_recursos**: Un recurso puede tener múltiples bloqueos

### **N:M (Muchos a Muchos)**
- **servicios** ↔ **recursos** (a través de **servicio_recursos**)
- **citas** ↔ **recursos** (a través de **cita_recursos**)

### **Tabla de Configuración**
- **configuracion_agenda**: 1:1 con negocios (configuración específica)

## 7. EJEMPLO DE DATOS

### Peluquería
```sql
-- Negocio
INSERT INTO negocios (nombre, tipo_negocio) VALUES ('Bella Hair', 'peluqueria');

-- Servicios
INSERT INTO servicios (negocio_id, nombre, duracion_minutos, precio) VALUES 
(1, 'Corte básico', 30, 25.00),
(1, 'Tinte + Corte', 90, 65.00);

-- Recursos
INSERT INTO recursos (negocio_id, nombre, tipo) VALUES 
(1, 'María Estilista', 'persona'),
(1, 'Silla Principal', 'espacio');

-- Relación servicio-recurso
INSERT INTO servicio_recursos (servicio_id, recurso_id) VALUES 
(1, 1), (1, 2), -- Corte básico necesita María + Silla
(2, 1), (2, 2); -- Tinte también necesita María + Silla
```

### Clínica
```sql
-- Negocio
INSERT INTO negocios (nombre, tipo_negocio) VALUES ('Clínica Salud', 'clinica');

-- Servicios
INSERT INTO servicios (negocio_id, nombre, duracion_minutos, precio) VALUES 
(2, 'Consulta General', 20, 40.00),
(2, 'Fisioterapia', 60, 35.00);

-- Recursos
INSERT INTO recursos (negocio_id, nombre, tipo) VALUES 
(2, 'Dr. Rodríguez', 'persona'),
(2, 'Fisioterapeuta Ana', 'persona'),
(2, 'Consultorio 1', 'espacio'),
(2, 'Sala Fisioterapia', 'espacio');
```

Esta estructura te permite manejar cualquier tipo de negocio de forma flexible, desde una pequeña peluquería hasta una clínica con múltiples especialistas.