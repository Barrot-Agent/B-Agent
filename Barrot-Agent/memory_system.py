"""
Barrot Advanced Memory System

Implements multi-tier memory architecture:
- Episodic Memory: Events and experiences
- Semantic Memory: Knowledge and concepts
- Working Memory: Active context buffer

Inspired by cognitive neuroscience and modern AI agent frameworks
including LangChain memory systems and RAG architectures.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque


@dataclass
class EpisodicMemoryEntry:
    """Entry in episodic memory - specific event or experience"""
    timestamp: str
    event_type: str
    description: str
    context: Dict[str, Any]
    outcome: Optional[str] = None
    importance: float = 0.5  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticMemoryEntry:
    """Entry in semantic memory - general knowledge"""
    concept: str
    knowledge: str
    category: str
    confidence: float = 0.8  # 0.0 to 1.0
    source: str = "learned"
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    access_count: int = 0
    related_concepts: List[str] = field(default_factory=list)


@dataclass
class WorkingMemoryItem:
    """Item in working memory - active context"""
    key: str
    value: Any
    timestamp: str
    ttl_seconds: int = 3600  # Time to live
    priority: int = 1  # Higher = more important


class EpisodicMemory:
    """
    Episodic Memory System
    
    Stores specific events, interactions, and experiences with temporal
    context. Enables the agent to remember and learn from past actions.
    """
    
    def __init__(
        self,
        storage_path: str = "memory-bundles/episodic-memory.json",
        max_entries: int = 10000,
        retention_days: int = 365
    ):
        self.storage_path = storage_path
        self.max_entries = max_entries
        self.retention_days = retention_days
        self.entries: List[EpisodicMemoryEntry] = []
        self._load_from_disk()
    
    def remember(
        self,
        event_type: str,
        description: str,
        context: Dict[str, Any],
        outcome: Optional[str] = None,
        importance: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Store a new episodic memory
        
        Args:
            event_type: Type of event (e.g., 'task_execution', 'interaction')
            description: Human-readable description
            context: Contextual information
            outcome: Result or outcome of the event
            importance: Importance score (0.0-1.0)
            tags: Optional tags for categorization
            
        Returns:
            Memory ID (timestamp)
        """
        entry = EpisodicMemoryEntry(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            description=description,
            context=context,
            outcome=outcome,
            importance=importance,
            tags=tags or []
        )
        
        self.entries.append(entry)
        self._maintain_size_limit()
        self._save_to_disk()
        
        return entry.timestamp
    
    def recall(
        self,
        event_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        time_range: Optional[Tuple[str, str]] = None,
        min_importance: float = 0.0,
        limit: int = 10
    ) -> List[EpisodicMemoryEntry]:
        """
        Retrieve episodic memories matching criteria
        
        Args:
            event_type: Filter by event type
            tags: Filter by tags (any match)
            time_range: Filter by time (start, end) ISO format
            min_importance: Minimum importance threshold
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        results = []
        
        for entry in reversed(self.entries):  # Most recent first
            # Apply filters
            if event_type and entry.event_type != event_type:
                continue
            
            if tags and not any(tag in entry.tags for tag in tags):
                continue
            
            if time_range:
                if entry.timestamp < time_range[0] or entry.timestamp > time_range[1]:
                    continue
            
            if entry.importance < min_importance:
                continue
            
            results.append(entry)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_recent_context(self, count: int = 5) -> str:
        """Get recent memories as context string"""
        recent = self.entries[-count:] if len(self.entries) >= count else self.entries
        context_parts = []
        
        for entry in recent:
            context_parts.append(
                f"[{entry.timestamp}] {entry.event_type}: {entry.description}"
            )
        
        return "\n".join(context_parts)
    
    def _maintain_size_limit(self):
        """Keep memory size within limits"""
        if len(self.entries) > self.max_entries:
            # Remove oldest, low-importance entries
            self.entries.sort(key=lambda e: (e.importance, e.timestamp))
            self.entries = self.entries[-(self.max_entries):]
            self.entries.sort(key=lambda e: e.timestamp)
    
    def _load_from_disk(self):
        """Load memories from disk"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.entries = [
                        EpisodicMemoryEntry(**entry) for entry in data
                    ]
            except Exception as e:
                print(f"Warning: Could not load episodic memory: {e}")
    
    def _save_to_disk(self):
        """Save memories to disk"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(
                    [asdict(entry) for entry in self.entries],
                    f,
                    indent=2
                )
        except Exception as e:
            print(f"Warning: Could not save episodic memory: {e}")


class SemanticMemory:
    """
    Semantic Memory System
    
    Stores general knowledge, facts, concepts, and learned patterns.
    Provides fast access to abstract knowledge independent of specific episodes.
    """
    
    def __init__(self, storage_path: str = "memory-bundles/semantic-memory.json"):
        self.storage_path = storage_path
        self.knowledge_base: Dict[str, SemanticMemoryEntry] = {}
        self.category_index: Dict[str, List[str]] = defaultdict(list)
        self._load_from_disk()
    
    def learn(
        self,
        concept: str,
        knowledge: str,
        category: str,
        confidence: float = 0.8,
        source: str = "learned",
        related_concepts: Optional[List[str]] = None
    ) -> bool:
        """
        Store or update semantic knowledge
        
        Args:
            concept: Concept identifier
            knowledge: Knowledge content
            category: Knowledge category
            confidence: Confidence level (0.0-1.0)
            source: Source of knowledge
            related_concepts: Related concept identifiers
            
        Returns:
            True if new knowledge, False if updated
        """
        is_new = concept not in self.knowledge_base
        
        entry = SemanticMemoryEntry(
            concept=concept,
            knowledge=knowledge,
            category=category,
            confidence=confidence,
            source=source,
            last_updated=datetime.utcnow().isoformat(),
            access_count=0,
            related_concepts=related_concepts or []
        )
        
        self.knowledge_base[concept] = entry
        
        # Update category index
        if category not in self.category_index:
            self.category_index[category] = []
        if concept not in self.category_index[category]:
            self.category_index[category].append(concept)
        
        self._save_to_disk()
        return is_new
    
    def retrieve(
        self,
        concept: str,
        include_related: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve semantic knowledge
        
        Args:
            concept: Concept to retrieve
            include_related: Whether to include related concepts
            
        Returns:
            Knowledge entry or None
        """
        if concept not in self.knowledge_base:
            return None
        
        entry = self.knowledge_base[concept]
        entry.access_count += 1
        
        result = asdict(entry)
        
        if include_related:
            related = {}
            for related_concept in entry.related_concepts:
                if related_concept in self.knowledge_base:
                    related[related_concept] = self.knowledge_base[related_concept].knowledge
            result['related_knowledge'] = related
        
        self._save_to_disk()  # Save updated access count
        return result
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search semantic memory
        
        Args:
            query: Search query (simple keyword matching)
            category: Filter by category
            min_confidence: Minimum confidence threshold
            limit: Maximum results
            
        Returns:
            List of matching knowledge entries
        """
        query_lower = query.lower()
        results = []
        
        for concept, entry in self.knowledge_base.items():
            # Apply filters
            if category and entry.category != category:
                continue
            
            if entry.confidence < min_confidence:
                continue
            
            # Simple keyword matching
            if (query_lower in concept.lower() or 
                query_lower in entry.knowledge.lower()):
                results.append(asdict(entry))
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_category(self, category: str) -> List[str]:
        """Get all concepts in a category"""
        return self.category_index.get(category, [])
    
    def _load_from_disk(self):
        """Load knowledge from disk"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for concept, entry_data in data.items():
                        entry = SemanticMemoryEntry(**entry_data)
                        self.knowledge_base[concept] = entry
                        
                        # Rebuild category index
                        if entry.category not in self.category_index:
                            self.category_index[entry.category] = []
                        if concept not in self.category_index[entry.category]:
                            self.category_index[entry.category].append(concept)
            except Exception as e:
                print(f"Warning: Could not load semantic memory: {e}")
    
    def _save_to_disk(self):
        """Save knowledge to disk"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                concept: asdict(entry)
                for concept, entry in self.knowledge_base.items()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save semantic memory: {e}")


class WorkingMemory:
    """
    Working Memory System
    
    Manages immediate, active context with automatic expiration.
    Similar to RAM - fast access but limited capacity and duration.
    """
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.buffer: Dict[str, WorkingMemoryItem] = {}
        self.access_queue = deque()  # For LRU eviction
    
    def store(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 3600,
        priority: int = 1
    ):
        """
        Store item in working memory
        
        Args:
            key: Item key
            value: Item value
            ttl_seconds: Time to live in seconds
            priority: Priority level (higher = more important)
        """
        item = WorkingMemoryItem(
            key=key,
            value=value,
            timestamp=datetime.utcnow().isoformat(),
            ttl_seconds=ttl_seconds,
            priority=priority
        )
        
        self.buffer[key] = item
        self.access_queue.append(key)
        
        self._cleanup_expired()
        self._maintain_size()
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve item from working memory
        
        Args:
            key: Item key
            
        Returns:
            Item value or None
        """
        if key not in self.buffer:
            return None
        
        item = self.buffer[key]
        
        # Check if expired
        timestamp = datetime.fromisoformat(item.timestamp)
        if (datetime.utcnow() - timestamp).total_seconds() > item.ttl_seconds:
            del self.buffer[key]
            return None
        
        # Update access order
        if key in self.access_queue:
            self.access_queue.remove(key)
        self.access_queue.append(key)
        
        return item.value
    
    def get_all_active(self) -> Dict[str, Any]:
        """Get all non-expired items"""
        self._cleanup_expired()
        return {key: item.value for key, item in self.buffer.items()}
    
    def clear(self):
        """Clear all working memory"""
        self.buffer.clear()
        self.access_queue.clear()
    
    def get_context_summary(self) -> str:
        """Get summary of current working memory state"""
        self._cleanup_expired()
        items = list(self.buffer.items())
        
        if not items:
            return "Working memory: empty"
        
        summary_parts = [f"Working memory: {len(items)} active items"]
        for key, item in items[:5]:  # Show first 5
            summary_parts.append(f"  - {key}: {type(item.value).__name__}")
        
        if len(items) > 5:
            summary_parts.append(f"  ... and {len(items) - 5} more")
        
        return "\n".join(summary_parts)
    
    def _cleanup_expired(self):
        """Remove expired items"""
        now = datetime.utcnow()
        expired_keys = []
        
        for key, item in self.buffer.items():
            timestamp = datetime.fromisoformat(item.timestamp)
            if (now - timestamp).total_seconds() > item.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.buffer[key]
            if key in self.access_queue:
                self.access_queue.remove(key)
    
    def _maintain_size(self):
        """Maintain size limit using LRU with priority"""
        while len(self.buffer) > self.max_size:
            # Find lowest priority, least recently used item
            candidates = []
            for key in self.access_queue:
                if key in self.buffer:
                    candidates.append((self.buffer[key].priority, key))
            
            if not candidates:
                break
            
            candidates.sort()  # Sort by priority
            evict_key = candidates[0][1]
            
            del self.buffer[evict_key]
            self.access_queue.remove(evict_key)


class MemoryManager:
    """
    Unified Memory Management System
    
    Orchestrates episodic, semantic, and working memory systems,
    providing a unified interface and cross-memory operations.
    """
    
    def __init__(
        self,
        episodic_config: Optional[Dict] = None,
        semantic_config: Optional[Dict] = None,
        working_config: Optional[Dict] = None
    ):
        self.episodic = EpisodicMemory(**(episodic_config or {}))
        self.semantic = SemanticMemory(**(semantic_config or {}))
        self.working = WorkingMemory(**(working_config or {}))
    
    def store_experience(
        self,
        event_type: str,
        description: str,
        context: Dict[str, Any],
        outcome: Optional[str] = None,
        extract_knowledge: bool = True
    ) -> str:
        """
        Store an experience in episodic memory and optionally extract knowledge
        
        Args:
            event_type: Type of event
            description: Description
            context: Context information
            outcome: Outcome
            extract_knowledge: Whether to extract semantic knowledge
            
        Returns:
            Memory ID
        """
        # Store in episodic memory
        memory_id = self.episodic.remember(
            event_type=event_type,
            description=description,
            context=context,
            outcome=outcome
        )
        
        # Optionally extract and store knowledge
        if extract_knowledge and outcome:
            # Simple pattern extraction (can be enhanced with ML)
            concept = f"{event_type}_pattern"
            knowledge = f"When {description}, outcome was: {outcome}"
            self.semantic.learn(
                concept=concept,
                knowledge=knowledge,
                category=event_type,
                source="experience"
            )
        
        return memory_id
    
    def get_relevant_context(
        self,
        task: str,
        include_episodic: bool = True,
        include_semantic: bool = True,
        include_working: bool = True
    ) -> str:
        """
        Retrieve relevant context from all memory systems
        
        Args:
            task: Current task
            include_episodic: Include episodic memories
            include_semantic: Include semantic knowledge
            include_working: Include working memory
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        if include_working:
            working_summary = self.working.get_context_summary()
            context_parts.append(f"## Current Context\n{working_summary}")
        
        if include_episodic:
            recent = self.episodic.get_recent_context(count=5)
            if recent:
                context_parts.append(f"## Recent Experiences\n{recent}")
        
        if include_semantic:
            # Search for relevant knowledge
            knowledge = self.semantic.search(task, limit=5)
            if knowledge:
                knowledge_str = "\n".join([
                    f"- {k['concept']}: {k['knowledge']}"
                    for k in knowledge
                ])
                context_parts.append(f"## Relevant Knowledge\n{knowledge_str}")
        
        return "\n\n".join(context_parts)
    
    def consolidate_memories(self):
        """
        Perform memory consolidation - transfer important patterns
        from episodic to semantic memory
        """
        # Get high-importance episodic memories
        important_memories = self.episodic.recall(
            min_importance=0.7,
            limit=100
        )
        
        # Extract patterns by event type
        patterns = defaultdict(list)
        for memory in important_memories:
            if memory.outcome:
                patterns[memory.event_type].append({
                    'description': memory.description,
                    'outcome': memory.outcome
                })
        
        # Store consolidated patterns as semantic knowledge
        for event_type, experiences in patterns.items():
            if len(experiences) >= 3:  # Need multiple examples
                concept = f"{event_type}_consolidated_pattern"
                knowledge = f"Pattern observed {len(experiences)} times in {event_type} events"
                
                self.semantic.learn(
                    concept=concept,
                    knowledge=knowledge,
                    category=f"{event_type}_patterns",
                    confidence=0.8,
                    source="consolidation"
                )


# Example usage and testing
if __name__ == "__main__":
    print("Barrot Advanced Memory System")
    print("=" * 50)
    
    # Initialize memory manager
    manager = MemoryManager()
    
    # Test episodic memory
    print("\n1. Testing Episodic Memory:")
    memory_id = manager.episodic.remember(
        event_type="framework_analysis",
        description="Analyzed LangChain framework",
        context={"framework": "LangChain", "features": ["modular", "chains"]},
        outcome="Identified ReAct pattern as beneficial",
        importance=0.8,
        tags=["analysis", "langchain"]
    )
    print(f"Stored memory: {memory_id}")
    
    # Test semantic memory
    print("\n2. Testing Semantic Memory:")
    manager.semantic.learn(
        concept="ReAct_algorithm",
        knowledge="Combines reasoning and acting in cycles: Thought -> Action -> Observation",
        category="algorithms",
        confidence=0.9,
        related_concepts=["chain_of_thought", "toolformer"]
    )
    print("Stored knowledge about ReAct algorithm")
    
    # Test working memory
    print("\n3. Testing Working Memory:")
    manager.working.store(
        key="current_task",
        value="Framework enhancement implementation",
        ttl_seconds=7200,
        priority=5
    )
    print("Stored current task in working memory")
    
    # Get relevant context
    print("\n4. Getting Relevant Context:")
    context = manager.get_relevant_context("ReAct implementation")
    print(context[:200] + "...")
    
    print("\n" + "=" * 50)
    print("Memory system initialized successfully!")
