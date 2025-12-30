# barrot/config.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

@dataclass
class IngestionConfig:
    arxiv_api_url: str = "https://export.arxiv.org/api/query"
    # endpoints/tokens for: hackathons, newsletters, forums, DAOs, Discord, etc.
    newsletters_sources: List[str] = field(default_factory=list)
    forums_sources: List[str] = field(default_factory=list)
    daos_sources: List[str] = field(default_factory=list)

@dataclass
class PathsConfig:
    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])
    
    @property
    def data_raw(self) -> Path:
        return self.base_dir / "data" / "raw"
    
    @property
    def data_processed(self) -> Path:
        return self.base_dir / "data" / "processed"
    
    @property
    def graphs_dir(self) -> Path:
        return self.base_dir / "data" / "graphs"
    
    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "barrot" / "logs"

def _default_ingestion_config() -> IngestionConfig:
    return IngestionConfig(
        newsletters_sources=[
            "https://api.buttondown.email/v1/subscribers",  # placeholder
        ],
        forums_sources=[
            "https://mathoverflow.net",
            "https://stackoverflow.com",
        ],
        daos_sources=[
            "https://snapshot.org/#/some-math-dao",  # placeholder
        ],
    )

@dataclass
class BarrotConfig:
    ingestion: IngestionConfig = field(default_factory=_default_ingestion_config)
    paths: PathsConfig = field(default_factory=PathsConfig)

config = BarrotConfig()
