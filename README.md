Web Booking Application

    Tech Stack: Flask, Python, PostgreSQL, SQLAlchemy, Flask-Migrate, HTML, CSS, Bootstrap, JavaScript.
    Hosting: Deployed on Amazon EC2.
    Features:
        Admin interface for managing events, ticket pricing, and bookings.
        Automated email notifications with Flask-Mail, including waiver requests.
        Integrated PayPal API for secure payment processing.
    Architecture:
        Initially a single-page app, refactored into modular blueprints for better scalability and maintainability.
        User authentication and session management with Flask-Login.
        Real-time event scheduling and a user-friendly booking interface.
    Security: Environment-based configuration management using dotenv.
