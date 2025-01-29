from pydantic import BaseModel


class DeviceData(BaseModel):
    deviceName: str
    image: str
    imei: str
    estPurchaseDate: int
    simLock: bool
    warrantyStatus: str
    repairCoverage: bool
    technicalSupport: bool
    modelDesc: str
    demoUnit: bool
    refurbished: bool
    purchaseCountry: str
    apple_region: str
    fmiOn: bool
    lostMode: bool
    usaBlockStatus: str
    network: str

class ImeiRequest(BaseModel):
    imei: str