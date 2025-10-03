-- Rentals database schema
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
