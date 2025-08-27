drop database pothole_detector_ai;
CREATE DATABASE pothole_detector_ai;
use pothole_detector_ai;


-- Thêm 10 user vào auth_user
INSERT INTO auth_user (username, password, email, first_name, last_name, is_staff, is_superuser, is_active, date_joined)
VALUES 
('admin1', 'pbkdf2_sha256$1000000$7MMFavJCUg9ol2hYHma7kc$+uaeNAz6tikChUfygyJCQg9ZcUdFrDO00N7mLAgEgFc=', 'admin1@example.com', '', '', 1, 0, 1, NOW()),
('user1',  'pbkdf2_sha256$1000000$7MMFavJCUg9ol2hYHma7kc$+uaeNAz6tikChUfygyJCQg9ZcUdFrDO00N7mLAgEgFc=', 'user1@example.com', '', '', 0, 0, 1, NOW()),
('user2',  'pbkdf2_sha256$1000000$7MMFavJCUg9ol2hYHma7kc$+uaeNAz6tikChUfygyJCQg9ZcUdFrDO00N7mLAgEgFc=', 'user2@example.com', '', '', 0, 0, 1, NOW()),
('user3',  'pbkdf2_sha256$1000000$7MMFavJCUg9ol2hYHma7kc$+uaeNAz6tikChUfygyJCQg9ZcUdFrDO00N7mLAgEgFc=', 'user3@example.com', '', '', 0, 0, 1, NOW()),
('user4',  'pbkdf2_sha256$1000000$7MMFavJCUg9ol2hYHma7kc$+uaeNAz6tikChUfygyJCQg9ZcUdFrDO00N7mLAgEgFc=', 'user4@example.com', '', '', 0, 0, 1, NOW()),
('user5',  'pbkdf2_sha256$1000000$7MMFavJCUg9ol2hYHma7kc$+uaeNAz6tikChUfygyJCQg9ZcUdFrDO00N7mLAgEgFc=', 'user5@example.com', '', '', 0, 0, 1, NOW()),
('user6',  'pbkdf2_sha256$1000000$7MMFavJCUg9ol2hYHma7kc$+uaeNAz6tikChUfygyJCQg9ZcUdFrDO00N7mLAgEgFc=', 'user6@example.com', '', '', 0, 0, 1, NOW()),
('user7',  'pbkdf2_sha256$1000000$7MMFavJCUg9ol2hYHma7kc$+uaeNAz6tikChUfygyJCQg9ZcUdFrDO00N7mLAgEgFc=', 'user7@example.com', '', '', 0, 0, 1, NOW()),
('user8',  'pbkdf2_sha256$1000000$7MMFavJCUg9ol2hYHma7kc$+uaeNAz6tikChUfygyJCQg9ZcUdFrDO00N7mLAgEgFc=', 'user8@example.com', '', '', 0, 0, 1, NOW()),
('user9',  'pbkdf2_sha256$1000000$7MMFavJCUg9ol2hYHma7kc$+uaeNAz6tikChUfygyJCQg9ZcUdFrDO00N7mLAgEgFc=', 'user9@example.com', '', '', 0, 0, 1, NOW());

INSERT INTO my_app_userprofile (user_id, role, created_at, updated_at)
VALUES
(1, 'admin', NOW(), NOW()),
(2, 'user', NOW(), NOW()),
(3, 'user', NOW(), NOW()),
(4, 'user', NOW(), NOW()),
(5, 'user', NOW(), NOW()),
(6, 'user', NOW(), NOW()),
(7, 'user', NOW(), NOW()),
(8, 'user', NOW(), NOW()),
(9, 'user', NOW(), NOW()),
(10, 'user', NOW(), NOW());


INSERT INTO my_app_pothole 
(latitude, longitude, first_detected_by_id, first_detected_at, status, confidence_avg, detections_count)
VALUES
(21.027763, 105.834160, 3, NOW(), 'active', 0.85, 2),
(21.028500, 105.835000, 4, NOW(), 'active', 0.92, 3),
(21.025000, 105.830000, 5, NOW(), 'fixed', 0.70, 1),
(21.029200, 105.836500, 6, NOW(), 'active', 0.95, 4),
(21.030000, 105.837000, 7, NOW(), 'fixed', 0.60, 1);


INSERT INTO my_app_potholedetection
(pothole_id, user_id, latitude, longitude, size, confidence, area, detected_at)
VALUES
(1, 3, 21.027800, 105.834200, 'small', 0.90, 1.5, NOW()),
(1, 4, 21.027750, 105.834150, 'small', 0.80, 1.2, NOW()),
(2, 4, 21.028600, 105.835100, 'large', 0.95, 3.0, NOW()),
(2, 5, 21.028550, 105.835050, 'small', 0.88, 2.0, NOW()),
(2, 6, 21.028520, 105.835070, 'large', 0.92, 2.8, NOW()),
(3, 5, 21.025050, 105.830020, 'small', 0.70, 1.0, NOW()),
(4, 6, 21.029250, 105.836550, 'large', 0.96, 3.2, NOW()),
(4, 7, 21.029300, 105.836600, 'large', 0.94, 3.5, NOW()),
(4, 8, 21.029280, 105.836580, 'small', 0.90, 2.5, NOW()),
(5, 7, 21.030050, 105.837050, 'small', 0.60, 1.0, NOW());



