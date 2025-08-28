from pydantic import BaseModel, Field

class BarcodeRead(BaseModel):
    serial_number: str | None = Field(
        None, description="The exact serial number decoded from the barcode/QR."
    )
