import pydantic


class AdBase(pydantic.BaseModel):
    title: str
    description: str
    owner: str


class CreateAd(AdBase):
    title: str
    description: str
    owner: str


class UpdateAd(AdBase):
    title: str | None = None
    description: str | None = None
    owner: str | None = None
