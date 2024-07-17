DROP SCHEMA IF EXISTS BruceBay_beans_bunks;
CREATE SCHEMA BruceBay_beans_bunks;
USE BruceBay_beans_bunks;

CREATE TABLE `auth` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` ENUM('customer', 'staff', 'manager') NOT NULL,
  `is_active` TINYINT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);

CREATE TABLE `customer` (
  `customer_id` INT NOT NULL,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `phone` VARCHAR(20) UNIQUE NOT NULL,
  `email` VARCHAR(100) UNIQUE NOT NULL,
  `address` VARCHAR(255) NOT NULL,
  `date_of_birth` DATE NOT NULL,
  `date_joined` DATE NOT NULL,
  PRIMARY KEY (`customer_id`),
  CONSTRAINT `fk_auth_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `auth` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `staff` (
  `staff_id` INT NOT NULL,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `position` VARCHAR(45) NOT NULL,
  `address` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20) UNIQUE NOT NULL,
  `email` VARCHAR(100) UNIQUE NOT NULL,
  PRIMARY KEY (`staff_id`),
  CONSTRAINT `fk_auth_staff_id`
    FOREIGN KEY (`staff_id`)
    REFERENCES `auth` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `manager` (
  `manager_id` INT NOT NULL,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `position` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20) UNIQUE NOT NULL,
  `email` VARCHAR(100) UNIQUE NOT NULL,
  PRIMARY KEY (`manager_id`),
  CONSTRAINT `fk_auth_manager_id`
    FOREIGN KEY (`manager_id`)
    REFERENCES `auth` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `gift_card_types` (
  `type_id` INT NOT NULL AUTO_INCREMENT,
  `amount` DECIMAL(10,2) NOT NULL,
  `description` TEXT,
  PRIMARY KEY (`type_id`)
);

CREATE TABLE `gift_cards` (
  `gift_card_id` INT NOT NULL AUTO_INCREMENT,
  `type_id` INT NOT NULL,
  `redemption_code` VARCHAR(10) NOT NULL,
  `gift_card_password` VARCHAR(4) NOT NULL,
  `current_balance` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  `issue_date` DATE NOT NULL,
  `expiry_date` DATE NULL,
  PRIMARY KEY (`gift_card_id`),
  CONSTRAINT `fk_gc_type_id`
    FOREIGN KEY (`type_id`)
    REFERENCES `gift_card_types` (`type_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `gift_card_transactions` (
  `transaction_id` INT NOT NULL AUTO_INCREMENT,
  `gift_card_id` INT NOT NULL,
  `transaction_type` ENUM('Redemption', 'Top-Up') NOT NULL,
  `amount` DECIMAL(10,2) NOT NULL,
  `transaction_date` DATETIME NOT NULL,
  `customer_id` INT NULL,
  PRIMARY KEY (`transaction_id`),
  CONSTRAINT `fk_gct_gift_card_id`
    FOREIGN KEY (`gift_card_id`)
    REFERENCES `gift_cards` (`gift_card_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_gct_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `product_category` (
  `category_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`category_id`));

CREATE TABLE `product` (
  `product_id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `description` TEXT NOT NULL,
  `price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `category_id` INT NULL,
  `image` VARCHAR(100) NULL,
  `is_available` TINYINT NOT NULL,
  `is_inventory` TINYINT NOT NULL DEFAULT 1,
  `average_rating` DECIMAL(3,2) DEFAULT NULL,
  PRIMARY KEY (`product_id`),
  CONSTRAINT `fk_product_category_id`
    FOREIGN KEY (`category_id`)
    REFERENCES `product_category` (`category_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE);

CREATE TABLE `product_variations` (
  `variation_id` INT NOT NULL AUTO_INCREMENT,
  `product_id` INT NOT NULL,
  `variation_name` VARCHAR(255) DEFAULT 'Standard',
  `additional_cost` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`variation_id`),
  CONSTRAINT `fk_pv_product_id`
    FOREIGN KEY (`product_id`)
    REFERENCES `product` (`product_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `promotions` (
  `promo_id` INT NOT NULL AUTO_INCREMENT,
  `promo_code` VARCHAR(50) NOT NULL,
  `description` TEXT NOT NULL,
  `discount_rate` DECIMAL(10,2) NOT NULL DEFAULT 1,
  `start_date` DATE NULL,
  `end_date` DATE NULL,
  `conditions` TEXT NULL,
  `points_cost` INT DEFAULT NULL,
  PRIMARY KEY (`promo_id`));

CREATE TABLE `promotion_products` (
  `promo_product_id` INT NOT NULL AUTO_INCREMENT,
  `promo_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  PRIMARY KEY (`promo_product_id`),
  INDEX `fk_pp_promo_id_idx` (`promo_id` ASC) VISIBLE,
  INDEX `fk_pp_product_id_idx` (`product_id` ASC) VISIBLE,
  CONSTRAINT `fk_pp_promo_id`
    FOREIGN KEY (`promo_id`)
    REFERENCES `promotions` (`promo_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_pp_product_id`
    FOREIGN KEY (`product_id`)
    REFERENCES `product` (`product_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);
  
CREATE TABLE `customer_promos` (
  `customer_promo_id` INT NOT NULL AUTO_INCREMENT,
  `customer_id` INT NOT NULL,
  `promo_id` INT NOT NULL,
  `used_date` DATE NOT NULL,
  PRIMARY KEY (`customer_promo_id`),
  INDEX `fk_cp_customer_id_idx` (`customer_id` ASC) VISIBLE,
  INDEX `fk_cp_promo_id_idx` (`promo_id` ASC) VISIBLE,
  CONSTRAINT `fk_cp_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_cp_promo_id`
    FOREIGN KEY (`promo_id`)
    REFERENCES `promotions` (`promo_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `carts` (
  `cart_id` INT NOT NULL AUTO_INCREMENT,
  `customer_id` INT NOT NULL,
  `creation_time` DATETIME NOT NULL,
  `last_updated` DATETIME NOT NULL,
  PRIMARY KEY (`cart_id`),
  INDEX `fk_carts_customer_id_idx` (`customer_id` ASC) VISIBLE,
  CONSTRAINT `fk_carts_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `cart_details` (
  `cart_detail_id` INT NOT NULL AUTO_INCREMENT,
  `cart_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  `quantity` INT NOT NULL,
  `price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`cart_detail_id`),
  INDEX `fk_cd_cart_id_idx` (`cart_id` ASC) VISIBLE,
  INDEX `fk_cd_product_id_idx` (`product_id` ASC) VISIBLE,
  CONSTRAINT `fk_cd_cart_id`
    FOREIGN KEY (`cart_id`)
    REFERENCES `carts` (`cart_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_cd_product_id`
    FOREIGN KEY (`product_id`)
    REFERENCES `product` (`product_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `cart_variations` (
  `cart_variation_id` INT NOT NULL AUTO_INCREMENT,
  `cart_detail_id` INT NOT NULL,
  `variation_id` INT NOT NULL,
  PRIMARY KEY (`cart_variation_id`),
  CONSTRAINT `fk_cv_cart_detail_id`
    FOREIGN KEY (`cart_detail_id`)
    REFERENCES `cart_details` (`cart_detail_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_cv_variation_id`
    FOREIGN KEY (`variation_id`)
    REFERENCES `product_variations` (`variation_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `orders` (
  `order_id` INT NOT NULL AUTO_INCREMENT,
  `customer_id` INT NOT NULL, 
  `order_time` DATETIME NOT NULL,
  `special_requests` TEXT NOT NULL,
  `status` ENUM("Pending", "Ready", "Collected") NOT NULL,
  `pickup_time` DATETIME NULL,
  `promo_id` INT NULL,
  PRIMARY KEY (`order_id`),
  INDEX `fk_orders_promo_id_idx` (`promo_id` ASC) VISIBLE,
  CONSTRAINT `fk_orders_promo_id`
    FOREIGN KEY (`promo_id`)
    REFERENCES `promotions` (`promo_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE);

CREATE TABLE `order_details` (
  `order_detail_id` INT NOT NULL AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `product_id` INT NULL,
  `quantity` INT NOT NULL,
  `price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`order_detail_id`),
  INDEX `fk_od_order_id_idx` (`order_id` ASC) VISIBLE,
  INDEX `fk_od_product_id_idx` (`product_id` ASC) VISIBLE,
  CONSTRAINT `fk_od_order_id`
    FOREIGN KEY (`order_id`)
    REFERENCES `orders` (`order_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_od_product_id`
    FOREIGN KEY (`product_id`)
    REFERENCES `product` (`product_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE);

CREATE TABLE `order_variations` (
  `order_variation_id` INT NOT NULL AUTO_INCREMENT,
  `order_detail_id` INT NOT NULL,
  `variation_id` INT NOT NULL,
  PRIMARY KEY (`order_variation_id`),
  CONSTRAINT `fk_ov_order_detail_id`
    FOREIGN KEY (`order_detail_id`)
    REFERENCES `order_details` (`order_detail_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_ov_variation_id`
    FOREIGN KEY (`variation_id`)
    REFERENCES `product_variations` (`variation_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `inventory` (
  `inventory_id` INT NOT NULL AUTO_INCREMENT,
  `product_id` INT NOT NULL,
  `stock_level` INT NOT NULL,
  `last_replenishment_date` DATE NOT NULL,
  PRIMARY KEY (`inventory_id`),
  INDEX `fk_inventory_product_id_idx` (`product_id` ASC) VISIBLE,
  CONSTRAINT `fk_inventory_product_id`
    FOREIGN KEY (`product_id`)
    REFERENCES `product` (`product_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `room` (
  `room_id` INT NOT NULL AUTO_INCREMENT,
  `type` ENUM("Dorm", "Twin", "Queen") NOT NULL,
  `capacity` INT NOT NULL,
  `description` TEXT NOT NULL,
  `price_per_night` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `image` VARCHAR(100) NULL,
  `amount` INT NOT NULL,
  PRIMARY KEY (`room_id`));

CREATE TABLE `bookings` (
  `booking_id` INT NOT NULL AUTO_INCREMENT,
  `customer_id` INT NOT NULL,
  `room_id` INT NOT NULL,
  `number_of_bunks` INT NULL, -- only for bunks
  `check_in_date` DATE NOT NULL,
  `check_out_date` DATE NOT NULL,
  `status` ENUM("Pending", "Paid", "Confirmed", "Cancelled", "Completed", "BLOCKED") NOT NULL,
  `price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`booking_id`),
  INDEX `fk_bookings_customer_id_idx` (`customer_id` ASC) VISIBLE,
  INDEX `fk_bookings_room_id_idx` (`room_id` ASC) VISIBLE,
  CONSTRAINT `fk_bookings_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_bookings_room_id`
    FOREIGN KEY (`room_id`)
    REFERENCES `room` (`room_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `order_payment` (
  `order_payment_id` INT NOT NULL AUTO_INCREMENT,
  `order_id` INT NOT NULL,
  `amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `payment_method` ENUM('Cash', 'Debit Card', 'Credit Card', 'Gift Card', 'Pay Later') NOT NULL,
  `payment_status` ENUM('Pending', 'Completed', 'Refunded') NOT NULL,
  `payment_date` DATETIME NOT NULL,
  `gift_card_id` INT NULL,
  `gift_card_amount` DECIMAL(10, 2) DEFAULT 0.00,
  PRIMARY KEY (`order_payment_id`),
  INDEX `fk_op_order_id_idx` (`order_id` ASC) VISIBLE,
  CONSTRAINT `fk_op_order_id`
    FOREIGN KEY (`order_id`)
    REFERENCES `orders` (`order_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_op_gift_card_id`
    FOREIGN KEY (`gift_card_id`)
    REFERENCES `gift_cards` (`gift_card_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE);

CREATE TABLE `booking_payment` (
  `booking_payment_id` INT NOT NULL AUTO_INCREMENT,
  `booking_id` INT NOT NULL,
  `amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `payment_method` ENUM('Cash', 'Debit Card', 'Credit Card', 'Gift Card') NOT NULL,
  `payment_status` ENUM('Pending', 'Completed', 'Refunded') NOT NULL,
  `payment_date` DATETIME NOT NULL,
  `gift_card_id` INT NULL,
  `gift_card_amount` DECIMAL(10, 2) DEFAULT 0.00,
  PRIMARY KEY (`booking_payment_id`),
  INDEX `fk_bp_booking_id_idx` (`booking_id` ASC) VISIBLE,
  CONSTRAINT `fk_bp_booking_id`
    FOREIGN KEY (`booking_id`)
    REFERENCES `bookings` (`booking_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_bp_gift_card_id`
    FOREIGN KEY (`gift_card_id`)
    REFERENCES `gift_cards` (`gift_card_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE);

CREATE TABLE `loyalty_points` (
  `customer_id` INT NOT NULL,
  `total_earned` INT DEFAULT 0,
  `total_spent` INT DEFAULT 0,
  `current_balance` INT GENERATED ALWAYS AS (`total_earned` - `total_spent`) STORED,
  PRIMARY KEY (`customer_id`),
  INDEX `fk_lp_customer_id_idx` (`customer_id` ASC) VISIBLE,
  CONSTRAINT `fk_lp_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `points_transactions` (
  `point_transaction_id` INT NOT NULL AUTO_INCREMENT,
  `customer_id` INT NOT NULL,
  `points` INT NOT NULL,
  `promo_id` INT NULL,
  `transaction_type` ENUM('Earned', 'Spent') NOT NULL,
  `description` TEXT,
  `transaction_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`point_transaction_id`),
  INDEX `fk_pt_customer_id_idx` (`customer_id` ASC) VISIBLE,
  CONSTRAINT `fk_pt_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_pt_promo_id`
    FOREIGN KEY (`promo_id`)
    REFERENCES `promotions` (`promo_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE);

CREATE TABLE `inquiries` (
  `inquiry_id` INT NOT NULL AUTO_INCREMENT,
  `customer_id` INT NOT NULL,
  `inquiry_text` TEXT NOT NULL,
  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `status` ENUM('unread','pending','responded') NOT NULL DEFAULT 'unread',
  PRIMARY KEY (`inquiry_id`),
  INDEX `fk_inquiries_customer_id_idx` (`customer_id` ASC) VISIBLE,
  CONSTRAINT `fk_inquiries_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `messages` (
  `message_id` INT NOT NULL AUTO_INCREMENT,
  `sender_id` INT,
  `customer_id` INT NOT NULL,
  `inquiry_id` INT NOT NULL,
  `message_text` TEXT NOT NULL,
  `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `status` ENUM('received', 'unread') DEFAULT 'unread',
  PRIMARY KEY (`message_id`),
  INDEX `fk_messages_sender_id_idx` (`sender_id` ASC) VISIBLE,
  INDEX `fk_messages_inquiry_id_idx` (`inquiry_id` ASC) VISIBLE,
  CONSTRAINT `fk_messages_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_messages_inquiry_id`
    FOREIGN KEY (`inquiry_id`)
    REFERENCES `inquiries` (`inquiry_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_messages_sender_id`
    FOREIGN KEY (`sender_id`)
    REFERENCES `auth` (`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE);

CREATE TABLE `news` (
  `news_id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `content` LONGTEXT NOT NULL,
  `publish_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `manager_id` INT NOT NULL,
  PRIMARY KEY (`news_id`),
  CONSTRAINT `fk_news_manager_id`
    FOREIGN KEY (`manager_id`)
    REFERENCES `manager` (`manager_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);
    
CREATE TABLE `opening_hours` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `days` VARCHAR(20) NOT NULL,
  `open_time` TIME,
  `close_time` TIME,
  PRIMARY KEY (`id`));

CREATE TABLE `point_exchange_rules` (
  `rule_id` INT NOT NULL AUTO_INCREMENT,
  `points_required` INT NOT NULL,
  `gift_card_type_id` INT NOT NULL,
  `description` TEXT,
  PRIMARY KEY (`rule_id`),
  CONSTRAINT `fk_per_gift_card_type_id`
    FOREIGN KEY (`gift_card_type_id`)
    REFERENCES `gift_card_types` (`type_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `point_exchange_transactions` (
  `transaction_id` INT NOT NULL AUTO_INCREMENT,
  `customer_id` INT NOT NULL,
  `rule_id` INT NOT NULL,
  `transaction_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`transaction_id`),
  CONSTRAINT `fk_pet_customer_id`
	FOREIGN KEY (`customer_id`) 
    REFERENCES `customer` (`customer_id`) 
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_pet_rule_id`
	FOREIGN KEY (`rule_id`) 
    REFERENCES `point_exchange_rules` (`rule_id`) 
    ON DELETE CASCADE
    ON UPDATE CASCADE);

CREATE TABLE `product_reviews` (
  `review_id` INT NOT NULL AUTO_INCREMENT,
  `customer_id` INT NOT NULL,
  `order_id` INT NOT NULL,
  `order_detail_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  `rating` INT NOT NULL CHECK (`rating` BETWEEN 1 AND 5),
  `feedback` TEXT NULL,
  `review_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_visible` TINYINT NOT NULL DEFAULT 1,	
  PRIMARY KEY (`review_id`),
  CONSTRAINT `fk_pr_customer_id`
    FOREIGN KEY (`customer_id`)
    REFERENCES `customer` (`customer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
	CONSTRAINT `fk_pr_order_id`
    FOREIGN KEY (`order_id`)
    REFERENCES `orders` (`order_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_pr_order_detail_id`
    FOREIGN KEY (`order_detail_id`)
    REFERENCES `order_details` (`order_detail_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_pr_product_id`
    FOREIGN KEY (`product_id`)
    REFERENCES `product` (`product_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE);
    


-- INSERT Statements for auth --
INSERT INTO `auth` (`username`, `password_hash`, `role`, `is_active`) VALUES
('user1', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user2', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user3', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user4', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user5', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user6', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('staff1', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'staff', 1),
('staff2', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'staff', 1),
('staff3', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'staff', 1),
('admin', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'manager', 1),
('user7', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user8', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user9', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user10', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user11', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user12', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user13', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user14', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user15', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user16', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user17', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user18', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user19', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('user20', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1),
('staff4', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'staff', 1),
('staff5', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'staff', 1);
-- For Admin
INSERT INTO `auth` (`username`, `password_hash`, `role`, `is_active`) VALUES 
('admin-block', 'scrypt:32768:8:1$3RY2MpKJfMBL6y2M$face964ccc797ac918e011d307e0d1b33c4d63ebce4a241d912edc0d498c47861f36ec03a6a39394376a930a982434b2edfa03283f4ea20f0b292c6514fce8e0', 'customer', 1);

-- INSERT Statements for customer --
INSERT INTO `customer` (`customer_id`, `first_name`, `last_name`, `phone`, `email`, `address`, `date_of_birth`, `date_joined`) VALUES
(1, 'John', 'Johnson', '0211234567', 'john.johnson@demo.org', '345 Main St', '2006-12-19', '2020-08-07'),
(2, 'Carol', 'Wilson', '0211234568', 'carol.wilson@demo.org', '435 Main St', '1994-06-13', '2021-10-11'),
(3, 'David', 'Wilson', '0211234569', 'david.wilson@example.com', '570 Third St', '1986-11-25', '2020-07-08'),
(4, 'Bob', 'Brown', '0211234560', 'bob.brown@example.com', '186 Third St', '1993-10-04', '2020-06-01'),
(5, 'John', 'Lee', '0211234561', 'john.lee@example.com', '456 Third St', '1995-06-19', '2021-09-26'),
(6, 'Jack', 'Johnson', '0211234562', 'jack.johnson@sample.net', '381 Main St', '2003-05-28', '2021-05-03'),
(11, 'Alice', 'Green', '0211111111', 'alice.green@demo.org', '123 Pine St', '1992-01-01', '2023-01-01'),
(12, 'Bob', 'Blue', '0212222222', 'bob.blue@demo.org', '456 Oak St', '1990-02-02', '2023-02-02'),
(13, 'Charlie', 'Brown', '0213333333', 'charlie.brown@demo.org', '789 Maple St', '1988-03-03', '2023-03-03'),
(14, 'David', 'White', '0214444444', 'david.white@demo.org', '101 Birch St', '1995-04-04', '2023-04-04'),
(15, 'Eve', 'Black', '0215555555', 'eve.black@demo.org', '202 Cedar St', '1991-05-05', '2023-05-05'),
(16, 'Frank', 'Gray', '0216666666', 'frank.gray@demo.org', '303 Elm St', '1989-06-06', '2023-06-06'),
(17, 'Grace', 'Pink', '0217777777', 'grace.pink@demo.org', '404 Ash St', '1994-07-07', '2023-07-07'),
(18, 'Hank', 'Purple', '0218888888', 'hank.purple@demo.org', '505 Spruce St', '1987-08-08', '2023-08-08'),
(19, 'Ivy', 'Yellow', '0219999999', 'ivy.yellow@demo.org', '606 Fir St', '1993-09-09', '2023-09-09'),
(20, 'Jack', 'Red', '0210000000', 'jack.red@demo.org', '707 Cherry St', '1996-10-10', '2023-10-10'),
(21, 'Karen', 'Orange', '0211212121', 'karen.orange@demo.org', '808 Willow St', '1985-11-11', '2023-11-11'),
(22, 'Leo', 'Cyan', '0212323232', 'leo.cyan@demo.org', '909 Poplar St', '1998-12-12', '2023-12-12'),
(23, 'Mia', 'Magenta', '0213434343', 'mia.magenta@demo.org', '110 Aspen St', '1984-01-13', '2024-01-13'),
(24, 'Nick', 'Teal', '0214545454', 'nick.teal@demo.org', '111 Maple St', '1983-02-14', '2024-02-14');

INSERT INTO `customer` (`customer_id`, `first_name`, `last_name`, `phone`, `email`, `address`, `date_of_birth`, `date_joined`) VALUES 
((SELECT `id` FROM `auth` WHERE `username` = 'admin-block'), 'Admin', 'Block', '000-000-0000', 'admin@block.com', 'Admin Address', '1970-01-01', CURDATE());

-- INSERT Statements for staff --
INSERT INTO `staff` (`staff_id`, `first_name`, `last_name`, `position`, `email`, `phone`, `address`) VALUES
(7, 'Carol', 'Wilson', 'Active managers', 'carol.wilson@demo.org', '0221234567', '816 Second St'),
(8, 'Alice', 'Smith', 'Sales', 'alice.smith@sample.net', '0221234568', '635 Main St'),
(9, 'Alice', 'Brown', 'Sales', 'alice.brown@sample.net', '0221234569', '296 Third St'),
(25, 'Olivia', 'Lime', 'Sales', '0221212121', 'olivia.lime@demo.org', '121 Apple St'),
(26, 'Peter', 'Moss', 'Barista', '0222323232', 'peter.moss@demo.org', '131 Banana St');


-- INSERT Statements for manager --
INSERT INTO `manager` (`manager_id`, `first_name`, `last_name`, `position`, `phone`, `email`) VALUES
(10, 'Bob', 'Smith', 'Manager', '0271231234', 'bob.smith@sample.net');

-- INSERT Statements for gift_card_types --
INSERT INTO `gift_card_types` (`amount`, `description`) VALUES
(50.00, 'Standard gift card worth $50'),
(100.00, 'Premium gift card worth $100'),
(200.00, 'Deluxe gift card worth $200');

-- INSERT Statements for gift_cards --
INSERT INTO `gift_cards` (`type_id`, `redemption_code`, `gift_card_password`, `current_balance`, `issue_date`, `expiry_date`) VALUES
(1, 'GC001', '2345', 50.00, '2023-01-15', '2025-01-15'),
(2, 'GC002', '6920', 100.00, '2023-02-20', '2025-02-20'),
(3, 'GC003', '6830', 200.00, '2023-03-25', '2025-03-25'),
(1, 'GC004', '7537', 46.00, '2023-04-10', '2025-04-10'),
(2, 'GC005', '1237', 94.00, '2023-05-05', '2025-05-05'),
(3, 'GC006', '6437', 200.00, '2023-06-01', '2025-06-01'),
(1, 'GC007', '1234', 50.00, '2024-01-01', '2026-01-01'),
(2, 'GC008', '5678', 100.00, '2024-02-01', '2026-02-01'),
(3, 'GC009', '9101', 200.00, '2024-03-01', '2026-03-01'),
(1, 'GC010', '1121', 50.00, '2024-04-01', '2026-04-01'),
(2, 'GC011', '3141', 100.00, '2024-05-01', '2026-05-01');

-- INSERT Statements for gift_card_transactions --
INSERT INTO `gift_card_transactions` (`gift_card_id`, `transaction_type`, `amount`, `transaction_date`, `customer_id`) VALUES
(1, 'Top-Up', 50.00, '2023-01-15', 1),
(2, 'Top-Up', 100.00, '2023-02-20', 2),
(3, 'Top-Up', 200.00, '2023-03-25', 3),
(4, 'Top-Up', 50.00, '2023-03-25', 4),
(5, 'Top-Up', 100.00, '2023-03-25', 5),
(6, 'Top-Up', 200.00, '2023-03-25', 6),
(4, 'Redemption', 4.00, '2023-04-11', 4),
(5, 'Redemption', 6.00, '2023-05-06', 5),
(7, 'Top-Up', 50.00, '2024-01-01', 11), 
(8, 'Top-Up', 100.00, '2024-02-01', 12), 
(9, 'Top-Up', 200.00, '2024-03-01', 13), 
(10, 'Top-Up', 50.00, '2024-04-01', 14), 
(11, 'Top-Up', 100.00, '2024-05-01', 15); 

-- INSERT Statements for product_category --
INSERT INTO `product_category` (`name`) VALUES
('Coffee'),
('Packaged Food'),
('Cooked Food'),
('Drink'),
('Merchandise'),
('Others');

-- INSERT Statements for product --
INSERT INTO `product` (`name`, `description`, `price`, `category_id`, `image`, `is_available`, `is_inventory`) VALUES
-- coffee
('Espresso', 'Strong and rich espresso, served plain.', 3.00, 1, 'espresso.jpg', 1, 0),
('Latte', 'Smooth and creamy latte with options for different milks.', 3.50, 1, 'latte.jpg', 1, 0),
('Cappuccino', 'Perfectly frothed cappuccino with a choice of toppings.', 3.50, 1, 'cappuccino.jpg', 1, 0),
('Americano', 'Diluted espresso for those who prefer a lighter coffee.', 3.00, 1, 'americano.jpg', 1, 0),
('Mocha', 'Chocolate-flavored coffee with milk and cocoa.', 4.00, 1, 'mocha.jpg', 1, 0),
('Iced Coffee', 'Chilled coffee with ice, perfect for hot days.', 4.00, 1, 'iced_coffee.jpg', 1, 0),
-- soft drinks
('Pepsi - 330ml', 'A refreshing soft drink known globally.', 2.00, 4, 'pepsi.jpg', 1, 1),
('Coca-Cola - 330ml', 'Classic cola flavor, loved around the world.', 2.00, 4, 'coca_cola.jpg', 1, 1),
('Sprite - 330ml', 'Lemon-lime flavored soft drink, crisp and refreshing.', 2.00, 4, 'sprite.jpg', 1, 1),
('V Energy Drink', 'Ignite your day with a surge of electrifying flavor, crafted to keep you energized and refreshed.', 2.00, 4, 'v_drink.jpg', 1, 1),
('Ice Lemon Tea', 'Savor the refreshing zest of lemon-infused tea, perfect for rejuvenating your senses anytime, anywhere.', 2.50, 4, 'ice_teas.jpg', 1, 1),
-- food
('Hotdogs', 'American style hotdogs with various toppings.', 3.50, 3, 'hotdogs.jpg', 1, 1),
('Sweetcorn & Kumara Patties', 'Delicious patties made from sweetcorn and kumara.', 4.00, 3, 'sweetcorn_kumara_patties.jpg', 1, 1),
('Chocolate Crepes', 'Indulge in decadent chocolate-filled crepes, a blissful delight for any sweet tooth craving.', 5.00, 3, 'crepes.jpg', 1, 1),
('BBQ Pulled Pork Bun', 'Smokey bbq pulled pork served in a soft bun.', 6.00, 3, 'bbq_pulled_pork_bun.jpg', 1, 1),
('Blueberry Muffins', 'Freshly baked blueberry muffins.', 2.50, 3, 'muffins.jpg', 1, 1),
-- Slices
('Chocolate Cake Slices', 'Delicious fresh chocolate cake slices perfect for any sweet tooth.', 8.00, 3, 'chocolate_slices.jpg', 1, 1),
('Lemon Cake Slices', 'Refreshing lemon flavored cake slices, light and tangy.', 8.00, 3, 'lemon_slices.jpg', 1, 1),
('Red Velvet Cake Slices', 'Classic red velvet cake slices with a rich cream cheese frosting.', 8.00, 3, 'red_velvet_slices.jpg', 1, 1),
('Carrot Cake Slices', 'Moist and flavorful carrot cake slices with a hint of spice.', 8.00, 3, 'carrot_cake_slices.jpg', 1, 1),
('Blueberry Cake Slices', 'Sweet and tart blueberry cake slices, bursting with fresh berries.', 8.00, 3, 'blueberry_slices.jpg', 1, 1),
-- Ice Blocks
('Strawberry Ice Blocks', 'Frozen strawberry flavored ice blocks, cool and refreshing.', 2.50, 2, 'strawberry_ice_blocks.jpg', 1, 1),
('Mango Ice Blocks', 'Tropical mango ice blocks, sweet and juicy.', 2.50, 2, 'mango_ice_blocks.jpg', 1, 1),
('Lime Ice Blocks', 'Zesty lime ice blocks, sharp and refreshing.', 2.50, 2, 'lime_ice_blocks.jpg', 1, 1),
('Pineapple Ice Blocks', 'Exotic pineapple ice blocks, rich and tangy.', 2.50, 2, 'pineapple_ice_blocks.jpg', 1, 1),
('Watermelon Ice Blocks', 'Summer-inspired watermelon ice blocks, light and hydrating.', 2.50, 2, 'watermelon_ice_blocks.jpg', 1, 1),
-- Fruit Ice Creams 
('Peach Ice Cream', 'Creamy peach ice cream, full of fresh peach chunks.', 4.50, 3, 'peach_ice_cream.jpg', 1, 1),
('Chocolate Chip Ice Cream', 'Rich chocolate chip ice cream with dark chocolate pieces.', 4.50, 3, 'chocolate_chip_ice_cream.jpg', 1, 1),
('Pistachio Ice Cream', 'Nutty pistachio ice cream, smooth with real pistachio pieces.', 4.50, 3, 'pistachio_ice_cream.jpg', 1, 1),
('Mango Ice Cream', 'Sweet mango ice cream, tropical and creamy.', 4.50, 3, 'mango_ice_cream.jpg', 1, 1),
('Berry Mix Ice Cream', 'Mixed berry ice cream, a medley of seasonal berries.', 4.50, 3, 'berry_mix_ice_cream.jpg', 1, 1),
-- Chips
('Salted Potato Chips', 'Crispy potato chips perfectly salted for a classic snack experience.', 6.00, 2, 'salted_potato_chips.jpg', 1, 1),
('Barbecue Potato Chips', 'Smoky barbecue flavored potato chips with a sweet and tangy finish.', 6.00, 2, 'bbq_potato_chips.jpg', 1, 1),
('Sour Cream & Onion Potato Chips', 'Creamy sour cream and a hint of chives give these potato chips a delicious tang.', 6.00, 2, 'sour_cream_chives_potato_chips.jpg', 1, 1),
('Salt & Vinegar Potato Chips', 'Tangy vinegar meets savory salt on crispy potato slices for an irresistibly zesty snack.', 6.00, 2, 'salt_vinegar_potato_chips.jpg', 1, 1),
('Jalapeño Potato Chips', 'Spicy jalapeño potato chips for those who like a little heat.', 6.00, 2, 'jalapeno_potato_chips.jpg', 1, 1),
-- Merchandise
('Mens Black T-Shirt', 'Bruce Bay Beans and Bunks t-shirt for men.', 30.00, 5, 'mens_black.jpg', 1, 1),
('Mens White T-Shirt', 'Bruce Bay Beans and Bunks t-shirt for men.', 30.00, 5, 'mens_white.jpg', 1, 1),
('Mens Logo Black T-Shirt', 'Bruce Bay Beans and Bunks t-shirt with logo for men.', 35.00, 5, 'mens_black_2.jpg', 1, 1),
('Womens Black T-Shirt', 'Bruce Bay Beans and Bunks t-shirt for women.', 30.00, 5, 'womens_black.jpg', 1, 1),
('Womens White T-Shirt', 'Bruce Bay Beans and Bunks t-shirt for women.', 30.00, 5, 'womens_white.jpg', 1, 1),
('Womens Logo Black T-Shirt', 'Bruce Bay Beans and Bunks t-shirt with logo.', 35.00, 5, 'womens_black_2.jpg', 1, 1),
('Mood Booster Mug', 'Start your day with a cup of mood booster!', 12.00, 5, 'mug.jpg', 1, 1),
-- Others
('Insect Repellant', 'Keep bugs at bay and adventure on with your essential outdoor companion.', 24.99, 6, 'repellant.jpg', 1, 1),
('Sunscreen', 'Enjoy the sun with confidence and comfort with broad-spectrum protection and moisturizing sunscreen.', 23.50, 6, 'sunscreen.jpg', 1, 1),
('Universal Travel Adaptor', 'Stay connected across the globe: Your ultimate travel companion for power anywhere, anytime.', 10.00, 6, 'adaptor.jpg', 1, 1),
-- more coffee
('Flat White', 'Smooth and velvety coffee made with steamed milk over a strong espresso base.', 3.00, 1, 'product-fw.jpg', 1, 0),
('Long Black', 'Bold and strong black coffee, brewed with hot water over a double shot of espresso.', 3.50, 1, 'product-lb.jpg', 1, 0),
('Hot Chocolate', 'Rich and creamy hot chocolate made with cocoa powder and steamed milk.', 3.00, 1, 'product-hc.jpg', 1, 0),
-- Milkshakes
('Banana Milkshake', 'Blending ripe banana with creamy vanilla ice cream, a classic combination sure to please.', 8.50, 4, 'banana_milkshake.jpg', 1, 0),
('Vanilla Milkshake', 'Made with velvety vanilla ice cream, it is a simple pleasure topped with a dollop of whipped cream.', 8.50, 4, 'vanilla_milkshake.jpg', 1, 0),
('Chocolate Milkshake', 'Rich chocolate ice cream drizzled with chocolate syrup, a decadent delight in every sip.', 8.50, 4, 'chocolate_milkshake.jpg', 1, 0),
('Strawberry Milkshake', 'Blending fresh strawberries with creamy ice cream for a refreshing treat.', 8.50, 4, 'strawberry_milkshake.jpg', 1, 0),
('Cookies and Cream Milkshake', 'Vanilla ice cream loaded with chocolate cookie chunks and topped with whipped cream, a delightful treat for any sweet tooth.', 8.50, 4, 'cookies_cream_milkshake.jpg', 1, 0),
-- more food
('French Vanilla Crepes', 'A delicate pancake filled with creamy vanilla custard and dusted with powdered sugar, a timeless indulgence.', 5.00, 3, 'fv_crepes.jpg', 1, 1),
('Berry Bliss Crepes', 'A burst of freshness with a medley of fresh berries, lightly dusted with powdered sugar and served with a dollop of whipped cream.', 5.00, 3, 'b_crepes.jpg', 1, 1),
('Caramelized Apple Cinnamon Crepes', 'Indulge in the comforting flavors of fall filled with warm spiced apples, drizzled with caramel sauce, and sprinkled with cinnamon sugar.', 5.00, 3, 'cac_crepes.jpg', 1, 1),
-- gift card
('Gift Card - $50.00', 'Standard gift card worth $50', 50.00, 6, 'gc_1.jpg', 1, 0),
('Gift Card - $100.00', 'Premium gift card worth $100', 100.00, 6, 'gc_2.jpg', 1, 0),
('Gift Card - $200.00', 'Deluxe gift card worth $200', 200.00, 6, 'gc_3.jpg', 1, 0),
-- more soft drink
('Pepsi - Bottle', 'A refreshing soft drink known globally.', 3.50, 4, 'pepsi_bottle.jpg', 1, 1),
('Coca-Cola - Bottle', 'Classic cola flavor, loved around the world.', 3.50, 4, 'coca_cola_bottle.jpg', 1, 1),
('Sprite - Bottle', 'Lemon-lime flavored soft drink, crisp and refreshing.', 3.50, 4, 'sprite_bottle.jpg', 1, 1);

-- INSERT Statements for product variations --
INSERT INTO `product_variations` (`product_id`, `variation_name`, `additional_cost`) VALUES
(1, 'With Soy Milk', 0.50),
(1, 'With Almond Milk', 0.75),
(1, 'With Vanilla Syrup', 0.50),
(1, 'With Caramel Syrup', 0.50),
(2, 'With Soy Milk', 0.50),
(2, 'With Almond Milk', 0.75),
(2, 'With Vanilla Syrup', 0.50),
(2, 'With Caramel Syrup', 0.50),
(3, 'With Soy Milk', 0.50),
(3, 'With Almond Milk', 0.75),
(3, 'With Vanilla Syrup', 0.50),
(3, 'With Caramel Syrup', 0.50),
(4, 'With Soy Milk', 0.50),
(4, 'With Almond Milk', 0.75),
(4, 'With Vanilla Syrup', 0.50),
(4, 'With Caramel Syrup', 0.50),
(5, 'With Soy Milk', 0.50),
(5, 'With Almond Milk', 0.75),
(5, 'With Vanilla Syrup', 0.50),
(5, 'With Caramel Syrup', 0.50),
(6, 'With Soy Milk', 0.50),
(6, 'With Almond Milk', 0.75),
(6, 'With Vanilla Syrup', 0.50),
(6, 'With Caramel Syrup', 0.50),
(47, 'With Soy Milk', 0.50),
(47, 'With Almond Milk', 0.75),
(47, 'With Vanilla Syrup', 0.50),
(47, 'With Caramel Syrup', 0.50),
(48, 'With Soy Milk', 0.50),
(48, 'With Almond Milk', 0.75),
(48, 'With Vanilla Syrup', 0.50),
(48, 'With Caramel Syrup', 0.50),
(49, 'With Soy Milk', 0.50),
(49, 'With Almond Milk', 0.75),
(49, 'With Vanilla Syrup', 0.50),
(49, 'With Caramel Syrup', 0.50),
(1, 'Medium Size', 0.50),
(1, 'Large Size', 1.00),
(2, 'Medium Size', 0.50),
(2, 'Large Size', 1.00),
(3, 'Medium Size', 0.50),
(3, 'Large Size', 1.00),
(4, 'Medium Size', 0.50),
(4, 'Large Size', 1.00),
(5, 'Medium Size', 0.50),
(5, 'Large Size', 1.00),
(6, 'Medium Size', 0.50),
(6, 'Large Size', 1.00),
(47, 'Medium Size', 0.50),
(47, 'Large Size', 1.00),
(48, 'Medium Size', 0.50),
(48, 'Large Size', 1.00),
(49, 'Medium Size', 0.50),
(49, 'Large Size', 1.00);

-- INSERT Statements for promotions --
INSERT INTO `promotions` (`promo_code`, `description`, `discount_rate`, `start_date`, `end_date`, `conditions`, `points_cost`) VALUES
('ORDER20', '20% off on all products', 0.80, NULL, NULL, 'Applies to all products', NULL),
('BIRTHDAY', '15% birthday discount', 0.85, NULL, NULL, "Valid on customer's birthday", NULL),
('SUMMER', 'Summer special: 10% off on all orders', 0.90, '2024-05-01', '2024-08-31', 'Applies to all ice cream products', NULL);

-- INSERT Statements for promotion_products --
INSERT INTO `promotion_products` (`promo_id`, `product_id`) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), -- COFFEE20 promo applied to all coffee types
(3, 19);  -- SUMMER promo applied to ice creams

-- INSERT Statements for customer_promos --
INSERT INTO `customer_promos` (`customer_id`, `promo_id`, `used_date`) VALUES
(2, 1, '2024-02-14'),
(3, 2, '2024-03-01'),
(5, 3, '2024-05-20'),
(11, 1, '2024-06-13'),
(13, 3, '2024-06-15'),
(17, 1, '2024-06-19'),
(20, 1, '2024-06-20');

-- INSERT Statements for orders --
INSERT INTO `orders` (`customer_id`, `order_time`, `special_requests`, `status`, `pickup_time`, `promo_id`) VALUES
(1, '2024-02-14 10:00:00', 'None', 'Collected', '2024-02-14 12:00:00', NULL),
(2, '2024-02-15 11:00:00', 'Extra napkins', 'Collected', '2024-02-15 13:00:00', 1),
(3, '2024-03-01 09:30:00', 'No onions', 'Collected', '2024-05-05 10:00:00', 2),
(4, '2024-03-10 14:00:00', 'Less ice', 'Ready', '2024-03-10 14:00:00', NULL),
(5, '2024-04-20 16:00:00', 'Birthday decorations', 'Ready', '2024-05-20 17:30:00', 3),
(6, '2024-05-01 08:00:00', 'Call on arrival', 'Pending', '2024-05-01 08:30:00', NULL),
(1, '2024-05-02 12:00:00', 'None', 'Collected', '2024-05-02 12:00:00', NULL),
(3, '2024-05-23 09:30:00', 'None', 'Collected', '2024-05-30 10:00:00', NULL),
(1, '2024-05-20 11:30:00', 'None', 'Collected', '2024-05-22 12:30:00', NULL),
(11, '2024-06-13 08:30:00', 'No onions', 'Pending', '2024-06-13 09:00:00', 1),
(12, '2024-06-14 10:15:00', 'Extra napkins', 'Pending', '2024-06-14 10:45:00', NULL),
(13, '2024-06-15 12:45:00', 'Less ice', 'Pending', '2024-06-15 13:15:00', 3),
(14, '2024-06-16 14:30:00', 'No sugar', 'Pending', '2024-06-16 15:00:00', NULL),
(15, '2024-06-17 09:00:00', 'Add soy milk', 'Pending', '2024-06-17 09:30:00', NULL),
(16, '2024-06-18 11:30:00', 'No dairy', 'Pending', '2024-06-18 12:00:00', NULL),
(17, '2024-06-19 13:00:00', 'Extra ice', 'Pending', '2024-06-19 13:30:00', 1),
(18, '2024-06-19 15:30:00', 'Gluten-free', 'Pending', '2024-06-19 16:00:00', NULL),
(19, '2024-06-20 10:45:00', 'Vegan', 'Pending', '2024-06-20 11:15:00', NULL),
(20, '2024-06-20 12:00:00', 'No peanuts', 'Pending', '2024-06-20 12:30:00', 1);

-- INSERT Statements for order_details --
INSERT INTO `order_details` (`order_id`, `product_id`, `quantity`, `price`) VALUES
(1, 12, 1, 3.50),
(1, 1, 1, 3.75), -- Espresso with almond milk
(1, 2, 1, 4.25), -- Latte with almond milk
(1, 3, 1, 4.00), -- Cappuccino with Vanilla Syrup  
(2, 13, 2, 4.00), 
(2, 4, 1, 3.00), -- Americano
(2, 5, 1, 4.50), -- Mocha with soy milk
(3, 1, 1, 3.00),  -- Espresso
(3, 6, 1, 4.75), -- Iced Coffee with almond milk
(3, 7, 3, 2.00),
(4, 19, 3, 8.00),
(5, 16, 1, 2.50),
(6, 15, 1, 6.00),
(7, 2, 1, 4.25),  -- Latte with almond milk
(8, 1, 1, 3.75), -- Espresso with almond milk
(8, 13, 2, 4.00),
(9, 7, 3, 2.00),
(9, 19, 3, 8.00),
(10, 1, 1, 3.00), -- Espresso
(10, 2, 1, 3.50), -- Latte
(11, 3, 1, 3.50), -- Cappuccino
(11, 4, 1, 3.00), -- Americano
(12, 5, 1, 4.00), -- Mocha
(12, 6, 1, 4.00), -- Iced Coffee
(13, 7, 1, 2.00), -- Pepsi - 330ml
(13, 8, 1, 2.00), -- Coca-Cola - 330ml
(14, 9, 1, 2.00), -- Sprite - 330ml
(14, 10, 1, 2.00), -- V Energy Drink
(15, 11, 1, 2.50), -- Ice Lemon Tea
(15, 12, 1, 3.50), -- Hotdogs
(16, 13, 1, 4.00), -- Sweetcorn & Kumara Patties
(16, 14, 1, 5.00), -- Chocolate Crepes
(17, 15, 1, 6.00), -- BBQ Pulled Pork Bun
(17, 16, 1, 2.50), -- Blueberry Muffins
(18, 17, 1, 8.00), -- Chocolate Cake Slices
(18, 18, 1, 8.00), -- Lemon Cake Slices
(19, 19, 1, 8.00), -- Red Velvet Cake Slices
(19, 20, 1, 8.00); -- Carrot Cake Slices

-- INSERT Statements for order_variations --
INSERT INTO `order_variations` (`order_detail_id`, `variation_id`) VALUES
(2, 2),  -- Espresso with almond milk
(3, 6),  -- Latte with almond milk
(4, 11),  -- Cappuccino with Vanilla Syrup
(7, 17),  -- Mocha with soy milk
(9, 22),  -- Iced Coffee with almond milk
(14, 6), -- Latte with almond milk
(15, 2); -- Espresso with almond milk

-- INSERT Statements for inventory -- 
INSERT INTO `inventory` (`product_id`, `stock_level`, `last_replenishment_date`) VALUES
-- start from 7, cos coffee dont need to track inventory
(7, 100, '2023-12-24'),  -- Pepsi
(8, 100, '2024-04-15'),  -- Coca-Cola
(9, 100, '2023-11-11'),  -- Sprite
(10, 60, '2023-12-21'),  -- V Energy Drink
(11, 60, '2024-04-19'),  -- Ice Lemon Tea
(12, 70, '2024-03-19'),  -- Hotdogs
(13, 70, '2024-01-10'),  -- Sweetcorn & Kumara Patties
(14, 70, '2024-01-20'),  -- Crepes
(15, 70, '2023-12-29'),  -- BBQ Pulled Pork Bun
(16, 70, '2024-01-18'),  -- Muffins
(17, 50, '2024-03-02'),  -- Chocolate Cake Slices
(18, 50, '2024-04-23'),  -- Lemon Cake Slices
(19, 50, '2023-11-11'),  -- Red Velvet Cake Slices
(20, 50, '2024-01-21'),  -- Carrot Cake Slices
(21, 50, '2023-12-23'),  -- Blueberry Cake Slices
(22, 50, '2024-03-23'),  -- Strawberry Ice Blocks
(23, 50, '2023-11-08'),  -- Mango Ice Blocks
(24, 50, '2023-12-13'),  -- Lime Ice Blocks
(25, 50, '2023-11-30'),  -- Pineapple Ice Blocks
(26, 50, '2024-04-01'),  -- Watermelon Ice Blocks
(27, 50, '2024-01-15'),  -- Peach Ice Cream
(28, 50, '2024-04-12'),  -- Chocolate Chip Ice Cream
(29, 50, '2024-03-05'),  -- Pistachio Ice Cream
(30, 50, '2024-01-21'),  -- Mango Ice Cream
(31, 50, '2024-02-19'),  -- Berry Mix Ice Cream
(32, 50, '2023-12-05'),  -- Salted Potato Chips
(33, 50, '2023-11-08'),  -- Barbecue Potato Chips
(34, 50, '2023-11-17'),  -- Sour Cream & Chives Potato Chips
(35, 50, '2023-11-19'),  -- Salt & Vinegar Potato Chips
(36, 50, '2023-11-17'),  -- Jalapeño Potato Chips
(37, 30, '2024-01-19'),  -- Mens Black T-Shirt
(38, 30, '2024-01-19'),  -- Mens White T-Shirt
(39, 30, '2024-01-19'),  -- Mens Logo Black T-Shirt
(40, 30, '2024-01-19'),  -- Womens Black T-Shirt
(41, 30, '2024-01-19'),  -- Womens White T-Shirt
(42, 30, '2024-01-19'),  -- Womens Logo Black T-Shirt
(43, 30, '2024-02-05'),  -- Mood Booster Mug
(44, 50, '2024-03-22'),  -- Insect Repellant
(45, 50, '2024-03-22'),  -- Sunscreen
(46, 40, '2024-01-10'),  -- Travel Adaptor
(55, 40, '2024-01-10'),  -- Classic French Vanilla Crepes
(56, 40, '2024-01-10'),  -- Berry Bliss Crepes
(57, 40, '2024-01-10'),  -- Caramelized Apple Cinnamon Crepes
(61, 9, '2024-04-10'),  -- Pepsi - Bottle
(62, 100, '2024-04-10'),  -- Coca-Cola - Bottle
(63, 100, '2024-04-10');  -- Sprite - Bottle

-- INSERT Statements for reviews --
INSERT INTO `product_reviews` (`customer_id`, `order_id`, `order_detail_id`, `product_id`, `rating`, `feedback`)
VALUES
(1, 1, 1, 13, 5, 'Absolutely loved the Sweetcorn & Kumara Patties, perfect start to my day!'),  -- Sweetcorn & Kumara Patties
(2, 2, 2, 4, 4, 'Americano was great, but I would have liked it a bit hotter.'),  -- Americano
(3, 3, 3, 1, 5, 'Espresso was perfect, loved it!'),  -- Espresso
(4, 4, 4, 15, 5, 'The BBQ Pulled Pork Bun was delicious, the flavors were amazing!'),  -- BBQ Pulled Pork Bun
(5, 5, 5, 16, 4, 'Blueberry Muffins were very fresh, perfect for summer.'),  -- Blueberry Muffins
(6, 6, 6, 18, 5, 'The Lemon Cake Slices were crispy and perfectly sweetened.'),  -- Lemon Cake Slices
(1, 1, 7, 1, 4, 'Espresso with almond milk was good, but I prefer it stronger.'),  -- Espresso
(2, 2, 8, 5, 3, 'Mocha with soy milk was okay, but it tasted a bit flat.'),  -- Mocha
(3, 3, 9, 7, 5, 'Pepsi was refreshing and perfectly chilled.'),  -- Pepsi - 330ml
(4, 4, 10, 22, 4, 'Strawberry Ice Blocks were great, but I would have liked it a bit more tangy.'),  -- Strawberry Ice Blocks
(5, 5, 11, 13, 5, 'Sweetcorn & Kumara Patties were absolutely delightful, full of flavor!'),  -- Sweetcorn & Kumara Patties
(6, 6, 12, 16, 4, 'Blueberry Muffins were moist and had a great flavor.'),  -- Blueberry Muffins
(1, 7, 13, 2, 5, 'Latte with almond milk was fantastic, very creamy and delicious.'),  -- Latte
(3, 8, 14, 1, 4, 'Espresso with almond milk was good, but I prefer my coffee a bit stronger.'),  -- Espresso
(1, 9, 15, 26, 4, 'Watermelon Ice Blocks are incredibly refreshing, loved it!');  -- Watermelon Ice Blocks


-- INSERT Statements for room --
INSERT INTO `room` (`type`, `capacity`, `description`, `price_per_night`, `image`, `amount`) VALUES
('Dorm', 8, 'Spacious dormitory room with 8 beds. Each bunk can be booked individually, suitable for groups or budget travelers looking for a social stay.', 50.00, 'room-1.jpg', 8),
('Twin', 2, 'Comfortable twin room with two beds, ideal for friends or colleagues sharing accommodation.', 200.00, 'room-2.jpg', 1),
('Queen', 3, 'Elegant queen room with a large bed and a pull out sofa, perfect for couples or travelers seeking more comfort.', 300.00, 'room-3.jpg', 1);

-- INSERT Statements for bookings --
INSERT INTO `bookings` (`customer_id`, `room_id`, `number_of_bunks`, `check_in_date`, `check_out_date`, `status`, `price`) VALUES
(3, 2, NULL, '2024-05-09 19:01:13', '2024-05-10 19:01:13', 'Completed', 200),
(1, 2, NULL, '2024-06-23 08:50:07', '2024-06-28 08:50:07', 'Confirmed', 1000),
(1, 2, NULL, '2024-05-21 17:59:52', '2024-05-27 17:59:52', 'Confirmed', 1200),
(1, 2, NULL, '2024-07-01 12:07:47', '2024-07-06 12:07:47', 'Confirmed', 1000),
(5, 3, NULL, '2024-06-19 13:34:03', '2024-06-22 13:34:03', 'Confirmed', 900),
(2, 3, NULL, '2024-06-30 05:22:47', '2024-07-01 05:22:47', 'Confirmed', 300),
(5, 1, 8, '2024-06-25 22:06:35', '2024-06-28 22:06:35', 'Confirmed', 1200),
(4, 1, 8, '2024-06-15 12:43:03', '2024-06-19 12:43:03', 'Confirmed', 1600),
(3, 1, 1, '2024-05-20 03:14:16', '2024-05-21 03:14:16', 'Confirmed', 50),
(6, 1, 2, '2024-06-28 06:26:52', '2024-07-01 06:26:52', 'Cancelled', 300),
(6, 1, 1, '2024-06-24 12:25:45', '2024-06-26 12:25:45', 'Confirmed', 100),
(1, 3, NULL, '2024-08-02 06:16:33', '2024-08-07 06:16:33', 'Confirmed', 1500),
(4, 1, 4, '2024-08-02 11:36:34', '2024-08-03 11:36:34', 'Confirmed', 200),
(2, 1, 4, '2024-05-10 03:02:48', '2024-05-11 03:02:48', 'Completed', 200),
(5, 3, NULL, '2024-05-29 07:06:31', '2024-06-05 07:06:31', 'Confirmed', 2100),
(11, 2, NULL, '2024-06-15', '2024-06-18', 'Confirmed', 600),
(12, 3, NULL, '2024-06-17', '2024-06-19', 'Confirmed', 400),
(13, 1, 2, '2024-06-20', '2024-06-23', 'Confirmed', 600),
(14, 1, 4, '2024-06-28', '2024-07-01', 'Confirmed', 1200),  
(15, 2, NULL, '2024-07-06', '2024-07-09', 'Confirmed', 800), 
(16, 3, NULL, '2024-07-06', '2024-07-10', 'Confirmed', 1000),
(17, 1, 1, '2024-07-10', '2024-07-12', 'Confirmed', 150),
(18, 1, 3, '2024-07-13', '2024-07-16', 'Confirmed', 450),
(19, 2, NULL, '2024-07-17', '2024-07-20', 'Confirmed', 600),
(21, 3, NULL, '2024-07-18', '2024-07-21', 'Confirmed', 600),
-- INSERT Statements for bookings from Feb 2023 to Mar 2024 --
-- 2023-02
(3, 1, 1, '2023-02-10', '2023-02-12', 'Completed', 100),
(5, 2, NULL, '2023-02-15', '2023-02-20', 'Completed', 1000),
-- 2023-03
(4, 3, NULL, '2023-03-05', '2023-03-10', 'Completed', 1500),
(6, 1, 2, '2023-03-12', '2023-03-15', 'Completed', 300),
-- 2023-04
(1, 2, NULL, '2023-04-10', '2023-04-15', 'Completed', 1000),
(2, 3, NULL, '2023-04-20', '2023-04-25', 'Completed', 1500),
-- 2023-05
(3, 1, 1, '2023-05-05', '2023-05-08', 'Completed', 150),
(4, 2, NULL, '2023-05-15', '2023-05-20', 'Completed', 1000),
-- 2023-06
(5, 3, NULL, '2023-06-10', '2023-06-12', 'Completed', 600),
(6, 1, 2, '2023-06-25', '2023-06-28', 'Completed', 600),
-- 2023-07
(1, 1, 4, '2023-07-05', '2023-07-10', 'Completed', 1200),
(2, 2, NULL, '2023-07-15', '2023-07-18', 'Completed', 600),
(3, 3, NULL, '2023-07-25', '2023-07-30', 'Completed', 1500),
(4, 1, 1, '2023-07-12', '2023-07-15', 'Completed', 150),
-- 2023-08
(5, 2, NULL, '2023-08-10', '2023-08-12', 'Completed', 400),
(6, 3, NULL, '2023-08-20', '2023-08-25', 'Completed', 1500),
-- 2023-09
(1, 1, 2, '2023-09-05', '2023-09-10', 'Completed', 300),
(2, 3, NULL, '2023-09-12', '2023-09-15', 'Completed', 900),
(3, 2, NULL, '2023-09-20', '2023-09-22', 'Completed', 400),
(4, 1, 1, '2023-09-25', '2023-09-28', 'Completed', 150),
(5, 3, NULL, '2023-09-10', '2023-09-14', 'Completed', 1200),
-- 2023-10
(6, 2, NULL, '2023-10-05', '2023-10-10', 'Completed', 1000),
(1, 3, NULL, '2023-10-15', '2023-10-20', 'Completed', 1500),
(2, 1, 2, '2023-10-22', '2023-10-25', 'Completed', 300),
-- 2023-11
(3, 1, 4, '2023-11-05', '2023-11-10', 'Completed', 600),
(4, 2, NULL, '2023-11-12', '2023-11-15', 'Completed', 800),
(5, 3, NULL, '2023-11-20', '2023-11-25', 'Completed', 1500),
-- 2023-12
(6, 1, 1, '2023-12-05', '2023-12-07', 'Completed', 100),
(1, 2, NULL, '2023-12-15', '2023-12-20', 'Completed', 1000),
(2, 3, NULL, '2023-12-22', '2023-12-25', 'Completed', 900),
-- 2024-01
(3, 1, 2, '2024-01-05', '2024-01-08', 'Completed', 300),
(4, 2, NULL, '2024-01-15', '2024-01-18', 'Completed', 600),
(5, 3, NULL, '2024-01-20', '2024-01-25', 'Completed', 1500),
-- 2024-02
(6, 1, 4, '2024-02-10', '2024-02-14', 'Completed', 600),
(1, 2, NULL, '2024-02-20', '2024-02-25', 'Completed', 1000),
-- 2024-03
(2, 3, NULL, '2024-03-05', '2024-03-10', 'Completed', 1500),
(3, 1, 2, '2024-03-12', '2024-03-15', 'Completed', 300);

-- INSERT Statements for order_payment --
INSERT INTO `order_payment` (`order_id`, `amount`, `payment_method`, `payment_status`, `payment_date`, `gift_card_id`, `gift_card_amount`) VALUES
(1, 15.50, 'Credit Card', 'Completed', '2024-02-14 10:05:00', NULL, NULL),
(2, 15.50, 'Cash', 'Completed', '2024-02-15 11:05:00', NULL, NULL),
(3, 13.75, 'Debit Card', 'Completed', '2024-03-01 09:35:00', NULL, NULL),
(4, 24.00, 'Credit Card', 'Completed','2024-03-10 14:05:00', NULL, NULL),
(5, 2.50, 'Gift Card', 'Completed', '2024-04-20 16:05:00', 4, 4.00),
(6, 6.00, 'Gift Card', 'Completed', '2024-05-01 08:05:00', 5, 6.00),
(7, 4.25, 'Credit Card', 'Completed', '2024-05-02 12:05:00', NULL, NULL),
(8, 11.75, 'Debit Card', 'Completed', '2024-05-20 11:00:00', NULL, NULL),
(9, 30.00, 'Pay Later', 'Pending', '2024-05-20 11:30:00', NULL, NULL),
(10, 6.50, 'Pay Later', 'Pending', '2024-06-13 08:35:00', NULL, NULL),
(11, 6.50, 'Pay Later', 'Pending', '2024-06-14 10:20:00', NULL, NULL),
(12, 8.00, 'Debit Card', 'Completed', '2024-06-15 12:50:00', NULL, NULL),
(13, 4.00, 'Credit Card', 'Completed', '2024-06-16 14:35:00', NULL, NULL),
(14, 4.00, 'Pay Later', 'Pending', '2024-06-17 09:05:00', NULL, NULL),
(15, 6.00, 'Debit Card', 'Completed', '2024-06-18 11:35:00', NULL, NULL),
(16, 9.00, 'Credit Card', 'Completed', '2024-06-19 13:05:00', NULL, NULL),
(17, 8.50, 'Pay Later', 'Pending', '2024-06-19 15:35:00', NULL, NULL),
(18, 16.00, 'Credit Card', 'Completed', '2024-06-20 10:50:00', NULL, NULL),
(19, 16.00, 'Debit Card', 'Completed', '2024-06-20 12:05:00', NULL, NULL);

-- INSERT Statements for booking_payment --
INSERT INTO `booking_payment` (`booking_id`, `amount`, `payment_method`, `payment_status`, `payment_date`, `gift_card_id`, `gift_card_amount`) VALUES
(1, 200, 'Credit Card', 'Completed', '2024-05-09', NULL, NULL),
(2, 1000, 'Debit Card', 'Completed', '2024-06-23', NULL, NULL),
(3, 1200, 'Credit Card', 'Completed', '2024-05-21', NULL, NULL),
(4, 1000, 'Debit Card', 'Completed', '2024-07-01', NULL, NULL),
(5, 900, 'Credit Card', 'Completed', '2024-06-19', NULL, NULL),
(6, 300, 'Debit Card', 'Completed', '2024-06-30', NULL, NULL),
(7, 1200, 'Credit Card', 'Completed', '2024-06-25', NULL, NULL),
(8, 1600, 'Debit Card', 'Completed', '2024-06-15', NULL, NULL),
(9, 50, 'Credit Card', 'Completed', '2024-05-20', NULL, NULL),
(10, 300, 'Debit Card', 'Refunded', '2024-06-28', NULL, NULL),
(11, 100, 'Credit Card', 'Completed', '2024-06-24', NULL, NULL),
(12, 1500, 'Debit Card', 'Completed', '2024-08-02', NULL, NULL),
(13, 200, 'Credit Card', 'Completed', '2024-08-02', NULL, NULL),
(14, 200, 'Debit Card', 'Completed', '2024-05-10', NULL, NULL),
(15, 2100, 'Credit Card', 'Completed', '2024-05-29', NULL, NULL),
(16, 600, 'Debit Card', 'Completed', '2024-06-08', NULL, NULL),
(17, 400, 'Credit Card', 'Completed', '2024-06-08', NULL, NULL),
(18, 600, 'Debit Card', 'Completed', '2024-06-05', NULL, NULL),
(19, 1200, 'Credit Card', 'Completed', '2024-06-07', NULL, NULL),
(20, 800, 'Debit Card', 'Completed', '2024-06-09', NULL, NULL),
(21, 1000, 'Credit Card', 'Completed', '2024-06-06', NULL, NULL),
(22, 150, 'Debit Card', 'Completed', '2024-06-10', NULL, NULL),
(23, 450, 'Credit Card', 'Completed', '2024-06-11', NULL, NULL),
(24, 600, 'Debit Card', 'Completed', '2024-06-12', NULL, NULL),
(25, 600, 'Credit Card', 'Completed', '2024-06-10', NULL, NULL),
-- INSERT Statements for booking_payment from Feb 2023 to Mar 2024--
(26, 100, 'Credit Card', 'Completed', '2023-02-10', NULL, NULL),
(27, 1000, 'Debit Card', 'Completed', '2023-02-15', NULL, NULL),
(28, 1500, 'Credit Card', 'Completed', '2023-03-05', NULL, NULL),
(29, 300, 'Debit Card', 'Completed', '2023-03-12', NULL, NULL),
(30, 1000, 'Credit Card', 'Completed', '2023-04-10', NULL, NULL),
(31, 1500, 'Debit Card', 'Completed', '2023-04-20', NULL, NULL),
(32, 150, 'Credit Card', 'Completed', '2023-05-05', NULL, NULL),
(33, 1000, 'Debit Card', 'Completed', '2023-05-15', NULL, NULL),
(34, 600, 'Credit Card', 'Completed', '2023-06-10', NULL, NULL),
(35, 600, 'Debit Card', 'Completed', '2023-06-25', NULL, NULL),
(36, 1200, 'Credit Card', 'Completed', '2023-07-05', NULL, NULL),
(37, 600, 'Debit Card', 'Completed', '2023-07-15', NULL, NULL),
(38, 1500, 'Credit Card', 'Completed', '2023-07-25', NULL, NULL),
(39, 150, 'Debit Card', 'Completed', '2023-07-12', NULL, NULL),
(40, 400, 'Credit Card', 'Completed', '2023-08-10', NULL, NULL),
(41, 1500, 'Debit Card', 'Completed', '2023-08-20', NULL, NULL),
(42, 300, 'Credit Card', 'Completed', '2023-09-05', NULL, NULL),
(43, 900, 'Debit Card', 'Completed', '2023-09-12', NULL, NULL),
(44, 400, 'Credit Card', 'Completed', '2023-09-20', NULL, NULL),
(45, 150, 'Debit Card', 'Completed', '2023-09-25', NULL, NULL),
(46, 1200, 'Credit Card', 'Completed', '2023-09-10', NULL, NULL),
(47, 1000, 'Debit Card', 'Completed', '2023-10-05', NULL, NULL),
(48, 1500, 'Credit Card', 'Completed', '2023-10-15', NULL, NULL),
(49, 300, 'Debit Card', 'Completed', '2023-10-22', NULL, NULL),
(50, 600, 'Credit Card', 'Completed', '2023-11-05', NULL, NULL),
(51, 800, 'Debit Card', 'Completed', '2023-11-12', NULL, NULL),
(52, 1500, 'Credit Card', 'Completed', '2023-11-20', NULL, NULL),
(53, 100, 'Debit Card', 'Completed', '2023-12-05', NULL, NULL),
(54, 1000, 'Credit Card', 'Completed', '2023-12-15', NULL, NULL),
(55, 900, 'Debit Card', 'Completed', '2023-12-22', NULL, NULL),
(56, 300, 'Credit Card', 'Completed', '2024-01-05', NULL, NULL),
(57, 600, 'Debit Card', 'Completed', '2024-01-15', NULL, NULL),
(58, 1500, 'Credit Card', 'Completed', '2024-01-20', NULL, NULL),
(59, 600, 'Debit Card', 'Completed', '2024-02-10', NULL, NULL),
(60, 1000, 'Credit Card', 'Completed', '2024-02-20', NULL, NULL),
(61, 1500, 'Debit Card', 'Completed', '2024-03-05', NULL, NULL),
(62, 300, 'Credit Card', 'Completed', '2024-03-12', NULL, NULL);

-- INSERT Statements for loyalty_points --
INSERT INTO `loyalty_points` (`customer_id`, `total_earned`, `total_spent`) VALUES
(1, 4450, 0),  -- John Johnson
(2, 1400, 0),  -- Carol Wilson
(3, 650, 0),   -- David Wilson
(4, 2200, 0),  -- Bob Brown
(5, 4200, 0),  -- John Lee
(6, 3700, 300),-- John Johnson, considering refund
(11, 600, 0),  -- Alice Green
(12, 1000, 0), -- Bob Blue
(13, 150, 0),  -- Charlie Brown
(14, 450, 0),  -- David White
(15, 600, 0),  -- Eve Black
(16, 1000, 0), -- Frank Gray
(17, 400, 0),  -- Grace Pink
(18, 800, 0),  -- Hank Purple
(19, 1500, 0), -- Ivy Yellow
(20, 1500, 0), -- Jack Red
(21, 0, 0),    -- Karen Orange
(22, 0, 0),    -- Leo Cyan
(23, 0, 0),    -- Mia Magenta
(24, 0, 0);    -- Nick Teal

-- Update Statements for loyalty_points --
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 3600 WHERE `customer_id` = 1;  -- John Johnson
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 1800 WHERE `customer_id` = 2;  -- Carol Wilson
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 4000 WHERE `customer_id` = 3;  -- David Wilson
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 2100 WHERE `customer_id` = 4;  -- Bob Brown
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 4500 WHERE `customer_id` = 5;  -- John Lee
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 2900 WHERE `customer_id` = 6;  -- John Johnson
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 2100 WHERE `customer_id` = 11; -- Alice Green
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 1900 WHERE `customer_id` = 12; -- Bob Blue
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 1200 WHERE `customer_id` = 13; -- Charlie Brown
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 1100 WHERE `customer_id` = 14; -- David White
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 1700 WHERE `customer_id` = 15; -- Eve Black
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 2300 WHERE `customer_id` = 16; -- Frank Gray
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 1800 WHERE `customer_id` = 17; -- Grace Pink
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 1800 WHERE `customer_id` = 18; -- Hank Purple
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 2600 WHERE `customer_id` = 19; -- Ivy Yellow
UPDATE `loyalty_points` SET `total_earned` = `total_earned` + 2500 WHERE `customer_id` = 20; -- Jack Red


-- INSERT Statements for points_transactions --
INSERT INTO `points_transactions` (`customer_id`, `points`, `transaction_type`, `description`, `transaction_date`) VALUES
(3, 200, 'Earned', 'Booking Payment', '2024-05-09'),
(1, 1000, 'Earned', 'Booking Payment', '2024-06-23'),
(1, 1200, 'Earned', 'Booking Payment', '2024-05-21'),
(1, 1000, 'Earned', 'Booking Payment', '2024-07-01'),
(5, 900, 'Earned', 'Booking Payment', '2024-06-19'),
(2, 300, 'Earned', 'Booking Payment', '2024-06-30'),
(5, 1200, 'Earned', 'Booking Payment', '2024-06-25'),
(4, 1600, 'Earned', 'Booking Payment', '2024-06-15'),
(3, 50, 'Earned', 'Booking Payment', '2024-05-20'),
(6, 300, 'Earned', 'Booking Payment', '2024-06-28'),
(6, 300, 'Spent', 'Cancelled Booking Refund', '2024-06-28'), -- refund
(6, 100, 'Earned', 'Booking Payment', '2024-06-24'),
(1, 1500, 'Earned', 'Booking Payment', '2024-08-02'),
(4, 200, 'Earned', 'Booking Payment', '2024-08-02'),
(2, 200, 'Earned', 'Booking Payment', '2024-05-10'),
(5, 2100, 'Earned', 'Booking Payment', '2024-05-29'),
(1, 15, 'Earned', 'Order Payment', '2024-02-14 10:05:00'),
(2, 15, 'Earned', 'Order Payment', '2024-02-15 11:05:00'),
(3, 13, 'Earned', 'Order Payment', '2024-03-01 09:35:00'),
(4, 24, 'Earned', 'Order Payment', '2024-03-10 14:05:00'),
(5, 2, 'Earned', 'Order Payment', '2024-04-20 16:05:00'),
(6, 6, 'Earned', 'Order Payment', '2024-05-01 08:05:00'),
(1, 4, 'Earned', 'Order Payment', '2024-05-02 12:05:00'),
(1, 11, 'Earned', 'Order Payment', '2024-05-20 11:00:00'),
(1, 30, 'Earned', 'Order Payment', '2024-05-20 11:30:00'),
-- INSERT Statements for points_transactions from Feb 2023 to Mar 2024 --
(3, 100, 'Earned', 'Booking Payment', '2023-02-10'),
(5, 1000, 'Earned', 'Booking Payment', '2023-02-15'),
(4, 1500, 'Earned', 'Booking Payment', '2023-03-05'),
(6, 300, 'Earned', 'Booking Payment', '2023-03-12'),
(1, 1000, 'Earned', 'Booking Payment', '2023-04-10'),
(2, 1500, 'Earned', 'Booking Payment', '2023-04-20'),
(3, 150, 'Earned', 'Booking Payment', '2023-05-05'),
(4, 1000, 'Earned', 'Booking Payment', '2023-05-15'),
(5, 600, 'Earned', 'Booking Payment', '2023-06-10'),
(6, 600, 'Earned', 'Booking Payment', '2023-06-25'),
(1, 1200, 'Earned', 'Booking Payment', '2023-07-05'),
(2, 600, 'Earned', 'Booking Payment', '2023-07-15'),
(3, 1500, 'Earned', 'Booking Payment', '2023-07-25'),
(4, 150, 'Earned', 'Booking Payment', '2023-07-12'),
(5, 400, 'Earned', 'Booking Payment', '2023-08-10'),
(6, 1500, 'Earned', 'Booking Payment', '2023-08-20'),
(1, 300, 'Earned', 'Booking Payment', '2023-09-05'),
(2, 900, 'Earned', 'Booking Payment', '2023-09-12'),
(3, 400, 'Earned', 'Booking Payment', '2023-09-20'),
(4, 150, 'Earned', 'Booking Payment', '2023-09-25'),
(5, 1200, 'Earned', 'Booking Payment', '2023-09-10'),
(6, 1000, 'Earned', 'Booking Payment', '2023-10-05'),
(1, 1500, 'Earned', 'Booking Payment', '2023-10-15'),
(2, 300, 'Earned', 'Booking Payment', '2023-10-22'),
(3, 600, 'Earned', 'Booking Payment', '2023-11-05'),
(4, 800, 'Earned', 'Booking Payment', '2023-11-12'),
(5, 1500, 'Earned', 'Booking Payment', '2023-11-20'),
(6, 100, 'Earned', 'Booking Payment', '2023-12-05'),
(1, 1000, 'Earned', 'Booking Payment', '2023-12-15'),
(2, 900, 'Earned', 'Booking Payment', '2023-12-22'),
(3, 300, 'Earned', 'Booking Payment', '2024-01-05'),
(4, 600, 'Earned', 'Booking Payment', '2024-01-15'),
(5, 1500, 'Earned', 'Booking Payment', '2024-01-20'),
(6, 600, 'Earned', 'Booking Payment', '2024-02-10'),
(1, 1000, 'Earned', 'Booking Payment', '2024-02-20'),
(2, 1500, 'Earned', 'Booking Payment', '2024-03-05'),
(3, 300, 'Earned', 'Booking Payment', '2024-03-12');

-- INSERT Statements for inquiries --
INSERT INTO `inquiries` (`customer_id`, `inquiry_text`, `timestamp`, `status`) VALUES
(1, 'Hello, can you update my booking details?', '2024-05-09 10:00:00', 'pending'),
(2, 'I need assistance with my last payment.', '2024-05-10 11:00:00', 'pending'),
(3, 'Could you please confirm the cancellation policy?', '2024-05-11 09:00:00', 'responded'),
(4, 'Thank you for your services!', '2024-05-12 12:00:00', 'pending'),
(5, 'Can I get an extra bed in my room?', '2024-05-13 15:00:00', 'responded'),
(6, 'I have a question regarding my loyalty points.', '2024-05-14 16:00:00', 'responded'),
(1, 'Is breakfast included with my stay?', '2024-05-15 08:00:00', 'unread');

-- INSERT Statements for messages --
INSERT INTO `messages` (`sender_id`, `customer_id`, `inquiry_id`, `message_text`, `timestamp`, `status`) VALUES
(8, 3, 3, 'Our cancellation policy allows you to cancel up to 24 hours before your stay without any charges.', '2024-05-11 10:00:00', 'received'),
(10, 5, 5, 'An extra bed has been added to your room as per your request.', '2024-05-13 16:00:00', 'received'),
(8, 6, 6, 'Your loyalty points have been updated. You can now use them for your next booking.', '2024-05-14 17:00:00', 'received');

-- INSERT Statements for news --
INSERT INTO `news` (`title`, `content`, `publish_time`, `manager_id`) VALUES
('Welcome to Our New Website!', 'We are pleased to announce the launch of our newly redesigned website. Explore the new features and improved user experience!', '2024-05-01 09:00:00', 10),
('Summer Special Offers', 'Check out our special summer offers and discounts on room bookings and spa services. Available until August!', '2024-05-10 10:00:00', 10),
('New Loyalty Program', "We have updated our loyalty program to provide you more benefits and flexibility. See what\'s new!", '2024-05-20 08:00:00', 10);

-- INSERT Statements for opening hours --
INSERT INTO `opening_hours` (`days`, `open_time`, `close_time`) VALUES
('Monday-Friday', '07:00', '18:00'),
('Saturday-Sunday', '08:00', '17:00');

-- INSERT Statements for point_exchange_rules --
INSERT INTO `point_exchange_rules` (`points_required`, `gift_card_type_id`, `description`) VALUES 
(2000, 1, 'Exchange 2000 points for a $50 gift card');
