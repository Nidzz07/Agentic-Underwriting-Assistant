"""Seeded synthetic profile factory (Sharpening 4 — the "seeded" half).

Distinct from the curated STATIC corpora C/L: these are SEEDED (Faker + a seeded
RNG) so they are reproducible by seed. All synthetic (DATA-4, zero real PII) —
deliberately NO email/SSN/card generation, only names/cities/financial numbers,
so the active PII guard stays green. This is intake's OWN small fixture factory —
NOT coupled to the separate build-time corpus-generator unit.
"""
from __future__ import annotations

import random

from faker import Faker


def synthetic_form(seed: int = 42) -> dict:
    """A deterministic synthetic extracted-draft form for gate tests."""
    fake = Faker("en_US")
    fake.seed_instance(seed)
    rng = random.Random(seed)

    age = rng.randrange(20, 60)
    birth_year = 2026 - age
    income = rng.randrange(300_000, 3_000_000)
    cover = income * rng.randrange(3, 10)
    debt = rng.randrange(0, income // 2)
    height = rng.randrange(150, 200)
    weight = rng.randrange(45, 110)

    return {
        "date_of_birth": f"{birth_year:04d}-06-15",
        "as_of_date": "2026-06-15",
        "verifiable_income_annual": f"{income}.00",
        "requested_cover_amount": f"{cover}.00",
        "height_cm": f"{height}.00",
        "weight_kg": f"{weight}.00",
        "existing_debt_obligations_annual": f"{debt}.00",
        "employment_type": rng.choice(["salaried", "self_employed", "contract"]),
        "smoking_status": rng.choice(["smoker", "non_smoker"]),
        "occupation": "office_worker",
        "health_flags": ["none"],
        "full_name": fake.name(),
        "gender": rng.choice(["male", "female", "unspecified"]),
        "city": fake.city(),
    }
