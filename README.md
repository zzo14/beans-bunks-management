# Bruce Bay Beans & Bunks Management System

Welcome to the Bruce Bay Beans & Bunks Management System! This Flask-based web application is designed to streamline the management of our cafe and accommodation business. It provides a user-friendly interface for customers to order food and drinks, book rooms, and interact with our staff. For our team, it offers robust tools for managing inventory, promotions, bookings, and generating insightful reports.

## Showcase
Check out our live demo here: [live demo](http://groupwp2.pythonanywhere.com/)

## Requirements
 - Python 3.12
 - Flask
 - MySQL
 - Javascript
 - Other dependencies listed in requirements.txt

## Features
 - **User Authentication**: Secure login and registration for customers, staff, and managers, with role-based access control.
 - **Online Ordering**: Customers can browse the menu, customize their orders, and securely checkout using various payment methods, including gift cards.
 - **Accommodation Booking**: An easy-to-use booking system for our various room types, with a calendar view for managers to oversee availability.
 - **Gift Cards and Loyalty Program**: Customers can purchase and redeem gift cards, and earn loyalty points for discounts and rewards.
 - **Promotions Management**: Managers can create and manage promotional offers to attract and retain customers.
 - **Inventory Management**: Staff can easily track and update stock levels for food, drinks, and merchandise.
 - **Customer Communication**: Customers can submit inquiries and receive messages from staff, fostering excellent customer service.
 - **News and Announcements**: Managers can publish news and updates to keep customers and staff informed.
 - **Comprehensive Reporting**: Managers have access to detailed reports on sales, finances, product popularity, and more.

## Installation and Setup
 - Clone the repository: `git clone https://github.com/LUMasterOfAppliedComputing2024S1/COMP639S1_Project_2_Group_W.git`
 - Install the required packages: `pip install -r requirements.txt`
 - Set up the database using the provided MySQL scripts.
 - Change `dbuser` and `dbpass` in `app/connect.py` to your MySQL username and password.
 - Run the application: `flask run`

## Login Information (for testing)
The application includes a login system with separate dashboards for three user roles: Customer, Staff, and Manager.

### Member
 - Username: user1
 - Password: 123456Zzz!

### Therapist
 - Username: staff1
 - Password: 123456Zzz!

### Manager
 - Username: admin
 - Password: 123456Zzz!

## Acknowledgements
Thanks to the team members who contributed to this project:
 - Menglin Chen
 - Letitia Sie
 - Loo See Yin
 - Ren Wang
 - Patrick Zou

