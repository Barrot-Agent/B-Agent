#!/usr/bin/env python3
"""
Dependency Micro-Ingestion System for Barrot-Agent

Massively ingests Python, PyTorch, and popular dependencies to enhance
Barrot's understanding and capabilities. Includes:
- Package metadata extraction
- Documentation parsing
- Architecture analysis
- Optimization recommendations
- Continuous update mechanisms

Designed to be fully automated and continuously evolving.
"""

import json
import os
import re
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

# Configuration constants
MAX_DOC_CONTENT_SIZE = 5000  # Maximum characters to extract per documentation source
                              # Prevents memory issues and focuses on key content


class PackageCategory(Enum):
    """Categories for dependency packages"""
    CORE_PYTHON = "core_python"
    ML_FRAMEWORK = "ml_framework"
    DATA_SCIENCE = "data_science"
    WEB_FRAMEWORK = "web_framework"
    UTILITY = "utility"
    SCIENTIFIC = "scientific"
    VISUALIZATION = "visualization"
    DATABASE = "database"
    TESTING = "testing"
    DEPLOYMENT = "deployment"


class OptimizationLevel(Enum):
    """Optimization applicability levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


@dataclass
class PackageMetadata:
    """Metadata for a Python package"""
    name: str
    version: str
    category: str
    description: str
    homepage: str
    documentation_url: str
    repository_url: str
    license: str
    dependencies: List[str] = field(default_factory=list)
    key_features: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    last_updated: str = ""


@dataclass
class ArchitectureComponent:
    """Architectural component of a package"""
    name: str
    type: str
    purpose: str
    key_classes: List[str] = field(default_factory=list)
    key_functions: List[str] = field(default_factory=list)
    design_patterns: List[str] = field(default_factory=list)


@dataclass
class APIEndpoint:
    """API endpoint or function signature"""
    name: str
    signature: str
    parameters: List[Dict[str, str]] = field(default_factory=list)
    return_type: str = ""
    description: str = ""
    examples: List[str] = field(default_factory=list)


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation for Barrot system"""
    package: str
    level: str
    category: str
    title: str
    description: str
    impact: str
    implementation_notes: List[str] = field(default_factory=list)
    code_examples: List[str] = field(default_factory=list)


@dataclass
class DependencyKnowledge:
    """Comprehensive knowledge about a dependency"""
    metadata: PackageMetadata
    architecture: List[ArchitectureComponent] = field(default_factory=list)
    api_endpoints: List[APIEndpoint] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    common_patterns: List[str] = field(default_factory=list)
    performance_tips: List[str] = field(default_factory=list)
    security_considerations: List[str] = field(default_factory=list)
    integration_notes: List[str] = field(default_factory=list)


class DocHTMLParser(HTMLParser):
    """HTML parser for documentation extraction"""
    
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.code_blocks = []
        self.in_script = False
        self.in_style = False
        self.in_code = False
        self.current_code = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.in_script = True
        elif tag == 'style':
            self.in_style = True
        elif tag in ['code', 'pre']:
            self.in_code = True
            self.current_code = []
            
    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False
        elif tag == 'style':
            self.in_style = False
        elif tag in ['code', 'pre']:
            self.in_code = False
            if self.current_code:
                self.code_blocks.append(''.join(self.current_code))
            
    def handle_data(self, data):
        if not self.in_script and not self.in_style:
            if self.in_code:
                self.current_code.append(data)
            else:
                text = data.strip()
                if text:
                    self.text_content.append(text)
                    
    def get_text(self):
        return ' '.join(self.text_content)
    
    def get_code_blocks(self):
        return self.code_blocks


class DependencyMicroIngestion:
    """Main micro-ingestion system for dependencies"""
    
    def __init__(self, config_file: str = "dependency-ingestion-config.yaml",
                 output_dir: str = "ingested_dependencies"):
        self.config_file = config_file
        self.output_dir = output_dir
        self.dependencies: Dict[str, DependencyKnowledge] = {}
        self.optimizations: List[OptimizationRecommendation] = []
        self.last_update: Dict[str, str] = {}
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file or use defaults
        
        Note: YAML parsing requires PyYAML which is not a standard library.
        The system uses hardcoded defaults that match the YAML config structure
        to maintain zero-dependency operation. The YAML file serves as
        documentation and can be used when PyYAML is available.
        """
        # Try to load YAML if available
        try:
            import yaml
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    full_config = yaml.safe_load(f)
                    # Extract the ingestion_config section which contains packages
                    if full_config and 'ingestion_config' in full_config:
                        ing_config = full_config['ingestion_config']
                        # Return in the expected format
                        return {
                            'packages': ing_config.get('packages', {}),
                            'ingestion': ing_config.get('settings', {}),
                            'analysis': ing_config.get('analysis', {}),
                        }
        except ImportError:
            pass  # PyYAML not available, use defaults
        except Exception as e:
            print(f"⚠️  Error loading YAML config: {e}")
        
        # Use default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for dependency ingestion"""
        return {
            'packages': {
                'python': {
                    'category': 'core_python',
                    'priority': 'critical',
                    'sources': [
                        'https://docs.python.org/3/',
                        'https://docs.python.org/3/library/',
                        'https://docs.python.org/3/reference/',
                    ]
                },
                'pytorch': {
                    'category': 'ml_framework',
                    'priority': 'critical',
                    'sources': [
                        'https://pytorch.org/docs/stable/',
                        'https://pytorch.org/tutorials/',
                        'https://pytorch.org/docs/stable/torch.html',
                    ]
                },
                'numpy': {
                    'category': 'scientific',
                    'priority': 'critical',
                    'sources': [
                        'https://numpy.org/doc/stable/',
                    ]
                },
                'pandas': {
                    'category': 'data_science',
                    'priority': 'high',
                    'sources': [
                        'https://pandas.pydata.org/docs/',
                    ]
                },
                'scikit-learn': {
                    'category': 'ml_framework',
                    'priority': 'high',
                    'sources': [
                        'https://scikit-learn.org/stable/documentation.html',
                    ]
                },
                'tensorflow': {
                    'category': 'ml_framework',
                    'priority': 'high',
                    'sources': [
                        'https://www.tensorflow.org/api_docs/python/tf',
                    ]
                },
                'matplotlib': {
                    'category': 'visualization',
                    'priority': 'medium',
                    'sources': [
                        'https://matplotlib.org/stable/contents.html',
                    ]
                },
                'requests': {
                    'category': 'utility',
                    'priority': 'high',
                    'sources': [
                        'https://requests.readthedocs.io/en/latest/',
                    ]
                },
                'flask': {
                    'category': 'web_framework',
                    'priority': 'medium',
                    'sources': [
                        'https://flask.palletsprojects.com/',
                    ]
                },
                'django': {
                    'category': 'web_framework',
                    'priority': 'medium',
                    'sources': [
                        'https://docs.djangoproject.com/',
                    ]
                },
            },
            'ingestion': {
                'rate_limit': 1.0,  # seconds between requests
                'max_retries': 3,
                'timeout': 10,
                'update_frequency': 'weekly',
            },
            'analysis': {
                'extract_architecture': True,
                'extract_api': True,
                'generate_optimizations': True,
                'track_updates': True,
            }
        }
    
    def ingest_package(self, package_name: str, package_config: Dict[str, Any]) -> bool:
        """Ingest a single package"""
        print(f"\n📦 Ingesting {package_name}...")
        
        try:
            # Create package metadata
            metadata = self._create_package_metadata(package_name, package_config)
            
            # Fetch documentation
            docs_content = self._fetch_documentation(package_config.get('sources', []))
            
            # Parse architecture
            architecture = self._analyze_architecture(package_name, docs_content)
            
            # Extract API endpoints
            api_endpoints = self._extract_api_endpoints(package_name, docs_content)
            
            # Extract best practices
            best_practices = self._extract_best_practices(package_name, docs_content)
            
            # Create knowledge structure
            knowledge = DependencyKnowledge(
                metadata=metadata,
                architecture=architecture,
                api_endpoints=api_endpoints,
                best_practices=best_practices,
                common_patterns=self._extract_patterns(package_name),
                performance_tips=self._extract_performance_tips(package_name),
                security_considerations=self._extract_security_considerations(package_name),
                integration_notes=self._extract_integration_notes(package_name)
            )
            
            self.dependencies[package_name] = knowledge
            
            # Generate optimizations
            if self.config['analysis']['generate_optimizations']:
                self._generate_optimizations(package_name, knowledge)
            
            # Save to file
            self._save_package_knowledge(package_name, knowledge)
            
            print(f"✅ Successfully ingested {package_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error ingesting {package_name}: {e}")
            return False
    
    def _create_package_metadata(self, package_name: str, config: Dict[str, Any]) -> PackageMetadata:
        """Create package metadata"""
        # This would ideally fetch from PyPI API, but for now use defaults
        return PackageMetadata(
            name=package_name,
            version="latest",
            category=config.get('category', 'utility'),
            description=f"{package_name} - Python package",
            homepage=config.get('sources', [''])[0] if config.get('sources') else '',
            documentation_url=config.get('sources', [''])[0] if config.get('sources') else '',
            repository_url=f"https://github.com/{package_name}/{package_name}",
            license="Various",
            dependencies=[],
            key_features=self._get_key_features(package_name),
            use_cases=self._get_use_cases(package_name),
            last_updated=datetime.now(timezone.utc).isoformat()
        )
    
    def _get_key_features(self, package_name: str) -> List[str]:
        """Get key features for a package"""
        features = {
            'python': [
                'Standard library with comprehensive modules',
                'Dynamic typing with type hints',
                'Object-oriented and functional programming',
                'Extensive built-in data structures',
                'Rich ecosystem of third-party packages'
            ],
            'pytorch': [
                'Dynamic computational graphs',
                'GPU acceleration via CUDA',
                'Automatic differentiation',
                'Neural network building blocks',
                'Distributed training support',
                'TorchScript for production deployment'
            ],
            'numpy': [
                'N-dimensional array operations',
                'Broadcasting and vectorization',
                'Linear algebra operations',
                'Fourier transforms',
                'Random number generation'
            ],
            'pandas': [
                'DataFrame and Series data structures',
                'Data cleaning and transformation',
                'Time series functionality',
                'SQL-like joins and merges',
                'I/O for various formats (CSV, JSON, SQL, etc.)'
            ],
            'scikit-learn': [
                'Classification and regression algorithms',
                'Clustering algorithms',
                'Dimensionality reduction',
                'Model selection and evaluation',
                'Preprocessing and feature extraction'
            ],
            'tensorflow': [
                'Static computational graphs',
                'Eager execution mode',
                'Keras high-level API',
                'TensorBoard visualization',
                'TensorFlow Lite for mobile',
                'TensorFlow.js for JavaScript'
            ],
        }
        return features.get(package_name, [f'Feature of {package_name}'])
    
    def _get_use_cases(self, package_name: str) -> List[str]:
        """Get use cases for a package"""
        use_cases = {
            'python': [
                'General-purpose programming',
                'Web development',
                'Data analysis and science',
                'Machine learning and AI',
                'Automation and scripting'
            ],
            'pytorch': [
                'Deep learning research',
                'Computer vision applications',
                'Natural language processing',
                'Reinforcement learning',
                'Generative models (GANs, VAEs, Diffusion)'
            ],
            'numpy': [
                'Scientific computing',
                'Matrix operations',
                'Signal processing',
                'Image processing',
                'Statistical analysis'
            ],
            'pandas': [
                'Data analysis and exploration',
                'Data cleaning and preprocessing',
                'Time series analysis',
                'Financial data analysis',
                'Business intelligence'
            ],
        }
        return use_cases.get(package_name, [f'Use case for {package_name}'])
    
    def _fetch_documentation(self, sources: List[str]) -> str:
        """Fetch documentation from sources"""
        content = []
        
        for source in sources[:2]:  # Limit to first 2 sources to avoid overwhelming
            try:
                req = Request(source, headers={'User-Agent': 'Barrot-Agent/1.0'})
                with urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                    parser = DocHTMLParser()
                    parser.feed(html)
                    content.append(parser.get_text()[:MAX_DOC_CONTENT_SIZE])
            except (URLError, HTTPError, Exception) as e:
                print(f"  ⚠️  Could not fetch {source}: {e}")
                continue
        
        return ' '.join(content)
    
    def _analyze_architecture(self, package_name: str, docs_content: str) -> List[ArchitectureComponent]:
        """Analyze package architecture"""
        # This is a simplified version. In production, this would use AST analysis
        components = []
        
        arch_info = {
            'pytorch': [
                ArchitectureComponent(
                    name='torch.nn',
                    type='module',
                    purpose='Neural network building blocks',
                    key_classes=['Module', 'Sequential', 'Linear', 'Conv2d', 'RNN', 'LSTM'],
                    key_functions=['forward'],
                    design_patterns=['Builder', 'Factory', 'Composite']
                ),
                ArchitectureComponent(
                    name='torch.optim',
                    type='module',
                    purpose='Optimization algorithms',
                    key_classes=['SGD', 'Adam', 'RMSprop', 'AdamW'],
                    design_patterns=['Strategy']
                ),
                ArchitectureComponent(
                    name='torch.autograd',
                    type='module',
                    purpose='Automatic differentiation',
                    key_classes=['Function', 'Variable'],
                    key_functions=['backward', 'grad'],
                    design_patterns=['Observer', 'Chain of Responsibility']
                ),
            ],
            'numpy': [
                ArchitectureComponent(
                    name='numpy.ndarray',
                    type='class',
                    purpose='N-dimensional array container',
                    key_functions=['reshape', 'transpose', 'dot', 'sum', 'mean'],
                    design_patterns=['Iterator', 'Template']
                ),
            ],
            'pandas': [
                ArchitectureComponent(
                    name='pandas.DataFrame',
                    type='class',
                    purpose='2D labeled data structure',
                    key_functions=['read_csv', 'to_csv', 'merge', 'groupby', 'pivot'],
                    design_patterns=['Builder', 'Facade']
                ),
            ],
        }
        
        return arch_info.get(package_name, [])
    
    def _extract_api_endpoints(self, package_name: str, docs_content: str) -> List[APIEndpoint]:
        """Extract API endpoints from documentation"""
        # Simplified API extraction
        apis = {
            'pytorch': [
                APIEndpoint(
                    name='torch.tensor',
                    signature='torch.tensor(data, dtype=None, device=None, requires_grad=False)',
                    parameters=[
                        {'name': 'data', 'type': 'array_like'},
                        {'name': 'dtype', 'type': 'torch.dtype'},
                        {'name': 'device', 'type': 'torch.device'},
                        {'name': 'requires_grad', 'type': 'bool'},
                    ],
                    return_type='torch.Tensor',
                    description='Constructs a tensor with data',
                    examples=['torch.tensor([[1, 2], [3, 4]])']
                ),
                APIEndpoint(
                    name='torch.nn.functional.relu',
                    signature='torch.nn.functional.relu(input, inplace=False)',
                    parameters=[
                        {'name': 'input', 'type': 'Tensor'},
                        {'name': 'inplace', 'type': 'bool'},
                    ],
                    return_type='Tensor',
                    description='Applies rectified linear unit activation',
                    examples=['F.relu(x)']
                ),
            ],
        }
        
        return apis.get(package_name, [])
    
    def _extract_best_practices(self, package_name: str, docs_content: str) -> List[str]:
        """Extract best practices"""
        practices = {
            'pytorch': [
                'Use DataLoader for efficient batch loading',
                'Move models and data to GPU with .to(device)',
                'Use torch.no_grad() for inference to save memory',
                'Implement proper weight initialization',
                'Use learning rate scheduling for better convergence',
                'Save checkpoints during training',
                'Use mixed precision training (torch.cuda.amp) for speed',
            ],
            'numpy': [
                'Vectorize operations instead of loops',
                'Use views instead of copies when possible',
                'Preallocate arrays for better performance',
                'Use appropriate dtypes to save memory',
                'Leverage broadcasting for element-wise operations',
            ],
            'pandas': [
                'Use vectorized operations instead of apply',
                'Set appropriate dtypes for columns',
                'Use categorical dtype for string columns with few unique values',
                'Chunk large datasets with read_csv(chunksize=...)',
                'Use query() for complex filtering',
            ],
        }
        
        return practices.get(package_name, [])
    
    def _extract_patterns(self, package_name: str) -> List[str]:
        """Extract common patterns"""
        patterns = {
            'pytorch': [
                'Training loop with forward-backward-optimize',
                'Custom Dataset and DataLoader pattern',
                'Model checkpointing pattern',
                'Transfer learning pattern',
                'Multi-GPU training with DistributedDataParallel',
            ],
            'pandas': [
                'Split-apply-combine pattern with groupby',
                'Method chaining for transformations',
                'MultiIndex for hierarchical data',
                'Pivot tables for aggregation',
            ],
        }
        
        return patterns.get(package_name, [])
    
    def _extract_performance_tips(self, package_name: str) -> List[str]:
        """Extract performance tips"""
        tips = {
            'pytorch': [
                'Pin memory for faster GPU transfers',
                'Use multiple workers in DataLoader',
                'Profile with torch.profiler',
                'Use JIT compilation with TorchScript',
                'Enable cudnn.benchmark for fixed input sizes',
            ],
            'numpy': [
                'Use ufuncs for element-wise operations',
                'Leverage BLAS libraries for linear algebra',
                'Use einsum for complex tensor operations',
                'Memory-map large arrays with np.memmap',
            ],
            'pandas': [
                'Use eval() for complex expressions',
                'Avoid frame copies with inplace=True cautiously',
                'Use HDFStore for large datasets',
                'Leverage numexpr for numerical operations',
            ],
        }
        
        return tips.get(package_name, [])
    
    def _extract_security_considerations(self, package_name: str) -> List[str]:
        """Extract security considerations"""
        considerations = {
            'python': [
                'Validate and sanitize user inputs',
                'Use parameterized queries to prevent SQL injection',
                'Avoid eval() and exec() with untrusted input',
                'Use secrets module for cryptographic operations',
                'Keep dependencies updated to patch vulnerabilities',
            ],
            'pytorch': [
                'Validate model inputs to prevent adversarial attacks',
                'Use secure model serialization (avoid pickle for untrusted sources)',
                'Implement input sanitization for inference endpoints',
                'Monitor for model poisoning in training data',
            ],
        }
        
        return considerations.get(package_name, [])
    
    def _extract_integration_notes(self, package_name: str) -> List[str]:
        """Extract integration notes for Barrot"""
        notes = {
            'pytorch': [
                'Can be integrated with Barrot AGI reasoning for neural architecture search',
                'Model outputs can feed into transformative insights system',
                'Training metrics can be analyzed by MMI data analyzer',
                'Supports distributed training for parallel model training across multiple GPUs/nodes',
            ],
            'numpy': [
                'Core dependency for all numerical operations in Barrot',
                'Used extensively in advanced algorithms module',
                'Critical for data transformation pipelines',
            ],
            'pandas': [
                'Essential for MMI data analysis',
                'Used in monetization engine for financial data',
                'Integrates with email analyzer for structured data extraction',
            ],
        }
        
        return notes.get(package_name, [])
    
    def _generate_optimizations(self, package_name: str, knowledge: DependencyKnowledge):
        """Generate optimization recommendations for Barrot"""
        # Generate package-specific optimizations
        optimizations = []
        
        if package_name == 'pytorch':
            optimizations.extend([
                OptimizationRecommendation(
                    package='pytorch',
                    level=OptimizationLevel.CRITICAL.value,
                    category='performance',
                    title='Implement GPU Acceleration for AGI Reasoning',
                    description='Leverage PyTorch CUDA capabilities to accelerate AGI reasoning computations',
                    impact='10-100x speedup for tensor operations in reasoning engine',
                    implementation_notes=[
                        'Move reasoning tensors to GPU: tensor.to(device)',
                        'Use torch.cuda.amp for mixed precision',
                        'Batch operations for better GPU utilization',
                    ],
                    code_examples=[
                        'device = torch.device("cuda" if torch.cuda.is_available() else "cpu")',
                        'model.to(device)',
                    ]
                ),
                OptimizationRecommendation(
                    package='pytorch',
                    level=OptimizationLevel.HIGH.value,
                    category='architecture',
                    title='Implement Neural Architecture Search for Barrot',
                    description='Use PyTorch to implement NAS for optimizing Barrot internal models',
                    impact='Automated discovery of optimal neural architectures',
                    implementation_notes=[
                        'Create searchable architecture space',
                        'Implement efficient search algorithm (DARTS, ENAS)',
                        'Integrate with existing AGI orchestrator',
                    ],
                )
            ])
        
        elif package_name == 'numpy':
            optimizations.append(
                OptimizationRecommendation(
                    package='numpy',
                    level=OptimizationLevel.HIGH.value,
                    category='performance',
                    title='Vectorize Barrot Data Processing Pipelines',
                    description='Replace loops with vectorized numpy operations',
                    impact='5-50x speedup in data transformation modules',
                    implementation_notes=[
                        'Identify loop-heavy code in data_transformation.py',
                        'Replace with numpy broadcasting',
                        'Use ufuncs for element-wise operations',
                    ],
                )
            )
        
        elif package_name == 'pandas':
            optimizations.append(
                OptimizationRecommendation(
                    package='pandas',
                    level=OptimizationLevel.MEDIUM.value,
                    category='memory',
                    title='Optimize MMI Data Analyzer Memory Usage',
                    description='Use categorical dtypes and chunking for large datasets',
                    impact='50-80% reduction in memory usage for large ingestions',
                    implementation_notes=[
                        'Convert string columns to categorical',
                        'Use read_csv with chunksize parameter',
                        'Leverage HDFStore for persistent storage',
                    ],
                )
            )
        
        self.optimizations.extend(optimizations)
    
    def _save_package_knowledge(self, package_name: str, knowledge: DependencyKnowledge):
        """Save package knowledge to JSON file"""
        filename = f"{self.output_dir}/dependency_{package_name.replace('-', '_')}.json"
        
        # Convert dataclass to dict
        data = {
            'metadata': asdict(knowledge.metadata),
            'architecture': [asdict(comp) for comp in knowledge.architecture],
            'api_endpoints': [asdict(api) for api in knowledge.api_endpoints],
            'best_practices': knowledge.best_practices,
            'common_patterns': knowledge.common_patterns,
            'performance_tips': knowledge.performance_tips,
            'security_considerations': knowledge.security_considerations,
            'integration_notes': knowledge.integration_notes,
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Saved to {filename}")
    
    def ingest_all(self) -> Dict[str, Any]:
        """Ingest all configured packages"""
        print("🚀 Starting Dependency Micro-Ingestion System")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📦 Packages to ingest: {len(self.config['packages'])}")
        
        start_time = datetime.now(timezone.utc)
        success_count = 0
        failure_count = 0
        
        for package_name, package_config in self.config['packages'].items():
            if self.ingest_package(package_name, package_config):
                success_count += 1
            else:
                failure_count += 1
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        summary = {
            'ingestion_timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'total_packages': len(self.config['packages']),
            'successful_ingestions': success_count,
            'failed_ingestions': failure_count,
            'packages_ingested': list(self.dependencies.keys()),
            'optimizations_generated': len(self.optimizations),
        }
        
        # Save summary
        self._save_summary(summary)
        
        # Save optimizations
        self._save_optimizations()
        
        # Save taxonomy
        self._save_taxonomy()
        
        print(f"\n✅ Ingestion complete!")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {failure_count}")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Optimizations generated: {len(self.optimizations)}")
        
        return summary
    
    def _save_summary(self, summary: Dict[str, Any]):
        """Save ingestion summary"""
        filename = f"{self.output_dir}/dependency_ingestion_summary.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"  📊 Summary saved to {filename}")
    
    def _save_optimizations(self):
        """Save optimization recommendations"""
        filename = f"{self.output_dir}/barrot_optimization_recommendations.json"
        
        data = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_recommendations': len(self.optimizations),
            'by_level': self._group_by_level(),
            'by_category': self._group_by_category(),
            'recommendations': [asdict(opt) for opt in self.optimizations],
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  🎯 Optimizations saved to {filename}")
    
    def _group_by_level(self) -> Dict[str, int]:
        """Group optimizations by level"""
        groups = {}
        for opt in self.optimizations:
            groups[opt.level] = groups.get(opt.level, 0) + 1
        return groups
    
    def _group_by_category(self) -> Dict[str, int]:
        """Group optimizations by category"""
        groups = {}
        for opt in self.optimizations:
            groups[opt.category] = groups.get(opt.category, 0) + 1
        return groups
    
    def _save_taxonomy(self):
        """Save dependency taxonomy"""
        filename = f"{self.output_dir}/dependency_taxonomy.json"
        
        taxonomy = {
            'by_category': self._taxonomize_by_category(),
            'by_priority': self._taxonomize_by_priority(),
            'by_use_case': self._taxonomize_by_use_case(),
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(taxonomy, f, indent=2, ensure_ascii=False)
        print(f"  🏷️  Taxonomy saved to {filename}")
    
    def _taxonomize_by_category(self) -> Dict[str, List[str]]:
        """Taxonomize packages by category"""
        taxonomy = {}
        for pkg_name, pkg_config in self.config['packages'].items():
            category = pkg_config.get('category', 'utility')
            if category not in taxonomy:
                taxonomy[category] = []
            taxonomy[category].append(pkg_name)
        return taxonomy
    
    def _taxonomize_by_priority(self) -> Dict[str, List[str]]:
        """Taxonomize packages by priority"""
        taxonomy = {}
        for pkg_name, pkg_config in self.config['packages'].items():
            priority = pkg_config.get('priority', 'medium')
            if priority not in taxonomy:
                taxonomy[priority] = []
            taxonomy[priority].append(pkg_name)
        return taxonomy
    
    def _taxonomize_by_use_case(self) -> Dict[str, List[str]]:
        """Taxonomize packages by use case"""
        taxonomy = {
            'machine_learning': ['pytorch', 'tensorflow', 'scikit-learn'],
            'data_analysis': ['pandas', 'numpy'],
            'web_development': ['flask', 'django', 'requests'],
            'visualization': ['matplotlib'],
            'general_purpose': ['python'],
        }
        return taxonomy


def main():
    """Main entry point"""
    print("=" * 70)
    print("🦜 Barrot Dependency Micro-Ingestion System")
    print("=" * 70)
    
    # Initialize system
    ingestion_system = DependencyMicroIngestion()
    
    # Run full ingestion
    summary = ingestion_system.ingest_all()
    
    print("\n" + "=" * 70)
    print("📊 Ingestion Summary")
    print("=" * 70)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
