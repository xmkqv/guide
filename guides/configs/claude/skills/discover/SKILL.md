---
name: discover
description: This skill should be used when the user asks to "research", "discover", "explore what exists", "find libraries for", "what tools exist for", "survey the landscape", "learn about approaches to", or mentions conducting online research, technology discovery, or surveying a technical domain. Provides methodology for AI agents to conduct effective web-based research and discovery.
version: 0.1.0
---

# Discover

Research methodology for AI agents conducting online discovery. Emphasizes external exploration over local reflection.

## Purpose

Enable systematic discovery of techniques, libraries, tools, and approaches within a technical domain. Transform open-ended exploration into structured, actionable knowledge.

## When to Use

- Surveying a technical landscape (e.g., "What spec-to-SQL tools exist?")
- Discovering libraries, frameworks, or approaches for a problem domain
- Learning about unfamiliar technology areas
- Gathering options before making architectural decisions
- Building knowledge foundations for implementation planning

## Research Methodology

### Phase 1: Frame the Domain

Before searching, decompose the inquiry into searchable facets:

```
Domain: {primary subject}
├── Core terms: {canonical vocabulary}
├── Adjacent terms: {synonyms, related concepts}
├── Directions: {input → output transformations}
└── Ecosystem: {languages, platforms, communities}
```

**Example: "spec to SQL"**
```
Domain: Specification-driven database schema generation
├── Core: schema generation, DDL, migration, code generation
├── Adjacent: ORM, type-safe SQL, declarative schemas
├── Directions: spec→SQL, SQL→types, bidirectional
└── Ecosystem: TypeScript, Go, Python, Rust, PostgreSQL, MySQL
```

### Phase 2: Search Strategy

Execute searches in waves, building on discoveries:

**Wave 1 - Canonical Tools**
Search for established, well-documented solutions:
- `"{domain} tools libraries {year}"`
- `"{input format} to {output format} generation"`
- `"best {domain} tools"`

**Wave 2 - Format-Specific**
Search by specification format:
- OpenAPI/Swagger → SQL
- JSON Schema → DDL
- GraphQL → database
- Protobuf → SQL
- TypeScript types → SQL

**Wave 3 - Ecosystem-Specific**
Search by language/platform:
- `"{language} {domain} library"`
- `"{framework} schema migration"`

**Wave 4 - Reverse Direction**
Often reveals bidirectional tools:
- SQL → TypeScript types
- Database → OpenAPI
- Schema → documentation

### Phase 3: Categorize Discoveries

Organize findings into a structured taxonomy:

```
Category: {transformation type}
├── Tool: {name}
│   ├── Input: {specification format}
│   ├── Output: {generated artifact}
│   ├── Languages: {supported}
│   └── URL: {reference}
```

**Standard Categories:**
1. **Declarative Schema DSLs** - Purpose-built schema languages
2. **ORM Migration Systems** - Code-first schema generation
3. **Specification Parsers** - OpenAPI, JSON Schema, GraphQL converters
4. **Type-to-Schema** - Language type systems to DDL
5. **AI-Assisted** - Natural language to schema
6. **Bidirectional** - Schema introspection and generation

### Phase 4: Synthesize Findings

Structure the synthesis for actionability:

```markdown
## {Domain} Landscape

### Approaches
| Approach | When to Use | Trade-offs |
|----------|-------------|------------|
| {name}   | {use case}  | {pros/cons}|

### Tool Matrix
| Tool | Input | Output | Maturity | Ecosystem |
|------|-------|--------|----------|-----------|

### Recommendations
- For {scenario}: Consider {tool} because {reason}
```

## Research Best Practices

### Query Construction

**Effective patterns:**
- Include year for currency: `"topic 2026"`
- Use quotes for exact phrases: `"JSON Schema to PostgreSQL"`
- Combine terms: `"{input} to {output} {language}"`
- Search alternatives: `"{topic} alternatives competitors"`

**Avoid:**
- Single-word queries
- Overly broad searches
- Queries without context anchors

### Progressive Refinement

1. Start broad, identify vocabulary
2. Use discovered terms in subsequent searches
3. Follow references and "see also" patterns
4. Cross-reference multiple sources

### Source Evaluation

**High signal sources:**
- Official documentation
- GitHub repositories with activity
- Technical blog posts with code examples
- Conference talks and papers
- Stack Overflow accepted answers

**Low signal sources:**
- AI-generated listicles without depth
- Outdated documentation (check dates)
- Marketing pages without technical content

### Citation Discipline

Always include sources with findings:
```markdown
**{Tool Name}** - {brief description}
- Source: [{Title}]({URL})
- Last updated: {date if available}
```

## Anti-Patterns

**Avoid these research failures:**

1. **Premature Closure** - Stopping at first result
2. **Echo Chamber** - Only searching one ecosystem
3. **Recency Bias** - Ignoring mature, stable tools
4. **Novelty Bias** - Chasing latest over proven
5. **Local Reflection** - Using training data instead of searching
6. **Shallow Synthesis** - Listing without categorizing

## Example Application

**Query**: "What spec-to-SQL techniques and libraries exist?"

**Execution:**
1. Frame: Specification → SQL DDL generation landscape
2. Wave 1: "spec to SQL schema generation tools 2026"
3. Wave 2: "OpenAPI to SQL", "JSON Schema to PostgreSQL", "GraphQL to database"
4. Wave 3: "Prisma schema migration", "Drizzle ORM SQL", "TypeScript to SQL"
5. Wave 4: "SQL to TypeScript types", "database to OpenAPI"
6. Categorize by approach type
7. Synthesize with tool matrix and recommendations

## Additional Resources

### Reference Files
- **`references/spec-to-sql-landscape.md`** - Comprehensive catalog of spec-to-SQL tools
- **`references/research-patterns.md`** - Extended methodology and examples

### Example Output
- **`examples/discovery-report.md`** - Sample discovery report structure
