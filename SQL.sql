CREATE TABLE user_registration.users(
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL
);

CREATE TABLE user_registration.contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

ALTER TABLE user_registration.contacts
ADD COLUMN `group` VARCHAR(20) NOT NULL DEFAULT 'personal';




