CREATE TABLE unifran_user (
    rgm INT PRIMARY KEY,
    user_id INT NOT NULL,
    `name` VARCHAR(250),
    `local` INT NOT NULL,
    `type` ENUM('student', 'teacher')
);

CREATE TABLE unifran_classroom (
    teacher_id INT NOT NULL,
    `date` DATE NOT NULL,
    `local` INT NOT NULL,
    `start_class` TIME NOT NULL,
    `end_class` TIME NOT NULL,
    start_interval TIME NOT NULL,
    end_interval TIME NOT NULL,
    learning_time INT NOT NULL,
    PRIMARY KEY (teacher_id, `date`, `local`)
);