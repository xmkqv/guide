# Spec-to-SQL Landscape

Comprehensive catalog of techniques and libraries for generating SQL database schemas from specifications.

## Approach Categories

### 1. Declarative Schema DSLs

Purpose-built languages for database schema definition.

#### DBML (Database Markup Language)
- **Input**: `.dbml` files
- **Output**: SQL DDL (MySQL, PostgreSQL, SQLite, SQL Server)
- **Direction**: Bidirectional (sql2dbml, dbml2sql)
- **Ecosystem**: JavaScript/Node.js, CLI
- **URL**: https://dbml.dbdiagram.io/
- **Notes**: Database-agnostic, human-readable. 2.5M+ docs created. Integrates with dbdiagram.io visualization.

#### Atlas HCL
- **Input**: HCL schema files, SQL, or ORM definitions
- **Output**: SQL migrations (MySQL, PostgreSQL, SQLite, SQL Server, CockroachDB, ClickHouse)
- **Direction**: Bidirectional (schema inspect, schema apply)
- **Ecosystem**: Go, CLI, Terraform integration
- **URL**: https://atlasgo.io/
- **Notes**: Declarative migrations like Terraform. Supports versioned and declarative workflows.

### 2. ORM Migration Systems

Code-first schema generation from language type definitions.

#### Prisma
- **Input**: Prisma Schema Language (`.prisma`)
- **Output**: SQL migrations
- **Languages**: TypeScript, JavaScript
- **Databases**: PostgreSQL, MySQL, MariaDB, SQLite, SQL Server, CockroachDB
- **URL**: https://www.prisma.io/migrate
- **Key Commands**:
  - `prisma migrate dev` - Generate and apply migrations
  - `prisma migrate diff` - Generate SQL from schema comparison

#### Drizzle ORM
- **Input**: TypeScript schema definitions
- **Output**: SQL migrations
- **Languages**: TypeScript, JavaScript
- **Databases**: PostgreSQL, MySQL, SQLite
- **URL**: https://orm.drizzle.team/
- **Key Commands**:
  - `drizzle-kit generate` - Generate SQL from TypeScript schema
  - `drizzle-kit push` - Push schema directly to database

#### TypeORM
- **Input**: TypeScript/JavaScript entity decorators
- **Output**: SQL migrations
- **Databases**: PostgreSQL, MySQL, MariaDB, SQLite, SQL Server, Oracle
- **URL**: https://typeorm.io/

#### SQLAlchemy (with Alembic)
- **Input**: Python class definitions
- **Output**: SQL migrations
- **Databases**: PostgreSQL, MySQL, SQLite, Oracle, SQL Server
- **URL**: https://alembic.sqlalchemy.org/

### 3. Specification Parsers

Convert API/data specifications to database schemas.

#### OpenAPI Generator (mysql-schema)
- **Input**: OpenAPI v2/v3 specification
- **Output**: MySQL DDL
- **URL**: https://openapi-generator.tech/docs/generators/mysql-schema/
- **Notes**: Maps OpenAPI types to MySQL types. Does not drop existing tables.

#### SQL::Translator::Parser::OpenAPI (Perl)
- **Input**: OpenAPI JSON/YAML
- **Output**: SQL DDL (SQLite, PostgreSQL, MySQL)
- **URL**: https://metacpan.org/pod/SQL::Translator::Parser::OpenAPI

#### jsonschema2ddl
- **Input**: JSON Schema
- **Output**: PostgreSQL, Redshift DDL
- **Languages**: Python
- **URL**: https://github.com/clarityai-eng/jsonschema2ddl
- **Notes**: Validates schema against $schema URI. Supports constraints and indexes.

#### json-schema-to-sql
- **Input**: JSON Schema
- **Output**: PostgreSQL, MySQL DDL
- **Languages**: JavaScript/TypeScript
- **URL**: https://github.com/VasilVelikov00/json-schema-to-sql
- **Notes**: Normalizes nested structures into tables with foreign keys.

#### jsonschema2db
- **Input**: JSON Schema
- **Output**: PostgreSQL tables
- **Languages**: Python
- **URL**: https://github.com/better/jsonschema2db
- **Notes**: Flattens complex JSON to relational tables. Creates foreign keys and analyzes.

#### graphql-to-sql
- **Input**: GraphQL SDL with @sql directives
- **Output**: SQL DDL
- **URL**: https://github.com/taylorgoolsby/graphql-to-sql
- **Notes**: Uses GraphQL SDL as lingua franca for data requirements.

### 4. Protobuf Converters

Protocol Buffer to SQL schema generation.

#### proto-sql
- **Input**: Protobuf definitions
- **Output**: MySQL DDL
- **Type**: protoc compiler plugin
- **URL**: https://github.com/commandus/proto-sql

#### protobuf-sql (bitquery)
- **Input**: Protobuf definitions
- **Output**: SQL DDL
- **Type**: protoc plugin
- **URL**: https://github.com/bitquery/protobuf-sql

#### protoc-gen-map
- **Input**: Protobuf + SQL templates
- **Output**: Go code with SQL mapping
- **URL**: https://github.com/jackskj/protoc-gen-map
- **Notes**: Maps SQL data to protobuf for gRPC services.

### 5. Type-to-Schema Generators

Language type systems to database schemas.

#### sqlc
- **Input**: SQL DDL + SQL queries
- **Output**: Type-safe Go/Python/Kotlin code
- **Direction**: SQL-first (opposite direction)
- **URL**: https://sqlc.dev/
- **Notes**: Parses DDL and queries to generate type-safe interfaces. Catches type errors at compile time.

#### Schemats
- **Input**: PostgreSQL/MySQL database
- **Output**: TypeScript interfaces
- **Direction**: DB-first (introspection)
- **URL**: https://github.com/SweetIQ/schemats

#### pg-to-ts
- **Input**: PostgreSQL database
- **Output**: TypeScript types
- **Direction**: DB-first (introspection)
- **URL**: https://github.com/danvk/pg-to-ts

### 6. AI-Assisted Schema Generation

Natural language to database schema.

#### AI2sql Schema Generator
- **Input**: Natural language description
- **Output**: MySQL, PostgreSQL DDL
- **URL**: https://ai2sql.io/sql-schema-generator
- **Notes**: Creates tables, relationships, constraints from descriptions.

#### Workik AI Database Schema Generator
- **Input**: Natural language, partial JSON/CSV schemas
- **Output**: SQL (MySQL, PostgreSQL, SQL Server) and NoSQL schemas
- **URL**: https://workik.com/ai-powered-database-schema-generator

#### DbSchema
- **Input**: Visual design, AI assistance
- **Output**: SQL DDL for all major databases
- **URL**: https://dbschema.com/
- **Notes**: Database-agnostic design with physical model transformation.

### 7. Bidirectional/Introspection Tools

Tools that work in both directions.

#### DB2OpenAPI
- **Input**: SQL database
- **Output**: OpenAPI specification
- **URL**: https://zuplo.com/learning-center/generate-openapi-from-database
- **Notes**: Uses Sequelize ORM. Generates CRUD routes and JSON schema.

#### Hasura
- **Input**: PostgreSQL database
- **Output**: GraphQL API with schema
- **URL**: https://hasura.io/
- **Notes**: Auto-generates GraphQL from existing database. Real-time subscriptions.

#### Postgraphile
- **Input**: PostgreSQL database
- **Output**: GraphQL API
- **URL**: https://www.graphile.org/postgraphile/
- **Notes**: Maximizes PostgreSQL features. No Docker required.

#### DDL.js
- **Input**: PostgreSQL/SQLite database
- **Output**: JSON Schema v4
- **URL**: https://github.com/moll/js-ddl
- **Notes**: Database introspection for domain model preparation.

## Tool Selection Matrix

| Use Case | Recommended Tools | Rationale |
|----------|-------------------|-----------|
| TypeScript-first development | Prisma, Drizzle | Native TS, excellent DX |
| OpenAPI-driven API | OpenAPI Generator | Direct spec-to-schema |
| JSON data modeling | jsonschema2ddl, jsonschema2db | JSON Schema expertise |
| Schema visualization | DBML + dbdiagram.io | Human-readable, visual |
| Infrastructure as Code | Atlas | Terraform-like workflow |
| Rapid prototyping | AI2sql, Workik | Natural language input |
| Existing database | pg-to-ts, Schemats | Introspection tools |
| GraphQL-first | graphql-to-sql, Hasura | SDL as source of truth |

## Ecosystem Notes

### Node.js/TypeScript
Richest ecosystem: Prisma, Drizzle, json-schema-to-sql, DBML CLI

### Python
jsonschema2ddl, SQLAlchemy+Alembic, jsonschema2db

### Go
Atlas, sqlc (opposite direction), protoc-gen-map

### Perl
SQL::Translator::Parser::OpenAPI

### Database Coverage
- **PostgreSQL**: Best supported across all tools
- **MySQL**: Good support, some type differences
- **SQLite**: Supported by ORM tools
- **SQL Server**: Limited in spec parsers, good in ORMs
