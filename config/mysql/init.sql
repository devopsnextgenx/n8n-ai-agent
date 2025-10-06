-- Grant all privileges to admn user on all databases
GRANT ALL PRIVILEGES ON *.* TO 'admn'@'%' WITH GRANT OPTION;

-- Allow admn to connect from any host
CREATE USER IF NOT EXISTS 'admn'@'localhost' IDENTIFIED BY 'p@ssw0rd';
GRANT ALL PRIVILEGES ON *.* TO 'admn'@'localhost' WITH GRANT OPTION;

-- Ensure the user can grant privileges to others
GRANT GRANT OPTION ON *.* TO 'admn'@'%';
GRANT GRANT OPTION ON *.* TO 'admn'@'localhost';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;