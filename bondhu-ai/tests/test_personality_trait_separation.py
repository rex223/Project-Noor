"""Regression tests ensuring PersonalityTrait enum remains iterable and
PersonalityTraitModel (Pydantic) is distinct to prevent prior confusion.
"""
import inspect

from core.database.models import PersonalityTrait
from api.models.schemas import PersonalityTraitModel


def test_enum_is_iterable_and_members_present():
    members = list(PersonalityTrait)
    assert len(members) >= 5
    names = {m.name.lower() for m in members}
    assert 'openness' in names
    assert 'neuroticism' in names


def test_model_and_enum_are_distinct():
    assert PersonalityTrait.__class__.__name__ == 'EnumMeta'
    assert PersonalityTraitModel.__class__.__name__ != 'EnumMeta'
    # Ensure we didn't accidentally alias the same object
    assert PersonalityTraitModel is not PersonalityTrait


def test_model_signature_has_expected_fields():
    sig = inspect.signature(PersonalityTraitModel)
    params = list(sig.parameters.keys())
    assert 'name' in params and 'score' in params and 'confidence' in params
