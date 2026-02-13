# Spec-to-SQL Discovery Report

## Executive Summary

The spec-to-SQL landscape offers diverse approaches: ORM-based migration systems (Prisma, Drizzle), specification parsers (OpenAPI Generator, JSON Schema tools), declarative DSLs (DBML, Atlas HCL), and AI-assisted generators. TypeScript/JavaScript ecosystem has the richest tooling. PostgreSQL enjoys the broadest support.

## Categories

```
Spec-to-SQL Tools
├── Declarative Schema DSLs
│   ├── DBML (database-agnostic, visual)
│   └── Atlas HCL (Terraform-like, IaC)
├── ORM Migration Systems
│   ├── Prisma (TypeScript, PSL)
│   ├── Drizzle (TypeScript, native)
│   ├── TypeORM (TypeScript, decorators)
│   └── SQLAlchemy+Alembic (Python)
├── Specification Parsers
│   ├── OpenAPI Generator (mysql-schema)
│   ├── jsonschema2ddl (Python)
│   ├── json-schema-to-sql (JS)
│   └── graphql-to-sql
├── Protocol Buffer Tools
│   ├── proto-sql
│   └── protobuf-sql
├── Type Generators (reverse)
│   ├── sqlc (SQL→Go/Python)
│   ├── pg-to-ts (PG→TS)
│   └── Schemats (DB→TS)
└── AI-Assisted
    ├── AI2sql
    ├── Workik
    └── DbSchema
```

## Comparison Matrix

| Tool | Input Format | Output | Languages | DB Support | Maturity |
|------|--------------|--------|-----------|------------|----------|
| Prisma | PSL | SQL migrations | TS/JS | PG, MySQL, SQLite, SQLServer, Cockroach | High |
| Drizzle | TypeScript | SQL migrations | TS/JS | PG, MySQL, SQLite | Medium |
| Atlas | HCL/SQL/ORM | SQL migrations | Any | PG, MySQL, SQLite, SQLServer, Cockroach, ClickHouse | High |
| DBML | DBML | SQL DDL | Any (CLI) | PG, MySQL, SQLite, SQLServer | High |
| OpenAPI Gen | OpenAPI | MySQL DDL | Any | MySQL | Medium |
| jsonschema2ddl | JSON Schema | PG DDL | Python | PG, Redshift | Medium |
| json-schema-to-sql | JSON Schema | SQL DDL | JS/TS | PG, MySQL | Low |
| sqlc | SQL queries | Type-safe code | Go, Python, Kotlin | PG, MySQL, SQLite | High |

## Recommendations

### For TypeScript Projects
**Recommended**: Prisma
- Rich ecosystem, excellent DX, strong community
- Declarative schema with type-safe client generation

**Alternative**: Drizzle
- More SQL-like, better performance characteristics
- Growing community, modern approach

### For OpenAPI-First Development
**Recommended**: OpenAPI Generator (mysql-schema)
- Direct specification-to-schema path
- Maintained by large open-source community

**Limitation**: MySQL only. For PostgreSQL, consider manual mapping or combining with json-schema-to-sql.

### For Infrastructure-as-Code Workflows
**Recommended**: Atlas
- Terraform-like declarative approach
- Supports HCL, SQL, and ORM schemas
- Versioned and declarative workflows

### For Schema Visualization/Documentation
**Recommended**: DBML + dbdiagram.io
- Human-readable DSL
- Bidirectional SQL conversion
- Visual diagram generation

### For Rapid Prototyping
**Recommended**: AI2sql or Workik
- Natural language to schema
- Quick iteration on ideas

### For SQL-First Development
**Recommended**: sqlc
- Write SQL, generate type-safe code
- Catches type errors at compile time

## Gaps and Opportunities

### Well-Served Areas
- TypeScript ORM migrations
- PostgreSQL schema generation
- OpenAPI → MySQL
- Schema visualization

### Underserved Areas
- Protobuf → PostgreSQL (limited tooling)
- GraphQL → SQL (mostly reverse direction)
- Multi-database sync from single spec
- OpenAPI → PostgreSQL (no direct generator)
- Cross-ORM migration

### Emerging Patterns
- AI-assisted schema design gaining traction
- HCL-based declarative migrations (Atlas)
- SQL-first with type generation (sqlc)

## Sources

### Official Documentation
- [Prisma Migrate](https://www.prisma.io/docs/orm/prisma-migrate)
- [Drizzle ORM Migrations](https://orm.drizzle.team/docs/migrations)
- [Atlas Documentation](https://atlasgo.io/docs)
- [DBML Documentation](https://dbml.dbdiagram.io/docs/)
- [OpenAPI Generator mysql-schema](https://openapi-generator.tech/docs/generators/mysql-schema/)
- [sqlc Documentation](https://sqlc.dev/)

### Libraries and Tools
- [jsonschema2ddl](https://github.com/clarityai-eng/jsonschema2ddl)
- [json-schema-to-sql](https://github.com/VasilVelikov00/json-schema-to-sql)
- [jsonschema2db](https://github.com/better/jsonschema2db)
- [graphql-to-sql](https://github.com/taylorgoolsby/graphql-to-sql)
- [proto-sql](https://github.com/commandus/proto-sql)
- [pg-to-ts](https://github.com/danvk/pg-to-ts)
- [Schemats](https://github.com/SweetIQ/schemats)

### AI-Assisted Tools
- [AI2sql Schema Generator](https://ai2sql.io/sql-schema-generator)
- [Workik AI Database Schema Generator](https://workik.com/ai-powered-database-schema-generator)
- [DbSchema](https://dbschema.com/)

### Related Resources
- [Hasura](https://hasura.io/)
- [Postgraphile](https://www.graphile.org/postgraphile/)
- [DB2OpenAPI](https://zuplo.com/learning-center/generate-openapi-from-database)
