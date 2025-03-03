Вот подробный `README.md` на английском языке для проекта **Mnemozer**, включающий описание структуры, используемых библиотек и инструкцию по развертыванию в Docker.  

---

# Mnemozer - Telegram Reminder Bot

## Project Description
**Mnemozer** is an electronic assistant system that allows users to set reminders for upcoming events via Telegram. Users can create notes and reminders, which the bot will send at the specified time. The project is built using **Python** and **Django**, with support for **PostgreSQL**, **Celery**, and **RabbitMQ** for task scheduling.

## Project Structure
The project is structured as follows:

```
mnemozer-telegram-bot/
│── mnemozer/
│   │── captain_bot/
│   │   │── management/
│   │   │── __init__.py
│   │   │── app.ini.example
│   │   │── bot.py
│   │   │── celery.py
│   │   │── config.py
│   │   │── date_parser.py
│   │   │── dbworker.py
│   │   │── flow_statuses.py
│   │   │── init.py
│   │   │── jobs.py
│   │   │── tasks.py
│   │   │── user.py
│   │   │── utils.py
│   │── captain_bot_control/
│   │   │── migrations/
│   │   │── __init__.py
│   │   │── admin.py
│   │   │── apps.py
│   │   │── models.py
│   │   │── tests.py
│   │   │── views.py
│   │── mnemozer/
│   │   │── __init__.py
│   │   │── settings.py
│   │   │── urls.py
│   │   │── asgi.py
│   │   │── wsgi.py
│   │── .dockerignore
│   │── .env.example
│   │── docker-compose.yml
│   │── Dockerfile
│   │── Makefile
│   │── manage.py
│   │── requirements.txt
```

### Main Components:
- **`captain_bot/`**: Contains the main logic for the Telegram bot.
  - `bot.py`: Handles interactions with Telegram.
  - `celery.py`: Configures Celery for background task execution.
  - `jobs.py`: Uses APScheduler to schedule and execute reminders.
  - `tasks.py`: Defines Celery tasks for managing bot messages and cleaning old notifications.
  - `user.py`: Manages user-related functions.
  - `utils.py`: Utility functions for various bot-related operations.
  
- **`captain_bot_control/`**: Contains Django models and migrations.
  - `models.py`: Defines database models for reminders and messages.
  - `views.py`: Django views for handling web requests.
  - `admin.py`: Admin interface configuration.
  - `migrations/`: Contains database migration files.

- **`mnemozer/`**: Core Django project settings and configurations.
  - `settings.py`: Configures Django settings, database, and Celery.
  - `urls.py`: Defines URL routing for the web interface.
  - `asgi.py` and `wsgi.py`: ASGI/WSGI entry points for running the application.

- **Configuration and Deployment Files:**
  - `.env.example`: Sample environment variables.
  - `docker-compose.yml`: Docker setup for running the app with PostgreSQL and RabbitMQ.
  - `Dockerfile`: Defines how to build the Docker image.
  - `Makefile`: Contains useful commands for development.
  - `requirements.txt`: Lists required Python dependencies.
  - `manage.py`: Django management script.

---

## Technologies Used
- **Backend**: Python, Django
- **Database**: PostgreSQL
- **Messaging & Tasks**: Celery, RabbitMQ, APScheduler
- **Telegram Bot**: Pyrogram, Telebot API
- **Cache & State Management**: Vedis
- **Containerization**: Docker, Docker Compose

---

## Installation and Setup

### 1. Clone the Repository
```sh
git clone https://github.com/axshaman/mnemozer.git
cd mnemozer-telegram-bot
```

### 2. Create a Telegram Bot
1. Go to [My Telegram](https://my.telegram.org/)
2. Register a new application to get `api_id` and `api_hash`
3. Use [@BotFather](https://t.me/BotFather) to create a new bot and get the `bot_token`

### 3. Configure the Application
Create a configuration file `app.ini` in `mnemozer/captain_bot/`:

```ini
[api]
api_id = yourAppIDFromTelegramAPP
api_hash = yourAppHashFromTelegramAPP
bot_token = YourBotTokenFromBotFather
```

Create a `.env` file based on `.env.example`:

```sh
cp .env.example .env
```

Edit `.env` with your values:

```sh
DEBUG=True
DJANGO_SECRET_KEY='your-django-secret-key'
DB_PORT='5432'
DB_HOST='db'
```

### 4. Install Dependencies
```sh
pip install -r requirements.txt
```

### 5. Run Database Migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the Application
Start the bot and web server:

```sh
python manage.py run_bot
python manage.py runserver
```

---

## Running with Docker
The project includes a `Dockerfile` and `docker-compose.yml` for containerized deployment.

### 1. Build and Start the Containers
```sh
docker-compose up --build -d
```

### 2. Check Running Containers
```sh
docker ps
```

### 3. Stopping and Removing Containers
```sh
docker-compose down
```

#### **Docker Components**
- **PostgreSQL Database**
- **Django Web Application**
- **Celery Worker**
- **RabbitMQ for Message Queueing**

**`docker-compose.yml`** (from the project) defines the services:

```yaml
version: "3.9"

services:
  db:
    image: postgres
    volumes:
      - ./data/db:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - ${DB_PORT_IN_DOCKER}

  web:
    build: .
    command: python manage.py runserver ${RUN_PORT_IN_DOCKER}
    volumes:
      - .:/code
    ports:
      - ${APP_PORT_IN_DOCKER}
    depends_on:
      - db

  celery_worker:
    build: .
    command: celery -A captain_bot worker -B -l INFO
    volumes:
      - .:/code/
    links:
      - db
      - rabbit

  rabbit:
    image: rabbitmq:3-management-alpine
    volumes:
      - ./docker/volumes/rabbit:/var/lib/rabbitmq
```

---

## Usage

### Available Commands in the Telegram Bot:
- `/start` – Start the bot
- `/new_note` – Create a new reminder
- `/help` – Display help information

### Date Input Formats:
1. `YYYY:MM:DD:HH:MM` (Full date and time)
2. `HH:MM` (Reminds at the next occurrence of this time)
3. `HH:MM:DayOfWeek` (Reminds on a specific day of the week)

The bot validates incorrect input and prevents setting reminders for past dates.

---

## Contribution
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch`
3. Make changes and commit: `git commit -m "Your changes"`
4. Push the branch: `git push origin feature-branch`
5. Create a Pull Request.

---

## License
This project is licensed under the MIT License.