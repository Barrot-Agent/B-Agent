from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class ProductionAsset:
    asset_id: str
    name: str
    asset_type: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    approved: bool = False


class AssetRegistry:
    """
    Tracks production assets without tying Barrot to any specific generation
    provider or editor.
    """

    def __init__(self) -> None:
        self.assets: dict[str, ProductionAsset] = {}

    def register(
        self,
        name: str,
        asset_type: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> ProductionAsset:
        asset = ProductionAsset(
            asset_id=str(uuid.uuid4()),
            name=name,
            asset_type=asset_type,
            source=source,
            metadata=metadata or {},
        )
        self.assets[asset.asset_id] = asset
        return asset

    def approve(self, asset_id: str) -> ProductionAsset:
        asset = self.assets[asset_id]
        asset.approved = True
        return asset

    def find(self, asset_type: str | None = None) -> list[ProductionAsset]:
        values = list(self.assets.values())
        if asset_type is None:
            return values
        return [asset for asset in values if asset.asset_type == asset_type]
