ALTER TABLE unifran_user
ADD FOREIGN KEY (user_id) REFERENCES system_user(id);

ALTER TABLE unifran_classroom
ADD FOREIGN KEY (teacher_id) REFERENCES unifran_user(user_id);

ALTER TABLE system_face
ADD FOREIGN KEY (user_id) REFERENCES system_user(id);

ALTER TABLE system_capture
ADD FOREIGN KEY (user_id) REFERENCES system_user(id),
ADD FOREIGN KEY (esp_id) REFERENCES system_esp(id);

ALTER TABLE system_esp
ADD FOREIGN KEY (register_user_id) REFERENCES system_user(id);
