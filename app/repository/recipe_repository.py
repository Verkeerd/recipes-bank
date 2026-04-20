import uuid

from sqlalchemy import func, or_, not_

from sqlalchemy.orm import Session, joinedload
from app.domain.model import Recipe, RecipeStep, Ingredient, RecipeIngredient
from app.domain.schema.recipe.recipe_query import RecipeQuery


class RecipeRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, recipe: Recipe):
        self.db.add(recipe)

    def get_all(self):
        return self.db.query(Recipe).options(
            joinedload(Recipe.recipe_ingredients),
            joinedload(Recipe.steps)
        ).all()

    def get_by_id(self, recipe_id: uuid.UUID):
        return self.db.query(Recipe).options(
            joinedload(Recipe.recipe_ingredients),
            joinedload(Recipe.steps)
        ).filter(Recipe.id == recipe_id).first()

    def delete(self, recipe: Recipe):
        self.db.delete(recipe)

    def refresh(self, entity):
        self.db.refresh(entity)
        return entity

    @staticmethod
    def apply_vegetarian_filter(query, vegetarian: bool | None):
        return query.filter(Recipe.vegetarian.is_(vegetarian))

    @staticmethod
    def apply_servings_filter(query, servings: int | None):
        if servings is not None:
            query = query.filter(Recipe.servings == servings)
        return query


    @staticmethod
    def apply_ingredient_filters(query, include_terms=None, exclude_terms=None):
        if include_terms or exclude_terms:
            query = query.join(Recipe.recipe_ingredients).join(RecipeIngredient.ingredient)

        if include_terms:
            include_conditions = [
                Ingredient.name.ilike(f"%{t}%")
                for t in include_terms
            ]
            query = query.filter(or_(*include_conditions))

        if exclude_terms:
            exclude_conditions = [
                Ingredient.name.ilike(f"%{t}%")
                for t in exclude_terms
            ]
            query = query.filter(not_(or_(*exclude_conditions)))

        return query

    @staticmethod
    def apply_step_filters(query, include_terms=None, exclude_terms=None):

        # include tems
        if include_terms:
            include_conditions = []

            for term in include_terms:
                include_conditions.append(
                    or_(
                        # search recipe description
                        func.to_tsvector("english", Recipe.description).match(term),
                        # search step descriptions
                        func.to_tsvector("english", RecipeStep.description).match(term),
                    )
                )

            query = query.filter(or_(*include_conditions))

        # exclude terms
        if exclude_terms:
            exclude_conditions = []

            for term in exclude_terms:
                exclude_conditions.append(
                    or_(
                        # search recipe description
                        func.to_tsvector("english", Recipe.description).match(term),
                        # search step descriptions
                        func.to_tsvector("english", RecipeStep.description).match(term),
                    )
                )

            query = query.filter(not_(or_(*exclude_conditions)))

        return query

    def build_query(self, request: RecipeQuery):
        query = self.db.query(Recipe).distinct()

        query = self.apply_step_filters(
            query,
            request.description_include,
            request.description_exclude
        )

        query = self.apply_ingredient_filters(
            query,
            request.ingredients_include,
            request.ingredients_exclude
            )

        if isinstance(request.vegetarian, bool):
            query = self.apply_vegetarian_filter(query, request.vegetarian)

        if request.servings:
            query = self.apply_servings_filter(query, request.servings)

        return query

