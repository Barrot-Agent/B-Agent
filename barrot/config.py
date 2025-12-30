# barrot/config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class IngestionConfig:
    arxiv_api_url: str = "https://export.arxiv.org/api/query"
    # endpoints/tokens for: hackathons, newsletters, forums, DAOs, Discord, etc.
    newsletters_sources: list = None
    forums_sources: list = None
    daos_sources: list = None

@dataclass
class PathsConfig:
    base_dir: Path = Path(__file__).resolve().parents[1]
    data_raw: Path = base_dir / "data" / "raw"
    data_processed: Path = base_dir / "data" / "processed"
    graphs_dir: Path = base_dir / "data" / "graphs"
    logs_dir: Path = base_dir / "barrot" / "logs"

@dataclass
class BarrotConfig:
    ingestion: IngestionConfig = IngestionConfig(
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
    paths: PathsConfig = PathsConfig()

config = BarrotConfig()
