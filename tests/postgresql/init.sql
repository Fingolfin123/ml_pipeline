-- init.sql
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    score NUMERIC
);

-- INSERT INTO employees (id, name, salary) VALUES
-- ('Alice', 'Engineer', 95000),
-- ('Bob', 'Manager', 120000),
-- ('Charlie', 'Analyst', 80000);
