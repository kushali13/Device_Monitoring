# Project Concepts – School Monitoring System

## Overview
This is a Django-based system for monitoring computer lab assets in schools across various districts. It helps track devices, their status, and school-level information in one place.

---

## Core Objects and Context

### 1. School
- Context: Basic school info and location.
- Important Info:
  - DISE code, school name
  - Village, block, district
  - Principal name, phone, pincode

### 2. Asset
- Context: Devices like PCs and their parts.
- Important Info:
  - Serial number
  - Linked school (by DISE code)
  - Hardware items: TFT, headphones, webcam
  - Status (active/inactive), install date

### 3. RegistrationInfo
- Context: Setup when school is added.
- Important Info:
  - School name, city, total PCs

---

## Main Features and Concepts

### 4. Monitoring
- Shows device status (active/inactive)
- Auto-refresh every 10 mins
- Filters by district or school

### 5. Reports
- PDF and CSV reports of usage
- Device timing and activity info
- Uses ReportLab for PDF

### 6. Dashboard
- Charts using ApexCharts
- Pie & bar charts for device stats

### 7. Admin Interface
- Uses Django Admin + AdminLTE theme
- Responsive design with Bootstrap

### 8. User Authentication
- Login/logout system
- Role-based access
- CSRF and input validation

### 9. Data Models
- Django models with foreign key (Asset → School)
- SQLite as default DB

---

## Extra Concepts

### 10. Map Visualization
- District-wise map (SVG based)
- Click to view schools and devices

### 11. Session & File Handling
- Session for temporary data
- Static/media files for uploads

### 12. Deployment (Basic)
- Uses Django’s WSGI
- Local or cloud hosting (e.g., PythonAnywhere)

---

## User Experience

- Simple navigation with clear menus
- Quick search for schools or assets
- Mobile-friendly admin pages
- Error messages are direct and easy to understand
- Most actions need only a few clicks

## Maintenance & Support

- Regular database backups recommended
- Admins can add or update school/device info anytime
- Log files help track issues or failed logins
- Static files (like images) should be optimized for faster loading

## Security Practices

- Passwords are hashed and never stored in plain text
- Only authorized users can access admin features
- All forms use CSRF protection by default
- User sessions expire after inactivity

## Typical Workflow

1. Admin logs in
2. Adds a new school or updates info
3. Registers new devices/assets
4. Monitors device status on dashboard
5. Downloads reports as needed

## Future Improvements (Ideas)

- SMS/email alerts for device issues
- More detailed user roles (e.g., district admin)
- Integration with external asset management tools
- Real-time device health monitoring
- Multi-language support for wider reach

---

## Summary
The system is simple to use and helps manage devices in schools efficiently. It’s built with Django, has a clean admin UI, and supports useful analytics and reporting for better monitoring.

