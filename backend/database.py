"""
database.py — SQLAlchemy models + SQLite setup for Prompt2Plan
Tables: projects, architectures, tasks, milestones
Auto-creates the SQLite file on first run.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

DATABASE_URL = "sqlite:///prompt2plan.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    idea_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    architecture = relationship("Architecture", back_populates="project", uselist=False, cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")


class Architecture(Base):
    __tablename__ = "architectures"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    json_data = Column(Text, nullable=False)  # Stores the full architecture JSON as a string

    project = relationship("Project", back_populates="architecture")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(500), nullable=False)
    component = Column(String(200), nullable=True)
    phase = Column(String(100), nullable=False, default="Setup")
    estimated_hours = Column(Float, nullable=False, default=4.0)
    actual_hours = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, default="todo")  # todo, in_progress, done

    project = relationship("Project", back_populates="tasks")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    phase_name = Column(String(100), nullable=False)
    start_day = Column(Integer, nullable=False, default=0)
    end_day = Column(Integer, nullable=False, default=1)
    total_hours = Column(Float, nullable=False, default=0.0)
    optimistic_hours = Column(Float, nullable=True, default=0.0)
    pessimistic_hours = Column(Float, nullable=True, default=0.0)

    project = relationship("Project", back_populates="milestones")


def init_db():
    """Create all tables if they don't exist and run auto-migrations for new columns."""
    Base.metadata.create_all(bind=engine)
    
    # Auto-migrate sqlite columns if database pre-existed
    with engine.connect() as conn:
        from sqlalchemy import text
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN actual_hours FLOAT"))
            conn.commit()
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE milestones ADD COLUMN optimistic_hours FLOAT"))
            conn.commit()
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE milestones ADD COLUMN pessimistic_hours FLOAT"))
            conn.commit()
        except Exception:
            pass


def get_db():
    """FastAPI dependency — yields a DB session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
