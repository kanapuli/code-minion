from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class IssueSeverity(Enum):
    """Enumeration of possible issue severities"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class CodeIssue:
    """Represents a code issue found during analysis"""

    file_path: str
    line_number: Optional[int]
    severity: IssueSeverity
    message: str
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    analyzer_name: str = ""
    issue_type: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Container for analysis results"""

    issues: List[CodeIssue] = field(default_factory=list)
    summary: str = ""
    analyzer_name: str = ""
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisContext:
    """Provides the context information for the analyzers"""

    repository_path: str
    target_files: List[str] = field(default_factory=list)
    base_revision: Optional[str] = None
    ignore_patterns: List[str] = field(default_factory=list)
    max_files: int = 100
    max_file_size: int = 1_000_000  # 1 MB
    metadata: Dict[str, Any] = field(default_factory=dict)
