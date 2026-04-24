from pydantic import BaseModel, UUID4


class InitiateBuyRequest(BaseModel):
    ticket_id: UUID4


class ConfirmPaymentRequest(BaseModel):
    order_id: UUID4
    payment_intent_id: str
