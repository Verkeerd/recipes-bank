from fastapi import FastAPI

from app.controller.auth_controller import auth_router
from app.controller.recipe_controller import recipe_router


app = FastAPI(title="Recipe API")

app.include_router(recipe_router)
app.include_router(auth_router)
