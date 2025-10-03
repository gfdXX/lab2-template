-- Create databases
CREATE DATABASE cars;
CREATE DATABASE rentals;
CREATE DATABASE payments;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cars TO program;
GRANT ALL PRIVILEGES ON DATABASE rentals TO program;
GRANT ALL PRIVILEGES ON DATABASE payments TO program;
