"""
barrot_agent.rendering — Comprehensive 3D Dataset Absorption System

Provides 15 pipeline modules giving Barrot full real-time 3D rendering
capability across 40+ globally integrated datasets.

Modules
-------
dataset_manager        Central registry & query interface (40+ datasets)
asset_loader           Multi-format 3D asset loader & GPU optimiser
material_integration   PBR material importer & compiler
scene_database         Large-scale indoor scene loader (ScanNet, Matterport3D…)
point_cloud_system     LiDAR & point cloud renderer (KITTI, Semantic3D…)
nerf_integration       Neural Radiance Field inference (LLFF, Synthetic…)
world_mapping          World-scale streaming (NYC, Berlin, Cesium 3D Tiles…)
photogrammetry_pipeline End-to-end photogrammetry pipeline
dataset_cache          Multi-tier GPU/CPU/SSD/Cloud LRU cache
dataset_indexing       Sub-10ms dataset search & indexing
format_converter       Bidirectional 3D format converter
streaming_loader       Chunked progressive streaming
quality_metrics        Geometry, texture & performance validation
dataset_renderer       Real-time rendering engine integration
dataset_analytics      Live statistics dashboard & build report
"""

from barrot_agent.rendering.dataset_manager import DatasetManager, DatasetRecord
from barrot_agent.rendering.asset_loader import AssetLoader, LoadedAsset
from barrot_agent.rendering.material_integration import MaterialIntegration, PBRMaterial
from barrot_agent.rendering.scene_database import SceneDatabase, LoadedScene
from barrot_agent.rendering.point_cloud_system import PointCloudSystem, LoadedPointCloud
from barrot_agent.rendering.nerf_integration import NeRFIntegration, NeRFScene
from barrot_agent.rendering.world_mapping import WorldMapping, WorldRegion
from barrot_agent.rendering.photogrammetry_pipeline import PhotogrammetryPipeline, ProcessedModel
from barrot_agent.rendering.dataset_cache import DatasetCache, CacheConfig
from barrot_agent.rendering.dataset_indexing import DatasetIndexing, SearchResult
from barrot_agent.rendering.format_converter import FormatConverter, ConversionResult
from barrot_agent.rendering.streaming_loader import StreamingLoader, StreamHandle
from barrot_agent.rendering.quality_metrics import QualityMetrics, ValidationReport
from barrot_agent.rendering.dataset_renderer import DatasetRenderer, RenderSession, RenderFrame
from barrot_agent.rendering.dataset_analytics import DatasetAnalytics, AnalyticsSummary

__all__ = [
    # Module 1
    "DatasetManager",
    "DatasetRecord",
    # Module 2
    "AssetLoader",
    "LoadedAsset",
    # Module 3
    "MaterialIntegration",
    "PBRMaterial",
    # Module 4
    "SceneDatabase",
    "LoadedScene",
    # Module 5
    "PointCloudSystem",
    "LoadedPointCloud",
    # Module 6
    "NeRFIntegration",
    "NeRFScene",
    # Module 7
    "WorldMapping",
    "WorldRegion",
    # Module 8
    "PhotogrammetryPipeline",
    "ProcessedModel",
    # Module 9
    "DatasetCache",
    "CacheConfig",
    # Module 10
    "DatasetIndexing",
    "SearchResult",
    # Module 11
    "FormatConverter",
    "ConversionResult",
    # Module 12
    "StreamingLoader",
    "StreamHandle",
    # Module 13
    "QualityMetrics",
    "ValidationReport",
    # Module 14
    "DatasetRenderer",
    "RenderSession",
    "RenderFrame",
    # Module 15
    "DatasetAnalytics",
    "AnalyticsSummary",
]
