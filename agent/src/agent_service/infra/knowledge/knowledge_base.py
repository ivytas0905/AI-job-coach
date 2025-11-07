"""
Knowledge Base Manager for Resume Optimization

This module loads and manages structured knowledge documents including:
- Powerful verbs categorization
- STAR framework guidelines
- Anti-hallucination rules
- Quantification guidelines
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Hint:
    """A hint to show the user for improving their resume bullet"""
    type: str
    message: str
    follow_up_question: Optional[str] = None
    placeholder: Optional[str] = None


class KnowledgeBase:
    """
    Manages structured knowledge for resume optimization.

    Loads and provides access to:
    - Powerful verbs by category
    - STAR framework principles
    - Anti-hallucination rules
    - Quantification guidelines
    """

    def __init__(self, knowledge_dir: Optional[str] = None):
        """
        Initialize knowledge base.

        Args:
            knowledge_dir: Path to knowledge base directory
                          (defaults to project root/knowledge_base)
        """
        if knowledge_dir is None:
            # Default to project root/knowledge_base
            current_file = Path(__file__)
            project_root = current_file.parents[4]  # Navigate up to project root
            knowledge_dir = project_root / "knowledge_base"

        self.knowledge_dir = Path(knowledge_dir)

        # Load all knowledge documents
        self.powerful_verbs = self._load_powerful_verbs()
        self.star_framework = self._load_star_framework()
        self.anti_hallucination_rules = self._load_anti_hallucination_rules()
        self.quantification_guidelines = self._load_quantification_guidelines()

    def _load_powerful_verbs(self) -> Dict[str, Any]:
        """Load powerful verbs categorization."""
        filepath = self.knowledge_dir / "powerful_verbs.json"
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            return {"categories": {}, "usage_rules": [], "avoid_list": []}

        with open(filepath, 'r') as f:
            return json.load(f)

    def _load_star_framework(self) -> str:
        """Load STAR framework guidelines."""
        filepath = self.knowledge_dir / "star_framework.md"
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            return ""

        with open(filepath, 'r') as f:
            return f.read()

    def _load_anti_hallucination_rules(self) -> Dict[str, Any]:
        """Load anti-hallucination rules."""
        filepath = self.knowledge_dir / "anti_hallucination_rules.json"
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            return {"core_principles": [], "validation_rules": {}, "hints_to_generate": []}

        with open(filepath, 'r') as f:
            return json.load(f)

    def _load_quantification_guidelines(self) -> str:
        """Load quantification guidelines."""
        filepath = self.knowledge_dir / "quantification_guidelines.md"
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            return ""

        with open(filepath, 'r') as f:
            return f.read()

    def get_verbs_by_category(self, category: str) -> List[str]:
        """
        Get list of verbs for a specific category.

        Args:
            category: Category name (e.g., 'innovation_creation', 'leadership_initiative')

        Returns:
            List of verbs in that category
        """
        categories = self.powerful_verbs.get("categories", {})
        category_data = categories.get(category, {})
        return category_data.get("verbs", [])

    def get_all_verb_categories(self) -> Dict[str, List[str]]:
        """Get all verb categories with their verbs."""
        return {
            category: data.get("verbs", [])
            for category, data in self.powerful_verbs.get("categories", {}).items()
        }

    def get_avoid_verbs(self) -> List[str]:
        """Get list of weak verbs to avoid."""
        return self.powerful_verbs.get("avoid_list", [])

    def get_verb_usage_rules(self) -> List[str]:
        """Get verb usage rules."""
        return self.powerful_verbs.get("usage_rules", [])

    def get_anti_hallucination_principles(self) -> List[str]:
        """Get core anti-hallucination principles."""
        return self.anti_hallucination_rules.get("core_principles", [])

    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules for different aspects."""
        return self.anti_hallucination_rules.get("validation_rules", {})

    def analyze_bullet_for_hints(self, bullet: str) -> List[Hint]:
        """
        Analyze a bullet point and generate hints for improvement.

        Args:
            bullet: Original bullet point text

        Returns:
            List of hints for user
        """
        hints = []

        # Check for quantification
        has_numbers = any(char.isdigit() for char in bullet)
        has_percentage = '%' in bullet

        if not has_numbers:
            hints.append(Hint(
                type="quantification",
                message="💡 **Add Scale**: Consider adding numbers to show the scale of your work",
                follow_up_question="How many users/systems/items were involved?",
                placeholder="[X users/systems]"
            ))

        if not has_percentage:
            hints.append(Hint(
                type="improvement_metric",
                message="💡 **Add Impact**: Consider adding percentage improvement",
                follow_up_question="By what percentage did performance/efficiency improve?",
                placeholder="[Y% improvement]"
            ))

        # Check for weak verbs
        first_word = bullet.split()[0].lower() if bullet else ""
        weak_verbs = self.get_avoid_verbs()
        if any(weak in first_word for weak in weak_verbs):
            hints.append(Hint(
                type="weak_verb",
                message="💡 **Stronger Verb**: Consider using a more impactful action verb",
                follow_up_question="What was your main contribution? (created, led, improved, etc.)"
            ))

        # Check for vague terms
        vague_terms = ["many", "several", "various", "multiple", "some", "improved", "helped"]
        if any(term in bullet.lower() for term in vague_terms):
            hints.append(Hint(
                type="specificity",
                message="💡 **Be Specific**: Replace vague terms with specific numbers and details",
                follow_up_question="Can you provide specific numbers or details?"
            ))

        # Check for technology mention
        tech_keywords = ["system", "application", "platform", "tool", "software"]
        has_tech_mention = any(keyword in bullet.lower() for keyword in tech_keywords)
        has_specific_tech = any(tech in bullet for tech in ["Python", "Java", "React", "AWS", "SQL"])

        if has_tech_mention and not has_specific_tech:
            hints.append(Hint(
                type="technology",
                message="💡 **Specify Technologies**: Consider naming the specific technologies/tools used",
                follow_up_question="Which specific technologies, frameworks, or tools did you use?",
                placeholder="[e.g., Python, React, AWS]"
            ))

        return hints

    def get_star_framework_summary(self) -> str:
        """Get concise STAR framework summary for prompts."""
        return """
STAR Framework:
- Situation/Task: Brief context (optional)
- Action: What you did (strong action verb)
- Result: Quantifiable impact with numbers

Formula: [Action Verb] + [What you did] + [How/Tools] + [Quantifiable Result]
Example: "Built automated pipeline using pytest, reducing bug rate by 60%"
"""

    def build_optimization_context(self) -> str:
        """
        Build comprehensive context for AI optimization.

        Returns:
            Formatted string with all relevant knowledge
        """
        verb_categories = self.get_all_verb_categories()

        context = f"""
# Resume Optimization Knowledge Base

## STAR Framework
{self.get_star_framework_summary()}

## Powerful Verbs by Category
"""
        for category, verbs in verb_categories.items():
            context += f"\n**{category.replace('_', ' ').title()}**: {', '.join(verbs[:10])}\n"

        context += f"""
## Verb Usage Rules
{chr(10).join('- ' + rule for rule in self.get_verb_usage_rules())}

## Anti-Hallucination Principles
{chr(10).join('- ' + principle for principle in self.get_anti_hallucination_principles())}

## Key Reminders
- NEVER invent facts, numbers, or technologies not in the original
- ALWAYS ask for clarification when information is missing
- Use varied verbs - avoid repetition
- Base ALL optimizations on user-provided information
"""

        return context


# Global instance
_knowledge_base = None

def get_knowledge_base() -> KnowledgeBase:
    """Get singleton knowledge base instance."""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base
