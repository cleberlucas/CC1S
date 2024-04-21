INSERT INTO `system_unifran`.`system_esp` (`id`, `url`, `ssid`, `mac`, `door`, `local`, `last_start`) VALUES ('3', '', '', '', 'exit', '69', '2024-01-01 00:00:00');

INSERT INTO `system_unifran`.`system_user` (`id`) VALUES ('1');
INSERT INTO `system_unifran`.`system_user` (`id`) VALUES ('2');
INSERT INTO `system_unifran`.`system_user` (`id`) VALUES ('3');

INSERT INTO `system_unifran`.`unifran_user` (`rgm`, `user_id`, `name`, `type`, `local`) VALUES ('25126284', '1', 'Rock', 'student', '69');
INSERT INTO `system_unifran`.`unifran_user` (`rgm`, `user_id`, `name`, `type`, `local`) VALUES ('25126285', '2', 'Elon', 'teacher', '69');
INSERT INTO `system_unifran`.`unifran_user` (`rgm`, `user_id`, `name`, `type`, `local`) VALUES ('25126286', '3', 'Will', 'student', '69');

INSERT INTO `system_unifran`.`unifran_classroom` (`teacher_id`, `date`, `local`, `start_class`, `end_class`, `start_interval`, `end_interval`, `learning_time`) VALUES ('2', '2024-04-21', '69', '19:15', '21:30', '20:30', '20:45', '85');

INSERT INTO `system_unifran`.`system_capture` (`esp_id`, `user_id`, `door`, `local`, `capture_time`) VALUES ('2', '1', 'entrance', '69', '2024-04-21 19:15:46');
INSERT INTO `system_unifran`.`system_capture` (`esp_id`, `user_id`, `door`, `local`, `capture_time`) VALUES ('2', '1', 'exit', '69', '2024-04-21 20:20:22');
INSERT INTO `system_unifran`.`system_capture` (`esp_id`, `user_id`, `door`, `local`, `capture_time`) VALUES ('3', '1', 'entrance', '69', '2024-04-21 20:30:38');
INSERT INTO `system_unifran`.`system_capture` (`esp_id`, `user_id`, `door`, `local`, `capture_time`) VALUES ('3', '1', 'exit', '69', '2024-04-21 21:15:22');
INSERT INTO `system_unifran`.`system_capture` (`esp_id`, `user_id`, `door`, `local`, `capture_time`) VALUES ('2', '2', 'entrance', '69', '2024-04-21 19:00:01');
INSERT INTO `system_unifran`.`system_capture` (`esp_id`, `user_id`, `door`, `local`, `capture_time`) VALUES ('3', '2', 'exit', '69', '2024-04-21 21:40:37');
INSERT INTO `system_unifran`.`system_capture` (`esp_id`, `user_id`, `door`, `local`, `capture_time`) VALUES ('2', '3', 'entrance', '69', '2024-04-21 19:50:25');
INSERT INTO `system_unifran`.`system_capture` (`esp_id`, `user_id`, `door`, `local`, `capture_time`) VALUES ('3', '3', 'exit', '69', '2024-04-21 21:50:17');
