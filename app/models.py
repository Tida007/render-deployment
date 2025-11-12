"""SQLAlchemy models for database tables"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class PollingUnit(Base):
    """Polling Unit model"""
    __tablename__ = "polling_unit"
    
    uniqueid = Column(Integer, primary_key=True, index=True)
    polling_unit_id = Column(Integer)
    ward_id = Column(Integer)
    lga_id = Column(Integer)
    uniquewardid = Column(Integer, nullable=True)
    polling_unit_number = Column(String(50), nullable=True)
    polling_unit_name = Column(String(50), nullable=True)
    polling_unit_description = Column(Text, nullable=True)
    lat = Column(String(255), nullable=True)
    long = Column(String(255), nullable=True)
    entered_by_user = Column(String(50), nullable=True)
    date_entered = Column(DateTime, nullable=True)
    user_ip_address = Column(String(50), nullable=True)


class LGA(Base):
    """Local Government Area model"""
    __tablename__ = "lga"
    
    uniqueid = Column(Integer, primary_key=True, index=True)
    lga_id = Column(Integer)
    lga_name = Column(String(50))
    state_id = Column(Integer)
    lga_description = Column(Text, nullable=True)
    entered_by_user = Column(String(50), nullable=True)
    date_entered = Column(DateTime, nullable=True)
    user_ip_address = Column(String(50), nullable=True)


class Party(Base):
    """Political Party model"""
    __tablename__ = "party"
    
    id = Column(Integer, primary_key=True, index=True)
    partyid = Column(String(11))
    partyname = Column(String(11))


class AnnouncedPUResult(Base):
    """Announced Polling Unit Results model"""
    __tablename__ = "announced_pu_results"
    
    result_id = Column(Integer, primary_key=True, index=True)
    polling_unit_uniqueid = Column(String(50))
    party_abbreviation = Column(String(11))
    party_score = Column(Integer)
    entered_by_user = Column(String(50), nullable=True)
    date_entered = Column(DateTime, nullable=True)
    user_ip_address = Column(String(50), nullable=True)


class Ward(Base):
    """Ward model"""
    __tablename__ = "ward"
    
    uniqueid = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer)
    ward_name = Column(String(50))
    lga_id = Column(Integer)
    ward_description = Column(Text, nullable=True)
    entered_by_user = Column(String(50), nullable=True)
    date_entered = Column(DateTime, nullable=True)
    user_ip_address = Column(String(50), nullable=True)

