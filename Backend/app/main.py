from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.jobs.auto_confirm import lifespan
from app.routes import health, users, cities, events, tickets, orders, confirmations

app = FastAPI(title="TicketVault API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(cities.router)
app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(orders.router)
app.include_router(confirmations.router)
