from fastapi import FastAPI
from app.controller.recipe_controller import recipe_router
from app.core.database import Base, engine


# Create database tables if absent.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recipe API")

app.include_router(recipe_router)
