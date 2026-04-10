---
name: new-domain
description: Start mapping a new ERP domain. Guides through domain
  understanding, table/model identification, and metadata collection.
  Use when beginning work on a new domain batch like Subscriptions,
  Invoicing, or Accounts. Trigger this skill when the user wants to
  start on a new area, says things like "let's do invoicing next",
  "I want to map GL accounts", "add a new domain", or asks about
  setting up metadata for a batch of tables.
---
# New Domain Setup: $ARGUMENTS

## Phase 1: Understand the Domain
Establish how both systems model this domain before any field work.

Determine:
1. **Exact's data model**: primary business object, config/reference 
   tables, child/detail records, relationships
2. **Odoo 18's data model**: primary model, expected data flow 
   (e.g., quotation → confirmation → subscription), mandatory fields, 
   computed state
3. **Architectural asymmetries** — check for these common patterns:
   - Exact standalone entity vs Odoo flags on broader entity
   - Exact richer config than Odoo offers natively
   - Exact denormalizes; Odoo uses relational lookups
   - Odoo distributes across models without shared keyword

Use your knowledge + web search of official docs when uncertain. 
Ask the user for clarification or documentation excerpts as needed.

## Phase 2: Identify Tables and Models
Classify relevance:
- **Primary** — core business entities and lines/details
- **Secondary** — config/reference tables for resolving relations
- **Tertiary** — reports, wizards, transient models (usually skip)

Check: has any prior domain already mapped shared tables? 
(Check /mappings/ for existing workbooks if available.)

Agree on batch scope before requesting metadata.

## Phase 3: Collect Metadata
Tell the user which metadata files are needed (primary tables first)
and where to place them:

- `/metadata/exact/{Service}{Endpoint}.csv` — camelCase service+endpoint, e.g. `CRMAccounts.csv`, `SalesInvoiceSalesInvoiceLines.csv`
- `/metadata/odoo/{model.name}.csv` — exact Odoo model name, e.g. `res.partner.csv`, `account.payment.term.line.csv`

**From Exact**: Name, Type (EDM), Description — from REST API Reference
**From Odoo**: Field Name, Field Type, Field Label, Field Help,
Model, Related Model — from Settings → Technical → Database Structure...

Once the user confirms the files are in place, read them from the
metadata folders to verify completeness before proceeding to /map.

Also create the domain's CSV output folder: `mappings/data/{domain}/`.
This is where /map will write its CSV source files.

Ask for additional context as dependencies surface.