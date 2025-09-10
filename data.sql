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

INSERT INTO my_app_userprofile (user_id, role, created_at, updated_at, is_deleted)
VALUES
(1, 'admin', NOW(), NOW(), 0),
(2, 'user', NOW(), NOW(), 0),
(3, 'user', NOW(), NOW(), 0),
(4, 'user', NOW(), NOW(), 0),
(5, 'user', NOW(), NOW(), 0),
(6, 'user', NOW(), NOW(), 0),
(7, 'user', NOW(), NOW(), 0),
(8, 'user', NOW(), NOW(), 0),
(9, 'user', NOW(), NOW(), 0),
(10, 'user', NOW(), NOW(), 0);




INSERT INTO my_app_pothole (first_detected_by_id, status, confidence_avg, detections_count)
VALUES
(4, 'active', 0.89, 3),    -- Hà Nội - Cầu Giấy
(6, 'active', 0.83, 2),    -- TP.HCM - Thủ Đức
(2, 'fixed', 0.94, 5),     -- Đà Nẵng - Sơn Trà
(7, 'active', 0.77, 1),    -- Hải Phòng
(8, 'active', 0.86, 3),    -- Hà Nội - Hoàng Mai
(9, 'fixed', 0.92, 4),     -- TP.HCM - Bình Thạnh
(3, 'active', 0.84, 2),    -- Cần Thơ - Ninh Kiều
(5, 'active', 0.88, 3),    -- Bắc Giang
(10, 'fixed', 0.96, 6),    -- Đà Nẵng - Hòa Vang
(1, 'active', 0.81, 2),    -- Quảng Ninh

(2, 'active', 0.79, 1),    -- Hà Nội - Hà Đông
(4, 'fixed', 0.93, 5),     -- TP.HCM - quận 3
(6, 'active', 0.87, 3),    -- Cần Thơ
(7, 'active', 0.82, 2),    -- Hải Phòng - Kiến An
(8, 'fixed', 0.95, 4),     -- Đà Nẵng - Liên Chiểu
(9, 'active', 0.85, 3),    -- Bắc Ninh
(5, 'active', 0.90, 4),    -- Hà Nội - Long Biên
(10, 'active', 0.83, 2),   -- Đồng Nai - Biên Hòa
(1, 'fixed', 0.97, 6),     -- TP.HCM - quận 5
(3, 'active', 0.78, 1);    -- Huế

INSERT INTO my_app_pothole (first_detected_by_id, status, confidence_avg, detections_count)
VALUES
(2, 'active', 0.82, 2),    -- Hà Nội - Tây Hồ
(4, 'active', 0.88, 3),    -- TP.HCM - Gò Vấp
(6, 'fixed', 0.94, 5),     -- Đà Nẵng - Thanh Khê
(7, 'active', 0.80, 2),    -- Hải Phòng - Lê Chân
(8, 'active', 0.86, 3),    -- Hà Nội - Nam Từ Liêm
(9, 'fixed', 0.92, 4),     -- TP.HCM - quận 10
(10, 'active', 0.83, 2),   -- Cần Thơ - Bình Thủy
(3, 'active', 0.89, 3),    -- Bắc Ninh
(5, 'fixed', 0.95, 2),     -- Đà Nẵng - Cẩm Lệ
(1, 'active', 0.81, 2),    -- Quảng Nam

(2, 'active', 0.79, 1),    -- Hà Nội - Đông Anh
(4, 'fixed', 0.93, 2),     -- TP.HCM - quận 7
(6, 'active', 0.87, 3),    -- Huế - trung tâm
(7, 'active', 0.82, 2),    -- Hải Phòng - Đồ Sơn
(8, 'fixed', 0.96, 4),     -- Đà Nẵng - Ngũ Hành Sơn
(9, 'active', 0.85, 3),    -- Bắc Giang
(10, 'active', 0.90, 4),   -- Hà Nội - Mỹ Đình
(1, 'active', 0.84, 2),    -- Đồng Nai - Nhơn Trạch
(3, 'fixed', 0.97, 3),     -- TP.HCM - Bình Tân
(5, 'active', 0.78, 1);    -- Thái Nguyên

INSERT INTO my_app_pothole (first_detected_by_id, status, confidence_avg, detections_count)
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



INSERT INTO my_app_potholedetection  
(pothole_id, user_id, latitude, longitude, size, level, confidence, area, detected_at)
VALUES
-- Pothole 1: Hà Nội - Cầu Giấy (3 detections)
(1, 4, 21.0300, 105.8000, '40x30', 'small', 0.90, 1200, NOW()),
(1, 6, 21.0302, 105.8005, '60x40', 'medium', 0.88, 2400, NOW()),
(1, 8, 21.0304, 105.8007, '45x35', 'small', 0.89, 1575, NOW()),

-- Pothole 2: TP.HCM - Thủ Đức (2 detections)
(2, 6, 10.8700, 106.7800, '65x45', 'medium', 0.82, 2925, NOW()),
(2, 7, 10.8705, 106.7810, '80x70', 'large', 0.84, 5600, NOW()),

-- Pothole 3: Đà Nẵng - Sơn Trà (5 detections)
(3, 2, 16.0700, 108.2500, '55x40', 'medium', 0.93, 2200, NOW()),
(3, 5, 16.0702, 108.2505, '80x60', 'large', 0.95, 4800, NOW()),
(3, 8, 16.0703, 108.2510, '70x45', 'medium', 0.94, 3150, NOW()),
(3, 9, 16.0706, 108.2513, '90x65', 'large', 0.96, 5850, NOW()),
(3, 3, 16.0708, 108.2517, '75x55', 'medium', 0.92, 4125, NOW()),

-- Pothole 4: Hải Phòng (1 detection)
(4, 7, 20.8500, 106.6800, '50x35', 'small', 0.77, 1750, NOW()),

-- Pothole 5: Hà Nội - Hoàng Mai (3 detections)
(5, 8, 20.9800, 105.8600, '45x40', 'small', 0.85, 1800, NOW()),
(5, 2, 20.9804, 105.8605, '70x55', 'medium', 0.87, 3850, NOW()),
(5, 6, 20.9807, 105.8609, '85x70', 'large', 0.86, 5950, NOW()),

-- Pothole 6: TP.HCM - Bình Thạnh (4 detections)
(6, 9, 10.8100, 106.7000, '70x65', 'medium', 0.91, 4550, NOW()),
(6, 3, 10.8104, 106.7005, '95x65', 'large', 0.93, 6175, NOW()),
(6, 5, 10.8108, 106.7009, '60x55', 'medium', 0.92, 3300, NOW()),
(6, 7, 10.8110, 106.7012, '85x65', 'large', 0.94, 5525, NOW()),

-- Pothole 7: Cần Thơ - Ninh Kiều (2 detections)
(7, 3, 10.0500, 105.7800, '60x45', 'medium', 0.85, 2700, NOW()),
(7, 6, 10.0503, 105.7805, '70x60', 'medium', 0.83, 4200, NOW()),

-- Pothole 8: Bắc Giang (3 detections)
(8, 5, 21.2700, 106.2000, '50x35', 'small', 0.87, 1750, NOW()),
(8, 8, 21.2704, 106.2005, '80x55', 'large', 0.88, 4400, NOW()),
(8, 9, 21.2706, 106.2009, '95x65', 'large', 0.89, 6175, NOW()),

-- Pothole 9: Đà Nẵng - Hòa Vang (6 detections)
(9, 10, 16.0500, 108.0200, '85x60', 'large', 0.95, 5100, NOW()),
(9, 4, 16.0503, 108.0205, '95x65', 'large', 0.96, 6175, NOW()),
(9, 6, 16.0506, 108.0209, '100x70', 'large', 0.97, 7000, NOW()),
(9, 7, 16.0508, 108.0212, '75x55', 'medium', 0.94, 4125, NOW()),
(9, 2, 16.0510, 108.0215, '90x65', 'large', 0.95, 5850, NOW()),
(9, 8, 16.0513, 108.0218, '95x65', 'large', 0.96, 6175, NOW()),

-- Pothole 10: Quảng Ninh (2 detections)
(10, 1, 21.0200, 107.3000, '70x55', 'medium', 0.82, 3850, NOW()),
(10, 9, 21.0204, 107.3005, '75x55', 'medium', 0.80, 4125, NOW());



INSERT INTO my_app_potholedetection (pothole_id, user_id, latitude, longitude, size, level, confidence, area, detected_at)
VALUES
-- Pothole 11: Hà Nội - Hà Đông (1 detection)
(11, 2, 20.9700, 105.7900, '40x50', 'small', 0.79, 2000, NOW()),

-- Pothole 12: TP.HCM - quận 3 (5 detections)
(12, 4, 10.7800, 106.6900, '45x55', 'small', 0.92, 2475, NOW()),
(12, 6, 10.7803, 106.6905, '60x60', 'medium', 0.93, 3600, NOW()),
(12, 8, 10.7805, 106.6910, '80x70', 'large', 0.94, 5600, NOW()),
(12, 9, 10.7808, 106.6915, '50x40', 'small', 0.92, 2000, NOW()),
(12, 3, 10.7810, 106.6920, '70x65', 'large', 0.95, 4550, NOW()),

-- Pothole 13: Cần Thơ (3 detections)
(13, 6, 10.0600, 105.7700, '45x50', 'small', 0.86, 2250, NOW()),
(13, 2, 10.0604, 105.7704, '70x70', 'large', 0.88, 4900, NOW()),
(13, 7, 10.0607, 105.7707, '60x55', 'medium', 0.87, 3300, NOW()),

-- Pothole 14: Hải Phòng - Kiến An (2 detections)
(14, 7, 20.8600, 106.6500, '40x45', 'small', 0.81, 1800, NOW()),
(14, 5, 20.8603, 106.6504, '65x60', 'medium', 0.83, 3900, NOW()),

-- Pothole 15: Đà Nẵng - Liên Chiểu (4 detections)
(15, 8, 16.0800, 108.1500, '70x65', 'large', 0.94, 4550, NOW()),
(15, 3, 16.0802, 108.1505, '80x70', 'large', 0.95, 5600, NOW()),
(15, 9, 16.0805, 108.1509, '55x50', 'medium', 0.96, 2750, NOW()),
(15, 6, 16.0808, 108.1512, '90x70', 'large', 0.95, 6300, NOW()),

-- Pothole 16: Bắc Ninh (3 detections)
(16, 9, 21.1800, 106.0700, '35x50', 'small', 0.84, 1750, NOW()),
(16, 4, 21.1803, 106.0705, '60x55', 'medium', 0.86, 3300, NOW()),
(16, 7, 21.1806, 106.0709, '75x65', 'large', 0.85, 4875, NOW()),

-- Pothole 17: Hà Nội - Long Biên (4 detections)
(17, 5, 21.0500, 105.9100, '50x55', 'small', 0.89, 2750, NOW()),
(17, 2, 21.0503, 105.9105, '65x60', 'medium', 0.91, 3900, NOW()),
(17, 8, 21.0506, 105.9109, '85x70', 'large', 0.90, 5950, NOW()),
(17, 6, 21.0509, 105.9112, '55x50', 'medium', 0.89, 2750, NOW()),

-- Pothole 18: Đồng Nai - Biên Hòa (2 detections)
(18, 10, 10.9500, 106.8200, '40x45', 'small', 0.82, 1800, NOW()),
(18, 4, 10.9504, 106.8205, '70x65', 'large', 0.84, 4550, NOW()),

-- Pothole 19: TP.HCM - quận 5 (6 detections)
(19, 1, 10.7600, 106.6700, '60x65', 'medium', 0.96, 3900, NOW()),
(19, 5, 10.7602, 106.6705, '75x70', 'large', 0.97, 5250, NOW()),
(19, 8, 10.7605, 106.6709, '90x80', 'large', 0.96, 7200, NOW()),
(19, 3, 10.7607, 106.6712, '70x70', 'large', 0.97, 4900, NOW()),
(19, 7, 10.7610, 106.6715, '85x75', 'large', 0.98, 6375, NOW()),
(19, 9, 10.7613, 106.6719, '65x60', 'medium', 0.97, 3900, NOW()),

-- Pothole 20: Huế (1 detection)
(20, 3, 16.4700, 107.5900, '35x55', 'small', 0.78, 1925, NOW());


INSERT INTO my_app_potholedetection  
(pothole_id, user_id, latitude, longitude, size, level, confidence, area, detected_at)
VALUES
-- Pothole 21: Hà Nội - Tây Hồ (2 detections)
(21, 2, 21.0800, 105.8200, '45x35', 'small', 0.81, 1575, NOW()),
(21, 5, 21.0803, 105.8204, '55x35', 'small', 0.83, 1925, NOW()),

-- Pothole 22: TP.HCM - Gò Vấp (3 detections)
(22, 4, 10.8300, 106.6700, '60x40', 'medium', 0.87, 2400, NOW()),
(22, 7, 10.8304, 106.6704, '70x50', 'medium', 0.89, 3500, NOW()),
(22, 9, 10.8308, 106.6708, '80x65', 'large', 0.88, 5200, NOW()),

-- Pothole 23: Đà Nẵng - Thanh Khê (5 detections)
(23, 6, 16.0700, 108.2100, '65x45', 'medium', 0.93, 2925, NOW()),
(23, 3, 16.0703, 108.2103, '80x65', 'large', 0.94, 5200, NOW()),
(23, 8, 16.0706, 108.2106, '70x50', 'medium', 0.95, 3500, NOW()),
(23, 2, 16.0709, 108.2109, '85x70', 'large', 0.94, 5950, NOW()),
(23, 9, 16.0712, 108.2112, '75x60', 'large', 0.93, 4500, NOW()),

-- Pothole 24: Hải Phòng - Lê Chân (2 detections)
(24, 7, 20.8500, 106.6800, '40x40', 'small', 0.79, 1600, NOW()),
(24, 5, 20.8504, 106.6803, '55x45', 'small', 0.81, 2475, NOW()),

-- Pothole 25: Hà Nội - Nam Từ Liêm (3 detections)
(25, 8, 21.0100, 105.7700, '60x45', 'medium', 0.85, 2700, NOW()),
(25, 2, 21.0103, 105.7704, '85x65', 'large', 0.87, 5525, NOW()),
(25, 6, 21.0106, 105.7708, '70x55', 'medium', 0.86, 3850, NOW()),

-- Pothole 26: TP.HCM - Quận 10 (4 detections)
(26, 9, 10.7700, 106.6600, '55x50', 'medium', 0.91, 2750, NOW()),
(26, 4, 10.7704, 106.6603, '70x60', 'medium', 0.92, 4200, NOW()),
(26, 1, 10.7707, 106.6607, '90x70', 'large', 0.93, 6300, NOW()),
(26, 7, 10.7710, 106.6610, '80x65', 'large', 0.92, 5200, NOW()),

-- Pothole 27: Cần Thơ - Bình Thủy (2 detections)
(27, 10, 10.0700, 105.7200, '50x35', 'small', 0.82, 1750, NOW()),
(27, 6, 10.0703, 105.7203, '55x40', 'small', 0.84, 2200, NOW()),

-- Pothole 28: Bắc Ninh (3 detections)
(28, 3, 21.1900, 106.0900, '65x45', 'medium', 0.88, 2925, NOW()),
(28, 5, 21.1904, 106.0903, '70x55', 'medium', 0.89, 3850, NOW()),
(28, 8, 21.1907, 106.0907, '85x65', 'large', 0.90, 5525, NOW()),

-- Pothole 29: Đà Nẵng - Cẩm Lệ (2 detections)
(29, 5, 16.0000, 108.2000, '55x45', 'small', 0.94, 2475, NOW()),
(29, 9, 16.0004, 108.2003, '75x60', 'large', 0.95, 4500, NOW()),

-- Pothole 30: Quảng Nam (2 detections)
(30, 1, 15.5700, 108.4700, '45x40', 'small', 0.80, 1800, NOW()),
(30, 6, 15.5703, 108.4704, '60x45', 'medium', 0.82, 2700, NOW());



INSERT INTO my_app_potholedetection  
(pothole_id, user_id, latitude, longitude, size, level, confidence, area, detected_at)
VALUES
-- Pothole 31: Hà Nội - Đông Anh (1 detection)
(31, 2, 21.1400, 105.8300, '55x45', 'medium', 0.79, 2475, NOW()),

-- Pothole 32: TP.HCM - quận 7 (2 detections)
(32, 4, 10.7300, 106.7200, '60x50', 'medium', 0.92, 3000, NOW()),
(32, 7, 10.7304, 106.7203, '85x65', 'large', 0.94, 5525, NOW()),

-- Pothole 33: Huế - trung tâm (3 detections)
(33, 6, 16.4600, 107.5900, '65x50', 'medium', 0.86, 3250, NOW()),
(33, 1, 16.4603, 107.5903, '85x65', 'large', 0.87, 5525, NOW()),
(33, 8, 16.4606, 107.5906, '70x55', 'medium', 0.88, 3850, NOW()),

-- Pothole 34: Hải Phòng - Đồ Sơn (2 detections)
(34, 7, 20.6700, 106.7800, '45x40', 'small', 0.81, 1800, NOW()),
(34, 3, 20.6703, 106.7803, '55x45', 'medium', 0.83, 2475, NOW()),

-- Pothole 35: Đà Nẵng - Ngũ Hành Sơn (4 detections)
(35, 8, 16.0100, 108.2500, '70x60', 'medium', 0.95, 4200, NOW()),
(35, 2, 16.0104, 108.2503, '85x65', 'large', 0.96, 5525, NOW()),
(35, 5, 16.0107, 108.2507, '90x70', 'large', 0.97, 6300, NOW()),
(35, 9, 16.0110, 108.2510, '75x60', 'large', 0.95, 4500, NOW()),

-- Pothole 36: Bắc Giang (3 detections)
(36, 9, 21.2800, 106.1900, '60x50', 'medium', 0.84, 3000, NOW()),
(36, 6, 21.2803, 106.1904, '70x55', 'medium', 0.86, 3850, NOW()),
(36, 4, 21.2807, 106.1907, '85x65', 'large', 0.85, 5525, NOW()),

-- Pothole 37: Hà Nội - Mỹ Đình (4 detections)
(37, 10, 21.0300, 105.7700, '65x55', 'medium', 0.89, 3575, NOW()),
(37, 2, 21.0304, 105.7703, '80x65', 'large', 0.91, 5200, NOW()),
(37, 7, 21.0307, 105.7707, '70x60', 'medium', 0.90, 4200, NOW()),
(37, 5, 21.0310, 105.7710, '85x65', 'large', 0.89, 5525, NOW()),

-- Pothole 38: Đồng Nai - Nhơn Trạch (2 detections)
(38, 1, 10.7400, 106.9300, '50x40', 'small', 0.83, 2000, NOW()),
(38, 8, 10.7404, 106.9303, '60x50', 'medium', 0.85, 3000, NOW()),

-- Pothole 39: TP.HCM - Bình Tân (3 detections)
(39, 3, 10.7600, 106.6200, '75x65', 'large', 0.96, 4875, NOW()),
(39, 6, 10.7604, 106.6203, '90x70', 'large', 0.97, 6300, NOW()),
(39, 9, 10.7607, 106.6207, '70x60', 'medium', 0.98, 4200, NOW()),

-- Pothole 40: Thái Nguyên (1 detection)
(40, 5, 21.5900, 105.8500, '55x45', 'medium', 0.78, 2475, NOW());


INSERT INTO my_app_potholedetection 
(pothole_id, user_id, latitude, longitude, size, level, confidence, area, detected_at)
VALUES
-- Pothole 41: Hà Nội (3 detections)
(41, 2, 21.0285, 105.8540, '40x50', 'small', 0.91, 2000, NOW()),
(41, 5, 21.0288, 105.8543, '45x60', 'medium', 0.93, 2700, NOW()),
(41, 7, 21.0291, 105.8546, '50x80', 'medium', 0.92, 4000, NOW()),

-- Pothole 42: TP.HCM (2 detections)
(42, 3, 10.7765, 106.7000, '38x50', 'small', 0.84, 1900, NOW()),
(42, 6, 10.7768, 106.7003, '45x55', 'medium', 0.86, 2475, NOW()),

-- Pothole 43: Đà Nẵng (5 detections)
(43, 1, 16.0600, 108.2200, '48x60', 'medium', 0.94, 2880, NOW()),
(43, 4, 16.0603, 108.2204, '55x70', 'medium', 0.95, 3850, NOW()),
(43, 7, 16.0606, 108.2207, '60x90', 'large', 0.96, 5400, NOW()),
(43, 9, 16.0609, 108.2210, '50x85', 'large', 0.94, 4250, NOW()),
(43, 2, 16.0612, 108.2213, '65x82', 'large', 0.95, 5330, NOW()),

-- Pothole 44: Hà Nội - khu khác (1 detection)
(44, 2, 21.0400, 105.8600, '35x45', 'small', 0.78, 1575, NOW()),

-- Pothole 45: TP.HCM - quận 1 (4 detections)
(45, 4, 10.7800, 106.6950, '42x55', 'medium', 0.87, 2310, NOW()),
(45, 6, 10.7803, 106.6953, '50x70', 'medium', 0.89, 3500, NOW()),
(45, 8, 10.7806, 106.6956, '65x85', 'large', 0.88, 5525, NOW()),
(45, 10, 10.7809, 106.6959, '45x60', 'medium', 0.89, 2700, NOW()),

-- Pothole 46: Đà Nẵng - ven biển (6 detections)
(46, 3, 16.0500, 108.2500, '48x55', 'medium', 0.90, 2640, NOW()),
(46, 5, 16.0504, 108.2504, '55x70', 'medium', 0.91, 3850, NOW()),
(46, 7, 16.0508, 108.2508, '80x85', 'large', 0.92, 6800, NOW()),
(46, 9, 16.0512, 108.2512, '50x75', 'medium', 0.91, 3750, NOW()),
(46, 2, 16.0516, 108.2516, '65x90', 'large', 0.92, 5850, NOW()),
(46, 6, 16.0520, 108.2520, '70x85', 'large', 0.91, 5950, NOW()),

-- Pothole 47: Hà Đông (2 detections)
(47, 2, 20.9700, 105.7700, '36x48', 'small', 0.79, 1728, NOW()),
(47, 8, 20.9703, 105.7703, '45x50', 'medium', 0.81, 2250, NOW()),

-- Pothole 48: Gò Vấp (3 detections)
(48, 5, 10.8300, 106.6800, '42x50', 'medium', 0.86, 2100, NOW()),
(48, 9, 10.8304, 106.6803, '55x80', 'large', 0.87, 4400, NOW()),
(48, 1, 10.8308, 106.6807, '65x85', 'large', 0.88, 5525, NOW()),

-- Pothole 49: Bắc Ninh (2 detections)
(49, 1, 21.1800, 106.0700, '45x55', 'medium', 0.81, 2475, NOW()),
(49, 7, 21.1804, 106.0704, '60x85', 'large', 0.83, 5100, NOW()),

-- Pothole 50: Cần Thơ (4 detections)
(50, 3, 10.0500, 105.7800, '48x60', 'medium', 0.89, 2880, NOW()),
(50, 6, 10.0503, 105.7803, '55x70', 'medium', 0.91, 3850, NOW()),
(50, 8, 10.0507, 105.7807, '65x85', 'large', 0.90, 5525, NOW()),
(50, 10, 10.0510, 105.7810, '70x80', 'large', 0.91, 5600, NOW());


