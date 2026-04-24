from pydantic import BaseModel, UUID4
from typing import Annotated
from decimal import Decimal
from pydantic import condecimal


class TicketCreateRequest(BaseModel):
    event_id: UUID4
    city_id: UUID4
    price: Annotated[Decimal, condecimal(gt=0, decimal_places=2)]
    original_price: Annotated[Decimal, condecimal(gt=0, decimal_places=2)]
