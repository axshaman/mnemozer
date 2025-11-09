# Mnemozer – Telegram Reminder Bot & API

Mnemozer is a Telegram assistant that helps users capture notes and schedule
reminders. It combines an interactive bot flow with a background scheduler and a
fresh REST API so that reminders can be managed programmatically as well.

## Key Features

- **Telegram bot** powered by `pyTelegramBotAPI` that guides users through note
  taking and reminder creation flows.
- **APScheduler** backed scheduler that triggers reminders and optionally moves
  them into the note history once delivered.
- **Celery & RabbitMQ** integration for background clean-up tasks.
- **New REST API** for listing, creating, updating and deleting reminders,
  including a JSON OpenAPI description (`docs/openapi.yaml`).
- **C4 architecture model** and updated documentation under `docs/` for quick
  onboarding.

## Project Structure

```
mnemozer/
├── captain_bot/              # Telegram bot logic, date parsing and scheduler hooks
├── captain_bot_control/      # Django models, migrations and REST API module
├── docs/                     # API specification and architecture diagrams
├── mnemozer/                 # Django project configuration
├── requirements.txt          # Python dependencies (Django 3.2 LTS + updates)
└── manage.py
```

## Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/axshaman/mnemozer.git
cd mnemozer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and adjust values as needed:

```bash
cp .env.example .env
```

- By default the project uses SQLite which works well for local development.
  Provide `DB_ENGINE=django.db.backends.postgresql_psycopg2` and related
  credentials to switch to PostgreSQL.
- `CELERY_BROKER_URL` should point at your RabbitMQ instance. The default value
  matches the provided Docker compose file.

### 3. Run Database Migrations

```bash
python manage.py migrate
```

### 4. Start Services

```bash
# Start the scheduler-backed bot (requires valid Telegram credentials)
python manage.py run_bot

# Launch the Django development server
python manage.py runserver
```

Alternatively, use Docker Compose to boot the complete stack (web, worker,
PostgreSQL and RabbitMQ):

```bash
docker-compose up --build -d
```

The Makefile contains shortcuts for installing dependencies and running common
operations:

```bash
make dependencies
make migrations
make run
```

## REST API

A lightweight REST API exposes reminder and note data to external systems. The
API lives under `/api/v1` and is backed by the same models used by the bot.

### Example – Create a Reminder

```bash
curl -X POST http://localhost:8000/api/v1/users/1234/reminders/ \
  -H "Content-Type: application/json" \
  -d '{
        "text": "Prepare release notes",
        "remind_at": "2024-08-01T09:00:00Z",
        "preserve_after_trigger": true
      }'
```

### Example – Mark a Reminder as Completed

```bash
curl -X PATCH http://localhost:8000/api/v1/users/1234/reminders/1/ \
  -H "Content-Type: application/json" \
  -d '{"is_completed": true}'
```

Refer to the OpenAPI specification for the full contract:

- [`docs/openapi.yaml`](docs/openapi.yaml)

## Architecture Documentation

The `docs/architecture` folder contains a Markdown overview and PlantUML source
(`c4-model.puml`) describing the system with the C4 model. You can render the
PlantUML diagrams locally or through an IDE plugin to better understand the
system boundaries and component interactions.

## Testing

Run the Django test suite to validate the REST API and core behaviour:

```bash
python manage.py test
```

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-improvement`.
3. Commit your changes with clear messages.
4. Run the tests.
5. Open a Pull Request describing the change.

## License

This project is licensed under the MIT License.
