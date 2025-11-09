# Mnemozer C4 Model

This document summarises the Mnemozer architecture using the C4 model. The
system helps Telegram users create reminders and notes while providing an HTTP
API for integrations.

## Context Diagram

```plantuml
@startuml C4Context
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(user, "Telegram User", "Creates notes and reminders through the bot")
System_Boundary(mnemozer, "Mnemozer") {
  System_Ext(messaging, "Telegram Platform", "Delivers bot updates and reminders")
  System(api, "Mnemozer HTTP API", "REST endpoints for reminders and notes")
  System(bot, "Captain Bot", "Conversational interface that parses user input")
  SystemDb(db, "PostgreSQL / SQLite", "Stores reminders, notes and bot metadata")
  System_Ext(queue, "RabbitMQ", "Broker for Celery tasks")
  System_Ext(worker, "Celery Worker", "Asynchronous job processing")
}

Rel(user, bot, "Chats with", "Telegram messages")
Rel(bot, messaging, "Receives updates", "Webhooks")
Rel(bot, db, "Reads & writes", "Django ORM")
Rel(bot, worker, "Dispatches background jobs")
Rel(worker, queue, "Consumes tasks")
Rel(bot, queue, "Queues tasks")
Rel(api, db, "Reads & writes", "Django ORM")
Rel(api, user, "Provides REST access", "HTTPS")
@enduml
```

## Container Diagram

```plantuml
@startuml C4Container
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(user, "Telegram User")
System_Ext(integration, "External Integration", "Calls the REST API")
System_Boundary(mnemozer, "Mnemozer") {
  Container(web, "Django Web App", "Python", "Hosts the Telegram webhook and REST API")
  Container(bot, "Captain Bot", "Python", "Handles dialog flows and scheduling")
  ContainerDb(db, "Relational Database", "PostgreSQL / SQLite", "Reminder and note storage")
  Container(worker, "Celery Worker", "Python", "Executes background jobs")
  Container(queue, "RabbitMQ", "Message Broker", "Queues Celery tasks")
  Container(scheduler, "APScheduler", "Python", "Schedules reminder triggers")
}

Rel(user, bot, "Creates reminders")
Rel(bot, scheduler, "Registers reminder jobs")
Rel(scheduler, bot, "Triggers reminder execution")
Rel(bot, db, "CRUD operations")
Rel(web, db, "CRUD operations")
Rel(web, integration, "Provides REST API")
Rel(bot, worker, "Dispatches long running work")
Rel(worker, queue, "Consumes tasks")
Rel(bot, queue, "Publishes tasks")
@enduml
```

## Component Diagram (Django Web App)

```plantuml
@startuml C4Component
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

Container(web, "Django Web App", "Python")
ContainerDb(db, "Database", "PostgreSQL / SQLite")
Component(api, "REST API Layer", "captain_bot_control.api")
Component(bot_webhook, "Telegram Webhook", "mnemozer.urls.webhook_receiver")
Component(models, "ORM Models", "captain_bot_control.models")
Component(scheduler, "Scheduler Integration", "captain_bot.jobs")

Rel(api, models, "Uses")
Rel(api, scheduler, "Schedules reminder jobs")
Rel(bot_webhook, models, "Reads/Writes user data")
Rel(bot_webhook, scheduler, "Schedules reminder jobs")
Rel(models, db, "Persists", "Django ORM")
@enduml
```

> Tip: render the diagrams locally with PlantUML (`plantuml docs/architecture/c4-model.puml`) or
> directly from the Markdown blocks using an editor extension.
