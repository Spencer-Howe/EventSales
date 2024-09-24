# Event Sales Application

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL, SQLAlchemy, Flask-Migrate
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Payment Integration**: PayPal API
- **Email Notifications**: Flask-Mail
- **Containerization**: Docker
- **Hosting**: Deployed on Amazon EC2

## Features

- **Admin Interface**: Manage events, set ticket pricing, and oversee bookings.
- **Email Notifications**: Automated emails, including waiver requests, are handled via Flask-Mail.
- **PayPal Integration**: Secure payment processing using PayPal API.
- **Real-time Event Scheduling**: Allows users to book events and admin to manage upcoming events.
- **Private Event Management**: Easily hide private events from the front end for exclusive URLs.

## Architecture

- The application uses **Flask Blueprints** for scalability and maintainability.
- **User Authentication** and session management with Flask-Login.
- Environment-based configuration management using `.env.local` and `.env.production`.
- Fully Dockerized for seamless switching between development and production environments.

## Deployment & Docker Configuration

The application is containerized using Docker, making it easy to manage different environments (local development and production).

### Local Development

To run the project locally:

```bash
docker-compose -f docker-compose.dev.yml up --build
```
