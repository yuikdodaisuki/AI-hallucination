from pydantic import BaseModel


class Venue(BaseModel):
    """
    Represents the data structure of a Venue.
    """
    year: int
    subject: str
    name: str
    layer: str
    
