CREATE TEMPORARY TABLE arduino_facial_recognition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    face_img BLOB NOT NULL
);

CREATE TABLE facial_recognition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    face_img BLOB NOT NULL
    #FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE users (
    id INT PRIMARY KEY
);

CREATE TABLE arduino (
    id INT PRIMARY KEY,
    `unlock` boolean
);
