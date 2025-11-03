# Event Sales Application

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL, SQLAlchemy, Flask-Migrate
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Payment Integration**: PayPal API
- **Email Notifications**: Flask-Mail
- **Containerization**: Docker
- **Hosting**: Deployed on AWS Lightsail with Cloudflare CDN

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

### Production Deployment

The application is deployed to AWS Lightsail with Cloudflare CDN integration using automated Docker deployment.

## Cloud Solution Justification (A1)

## Cloud Solution Justification (A1)

AWS Lightsail with Cloudflare was selected as the cloud solution provider for this deployment because it provides simplified infrastructure management with predictable pricing and integrated tooling.

Lightsail offers fixed monthly instance pricing (the 2GB RAM plan is approximately $11 per month), which is more cost-effective than deploying an equivalent configuration on EC2 for this workload (AWS, 2024). Lightsail also provides pre-configured SSH access, enabling immediate secure administration without requiring additional OS user configuration or VPC-level networking setup.

Lightsail includes automated 7-day snapshot retention, which supports reliable point-in-time recovery without manual backup scripting. Instance sizing can be upgraded vertically in a few clicks, allowing the system to scale compute resources as traffic increases (AWS, 2024). This aligns well with the expected workload growth of this application.

Containerized deployment is supported by Docker, allowing the Flask web application to be deployed consistently across environments. Reliability requirements are met through Lightsail’s high-availability VM infrastructure, and security is enhanced by placing Cloudflare in front of the Lightsail public endpoint for DDoS mitigation, HTTPS termination, and global edge caching. Cloudflare’s CDN also improves performance for geographically distributed users through reduced latency (Cloudflare, 2024).




## Container Images Implementation (A2)

The application implements a multi-container Docker architecture:

**Application Container**:
- Built from `python:3.10-slim` base image
- Contains Flask web application with all dependencies
- Exposes port 5000 for web traffic
- Uses Gunicorn WSGI server in production for handling concurrent requests

**Database Container**:
- Uses official `postgres:13` image for data persistence
- Configured with environment variables from `.env.production`
- Persistent volume storage for data retention across deployments

**Container Orchestration**:
- **Development**: `docker-compose.dev.yml` with Flask development server
- **Production**: `docker-compose.cloudflare.yml` with Gunicorn and multiple workers
- Automated deployment via `deploy.sh` script with health checks

**Networking**:
- Internal Docker network for container communication
- Only web container exposes ports to host system
- Database isolated from direct internet access for security

## References

Amazon Web Services. (2024). *AWS Lightsail Documentation*. Amazon Web Services, Inc. https://docs.aws.amazon.com/lightsail/

Cloudflare, Inc. (2024). *Cloudflare Developer Documentation*. https://developers.cloudflare.com/

Docker, Inc. (2024). *Docker Documentation: Get Started Guide*. https://docs.docker.com/get-started/

Flask Development Team. (2024). *Flask Documentation*. Pallets Projects. https://flask.palletsprojects.com/

PostgreSQL Global Development Group. (2024). *PostgreSQL 13 Documentation*. https://www.postgresql.org/docs/13/

Gunicorn Development Team. (2024). *Gunicorn Documentation*. https://docs.gunicorn.org/
