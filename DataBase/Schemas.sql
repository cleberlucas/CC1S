CREATE TABLE facial_recognition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    face_img BLOB NOT NULL
    #FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE `user` (
    id INT PRIMARY KEY,
	`name` VARCHAR(255) NOT NULL,
    `local` INT NOT NULL
);

CREATE TABLE esp_info (
    id INT PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    ssid VARCHAR(255) NOT NULL,
    `local` INT NOT NULL,
    user_id_register INT NOT NULL DEFAULT 0,
    last_start DATETIME
    #FOREIGN KEY (user_id_register) REFERENCES user(id)
);

CREATE TABLE unifran (
    rgm INT PRIMARY KEY,
    user_id INT NOT NULL
    #FOREIGN KEY (user_id) REFERENCES user(id)
);

DELIMITER //

CREATE TRIGGER update_last_start_before_insert
BEFORE INSERT ON esp_info
FOR EACH ROW
BEGIN
    SET NEW.last_start = CURRENT_TIMESTAMP;
END;
//

CREATE TRIGGER update_last_start_before_update
BEFORE UPDATE ON esp_info
FOR EACH ROW
BEGIN
    SET NEW.last_start = CURRENT_TIMESTAMP;
END;
//

DELIMITER ;
