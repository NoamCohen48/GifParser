from attrs import define


@define
class ApplicationExtension:
    application_name: str | None = None
    identify: str | None = None
    data: bytes | None = None
