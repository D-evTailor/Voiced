-- Ejemplo: ¿Está disponible el servicio "Corte básico" el 15/03/2024 a las 10:00?

-- 1. Obtener recursos necesarios para el servicio
SELECT r.id, r.nombre 
FROM recursos r
JOIN servicio_recursos sr ON r.id = sr.recurso_id
WHERE sr.servicio_id = 1; -- ID del servicio "Corte básico"

-- 2. Verificar que NO estén ocupados en ese horario
SELECT COUNT() = 0 as disponible
FROM cita_recursos cr
WHERE cr.recurso_id IN (recursos_del_paso_1)
AND cr.fecha_hora_inicio < '2024-03-15 10:30:00'
AND cr.fecha_hora_fin > '2024-03-15 10:00:00';

-- 3. Verificar que NO estén bloqueados
SELECT COUNT() = 0 as no_bloqueado
FROM bloqueos_recursos br
WHERE br.recurso_id IN (recursos_del_paso_1)
AND br.fecha_hora_inicio < '2024-03-15 10:30:00'
AND br.fecha_hora_fin > '2024-03-15 10:00:00'
AND br.activo = TRUE;