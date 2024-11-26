CREATE DATABASE hospital;
GRANT ALL PRIVILEGES ON hospital.* TO 'admin'@'localhost';
USE hospital;

CREATE TABLE DOCTOR (
    matricula varchar(10) not null,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    telefono VARCHAR(20),
    PRIMARY KEY (matricula)
);

CREATE TABLE PACIENTE (
    nSocial VARCHAR(10) NOT NULL,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    telefono VARCHAR(20),
    PRIMARY KEY (nSocial)
);

CREATE TABLE TRABAJADOR_SOCIAL (
    rfc VARCHAR(10) NOT NULL,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    telefono VARCHAR(20),
    PRIMARY KEY (rfc)
);

CREATE TABLE CAMA_ATENCION (
    id INT AUTO_INCREMENT PRIMARY KEY,
    modelo VARCHAR(100),
    marca VARCHAR(100),
    sala INT
);

CREATE TABLE VISITA_EMERGENCIA (
    folio INT AUTO_INCREMENT PRIMARY KEY,
    paciente_id VARCHAR(10) NOT NULL,
    doctor_id VARCHAR(10) NOT NULL,
    cama_id INT,
    fecha DATE,
    status BIT default 0,
    FOREIGN KEY (paciente_id) REFERENCES PACIENTE(nSocial),
    FOREIGN KEY (doctor_id) REFERENCES DOCTOR(matricula),
    FOREIGN KEY (cama_id) REFERENCES CAMA_ATENCION(id)
);



