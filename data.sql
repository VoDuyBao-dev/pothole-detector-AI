drop database if exists pothole_detector_ai;
create database pothole_detector_ai;
use pothole_detector_ai;


-- Thêm 10 user vào auth_user
INSERT INTO auth_user(username, password, email, first_name, last_name, is_staff, is_superuser, is_active, date_joined)
VALUES
    ('admin1@example.com', 'pbkdf2_sha256$1000000$T4PtqQKFMNbe28JknKMP4g$h3KYcK0H1+DCQcfywuXPjtbBXT09Eng7fU4zadB1WvQ=', 'admin1@example.com', '', '', 1, 0, 1, NOW()),
    ('user1@example.com', 'pbkdf2_sha256$1000000$T4PtqQKFMNbe28JknKMP4g$h3KYcK0H1+DCQcfywuXPjtbBXT09Eng7fU4zadB1WvQ=', 'user1@example.com', '', '', 0, 0, 1, NOW()),
    ('user2@example.com', 'pbkdf2_sha256$1000000$T4PtqQKFMNbe28JknKMP4g$h3KYcK0H1+DCQcfywuXPjtbBXT09Eng7fU4zadB1WvQ=', 'user2@example.com', '', '', 0, 0, 1, NOW()),
    ('user3@example.com', 'pbkdf2_sha256$1000000$T4PtqQKFMNbe28JknKMP4g$h3KYcK0H1+DCQcfywuXPjtbBXT09Eng7fU4zadB1WvQ=', 'user3@example.com', '', '', 0, 0, 1, NOW()),
    ('user4@example.com', 'pbkdf2_sha256$1000000$T4PtqQKFMNbe28JknKMP4g$h3KYcK0H1+DCQcfywuXPjtbBXT09Eng7fU4zadB1WvQ=', 'user4@example.com', '', '', 0, 0, 1, NOW()),
    ('user5@example.com', 'pbkdf2_sha256$1000000$T4PtqQKFMNbe28JknKMP4g$h3KYcK0H1+DCQcfywuXPjtbBXT09Eng7fU4zadB1WvQ=', 'user5@example.com', '', '', 0, 0, 1, NOW()),
    ('user6@example.com', 'pbkdf2_sha256$1000000$T4PtqQKFMNbe28JknKMP4g$h3KYcK0H1+DCQcfywuXPjtbBXT09Eng7fU4zadB1WvQ=', 'user6@example.com', '', '', 0, 0, 1, NOW()),
    ('user7@example.com', 'pbkdf2_sha256$1000000$T4PtqQKFMNbe28JknKMP4g$h3KYcK0H1+DCQcfywuXPjtbBXT09Eng7fU4zadB1WvQ=', 'user7@example.com', '', '', 0, 0, 1, NOW()),
    ('user8@example.com', 'pbkdf2_sha256$1000000$T4PtqQKFMNbe28JknKMP4g$h3KYcK0H1+DCQcfywuXPjtbBXT09Eng7fU4zadB1WvQ=', 'user8@example.com', '', '', 0, 0, 1, NOW()),
    ('user9@example.com', 'pbkdf2_sha256$1000000$T4PtqQKFMNbe28JknKMP4g$h3KYcK0H1+DCQcfywuXPjtbBXT09Eng7fU4zadB1WvQ=', 'user9@example.com', '', '', 0, 0, 1, NOW());
-- Password for all users: 123456

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


INSERT INTO my_app_pothole (latitude, longitude, first_detected_by_id, status, confidence_avg, detections_count)
VALUES 
(2, 'active', 0.92, 3),   -- Hà Nội
(3, 'active', 0.85, 2),   -- TP.HCM
(1, 'fixed', 0.95, 5),    -- Đà Nẵng
(2, 'active', 0.78, 1),   -- Hà Nội - khu khác
(4, 'active', 0.88, 4),   -- TP.HCM - quận 1
(3, 'fixed', 0.91, 6),    -- Đà Nẵng - ven biển
(2, 'active', 0.80, 2),   -- Hà Đông
(5, 'active', 0.87, 3),   -- Gò Vấp
(1, 'active', 0.82, 2),   -- Bắc Ninh
(3, 'active', 0.90, 4);   -- Cần Thơ



INSERT INTO my_app_potholedetection (pothole_id, user_id, latitude, longitude, size, level, confidence, area, detected_at)
VALUES
-- Pothole 1 (ổ gà nhỏ, area ~4500-5200 → small)
(1, 2, 21.028511, 105.804817, '100x50', 'small', 0.91, 5000, NOW()),
(1, 3, 21.028511, 105.804817, '98x52', 'large', 0.88, 5096, NOW()),
(1, 4, 21.028511, 105.804817, '95x48', 'small', 0.92, 5096, NOW()),
(1, 6, 21.028511, 105.804817, '102x49', 'small', 0.85, 5096, NOW()),
(1, 7, 21.028511, 105.804817, '97x51', 'small', 0.83, 5096, NOW()),

-- Pothole 2 (ổ gà lớn, area ~15000-16000 → large)
(2, 5, 10.762622, 106.660172, '200x80', 'large', 0.89, 15096, NOW()),
(2, 8, 10.762622, 106.660172, '195x78', 'large', 0.91, 15096, NOW()),
(2, 9, 10.762622, 106.660172, '198x79', 'large', 0.84, 15096, NOW()),

-- Pothole 3 (ổ gà nhỏ → vừa, area ~3000-3600 → small)
(3, 1, 16.047079, 108.206230, '70x50', 'small', 0.95, 5096, NOW()),
(3, 2, 16.047079, 108.206230, '68x47', 'small', 0.93, 5096, NOW()),
(3, 4, 16.047079, 108.206230, '72x48', 'small', 0.90, 5096, NOW()),
(3, 10,16.047079, 108.206230, '71x49', 'small', 0.92, 5096, NOW()),
(3, 6, 16.047079, 108.206230, '69x46', 'small', 0.90, 5096, NOW()),
(3, 7, 16.047079, 108.206230, '70x52', 'small', 0.85, 5096, NOW()),

-- Pothole 4 (ổ gà trung bình, area ~6000-7000 → large)
(4, 8, 16.047079, 108.206230, '85x80', 'large', 0.83, 5096, NOW()),
(4, 2, 21.033781, 105.835546, '86x78', 'large', 0.80, 5096, NOW()),
(4, 3, 21.033781, 105.835546, '84x75', 'large', 0.82, 5096, NOW()),
(4, 5, 21.033781, 105.835546, '87x79', 'large', 0.84, 5096, NOW()),

-- Pothole 5 (ổ gà lớn, area ~11000-13000 → large)
(5, 4, 10.776530, 106.700981, '120x95', 'large', 0.92, 15096, NOW()),
(5, 1, 10.776530, 106.700981, '125x96', 'large', 0.87, 15096, NOW()),
(5, 2, 10.776530, 106.700981, '118x92', 'large', 0.89, 15096, NOW()),
(5, 9, 10.776530, 106.700981, '122x94', 'large', 0.88, 15096, NOW()),
(5, 10,10.776530, 106.700981, '121x97', 'large', 0.86, 15096, NOW()),

-- Pothole 6 (ổ gà lớn vừa, area ~7500-8500 → large)
(6, 3, 16.060000, 108.220000, '92x90', 'large', 0.91, 5096, NOW()),
(6, 5, 16.060000, 108.220000, '88x85', 'large', 0.88, 5096, NOW()),
(6, 2, 16.060000, 108.220000, '90x86', 'large', 0.90, 5096, NOW()),
(6, 6, 16.060000, 108.220000, '91x87', 'large', 0.89, 5096, NOW()),
(6, 7, 16.060000, 108.220000, '89x84', 'large', 0.87, 5096, NOW()),
(6, 8, 16.060000, 108.220000, '93x89', 'large', 0.90, 5096, NOW()),
(6, 9, 16.060000, 108.220000, '90x88', 'large', 0.88, 5096, NOW()),
(6, 10,16.060000, 108.220000, '92x85', 'large', 0.92, 5096, NOW()),

-- Pothole 7 (ổ gà nhỏ, area ~4000-4500 → small)
(7, 1, 20.999999, 105.850000, '65x65', 'small', 0.85, 5096, NOW()),
(7, 4, 20.999999, 105.850000, '66x64', 'small', 0.86, 5096, NOW()),
(7, 5, 20.999999, 105.850000, '67x63', 'small', 0.88, 5096, NOW()),

-- Pothole 8 (ổ gà lớn, area ~9000-10000 → large)
(8, 3, 10.830000, 106.680000, '100x95', 'large', 0.90, 5096, NOW()),
(8, 2, 10.830000, 106.680000, '98x96', 'large', 0.87, 5096, NOW()),
(8, 1, 10.830000, 106.680000, '102x97', 'large', 0.85, 5096, NOW()),

-- Pothole 9 (ổ gà vừa, area ~5000-6000 → large)
(9, 4, 21.150000, 105.500000, '80x75', 'large', 0.89, 5096, NOW()),
(9, 5, 21.150000, 105.500000, '78x72', 'large', 0.86, 5096, NOW()),
(9, 2, 21.150000, 105.500000, '79x74', 'large', 0.92, 5096, NOW()),
(9, 7, 21.150000, 105.500000, '77x76', 'large', 0.91, 5096, NOW()),
(9, 8, 21.150000, 105.500000, '80x73', 'large', 0.87, 5096, NOW()),
(9, 9, 21.150000, 105.500000, '81x74', 'large', 0.88, 5096, NOW()),

-- Pothole 10 (ổ gà lớn, area ~7000-8000 → large)
(10, 10,10.290000, 105.750000, '90x80', 'large', 0.85, 5096, NOW()),
(10, 1, 10.290000, 105.750000, '92x85', 'large', 0.93, 5096, NOW()),
(10, 3, 10.290000, 105.750000, '88x79', 'large', 0.91, 5096, NOW()),
(10, 4, 10.290000, 105.750000, '91x83', 'large', 0.90, 7553, NOW());





