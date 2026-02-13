# Research Patterns for AI Agents

Extended methodology and patterns for effective online research.

## Core Principles

### 1. External Over Internal

**Mandate**: Prefer web search over training data for discovery tasks.

Training data is:
- Static (knowledge cutoff)
- Potentially outdated
- Missing recent developments
- Subject to hallucination risk

Web search provides:
- Current information
- Verifiable sources
- Multiple perspectives
- Citation chains

**Application**: When researching, always search first. Use training knowledge only to:
- Frame initial queries
- Recognize terminology
- Evaluate source quality

### 2. Progressive Refinement

Research is iterative. Each search informs the next.

```
Round 1: Broad → Discover vocabulary
Round 2: Specific → Target promising areas
Round 3: Deep → Exhaustive coverage
Round 4: Synthesis → Connect findings
```

### 3. Multi-Angle Coverage

Same topic, different entry points:

| Angle | Query Pattern | Discovers |
|-------|---------------|-----------|
| Tool-centric | "{tool} for {task}" | Specific solutions |
| Problem-centric | "how to {task}" | Approaches, not just tools |
| Comparison | "{tool A} vs {tool B}" | Trade-offs, alternatives |
| Migration | "migrate from {old} to {new}" | Transition paths |
| Critique | "{tool} problems issues" | Limitations, edge cases |

## Query Engineering

### Effective Patterns

**Temporal anchoring**
```
"{topic} 2026"
"{topic} latest"
"{topic} new release"
```

**Exact phrase matching**
```
"JSON Schema to PostgreSQL"
"spec to SQL"
"type-safe database"
```

**Ecosystem scoping**
```
"{topic} TypeScript"
"{topic} Go library"
"{topic} Python package"
```

**Community signals**
```
"{topic} github stars"
"{topic} actively maintained"
"{topic} production ready"
```

**Documentation patterns**
```
"{tool} documentation"
"{tool} getting started"
"{tool} API reference"
```

### Query Refinement Flow

```
Initial: "database schema generation"
         ↓ Too broad, thousands of results
Refined: "database schema generation from specification"
         ↓ Better, but still generic
Targeted: "OpenAPI to PostgreSQL schema generation"
         ↓ Specific, actionable results
Exhaustive: "OpenAPI to PostgreSQL DDL library npm"
         ↓ Ecosystem-specific, implementation-ready
```

## Source Evaluation

### Credibility Indicators

**High credibility:**
- Official project documentation
- GitHub README with >1000 stars
- Technical blog posts with code examples
- Conference presentations (PyCon, JSConf, etc.)
- Academic papers (for foundational concepts)

**Medium credibility:**
- Stack Overflow accepted answers (check date)
- Medium/Dev.to posts (verify author expertise)
- Tutorial sites (check code correctness)
- Reddit discussions (check voting patterns)

**Low credibility:**
- AI-generated listicles
- SEO-optimized aggregator sites
- Outdated documentation (>2 years old for fast-moving fields)
- Marketing pages without technical depth

### Recency Considerations

| Domain | Freshness Threshold | Reason |
|--------|---------------------|--------|
| JavaScript ecosystem | 6-12 months | Rapid evolution |
| Database tools | 1-2 years | More stable |
| API specifications | 1-2 years | Versioned standards |
| Language features | Per-version | Check against target version |

## Discovery Patterns

### Pattern 1: Snowball Discovery

Start with one known tool, follow references.

```
1. Search: "Prisma schema migration"
2. Find: Prisma docs mention Drizzle as alternative
3. Search: "Drizzle ORM migration"
4. Find: Drizzle docs compare to TypeORM
5. Search: "TypeORM vs Prisma vs Drizzle"
6. Result: Comprehensive ORM landscape
```

### Pattern 2: Taxonomy Building

Categorize as you discover.

```
Spec-to-SQL Tools
├── ORM-based
│   ├── Prisma
│   ├── Drizzle
│   └── TypeORM
├── Specification-based
│   ├── OpenAPI Generator
│   └── JSON Schema parsers
├── DSL-based
│   ├── DBML
│   └── Atlas HCL
└── AI-assisted
    ├── AI2sql
    └── Workik
```

### Pattern 3: Reverse Discovery

Search the opposite direction.

```
Goal: Find tools that generate SQL from specs
Reverse: "generate TypeScript from SQL schema"
Finds: Tools like pg-to-ts, Schemats
Insight: Many tools are bidirectional or have sister projects
```

### Pattern 4: Ecosystem Mapping

Map tools to their communities.

```
TypeScript ecosystem:
  - Prisma (large community, well-funded)
  - Drizzle (growing, performance-focused)
  - json-schema-to-sql (smaller, focused)

Go ecosystem:
  - Atlas (modern, Terraform-like)
  - sqlc (SQL-first, type-safe)
  - ent (Facebook, graph-oriented)

Python ecosystem:
  - SQLAlchemy + Alembic (mature, standard)
  - jsonschema2ddl (specialized)
```

## Synthesis Techniques

### Comparison Matrix

Build matrices to compare findings:

```markdown
| Tool | Input | Output | Languages | Maturity | Active |
|------|-------|--------|-----------|----------|--------|
| Prisma | PSL | SQL | TS/JS | High | Yes |
| Drizzle | TS | SQL | TS/JS | Medium | Yes |
| Atlas | HCL/SQL | SQL | Go | High | Yes |
```

### Decision Tree

Structure recommendations as decisions:

```
Need schema generation?
├── Have existing TypeScript codebase?
│   ├── Yes → Prisma or Drizzle
│   └── No → Continue
├── Have OpenAPI specification?
│   ├── Yes → OpenAPI Generator
│   └── No → Continue
├── Need database-agnostic design?
│   ├── Yes → DBML
│   └── No → Continue
└── Starting fresh?
    └── Consider Atlas HCL for IaC workflow
```

### Gap Analysis

Identify what tools don't cover:

```
Well-covered:
- TypeScript ORM-based migrations
- PostgreSQL schema generation
- OpenAPI to MySQL

Gaps:
- Protobuf to PostgreSQL (limited options)
- GraphQL to SQL (mostly reverse direction)
- Multi-database sync from single spec
```

## Anti-Patterns to Avoid

### 1. First-Result Bias

**Problem**: Accepting first search result as complete answer.
**Fix**: Always execute 3+ search queries with different angles.

### 2. Recency Obsession

**Problem**: Only considering tools from last year.
**Fix**: Include mature tools. Stability has value.

### 3. Star Worship

**Problem**: Equating GitHub stars with quality.
**Fix**: Check issues, recent commits, documentation quality.

### 4. Marketing Acceptance

**Problem**: Trusting tool marketing claims.
**Fix**: Find independent reviews, GitHub issues, community feedback.

### 5. Ecosystem Lock-in

**Problem**: Only searching one language ecosystem.
**Fix**: Cross-pollinate ideas. Go tools may inspire TypeScript choices.

### 6. Shallow Listing

**Problem**: Creating lists without analysis.
**Fix**: Always categorize, compare, and recommend.

## Output Structure

### Standard Discovery Report

```markdown
# {Domain} Discovery Report

## Executive Summary
{2-3 sentence overview of the landscape}

## Categories
{Taxonomy of discovered tools/approaches}

## Tool Catalog
{Detailed entries for each tool}

## Comparison Matrix
{Feature/capability comparison table}

## Recommendations
{Contextual recommendations by use case}

## Gaps and Opportunities
{What's missing or underserved}

## Sources
{All URLs referenced during research}
```

### Quick Reference Card

```markdown
## {Domain} Quick Reference

### Best For {Use Case 1}
- **Recommended**: {Tool}
- **Alternative**: {Tool}

### Best For {Use Case 2}
- **Recommended**: {Tool}
- **Alternative**: {Tool}

### Avoid If
- {Anti-pattern/constraint}: Don't use {Tool}
```
