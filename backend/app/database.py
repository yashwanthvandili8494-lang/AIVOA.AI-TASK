import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./interactions.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class HCPProfile(Base):
    __tablename__ = "hcp_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    specialty = Column(String(100))
    clinic = Column(String(200))
    historical_sentiment = Column(String(50))
    email = Column(String(100))

class MarketingMaterial(Base):
    __tablename__ = "marketing_materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    category = Column(String(50))
    url = Column(String(250))

class HCPInteraction(Base):
    __tablename__ = "hcp_interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(100), nullable=True)
    interaction_type = Column(String(50), nullable=True)
    date = Column(String(50), nullable=True)
    time = Column(String(50), nullable=True)
    attendees = Column(String(200), nullable=True)
    topics_discussed = Column(Text, nullable=True)
    materials_shared = Column(Text, nullable=True) # JSON list serialized as string
    samples_distributed = Column(Text, nullable=True) # JSON list serialized as string
    sentiment = Column(String(50), nullable=True)
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)

class FollowUpTask(Base):
    __tablename__ = "follow_up_tasks"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(100))
    description = Column(Text)
    due_date = Column(String(50))
    status = Column(String(50), default="Pending")

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if we already have HCP profiles seeded
        if db.query(HCPProfile).count() == 0:
            profiles = [
                HCPProfile(name="Dr. John Doe", specialty="Cardiologist", clinic="Heart & Vascular Center", historical_sentiment="Positive", email="j.doe@heartcenter.com"),
                HCPProfile(name="Dr. Sarah Jenkins", specialty="Oncologist", clinic="City Cancer Institute", historical_sentiment="Neutral", email="s.jenkins@citycancer.org"),
                HCPProfile(name="Dr. Robert Adams", specialty="Neurologist", clinic="Neurological Clinic", historical_sentiment="Neutral", email="r.adams@neurology.net"),
                HCPProfile(name="Dr. Emily Taylor", specialty="Pediatrician", clinic="Children's Health Hospital", historical_sentiment="Positive", email="e.taylor@childrens.com")
            ]
            db.add_all(profiles)
            
        # Check if we already have marketing materials seeded
        if db.query(MarketingMaterial).count() == 0:
            materials = [
                MarketingMaterial(name="Product Brochure", category="Brochure", url="https://example.com/materials/product-brochure.pdf"),
                MarketingMaterial(name="Clinical Study", category="Clinical Study", url="https://example.com/materials/phase3-study.pdf"),
                MarketingMaterial(name="Prescribing Info", category="Prescribing Information", url="https://example.com/materials/prescribing-info.pdf")
            ]
            db.add_all(materials)
            
        db.commit()
    finally:
        db.close()
