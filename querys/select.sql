SELECT IPSRemitente,
    COUNT(*) AS Remisiones
FROM
    Admisiones.PacientesRemision
GROUP BY
    IPSRemitente
ORDER BY
    Remisiones DESC;