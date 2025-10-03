-- Payments database schema
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
