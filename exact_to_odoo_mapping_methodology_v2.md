# Exact Online → Odoo 18: Migration Mapping Methodology

## 1. Purpose

This document describes a repeatable methodology for mapping data structures from Exact Online to Odoo 18. The goal is to produce a field-level mapping specification that can serve as the blueprint for an actual data migration.

The methodology is **domain-agnostic** — it works for subscriptions, accounts, invoices, projects, or any other functional area. What changes per domain is the input data (source and target field metadata), not the process.

The mapping is executed collaboratively between a user and an LLM loaded with a dedicated set of instructions (see *Exact Online → Odoo 18: Migration Mapping — LLM Instructions*). This document provides the full context of the methodology and serves as a practical guide for the user's side of that collaboration. Sections 2 and 3 establish the principles and preparation; Section 4 is a step-by-step walkthrough of executing a domain mapping batch from start to finish.

---

## 2. Core Principles

### 2.1 Mapping Philosophy

Every Exact field must be classified into exactly one of five categories:

| Category | Rule | Example |
|---|---|---|
| **Direct** | Clear semantic equivalence. Map 1:1 with at most a type conversion. | `StartDate` → `start_date` |
| **Relational** | Maps to an Odoo relational field (`many2one`, `many2many`). Requires a lookup/resolution step against another migrated or pre-existing table. | `OrderedBy` (Account GUID) → `partner_id` (many2one → res.partner) |
| **Custom** | No native Odoo equivalent. Create a custom field prefixed `x_aa_` on the target Odoo model to preserve the data. | `InvoiceDay` → `x_aa_invoice_day` |
| **Derived** | No Exact source field exists. The Odoo field must be computed, defaulted, or inferred by migration logic. | `is_subscription` ← always `True` |
| **Skip** | Denormalized display copy (e.g., `OrderedByName` alongside `OrderedBy`), obsolete field, or system metadata not needed in Odoo. Not migrated, but noted for reference. | `CreatorFullName` (derivable from Creator → res.users.name) |

### 2.2 Standing Rules

These rules apply to every mapping, regardless of domain:

1. **Always preserve the Exact primary key.** Every Exact table's ID/EntryID field maps to `x_aa_exact_id` (char) on the target Odoo model. This is non-negotiable — it is needed for reconciliation, re-runs, deduplication, and relationship resolution.

2. **Never override standard Odoo semantics.** If an Odoo field has a well-defined meaning (e.g., `name` on sale.order is an auto-generated order reference), do not repurpose it to store something different. Create a custom field instead.

3. **Prefer native Odoo fields when the semantic match is clear.** Only create `x_aa_` custom fields when there is no clean equivalent. The bar for "clear" is: the field descriptions on both sides describe the same business concept, not merely similar-sounding names.

4. **Custom field naming convention:** `x_aa_` prefix, then `snake_case` preserving the semantic meaning of the Exact field. Example: `InvoicingStartDate` → `x_aa_invoicing_start_date`.

5. **Denormalized display fields are skipped, not mapped.** Exact's REST API frequently includes convenience copies of related data (e.g., `OrderedByName` alongside `OrderedBy`). These are read-only display values that are derivable from the relation itself. Skip them but note them in the comments column so a reviewer can see they were considered, not overlooked.

6. **Type conversion defaults:**

   | Exact Type | Default Odoo Type | Notes |
   |---|---|---|
   | `Edm.Guid` | `char` | Unless it's a foreign key → then `many2one` |
   | `Edm.String` | `char` | Use `text` if the field is known to hold long content |
   | `Edm.Int16` / `Edm.Int32` | `integer` | |
   | `Edm.Double` | `float` | Use `monetary` only if Odoo's target field is monetary |
   | `Edm.DateTime` | `datetime` or `date` | Strip time component when mapping to an Odoo `date` field |
   | `Edm.Boolean` | `boolean` | |
   | `Edm.Byte` | `boolean` or `integer` | Byte flags (0/1) → boolean; actual numeric values → integer |
   | `Edm.Binary` | `binary` | Typically images |
   | Collection | — | Structural reference to a child table; mapped via one2many on the parent |

7. **Derived fields must document their derivation logic.** The Notes column should describe how the value is computed (e.g., "Set to True for all migrated subscription records" or "Derive from CancellationDate: if set → '6_churn'").

---

## 3. Information Sources and Data Preparation

The mapping process requires field metadata from both Exact Online and Odoo 18. This section documents what is needed and how to extract it. It is reference material — the workflow in Section 4 will direct you here at the appropriate moment (Step 4: Metadata Collection).

### 3.1 Exact Online — Source Metadata

**What is needed:** For each relevant Exact table, a CSV with three columns:

| Column | Content |
|---|---|
| Name | The technical field name (e.g., `EntryID`, `OrderedBy`) |
| Type | The EDM type (e.g., `Edm.Guid`, `Edm.String`, `Edm.DateTime`) |
| Description | A short description of the field's purpose |

**How to extract it:**

1. Navigate to the Exact Online REST API Reference at https://start.exactonline.nl/docs/HlpRestAPIResources.aspx?SourceAction=10
2. Locate the intended endpoint using the page's module listing or the Search bar.
3. Run the script `Exact_REST_API_scraper.py` against the endpoint page URL. The script scrapes the field table and produces a CSV with the columns `Name`, `Type`, `Description`.

**Supplementary source:** Exact Online's user-facing help documentation and community knowledge base can clarify business semantics when the API field descriptions are terse. The LLM will also consult these during domain research.

### 3.2 Odoo 18 — Target Metadata

**What is needed:** For each relevant Odoo model, a CSV containing at minimum:

| Column | Content |
|---|---|
| Field Name | The technical field name (e.g., `partner_id`, `start_date`) |
| Field Type | The Odoo field type (e.g., `many2one`, `char`, `date`) |
| Field Label | The human-readable label (e.g., "Customer", "Start Date") |
| Field Help | Tooltip/help text describing the field's purpose |
| Model | The model name (e.g., `sale.order`) |
| Related Model | For relational fields, the target model (e.g., `res.partner`) |

Additional columns (e.g., Dependencies, Type) are acceptable and will be used if informative, but these six are the essential ones.

**How to extract it:**

1. In the Odoo.sh project, navigate to Settings and activate Developer Mode.
2. Go to Technical → Database Structure → Fields.
3. In the Search bar, add a Custom Filter to filter by the desired Model Name.
4. Select all fields: tick the checkbox next to "Field Name" in the top left. If there are multiple pages, click "Select all" in the search bar to include all records.
5. Go to Actions → Export.
6. Select CSV as the Export Format.
7. Select the saved export template (which defines the column set above).
8. Click Export and rename the downloaded file to match the Model Name.

Repeat for each Odoo model in scope.

**Supplementary source:** Odoo 18's official user documentation (https://www.odoo.com/documentation/18.0/) and developer documentation. These explain how modules work conceptually — which is critical for understanding whether a field is a genuine data target or a computed/transient/UI-only artifact. The LLM will also consult these during domain research.

---

## 4. Workflow

This section walks through the execution of one domain mapping batch from start to finish. Each step describes what happens, who is responsible (user, LLM, or both), and what the output is.

The LLM must be loaded with the *Exact Online → Odoo 18: Migration Mapping — LLM Instructions* as its system prompt before beginning.

### Step 1: Define the Domain

**Who:** User.

Start a session with the LLM and state the domain to be mapped (e.g., "I want to map subscription data from Exact Online to Odoo 18" or "Let's map the Accounts/Contacts domain"). This anchors the entire session. One domain per batch keeps the work manageable and reviewable.

If other domains have already been mapped in previous sessions, it is recommended to let the LLM know which ones and, if possible, which Exact tables and Odoo models were covered. This allows the LLM to skip tables that have already been handled and reference resolved dependencies. The LLM may later ask for specific mapping workbooks from prior batches if it needs to consult them.

### Step 2: Domain Research

**Who:** LLM, with user input.

The LLM researches how both Exact Online and Odoo 18 model the stated domain. It draws on its own knowledge, web search of official documentation, and questions to the user about business-specific usage.

The goal is to establish:
- Which Exact tables belong to this domain and how they relate to each other (primary business entity, configuration tables, child/detail records).
- Which Odoo models are the targets and how the domain's functionality is distributed across them.
- Where the two systems differ architecturally.

This step is conversational. For example, when mapping the Subscriptions domain, this research surfaced that Exact exposes subscriptions as standalone entities (`Subscriptions`, `SubscriptionTypes`, `SubscriptionLines`), while Odoo implements subscriptions as sales orders with recurring plans — `sale.order` with `is_subscription=True` and a link to `sale.subscription.plan`. That asymmetry shaped every subsequent mapping decision.

Expect the LLM to ask clarifying questions during this step, particularly around how the domain's data model is structured and which tables or models are relevant.

**Output:** A shared understanding of the domain's structure in both systems, including any architectural asymmetries.

### Step 3: Scope Agreement

**Who:** Together.

Based on the domain research, agree on which Exact tables and Odoo models are in scope for this batch. The LLM will propose a relevance ranking:

- **Primary** — core business entities and their lines/details.
- **Secondary** — configuration/reference tables needed to resolve relational fields.
- **Tertiary** — reports, wizards, transient models (usually excluded).

This step determines what metadata needs to be collected. Not everything needs to be mapped at once — secondary tables can be deferred if they represent dependencies that belong to a different domain batch.

**Output:** An agreed list of Exact tables and Odoo models to map, with their priority ranking.

### Step 4: Metadata Collection

**Who:** User.

Extract field metadata from both platforms following the procedures in Section 3. Provide the CSVs to the LLM.

Work incrementally: start with the primary tables. The LLM may identify additional tables as dependencies during the mapping phase, at which point you would return to this step to extract more metadata.

For example, in the Subscriptions domain, the initial scope was `Subscriptions`, `SubscriptionTypes`, and `SubscriptionLines` on the Exact side, and `sale.order`, `sale.subscription.plan`, and `sale.order.line` on the Odoo side. During mapping, the need for `SubscriptionReasonCodes` → `sale.order.close.reason` and `LogisticsItems` → `product.template` emerged as dependencies, requiring additional metadata collection.

**Output:** Field metadata CSVs for all in-scope tables and models, provided to the LLM.

### Step 5: Mapping

**Who:** LLM, with user review.

The LLM produces the field-level mapping for each Exact-to-Odoo table pair. For each table pair, it:

1. Determines the structural mapping at the table level and documents the rationale.
2. Classifies every Exact field into one of the five categories (Direct, Relational, Custom, Derived, Skip) and assigns the target Odoo field.
3. Identifies Odoo-side derived fields that have no Exact source but must be set for the target model to function correctly.
4. Flags cross-domain dependencies — references to tables not yet mapped.

The user reviews the mapping as it is produced. This is the point to challenge individual decisions, ask about alternatives, or adjust the approach. For instance, the LLM might initially propose creating a small custom Odoo model for a simple Exact lookup table, and the user might prefer denormalizing the values as flat custom fields instead. These are design decisions best made together.

**Output:** Reviewed field-level mappings for all table pairs in the batch.

### Step 6: Delivery

**Who:** LLM.

The LLM produces the mapping as a formatted Excel workbook (.xlsx) conforming to the output specification in Section 6. It presents the deliverable with a concise summary of key decisions, notable asymmetries, and any open dependencies.

The user should review the deliverable against the quality checklist in Section 7 to confirm completeness.

**Output:** The mapping workbook.

### Step 7: Dependency Closure

**Who:** Together.

If the mapping surfaced dependencies on unmapped tables (e.g., the Subscriptions mapping depends on Items being migrated into `product.template`), decide how to handle them:

- **Map now** — extend the current batch by returning to Step 3 with the dependency tables added to scope.
- **Defer** — document the dependency and handle it in a future domain batch.

The general principle is: close dependencies that are essential for the current domain to function in Odoo. Defer dependencies that are shared across many domains and warrant their own batch (e.g., `res.partner` is referenced by nearly everything but may deserve a dedicated Accounts/Contacts batch).

**Output:** Dependencies either resolved or explicitly deferred with documentation.

---

## 5. Dependency Resolution

Migrations are never isolated to a single table. Relational fields create dependencies that must be resolved in the correct order.

### 5.1 Migration Order

The general principle: **reference/master data before transactional data, parents before children.** A typical order:

1. **Foundational master data** (usually pre-existing in Odoo, may need enrichment):
   - `res.company` (from Exact Divisions)
   - `res.users` (from Exact Users — often defaulted to admin)
   - `res.currency` (standard ISO currencies, usually pre-loaded)
   - `uom.uom` (units of measure)
   - `account.tax` (tax codes)
   - `account.account` (GL accounts)
   - `account.payment.term` (payment conditions)

2. **Domain-specific master data:**
   - `product.template` → auto-creates `product.product` (from Exact Items)
   - `res.partner` (from Exact Accounts/Contacts)
   - Domain-specific configurations (e.g., `sale.subscription.plan`, `sale.order.close.reason`)

3. **Transactional data:**
   - Orders, order lines, invoices, invoice lines, etc.

### 5.2 Cross-Domain Dependencies

When mapping a new domain, check whether it depends on tables already mapped in a previous domain, or vice versa. Common shared dependencies include:

- `res.partner` — used by nearly everything (sales, purchasing, invoicing, subscriptions)
- `product.template` / `product.product` — used by sales, purchasing, inventory, manufacturing
- `account.account` — used by products, invoicing, payments
- `res.currency`, `res.users`, `res.company` — universal

If a dependency has already been mapped, reference it. If it hasn't, flag it as a prerequisite.

---

## 6. Output Specification

The deliverable for each mapping batch is an Excel workbook (.xlsx) with:

1. **One sheet per Exact-to-Odoo table mapping**, named descriptively (e.g., "Subscriptions → sale.order").
2. **Seven columns per sheet:**

   | Column | Content |
   |---|---|
   | Exact Field | The Exact field name (or "—" for Derived rows) |
   | Exact Type | The Exact EDM type (or "—" for Derived rows) |
   | Category | One of: Direct, Relational, Custom, Derived, Skip |
   | Odoo Field | The target Odoo field name (or `x_aa_...` for Custom, or "—" for Skip) |
   | Odoo Type | The Odoo field type |
   | Odoo Model | The target Odoo model |
   | Notes | Rationale, conversion rules, caveats, cross-references |

3. **Color-coded Category column** for quick visual scanning (blue=Direct, green=Relational, yellow=Custom, pink=Derived, grey=Skip).
4. **Frozen header row** and auto-filter enabled for easy sorting/filtering.
5. **A Legend sheet** explaining the five category colors and their meanings.

All sheets should be filterable by Category so a reviewer can quickly see, for example, all Custom fields that need to be created in Odoo, or all Relational fields that need lookup resolution logic.

---

## 7. Quality Checklist

Before declaring a domain batch complete, verify:

- [ ] Every Exact field in every in-scope table has a row in the mapping.
- [ ] Every row has a Category assigned.
- [ ] Every Relational row identifies the target Odoo model and the resolution path.
- [ ] Every Custom row uses the `x_aa_` prefix and follows snake_case naming.
- [ ] Every Derived row documents how the value is determined.
- [ ] Every Skip row has a justification in the Notes column.
- [ ] The Exact primary key (`x_aa_exact_id`) is present on every target Odoo model.
- [ ] Cross-domain dependencies are identified and documented.
- [ ] The migration order for the domain's tables is clear.
- [ ] Odoo-side mandatory fields and behavioral flags are accounted for.
