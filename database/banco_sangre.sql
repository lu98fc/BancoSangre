CREATE DATABASE bancodesangre;
USE bancodesangre;

CREATE TABLE TipodeSangre (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    TipodeSangre ENUM('A+', 'A-', 'B+', 'B-', 'O+', 'O-','AB+', 'AB-') NOT NULL
);

CREATE TABLE CompatibilidadSangre (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    Donante ENUM('A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-') NOT NULL,
    Receptor VARCHAR (50) NOT NULL
);

CREATE TABLE Donante (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_n DATE NOT NULL,
    sexo ENUM('M', 'F', 'otro') NOT NULL,
    DNI VARCHAR(10),
    telefono VARCHAR(15),
    Correo VARCHAR(100),
    direccion VARCHAR(255) NOT NULL,
    UltimaD DATE,
    id_TipodeSangre INT UNSIGNED NOT NULL,
    FOREIGN KEY (id_TipodeSangre) REFERENCES TipodeSangre (id)
);

CREATE TABLE Reserva (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    VolumenDisp DECIMAL(7, 2),
    FechaExtraccion DATE NOT NULL,
    Vencimiento DATE NOT NULL,
    TipodeSangre ENUM('A+', 'A-', 'B+', 'B-','O+','O-', 'AB+', 'AB-') NOT NULL,
    Estado ENUM('Vencida', 'No vencida') DEFAULT 'No vencida',
    id_Donante INT UNSIGNED,
    id_Compatibilidad INT UNSIGNED,
    FOREIGN KEY (id_Donante) REFERENCES Donante(id),
    FOREIGN KEY (id_Compatibilidad) REFERENCES CompatibilidadSangre(id)
);

CREATE TABLE Hospital (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    Nombre VARCHAR(255) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    Correo VARCHAR(100)
);

CREATE TABLE Solicitud (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    VolumenSolic DECIMAL(5, 2) NOT NULL,
    Estado ENUM('Aceptada', 'Rechazada', 'Pendiente') DEFAULT 'Pendiente',
    id_Hospital INT UNSIGNED NOT NULL,
    id_TipodeSangre INT UNSIGNED NOT NULL,
    id_Reserva INT UNSIGNED,
    FOREIGN KEY (id_Hospital) REFERENCES Hospital (id),
    FOREIGN KEY (id_TipodeSangre) REFERENCES TipodeSangre (id),
    FOREIGN KEY (id_Reserva) REFERENCES Reserva (id)
);


CREATE TABLE Transfusion (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    FechaTransf DATE NOT NULL,
    VolumenTransf DECIMAL(5, 2) NOT NULL,
    id_Reserva INT UNSIGNED,
    FOREIGN KEY (id_Reserva) REFERENCES Reserva (id)
);

INSERT INTO TipodeSangre (TipodeSangre) VALUES
('A+'), ('A-'), ('B+'), ('B-'), ('O+'), ('O-'), ('AB+'), ('AB-');
INSERT INTO CompatibilidadSangre (Donante, Receptor) VALUES
('A+', 'A+, AB+'),
('A-', 'A+, A-, AB+, AB-'), 
('B+', 'B+, AB+'), 
('B-', 'B+, B-, AB+, AB-'), 
('O+', 'A+, B+, O+, AB+'), 
('O-', 'A+, A-, B+, B-, O+, O-, AB+, AB-'), 
('AB+', 'AB+'),
('AB-', 'AB+, AB-');

INSERT INTO Donante (nombre, apellido, fecha_n, sexo, DNI, telefono, Correo, direccion, UltimaD, id_TipodeSangre) VALUES
('Juan', 'Perez', '1980-01-01', 'M', '12345678', '555-1234', 'juan.perez@example.com', '123 Main St', '2024-01-01', 1),
('Maria', 'Gomez', '1985-05-15', 'F', '23456789', '555-2345', 'maria.gomez@example.com', '456 Elm St', '2024-06-15', 2);

INSERT INTO Reserva (VolumenDisp, FechaExtraccion, Vencimiento, TipodeSangre, Estado, id_Donante, id_Compatibilidad) VALUES
(450.00, '2024-07-01', '2025-07-01', 'A+', 'No vencida', 1, 1),
(500.00, '2024-08-01', '2025-08-01', 'A-', 'No vencida', 2, 2);
INSERT INTO Hospital (Nombre, direccion, telefono, Correo) VALUES
('Hospital Central', '789 Oak St', '555-3456', 'central@example.com'),
('Clinica Norte', '321 Pine St', '555-4567', 'norte@example.com');
INSERT INTO Solicitud (VolumenSolic, Estado, id_Hospital, id_TipodeSangre, id_Reserva) VALUES
(300.00,'Pendiente', 1, 1, 1),
(200.00,'Pendiente', 2, 2, 2);



INSERT INTO Transfusion (FechaTransf, VolumenTransf, id_Reserva) VALUES
( '2024-07-02', 450.00, 1),
( '2024-08-02', 500.00, 2);


DELIMITER //

CREATE PROCEDURE ConsultarCompatibilidad(IN tipoDonante ENUM('A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'))
BEGIN
    SELECT Receptor
    FROM CompatibilidadSangre
    WHERE Donante = tipoDonante;
END //

DELIMITER ;
CALL ConsultarCompatibilidad('O+');
CALL ConsultarCompatibilidad('O-');
CALL ConsultarCompatibilidad('A+');
CALL ConsultarCompatibilidad('A-');
CALL ConsultarCompatibilidad('B+');
CALL ConsultarCompatibilidad('B-');
CALL ConsultarCompatibilidad('AB+');
CALL ConsultarCompatibilidad('AB-');


SELECT r.ID, r.VolumenDisp, r.Vencimiento, r.TipodeSangre
            FROM reserva r;
            
select * from donante;

select h.id, h.Nombre, h.direccion, h.telefono, s.VolumenSolic, ts.TipodeSangre 
from hospital h
join solicitud s on h.id = s.id_Hospital
join tipodesangre ts on ts.id = s.id_TipodeSangre;

select d.id, d.nombre, d.apellido, d.fecha_n, d.sexo, d.DNI, d.telefono, d.Correo, d.direccion, d.UltimaD, ts.TipodeSangre 
from donante d 
join TipodeSangre ts on ts.id = d.id_TipodeSangre;


