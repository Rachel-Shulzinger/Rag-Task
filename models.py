import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

# =====================================================================
# 📑 חלק א': סכמות עזר עבור מקורות המידע והמיקומים הפיזיים בקבצים
# =====================================================================

class FileMeta(BaseModel):
    path: str = Field(..., description="The absolute or relative path to the markdown file.")
    last_modified: str = Field(..., description="ISO 8601 timestamp of when the file was last modified.")
    hash: str = Field(..., description="SHA-256 hash of the file content to identify changes.")

class SourceMeta(BaseModel):
    tool: str = Field(..., description="The tool name: 'cursor', 'claude_code', or 'kiro'.")
    root_path: str = Field(..., description="The root directory path for this tool's config/notes.")
    files: List[FileMeta] = Field(default=[], description="List of processed files under this tool.")

class SourceLocation(BaseModel):
    tool: str = Field(..., description="The tool identity from which this item was extracted.")
    file: str = Field(..., description="The exact file path containing this information.")
    anchor: str = Field(..., description="The nearest markdown heading or anchor, e.g., '#db' or '## UI Rules'.")
    line_range: List[int] = Field(..., description="The exact starting and ending line numbers as [start, end]. Example: [120, 145]")

# =====================================================================
# 📦 חלק ב': סכמות הפריטים המובנים (Decisions, Rules, Warnings)
# =====================================================================

class DecisionItem(BaseModel):
    id: str = Field(..., description="Unique incremental identifier. Format: 'dec-XXX' (e.g., dec-001).")
    title: str = Field(..., description="Short, concise title of the technical decision.")
    summary: str = Field(..., description="A complete, detailed summary of the architectural choice and its implications.")
    tags: List[str] = Field(default=[], description="Subject tags for indexing, e.g., ['db', 'architecture', 'auth'].")
    source: SourceLocation = Field(..., description="Precise physical source location within the codebase documentation.")
    observed_at: str = Field(..., description="ISO 8601 timestamp representing when this item was extracted or noted.")

class RuleItem(BaseModel):
    id: str = Field(..., description="Unique incremental identifier. Format: 'rule-XXX' or 'rule-topic-XXX'.")
    rule: str = Field(..., description="The explicit rule, constraint, or development guideline stated in the file.")
    scope: str = Field(..., description="The system scope affected by this rule, e.g., 'ui', 'backend', 'security', 'general'.")
    notes: Optional[str] = Field(default="", description="Any exceptions, special notes, or edge cases related to this rule.")
    source: SourceLocation = Field(..., description="Precise physical source location within the codebase documentation.")
    observed_at: str = Field(..., description="ISO 8601 timestamp representing when this item was extracted or noted.")

class WarningItem(BaseModel):
    id: str = Field(..., description="Unique incremental identifier. Format: 'warn-XXX'.")
    area: str = Field(..., description="The code module or architecture area marked as sensitive, e.g., 'auth', 'payment'.")
    message: str = Field(..., description="The critical warning message or strict 'do not touch' instruction.")
    severity: str = Field(..., description="Severity level of the warning: 'high', 'medium', or 'low'.")
    source: SourceLocation = Field(..., description="Precise physical source location within the codebase documentation.")
    observed_at: str = Field(..., description="ISO 8601 timestamp representing when this item was extracted or noted.")

# =====================================================================
# 🗺️ חלק ג': סכמת העל (The Root Container Object)
# =====================================================================

class ItemsContainer(BaseModel):
    decisions: List[DecisionItem] = Field(default=[], description="Array of all extracted architectural decisions.")
    rules: List[RuleItem] = Field(default=[], description="Array of all extracted development rules/guidelines.")
    warnings: List[WarningItem] = Field(default=[], description="Array of all extracted warnings or code sensitivities.")

class ProjectKnowledgeSchema(BaseModel):
    schema_version: str = Field(default="1.0", description="The current version of the data schema blueprint.")
    generated_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp indicating exactly when this data payload was generated."
    )
    sources: List[SourceMeta] = Field(default=[], description="Metadata detailing the tools and files scanned during ingestion.")
    items: ItemsContainer = Field(..., description="The main inventory container encapsulating all structured items found.")