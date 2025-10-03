-- Create databases
CREATE DATABASE cars;
GRANT ALL PRIVILEGES ON DATABASE cars TO program;

CREATE DATABASE rentals;
GRANT ALL PRIVILEGES ON DATABASE rentals TO program;

CREATE DATABASE payments;
GRANT ALL PRIVILEGES ON DATABASE payments TO program;

-- Connect to cars database and create schema
\c cars;
CREATE TABLE cars
(
    id                  SERIAL PRIMARY KEY,
    car_uid             uuid UNIQUE NOT NULL,
    brand               VARCHAR(80) NOT NULL,
    model               VARCHAR(80) NOT NULL,
    registration_number VARCHAR(20) NOT NULL,
    power               INT,
    price               INT         NOT NULL,
    type                VARCHAR(20)
        CHECK (type IN ('SEDAN', 'SUV', 'MINIVAN', 'ROADSTER')),
    availability        BOOLEAN     NOT NULL DEFAULT TRUE
);

-- Grant permissions on sequence and table
GRANT USAGE, SELECT ON SEQUENCE cars_id_seq TO program;
GRANT ALL PRIVILEGES ON TABLE cars TO program;

-- Insert test data
INSERT INTO cars (car_uid, brand, model, registration_number, power, price, type, availability) VALUES
('109b42f3-198d-4c89-9276-a7520a7120ab', 'Mercedes Benz', 'GLA 250', 'ЛО777Х799', 249, 3500, 'SEDAN', true),
('209b42f3-198d-4c89-9276-a7520a7120ab', 'BMW', 'X5', 'А123БВ777', 300, 5000, 'SUV', true),
('309b42f3-198d-4c89-9276-a7520a7120ab', 'Audi', 'A4', 'В456ГД777', 200, 4000, 'SEDAN', true);

-- Connect to rentals database and create schema
\c rentals;
CREATE TABLE rental
(
    id          SERIAL PRIMARY KEY,
    rental_uid  uuid UNIQUE NOT NULL,
    username    VARCHAR(80) NOT NULL,
    payment_uid uuid        NOT NULL,
    car_uid     uuid        NOT NULL,
    date_from   TIMESTAMP   NOT NULL,
    date_to     TIMESTAMP   NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'IN_PROGRESS'
);

-- Grant permissions
GRANT USAGE, SELECT ON SEQUENCE rental_id_seq TO program;
GRANT ALL PRIVILEGES ON TABLE rental TO program;

-- Connect to payments database and create schema
\c payments;
CREATE TABLE payment
(
    id          SERIAL PRIMARY KEY,
    payment_uid uuid UNIQUE NOT NULL,
    status      VARCHAR(20) NOT NULL,
    price       INT         NOT NULL
);

-- Grant permissions
GRANT USAGE, SELECT ON SEQUENCE payment_id_seq TO program;
GRANT ALL PRIVILEGES ON TABLE payment TO program;
