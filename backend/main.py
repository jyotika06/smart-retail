
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security.api_key import APIKeyHeader, APIKey
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Campaign
from pydantic import BaseModel
from datetime import date
import qrcode
import os
import secrets

API_KEY = "sk_myfixedapikey123"

from fastapi.responses import JSONResponse
from fastapi.requests import Request as FastAPIRequest

app = FastAPI()

# Custom error handler for 500 Internal Server Error
@app.exception_handler(Exception)
async def internal_exception_handler(request: FastAPIRequest, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI APIKey security scheme for Swagger UI
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key_header: str = Depends(api_key_header)) -> str:
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )


# Pydantic model for Campaign creation
class CampaignCreate(BaseModel):
    Name: str
    Description: str = None
    StartDate: date = None
    EndDate: date = None
    DiscountType: str = None
    DiscountValue: float = None
    Status: str = None

# CRUD Endpoints for Campaigns
@app.post("/campaigns")
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    new_campaign = Campaign(**campaign.dict())
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign

@app.get("/campaigns")
def read_campaigns(db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    return db.query(Campaign).all()

@app.get("/campaigns/{campaign_id}")
def read_campaign(campaign_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    campaign = db.query(Campaign).filter(Campaign.CampaignID == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@app.put("/campaigns/{campaign_id}")
def update_campaign(campaign_id: int, campaign: CampaignCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_campaign = db.query(Campaign).filter(Campaign.CampaignID == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for key, value in campaign.dict().items():
        setattr(db_campaign, key, value)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@app.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_campaign = db.query(Campaign).filter(Campaign.CampaignID == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(db_campaign)
    db.commit()
    return {"detail": "Deleted"}

# Publish Campaign Endpoint
@app.post("/publishCampaign/{campaign_id}")
def publish_campaign(campaign_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    campaign = db.query(Campaign).filter(Campaign.CampaignID == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.Status = "Live"
    db.commit()
    db.refresh(campaign)
    public_url = f"https://mockcampaigns.com/campaign/{campaign_id}"
    # Generate QR code
    qr_img = qrcode.make(public_url)
    qr_path = f"qr_{campaign_id}.png"
    qr_img.save(qr_path)
    return {"public_url": public_url, "qr_code_path": qr_path}

@app.get("/qr/{campaign_id}")
def get_qr_code(campaign_id: int, api_key: APIKey = Depends(get_api_key)):
    qr_path = f"qr_{campaign_id}.png"
    if not os.path.exists(qr_path):
        raise HTTPException(status_code=404, detail="QR code not found")
    return FileResponse(qr_path, media_type="image/png")
