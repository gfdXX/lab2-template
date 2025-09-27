CREATE DATABASE cars;
GRANT ALL PRIVILEGES ON DATABASE cars TO program;

CREATE DATABASE rentals;
GRANT ALL PRIVILEGES ON DATABASE rentals TO program;

CREATE DATABASE payments;
GRANT ALL PRIVILEGES ON DATABASE payments TO program;

-- Create tables for each database
\i /docker-entrypoint-initdb.d/scripts/cars-schema.sql
\i /docker-entrypoint-initdb.d/scripts/rentals-schema.sql
\i /docker-entrypoint-initdb.d/scripts/payments-schema.sql