from app.dependencies.rules import RULES, _index
from app.models.relationship import Relationship
from app.models.resource import Resource


class DependencyEngine:
    def __init__(self, rules=None) -> None:
        self.rules = rules or RULES

    def build(self, resources: list[Resource]) -> list[Relationship]:
        index = _index(resources)
        seen: set[tuple[str, str, str]] = set()
        relationships: list[Relationship] = []
        for rule in self.rules:
            for rel in rule(resources, index):
                key = (rel.source, rel.target, rel.relationship)
                if key in seen:
                    continue
                if rel.source == rel.target:
                    continue
                if not any(item.id == rel.source for item in resources):
                    continue
                if not any(item.id == rel.target for item in resources):
                    continue
                seen.add(key)
                relationships.append(rel)
        return relationships
