-- Create transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    amount DECIMAL(10, 2),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert dummy data
INSERT INTO transactions (user_id, amount)
SELECT 
    floor(random() * 1000 + 1)::int,
    (random() * 1000)::decimal(10,2)
FROM 
    generate_series(1, 1000000);


-- On source PostgreSQL
CREATE PUBLICATION source_pub FOR TABLE transactions;

-- On Citus
CREATE SUBSCRIPTION citus_sub 
CONNECTION 'host=postgres_source port=5432 dbname=testdb user=testuser password=testpass' 
PUBLICATION source_pub;

-- Distribute the table on Citus
CREATE TABLE transactions (
    id SERIAL,
    user_id INTEGER,
    amount DECIMAL(10, 2),
    transaction_date TIMESTAMP
);

SELECT create_distributed_table('transactions', 'id');