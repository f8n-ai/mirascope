"""Tests that `Partial` works to make all fields optional."""
from typing import Optional

from pydantic import BaseModel

from mirascope.partial import Partial


class ShallowModel(BaseModel):
    """A test model."""

    param: str
    default: int = 0


class PartialShallowModel(BaseModel):
    """A test model."""

    param: Optional[str] = None
    default: Optional[int] = None


def test_shallow_partial():
    """Tests that `Partial` works to make all fields optional in a shallow model."""
    assert (
        Partial[ShallowModel].model_json_schema()
        == PartialShallowModel.model_json_schema()
    )


class DeeperModel(BaseModel):
    """A deeper model."""

    shallow: ShallowModel
    param: str


class PartialDeeperModel(BaseModel):
    """A deeper model."""

    shallow: Optional[PartialShallowModel] = {}  # type: ignore
    param: Optional[str] = None


def test_deeper_partial():
    """Tests that `Partial` works to make all fields optional in a deeper model."""
    print(Partial[DeeperModel].model_json_schema())
    print(PartialDeeperModel.model_json_schema())
    assert (
        Partial[DeeperModel].model_json_schema()
        == PartialDeeperModel.model_json_schema()
    )


class DeepestModel(BaseModel):
    """A deepest model."""

    shallow: ShallowModel
    deeper: DeeperModel
    param: str


class PartialDeepestModel(BaseModel):
    """A deepest model."""

    shallow: Optional[PartialShallowModel] = {}  # type: ignore
    deeper: Optional[PartialDeeperModel] = {}  # type: ignore
    param: Optional[str] = None


def test_deepest_partial():
    """Tests that `Partial` works to make all fields optional in a deeper model."""
    assert (
        Partial[DeepestModel].model_json_schema()
        == PartialDeepestModel.model_json_schema()
    )
