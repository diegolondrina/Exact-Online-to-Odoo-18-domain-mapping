# Exact Online to Odoo 18 Migration Mapping

> **New to the project?** Jump to [Getting Started](#getting-started) for clone, install, and first-run instructions. The numbered sections below are the workflow reference.

## Contents

1. [**Purpose**](#1-purpose) — what this project produces and who drives it.
2. [**Claude Code and skills**](#2-claude-code-and-skills) — the tooling the workflow runs on and why it is structured this way.
3. [**Pipeline at a glance**](#3-pipeline-at-a-glance) — the three artifact stages a domain batch passes through.
4. [**Project layout**](#4-project-layout) — annotated directory tree.
5. [**Classification system**](#5-classification-system) — the five categories every Exact field is sorted into.
6. [**Non-negotiable rules**](#6-non-negotiable-rules) — the rules that hold for every mapping.
7. [**Extracting metadata**](#7-extracting-metadata) — how to pull the source and target field lists from each system.
8. [**The four skills**](#8-the-four-skills) — when each skill runs, what it expects, what it produces.
9. [**End-to-end walkthrough**](#9-end-to-end-walkthrough) — one complete domain batch from start to finish.
10. [**Reference material**](#10-reference-material) — the standing defaults the `/map` skill applies.
11. [**Dependency tracking across batches**](#11-dependency-tracking-across-batches) — how cross-domain dependencies are recorded.
12. [**Quality checklist**](#12-quality-checklist) — the full list `/quality-gate` enforces.
13. [**Output specification**](#13-output-specification) — the shape of the final xlsx deliverable.

Sections 1–8 cover what the project is and how the pieces fit together; read them if you want to understand the workflow before using it. If you already have context and just want to drive the tool, jump straight to the [walkthrough](#9-end-to-end-walkthrough) — sections 10–13 are reference material you can consult on demand.

---

## Getting Started

### Prerequisites

- **Python 3.10+** with `pip` on your `PATH`.
- **Claude Code** — Anthropic's agentic CLI. Install via the [official quickstart](https://docs.claude.com/en/docs/claude-code/quickstart).
- **Git**.

### First-time setup

```bash
git clone <this-repo-url>
cd Exact-Online-to-Odoo-18-domain-mapping
pip install -r requirements.txt
```

The three Python dependencies (`openpyxl`, `requests`, `beautifulsoup4`) back the two delivery scripts and the Exact metadata scraper. Nothing else needs to be installed.

### Running Claude Code in this project

> **Critical:** Claude Code must be started *from inside the project directory*. `CLAUDE.md`, the four skills under `.claude/skills/`, and the environment-check hook all live under this folder. If you run `claude` from anywhere else, none of the project-specific behavior loads — Claude will have no idea this project exists, and the slash commands (`/new-domain`, `/map`, `/quality-gate`, `/deliver`) will not be available.

```bash
# from inside the cloned repo:
claude
```

To verify your environment at any time, run the check script manually:

```bash
python check_env.py
```

It reports either a green "Environment check: OK" summary or a specific list of problems (missing package, missing directory, wrong working directory).

### Your first session

Once the environment check passes, try a natural-language prompt such as:

> "Let's start mapping the Subscriptions domain."

Claude will match that intent to the `/new-domain` skill and begin the scoping procedure. For the full narrative of one complete domain batch, read the [end-to-end walkthrough](#9-end-to-end-walkthrough).

---

## 1. Purpose

This project produces field-level mapping specifications between Exact Online and Odoo 18 — the blueprint a migration engineer follows when actually moving data between the two systems. The deliverable for each batch is an Excel workbook: one sheet per Exact-to-Odoo table pair, with every source field classified, every target field identified, and every decision explained in the Notes.

The workflow is **domain-agnostic**. Subscriptions, Accounts, Purchases, Invoicing — the process is the same; only the input data (the source and target metadata) changes per domain. Work proceeds one domain at a time in reviewable batches.

You collaborate with an LLM that has been loaded with project instructions and a small set of skills that carry the phase-specific procedures. You steer decisions and provide data; the LLM brings structure, domain knowledge, and consistency.

---

## 2. Claude Code and skills

### What Claude Code is

Claude Code is Anthropic's agentic coding tool. It runs in your terminal, IDE, desktop app, or browser, holds a conversation with an LLM, and gives the LLM tools to read and edit files on disk, run shell commands, and call external integrations. You interact with it the way you would interact with a chat assistant — by typing messages — but the LLM can act on your project, not just talk about it. For this workflow, that means the same session can read the metadata CSVs you drop into `/metadata/`, write mapping CSVs into `/mappings/data/`, run the two Python scripts in `/deliver`, and update `references/dependency-tracker.md` — without you having to copy-paste anything between the chat and your filesystem.

Two pieces of Claude Code carry this project's structure: **`CLAUDE.md`** and **skills**.

### `CLAUDE.md` — the always-loaded baseline

`CLAUDE.md` is a markdown file at the project root that Claude Code reads at the start of every session. Whatever you put there becomes standing context the LLM applies on every turn, without you having to remind it. This project's `CLAUDE.md` is intentionally lean: just the role, the five-category classification system, and the six non-negotiable rules. These are the things that *must* hold no matter which phase of the workflow you are in, so they live in always-on context.

### Skills — phase-specific procedures, loaded on demand

A **skill** is a folder under `.claude/skills/` containing a `SKILL.md` file and optionally bundled reference files, examples, or scripts. The `SKILL.md` has YAML frontmatter (a `name` and a `description`) followed by the procedure the LLM should follow when the skill is invoked. For this project, the four skills are `/new-domain`, `/map`, `/quality-gate`, and `/deliver`.

Skills can be invoked two ways. The direct way is to type the slash command — `/map subscriptions`. The other way, and often the more useful one in practice, is to describe what you want in natural language: *"let's map the Subscriptions domain"*. The LLM reads every skill's `description` as standing context, matches your intent against the available skills, and loads the right one. Natural-language invocation lets you front-load nuance — business context, caveats, a particular concern — before the skill's procedure kicks in, and that extra context is available to the skill as it runs. The slash command is direct; natural language is flexible. Both are first-class.

Two properties of skills make them well-suited to this workflow:

1. **Skills load on demand, not always-on.** A skill's `description` is always visible to the LLM (so it knows the skill exists), but the full body of `SKILL.md` only enters the conversation when the skill is invoked. The long, phase-specific procedure for `/map` — including its bundled reference patterns — does not bloat context during `/new-domain` or `/deliver`. It appears when it is relevant and not before.
2. **Skills can bundle supporting files.** Anything in the skill's folder is referencable from `SKILL.md`. The `/map` skill ships with `reference/type-conversions.md`, `reference/exact-patterns.md`, `reference/odoo-skip-patterns.md`, and `examples/worked-example.md`. The skill body points the LLM at these files so the standing defaults (Edm.Guid → char unless FK; audit fields → `create_date`/`create_uid`; skip Odoo chatter and KPI fields) are applied consistently every time the skill runs, regardless of whether you remembered to remind it.

Once a skill is invoked, its rendered content stays in the conversation for the rest of the session. You do not need to re-invoke it to keep its instructions in effect.

### How this project uses the two

The split between `CLAUDE.md` and skills mirrors the split between **rules that must always hold** and **procedures that depend on which phase you are in**:

| Lives in | Loaded | Holds |
|---|---|---|
| `CLAUDE.md` | Every turn, every session | Role, classification system, non-negotiable rules |
| `.claude/skills/new-domain/` | When `/new-domain` is invoked | Domain scoping procedure |
| `.claude/skills/map/` + reference files | When `/map` is invoked | Mapping procedure + standing defaults + worked example |
| `.claude/skills/quality-gate/` | When `/quality-gate` is invoked | Pre-delivery checklist |
| `.claude/skills/deliver/` | When `/deliver` is invoked | Workbook generation procedure |

The four skills are four chapters of a playbook. The LLM is not handed the whole playbook at once; it is handed the chapter that matches the phase you are in. This keeps each phase focused, makes it easy to see what the LLM is and is not supposed to be doing, and means the procedure for any phase can be revised in a single file without touching the others.

### Why this design

LLMs are non-deterministic, but a mapping workflow needs to be repeatable, consistent, and systematic. The `CLAUDE.md` + skills split addresses this by being deliberate about what is rigid and what is conversational. Rules, defaults, checklists, and file layouts are rigid — codified once in `CLAUDE.md`, the skills, and the CSV pipeline, so they cannot drift between sessions. Judgment calls (which classification fits a tricky field, when to defer a dependency, how to handle a structural asymmetry) stay conversational. And because the source-of-truth artifacts are durable plain text, you can pick up at any intermediate step, revise outputs in place, or improve the skills themselves as you learn — the workflow gets better with use.

---

## 3. Pipeline at a glance

Mapping data flows through three artifact stages:

```
 Metadata CSVs          Mapping CSVs                 Mapping workbook
 ─────────────          ────────────                 ────────────────
 /metadata/exact/   ►   /mappings/data/{domain}/ ►   /mappings/{domain}_mapping.xlsx
 /metadata/odoo/        NN_[Exact]-[Odoo].csv
 (you provide)          (LLM writes)                 (scripts generate + format)
```

1. **Metadata CSVs** — the field catalogues for each Exact table and each Odoo model in scope. More than just names and types: each Exact row carries the API description of the field (its business meaning), and each Odoo row carries the field label, the help text, the related model for relational fields, and dependency information for computed fields. This is what lets the LLM reason about semantic equivalence rather than guessing from field names alone. You extract these once per table and drop them in `/metadata/exact/` and `/metadata/odoo/`. They are inputs: the LLM reads them but never writes them.
2. **Mapping CSVs** — the source of truth for a domain's mapping. One CSV per Exact-to-Odoo table pair, written by the LLM during `/map`. Plain text, human-editable, diffable, and the thing you review.
3. **The formatted xlsx** — the deliverable. Generated from the mapping CSVs by two Python scripts (`generate_workbook.py` then `format_workbooks.py`). You never hand-edit the xlsx; if something needs to change, edit the CSV and regenerate.

Keeping the CSV as the source of truth means every change is a clean text diff, mappings can be reviewed in isolation, and the xlsx is reproducible from scratch at any time.

---

## 4. Project layout

```
Exact-Online-to-Odoo-18-domain-mapping/
├── CLAUDE.md                        Always-loaded project instructions: role,
│                                    classification system, non-negotiable rules.
├── README.md                        This document.
├── requirements.txt                 Python dependencies for the delivery scripts
│                                    and the Exact metadata scraper.
├── .claude/
│   ├── settings.json                Claude Code project settings (committed).
│   └── skills/
│       ├── new-domain/SKILL.md      Phase 1: scope a new domain batch.
│       ├── map/
│       │   ├── SKILL.md             Phase 2: field-level classification.
│       │   ├── examples/worked-example.md
│       │   └── reference/           Type conversions, Exact patterns,
│       │                            Odoo skip patterns.
│       ├── quality-gate/SKILL.md    Phase 3: pre-delivery checklist.
│       └── deliver/
│           ├── SKILL.md             Phase 4: workbook generation.
│           └── spec/output-spec.md
├── metadata/
│   ├── exact/                       Source metadata CSVs, one per Exact endpoint.
│   └── odoo/                        Target metadata CSVs, one per Odoo model.
├── mappings/
│   ├── data/{domain}/               Mapping CSVs — source of truth per domain.
│   └── {domain}_mapping.xlsx        Generated deliverable per domain.
├── references/
│   └── dependency-tracker.md        Living cross-batch ledger.
├── check_env.py                     Verifies Python deps + project structure.
│                                    Run manually: python check_env.py
├── generate_workbook.py             CSVs → xlsx (sheets + Legend).
├── format_workbooks.py              Applies colors, fonts, borders,
│                                    freeze panes, auto-filter.
└── Exact_REST_API_scraper.py        Scrapes an Exact endpoint details page
                                     into metadata/exact/<name>.csv.
```

---

## 5. Classification system

Every Exact field gets exactly one category:

| Category | Rule | Example |
|---|---|---|
| **Direct** | Clear semantic equivalence. Map 1:1 with at most a type conversion. | `StartDate` → `start_date` |
| **Relational** | Maps to an Odoo relational field (`many2one`, `many2many`). Requires a lookup/resolution step against another migrated or pre-existing table. | `OrderedBy` (Account GUID) → `partner_id` (many2one → res.partner) |
| **Custom** | No native Odoo equivalent. Create a custom field prefixed `x_aa_` on the target Odoo model. | `InvoiceDay` → `x_aa_invoice_day` |
| **Derived** | No Exact source. The Odoo field must be computed, defaulted, or inferred by migration logic. | `is_subscription` ← always `True` |
| **Skip** | Denormalized display copy, obsolete field, or system metadata. Not migrated, but noted. | `OrderedByName` (derivable from `OrderedBy`) |

These five categories are exhaustive and mutually exclusive — every field lands in exactly one. The classification is the primary intellectual work of the whole process.

---

## 6. Non-negotiable rules

1. **Always preserve the Exact primary key.** Every Exact table's ID/EntryID maps to `x_aa_exact_id` (char) on the target Odoo model. Needed for reconciliation, re-runs, deduplication, and relationship resolution.
2. **Never override standard Odoo semantics.** If an Odoo field has a well-defined meaning (e.g., `name` on `sale.order` is an auto-generated order reference), do not repurpose it. Create a custom field instead.
3. **Prefer native Odoo fields when the semantic match is clear.** Only create `x_aa_` custom fields when there is no clean equivalent. The bar for "clear" is that the field descriptions on both sides describe the same business concept, not merely similar-sounding names.
4. **Custom field naming:** `x_aa_` prefix, then `snake_case` preserving the semantic meaning. Example: `InvoicingStartDate` → `x_aa_invoicing_start_date`.
5. **Skip denormalized display fields.** Exact's REST API ships convenience copies alongside GUIDs (e.g., `OrderedByName` next to `OrderedBy`). Skip them but note them in Notes so a reviewer sees they were considered, not overlooked.
6. **Derived fields must document their derivation logic** in the Notes column — the constant, default, or conditional rule used to produce the value.

These rules live in `CLAUDE.md` and are loaded on every turn, so the LLM applies them on every mapping without being reminded.

---

## 7. Extracting metadata

Before mapping a domain, you need field metadata from both sides. The LLM cannot see either system directly — it reads whatever CSVs you drop into `/metadata/exact/` and `/metadata/odoo/`.

You do not need every metadata file upfront. Start with the primary tables for the domain you are about to map — the `/new-domain` skill will tell you exactly which files it needs, and will ask for more if additional dependencies surface mid-batch.

### 7.1 Exact Online — source metadata

Each file lives at `/metadata/exact/{Service}{Endpoint}.csv` (camelCase service + endpoint concatenated, e.g. `CRMAccounts.csv`, `SubscriptionLines.csv`, `PurchaseOrderPurchaseOrderLines.csv`) and contains three columns:

| Column | Content |
|---|---|
| Name | Technical field name (e.g., `EntryID`, `OrderedBy`) |
| Type | EDM type (e.g., `Edm.Guid`, `Edm.String`, `Edm.DateTime`) |
| Description | Short description of the field's purpose |

**How to extract it:**

1. Open the Exact Online REST API Reference at <https://start.exactonline.nl/docs/HlpRestAPIResources.aspx?SourceAction=10>.
2. Locate the intended endpoint using the page's module listing or the Search bar. Each endpoint has its own details page — for example, `SubscriptionLines` lives at <https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SubscriptionSubscriptionLines>.
3. Run `Exact_REST_API_scraper.py` with the endpoint details page URL as the argument:

   ```
   python Exact_REST_API_scraper.py "https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SubscriptionSubscriptionLines"
   ```

   The script reads the `name` query parameter from the URL, scrapes the field table, and writes `metadata/exact/SubscriptionSubscriptionLines.csv` with the columns `Name`, `Type`, `Description`. The path and filename are derived automatically — you do not need to edit the script or specify an output location.

**Supplementary source:** Exact Online's user-facing help documentation and community knowledge base can clarify business semantics when the API field descriptions are terse. The LLM will also consult these during `/new-domain`.

### 7.2 Odoo 18 — target metadata

Each file lives at `/metadata/odoo/{model.name}.csv` (exact Odoo model name, e.g. `res.partner.csv`, `sale.subscription.plan.csv`) and contains at minimum:

| Column | Content |
|---|---|
| Field Name | Technical field name (e.g., `partner_id`, `start_date`) |
| Field Type | Odoo field type (e.g., `many2one`, `char`, `date`) |
| Field Label | Human-readable label |
| Field Help | Tooltip/help text |
| Model | Model name (e.g., `sale.order`) |
| Related Model | For relational fields, the target model |

Additional columns are fine and will be used if informative, but these six are the essential ones.

**How to extract it:**

1. In the Odoo.sh project, open Settings and activate **Developer Mode**.
2. Navigate to **Technical → Database Structure → Fields**.
3. In the Search bar, add a Custom Filter to filter by the desired Model Name.
4. Select all fields: tick the checkbox next to "Field Name" in the top left. If there are multiple pages, click "Select all" in the search bar to include every record.
5. Open **Actions → Export**.
6. Choose **CSV** as the Export Format.
7. Select the saved export template that defines the column set above.
8. Click **Export** and save the downloaded file to `/metadata/odoo/` as `{model.name}.csv`.

Repeat for each Odoo model in scope.

**Supplementary source:** Odoo 18's official user documentation (<https://www.odoo.com/documentation/18.0/>) and developer documentation. These explain how modules work conceptually — which is critical for understanding whether a field is a genuine data target or a computed/transient/UI-only artifact. The LLM will also consult these during `/new-domain`.

---

## 8. The four skills

Each skill is a phase-specific procedure the LLM follows when invoked. You can invoke a skill directly with its slash command (`/new-domain`, `/map`, etc.), or simply explain what you want in natural language — the LLM reads the skill descriptions and loads the right one automatically. Both paths are equivalent; the slash command is direct, natural language is flexible. Providing extra context in natural language before the skill runs is often useful: anything you say before the skill kicks in is available to it, so you can front-load domain knowledge, business context, or caveats that would otherwise only emerge mid-conversation.

### `/new-domain {domain}` — scope a new batch

**When to use:** Starting work on a new functional area ("Subscriptions", "Invoicing", "Accounts").

**What it does:**
1. *Understand the domain* — researches how Exact and Odoo model this area, identifies architectural asymmetries (e.g., Exact has a standalone Subscriptions entity; Odoo represents subscriptions as `sale.order` rows with `is_subscription=True`).
2. *Identify tables and models* — classifies them as Primary (core entities), Secondary (config/reference for relational resolution), or Tertiary (usually skipped).
3. *Agree on batch scope* — you confirm which tables/models are in for this batch.
4. *Request metadata* — tells you which CSVs are needed and where to put them, then reads them to confirm completeness before handing off.

**You provide:** the domain name, answers to business-context questions, and the metadata CSVs when asked.

**Output:** an agreed scope, verified metadata in place, and an empty `mappings/data/{domain}/` folder ready for `/map`.

### `/map {domain}` — field-level mapping

**When to use:** After `/new-domain` has completed and the metadata CSVs are in place.

**What it does:**
1. Re-reads the metadata CSVs to confirm completeness.
2. For each Exact-to-Odoo table pair:
   - Documents the table-level structural mapping and its rationale.
   - Classifies every Exact field into one of the five categories.
   - Adds Derived rows for Odoo fields that have no Exact source but must be set for the target model to function.
   - Flags cross-domain dependencies (references to unmapped tables).
3. Applies the standing patterns in the skill's `reference/` folder (audit fields, denormalized display fields, free fields, type conversion defaults, Odoo skip patterns).
4. Writes one CSV per table pair to `mappings/data/{domain}/` using the naming convention `NN_[ExactEntity]-[OdooModel].csv`. The `NN_` prefix controls sheet order in the final workbook.
5. Updates `references/dependency-tracker.md` with new pending dependencies or newly resolved ones.

**You provide:** review and feedback as mappings are produced. This is the single most important point to challenge individual decisions, ask about alternatives, or redirect the approach.

**Output:** the source-of-truth mapping CSVs for the domain, plus an updated dependency tracker.

### `/quality-gate {domain}` — pre-delivery checklist

**When to use:** After `/map` completes, before `/deliver`.

**What it does:** runs a structural + classification + completeness checklist against the domain's CSVs. Verifies every Exact field has a row, every row has a Category, every Relational row names a target model and resolution path, every Custom row uses `x_aa_` + snake_case, every Derived row documents its logic, every Skip row has a justification, `x_aa_exact_id` is present on every target model, and cross-domain dependencies are tracked.

**Output:** a pass/fail report per item. Failures are fixed by editing the CSVs (by hand or by asking the LLM) and re-running the gate.

### `/deliver {domain}` — generate the workbook

**When to use:** After `/quality-gate` passes.

**What it does:**
1. Confirms the CSVs exist in `mappings/data/{domain}/`.
2. Runs `python generate_workbook.py {domain}` — reads all CSVs, writes one sheet per CSV (with title `ExactEntity → OdooModel` derived from the filename), appends the Legend sheet, saves to `mappings/{domain}_mapping.xlsx`.
3. Runs `python format_workbooks.py` — applies colors, fonts, borders, freeze panes, and auto-filter across every workbook in `mappings/`.
4. Presents a closing summary: key decisions, notable asymmetries, open dependencies, and migration-order recommendation.

**Output:** the final, formatted `.xlsx` deliverable.

---

## 9. End-to-end walkthrough

This section walks through one complete domain batch using the Subscriptions domain as the example. The steps are the same for any domain.

Throughout this walkthrough, interactions are shown as natural language — which is the normal way to work. You can also invoke any skill directly with its slash command if you prefer; the two are equivalent.

### Step 1 — Start the session

Open Claude Code in the project directory. `CLAUDE.md` loads automatically, so the LLM already knows the role, the classification system, and the non-negotiable rules. You do not need to paste any system prompt.

### Step 2 — Scope the domain

Tell the LLM what you want to work on. This can be as brief or as detailed as is useful:

> "We are going to work on the Subscriptions domain. You know what to do."

You can also front-load context to shape the research.

The LLM recognizes the intent, loads the `/new-domain` skill, and begins domain research without waiting for further prompting. It establishes how each system models the domain — in this case surfacing the core architectural asymmetry: Exact exposes subscriptions as a standalone entity (`Subscriptions`, `SubscriptionTypes`, `SubscriptionLines`), while Odoo implements them as `sale.order` rows with `is_subscription=True`, a recurring plan on `sale.subscription.plan`, and close reasons on `sale.order.close.reason`.

Based on this, the LLM proposes a scope:

- **Primary:** `Subscriptions` → `sale.order`, `SubscriptionLines` → `sale.order.line`
- **Secondary:** `SubscriptionTypes` → `sale.subscription.plan`, `SubscriptionReasonCodes` → `sale.order.close.reason`
- **Tertiary:** restriction tables, webhooks — excluded

You confirm, push back, or defer parts to a later batch. Once scope is agreed, the LLM tells you which metadata files it needs and where to put them:

> Please extract and place the following:
> - `metadata/exact/Subscriptions.csv`
> - `metadata/exact/SubscriptionTypes.csv`
> - `metadata/exact/SubscriptionLines.csv`
> - `metadata/exact/SubscriptionReasonCodes.csv`
> - `metadata/odoo/sale.order.csv`
> - `metadata/odoo/sale.subscription.plan.csv`
> - `metadata/odoo/sale.order.line.csv`
> - `metadata/odoo/sale.order.close.reason.csv`

### Step 3 — Extract and place metadata

Follow the procedures in Section 7 to produce each CSV and drop it in the right folder. When done, tell the LLM:

> "Metadata is in place."

It will read the files to confirm completeness, create the empty `mappings/data/subscriptions/` folder, and let you know it is ready to map.

If any file is missing or malformed, fix it and re-notify — the LLM will not proceed without all required metadata in place.

### Step 4 — Produce the mapping

> "Go ahead and map."

The LLM loads the `/map` skill and works through the table pairs systematically. For each pair it opens with the table-level structural decision and its rationale, then classifies fields group by group: identity first, then relational, then dates, then amounts and quantities, then audit fields. It applies the standing reference patterns (audit fields, denormalized display fields, free fields, type conversions) consistently.

Expect the LLM to:

- Propose a classification and rationale for each field, pausing at non-obvious cases to get your input.
- Add Derived rows for Odoo fields that have no Exact source but must be set for the target model to function — for example, `is_subscription=True` on `sale.order`, which has no counterpart in Exact but is required for Odoo to treat the record as a subscription.
- Flag references to unmapped tables and log them in `references/dependency-tracker.md` — for example, `LogisticsItems` surfacing as a dependency for the line-level `product_id`.
- Ask you to extract metadata for any new dependency tables not in the initial scope, in which case you loop back to Step 3 for those files.

Review as the mapping is produced. This is the point to push back hardest. The LLM's classifications are well-informed — the reference patterns, metadata descriptions, and domain research all feed into them — but judgment calls, such as whether a subscription configuration field maps to a native Odoo plan attribute or warrants a custom field, still benefit from your context about how the data is actually used.

When you are satisfied with the content of the CSVs in `mappings/data/subscriptions/`, say so and move on.

### Step 5 — Verify

> "Run the quality gate."

The LLM loads `/quality-gate` and walks the checklist against the CSVs, reporting pass/fail per item. Common failures:

- A row missing a Category.
- A Relational row without a resolution path in Notes.
- A Custom row that forgot the `x_aa_` prefix or used camelCase instead of snake_case.
- A Skip row with no justification.
- `x_aa_exact_id` missing on one of the target models.

Fix any failures by asking the LLM to correct the CSVs (or edit them yourself — they are plain text), then re-run until everything passes.

### Step 6 — Generate the deliverable

> "Looks good, deliver it."

The LLM loads `/deliver` and runs the two scripts in order:

```
python generate_workbook.py subscriptions
python format_workbooks.py
```

The first writes `mappings/subscriptions_mapping.xlsx` with one sheet per CSV (titles rendered as `ExactEntity → OdooModel`) and a Legend sheet. The second applies visual formatting across every workbook in `mappings/`. You will see per-sheet console output from both scripts.

The LLM then presents a closing summary: key decisions taken, notable asymmetries, open dependencies still pending, and the recommended migration order for the domain's tables.

### Step 7 — Close out dependencies

If the dependency tracker has new pending entries, decide for each: **map now** (loop back to Step 2 with the dependency added to scope) or **defer** (document and handle in a future batch). General principle: close dependencies that are essential for the current domain to function in Odoo; defer shared dependencies that warrant their own batch (e.g., `res.partner` for Accounts/Contacts, `product.template` for Items).

### After the batch

The deliverable (`mappings/subscriptions_mapping.xlsx`) is the output you hand off. The mapping CSVs (`mappings/data/subscriptions/*.csv`) remain as the source of truth — if anything needs to change later, edit the CSVs and re-run `/deliver`. Never hand-edit the xlsx.

The intended consumer of this output is a migration script — the actual process that reads data from Exact, transforms and loads it into Odoo. The mapping workbook is its specification: Direct fields tell it which source column maps to which target column; Relational fields tell it which foreign key lookups are needed and which already-migrated table to resolve against; Derived fields document the constants, defaults, or conditional logic the script must apply where Exact has no source; Skip fields are explicitly accounted for so nothing is missed by accident. The Notes column carries the reasoning behind each decision, and the dependency tracker provides the batch execution order — which tables must be loaded before which.

Beyond the column assignments, the workflow produces understanding — of the domain, the architectural asymmetries between the two systems, and the reasoning behind each mapping decision. The goal is for as much of that understanding as possible to be baked into the Notes column itself, so the workbook is self-explanatory to someone who was not in the room. The conversation that produced it is a fallback: if a decision is unclear or a question arises during implementation that the Notes do not fully answer, that conversation is available to revisit for the fuller context.


---

**A note on the example prompts.** The natural-language prompts shown above (*"you know what to do"*, *"Metadata is in place"*, *"Run the quality gate"*, *"Looks good, deliver it"*) are illustrative, not a fixed script. The LLM matches intent, not exact wording — any phrasing that unambiguously points at the next phase will work, and if you prefer the direct route you can always type the slash command instead. The walkthrough above is the happy path; once you know what you are doing, the order and wording are yours.

---

## 10. Reference material

The `/map` skill pulls in three reference files for consistency. You do not need to memorize them — they are loaded automatically during mapping — but knowing they exist helps you understand the LLM's standing defaults and saves time when you are reviewing.

### Type conversion defaults (`map/reference/type-conversions.md`)

| Exact Type | Default Odoo Type | Notes |
|---|---|---|
| `Edm.Guid` | `char` | Unless foreign key → `many2one` |
| `Edm.String` | `char` | `text` for known long-content fields |
| `Edm.Int16` / `Edm.Int32` | `integer` | |
| `Edm.Double` | `float` | `monetary` only if Odoo target is monetary |
| `Edm.DateTime` | `datetime` or `date` | Strip time when mapping to `date` |
| `Edm.Boolean` | `boolean` | |
| `Edm.Byte` | `boolean` or `integer` | 0/1 flags → boolean; numeric → integer |
| `Edm.Binary` | `binary` | Typically images |

### Common Exact patterns (`map/reference/exact-patterns.md`)

- **Audit fields** (on nearly every table): `Created → create_date`, `Creator → create_uid` (default admin), `Modified → write_date`, `Modifier → write_uid`, `Division → company_id`. `CreatorFullName` / `ModifierFullName` are skipped as denormalized display.
- **Denormalized display fields**: pattern `SomeField` (GUID) + `SomeFieldCode` + `SomeFieldDescription` — map the GUID, skip the display copies with a note.
- **Free fields** (`FreeBoolField_01`–`05`, `FreeTextField_01`–`10`, etc.) — mapped as `x_aa_free_bool_01` and so on; the LLM will ask you to check actual population before deciding whether to migrate them.
- **CustomField endpoint** (Premium-only) — always skipped.

### Odoo skip patterns (`map/reference/odoo-skip-patterns.md`)

Skip unless specifically needed: chatter/activity fields (`message_ids`, `activity_ids`), KPI/analytics fields, portal/website runtime fields, count fields, display fields. Focus on stored, writable, business-meaningful fields.

### Worked example (`map/examples/worked-example.md`)

Contains one example row per category (Direct, Relational, Custom, Derived, Skip) extracted from a real completed mapping, each with commentary on what makes it a good example. Useful to read once to calibrate expectations for the level of detail in the Notes column.

---

## 11. Dependency tracking across batches

`references/dependency-tracker.md` is the living cross-batch ledger. It tracks:

- **Mapped** — which domains have been completed and where their workbooks live.
- **Dependency chain** — which domains depend on which, shown as a rough diagram.
- **Pending dependencies** — Relational fields in completed mappings that reference tables not yet mapped. Each entry names the source field, the target model, and the domain(s) where it appeared.

`/map` updates this file as part of its normal output — you should not need to edit it by hand, but it is worth reading before starting a new batch to see what is already resolved and what still blocks which mapping.

The general principles for handling pending dependencies across batches:

1. **Reference/master data before transactional data, parents before children.** Foundational tables (`res.company`, `res.users`, `res.currency`, `uom.uom`, `account.tax`, `account.account`, `account.payment.term`) should be mapped early; transactional data (orders, lines, invoices) maps late.
2. **Shared dependencies deserve their own batch.** `res.partner`, `product.template`, and `account.account` are referenced by many domains — give them a dedicated batch instead of mapping them opportunistically inside another domain.
3. **A pending dependency does not block delivery of the current batch.** Document it, deliver the workbook, and resolve in a later batch. Migration sequencing is the engineer's problem, not the mapper's.

---

## 12. Quality checklist

`/quality-gate` automates this, but the full list is worth knowing:

**Structural**
- [ ] CSVs exist in `mappings/data/{domain}/` with correct naming (`NN_[ExactEntity]-[OdooModel].csv`).
- [ ] Each CSV has the standard 7-column header: Exact Field, Exact Type, Category, Odoo Field, Odoo Type, Odoo Model, Notes.
- [ ] Every Exact field in every in-scope metadata table has a row.

**Classification**
- [ ] Every row has a Category.
- [ ] Every Relational row identifies the target model and resolution path.
- [ ] Every Custom row uses `x_aa_` prefix + snake_case.
- [ ] Every Derived row documents its derivation logic.
- [ ] Every Skip row has a justification.

**Completeness**
- [ ] `x_aa_exact_id` present on every target Odoo model.
- [ ] Cross-domain dependencies identified and logged in `references/dependency-tracker.md`.
- [ ] Migration order for the domain's tables is clear.
- [ ] Odoo-side mandatory fields and behavioral flags accounted for.

---

## 13. Output specification

The deliverable for each domain is an Excel workbook at `mappings/{domain}_mapping.xlsx` with:

1. **One sheet per Exact-to-Odoo table mapping**, titled `ExactEntity → OdooModel` (derived from the CSV filename; the `NN_` prefix controls sheet order and is stripped from the title).
2. **Seven columns per sheet:**

   | Column | Content |
   |---|---|
   | Exact Field | Exact field name (or `—` for Derived rows) |
   | Exact Type | Exact EDM type (or `—` for Derived rows) |
   | Category | One of: Direct, Relational, Custom, Derived, Skip |
   | Odoo Field | Target Odoo field, `x_aa_...` for Custom, `—` for Skip |
   | Odoo Type | Odoo field type |
   | Odoo Model | Target Odoo model |
   | Notes | Rationale, conversion rules, caveats, cross-references |

3. **Color-coded Category column**: Direct = light blue, Relational = light green, Custom = light yellow, Derived = light red/pink, Skip = grey.
4. **Formatting:** dark-blue header row with white bold text, Arial 10pt everywhere, thin bottom borders on data rows, Category column bold.
5. **Frozen header row** (`A2`) and **auto-filter** on every data sheet for quick sorting and filtering.
6. **Legend sheet** appended automatically, explaining the five categories.

All sheets are filterable by Category so a reviewer can quickly see, for example, every Custom field that needs to be created in Odoo, or every Relational field that needs lookup resolution logic in the migration scripts.
