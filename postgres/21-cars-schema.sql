-- Cars database schema and data
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
