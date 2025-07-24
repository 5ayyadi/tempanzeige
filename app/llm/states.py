"""State models for the preference extraction workflow."""

from pydantic import BaseModel
from app.models.preferences import Preference

class PreferenceState(BaseModel):
    user_input: str = ""
    user_id: int = 0
    extracted_data: dict = {}
    preference: Preference | None = None
    message: str = ""
    next_action: str = "start"
    is_complete: bool = False
    needs_location: bool = False
    needs_refinement: bool = False
