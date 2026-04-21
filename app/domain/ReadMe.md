Here’s a more **compact, interview/README-ready version** that keeps the reasoning but removes repetition.

---

# 🧠 Database Design Rationale (Summary)

The schema is designed using a **normalized relational model (PostgreSQL)** with a focus on **clear domain boundaries, data integrity, and future extensibility**.

---

## `user` vs `account` (1:1)

`user` stores public profile data, while `account` stores authentication credentials (passwords).

### Why split them:

* Improves security by isolating sensitive data
* Keeps authentication concerns separate from domain identity
* Enables future auth methods (OAuth, MFA, multiple accounts)

**Trade-off: requires joins, but improves security and flexibility.**

---

## `recipe` (core entity)

`recipe` is the central aggregate root of the system.

### Why:

* All main functionality revolves around recipes (create, query, update)
* Acts as the domain anchor for related data

---

## 🧂 `ingredient` (normalized entity)

Ingredients are stored once globally instead of inside recipes.

### Why:

* Prevents duplication and inconsistent naming
* Enables reuse across recipes
* Supports future features (allergens, nutrition, search)

---

## `recipe_ingredient` (many-to-many + attributes)

Associates recipes with ingredients and stores:

* amount
* unit

### Why:

* A recipe-ingredient relationship is **quantitative**.
* Enables precise cooking instructions and scaling.

**Trade-off: more complex writes, but much richer modeling.**

---

## `recipe_step` (1:M ordered structure)

Steps are stored in a separate table with ordering (`step_number`).

### Why:

* Steps are ordered
* Supports partial updates and step-level queries
* Avoids limitations of JSON storage (difficult updates, poor indexing)

**Trade-off: more rows, but better control and structure.**

---

## Vegetarian modeling trade-off (design decision)

Originally, vegetarian information was considered to be stored at the **ingredient level** instead of on `recipe`.

### Why this would have been better in theory:

* Better real-world modelling (dietary properties belong to ingredients)
* Stronger validation possibilities (automatic recipe classification)
* Reduced redundancy in the long run
* Slight space savings at recipe level

### Why it was not implemented:

* It creates a **user experience problem**

  * Users would need to create ingredients before creating recipes
  * This would make recipe creation unnecessarily frustrating

* It introduces **overengineering for the current scope**
  * The validation benefit does not justify the added workflow complexity

### Final decision:

Vegetarian information is stored on `recipe` instead. This prioritizes **usability and simplicity**, avoiding an 
awkward dependency chain in the API.

---

# Relationship Summary

* **User ↔ Account (1:1)** → separates identity from authentication
* **Recipe ↔ Ingredient (M:N)** → real-world reuse of ingredients
* **Recipe ↔ Step (1:M)** → ordered, compositional structure

---

# Key Design Trade-offs

| Decision                   | Benefit                | Trade-off                     |
| -------------------------- |------------------------|-------------------------------|
| Separate `account`         | Security + flexibility | Extra joins                   |
| Normalized ingredients     | Consistency + reuse    | More complex queries          |
| Join table with attributes | Rich modeling          | More write complexity         |
| Steps as table             | Editability + ordering | More rows than JSON           |
| Vegetarian on recipe       | Simplicity + UX        | Less theoretically pure model |

---
