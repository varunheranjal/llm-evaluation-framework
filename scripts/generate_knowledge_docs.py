"""Generate retrieval-friendly Markdown knowledge documents from the source CSV files."""

from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "source_data"
OUTPUT_DIR = ROOT / "datasets" / "business"
PROJECTS_DIR = OUTPUT_DIR / "projects"
OPPORTUNITIES_DIR = OUTPUT_DIR / "opportunities"
REFERENCE_DIR = OUTPUT_DIR / "reference"

for directory in [PROJECTS_DIR, OPPORTUNITIES_DIR, REFERENCE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def read_csv(name):
    with (SOURCE_DIR / name).open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))

def money(value):
    return f"${int(value):,}"

def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", text.strip()).strip("_").lower()

accounts = read_csv("accounts.csv")
opportunities = read_csv("opportunities.csv")
sales_reps = read_csv("sales_reps.csv")
resources = read_csv("project_resources.csv")
projects = read_csv("projects.csv")
revenue = read_csv("revenue.csv")

accounts_by_id = {row["account_id"]: row for row in accounts}
reps_by_id = {row["sales_rep_id"]: row for row in sales_reps}
resources_by_project = {}
for row in resources:
    resources_by_project.setdefault(row["project_id"], []).append(row)

for project in projects:
    account = accounts_by_id[project["account_id"]]
    assigned = resources_by_project.get(project["project_id"], [])
    delay = int(project["delay_days"])

    lines = [
        f"# Project: {project['name']}",
        "",
        f"- **Project ID:** {project['project_id']}",
        f"- **Client:** {account['name']} ({account['account_id']})",
        f"- **Client industry:** {account['industry']}",
        f"- **Client region:** {account['region']}",
        f"- **Client status:** {account['status']}",
        f"- **Technology:** {project['technology']}",
        f"- **Project status:** {project['status']}",
        f"- **Budget:** {money(project['budget'])}",
        f"- **Actual cost:** {money(project['actual_cost'])}",
        f"- **Delay:** {delay} days",
        "",
        "## Assigned resources",
        "",
    ]
    for resource in assigned:
        lines.append(
            f"- **{resource['employee_name']}** — {resource['skill']} — "
            f"{resource['allocation_percent']}% allocation"
        )
    if not assigned:
        lines.append("- No assigned resource is recorded in the source data.")

    summary = (
        f"{project['name']} is a {project['technology']} project for {account['name']} "
        f"in the {account['industry']} industry. The project is {project['status'].lower()}, "
        f"with a budget of {money(project['budget'])} and an actual cost of "
        f"{money(project['actual_cost'])}."
    )
    summary += f" It is delayed by {delay} days." if delay else " It has no recorded delay."
    if assigned:
        people = ", ".join(
            f"{r['employee_name']} ({r['skill']}, {r['allocation_percent']}% allocation)"
            for r in assigned
        )
        summary += f" Assigned resource: {people}."
    lines += ["", "## Summary", "", summary]

    path = PROJECTS_DIR / f"{project['project_id']}_{slug(project['name'])}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

for opportunity in opportunities:
    account = accounts_by_id[opportunity["account_id"]]
    rep = reps_by_id[opportunity["sales_rep_id"]]
    loss_reason = (opportunity.get("loss_reason") or "").strip()

    lines = [
        f"# Sales Opportunity: {opportunity['title']}",
        "",
        f"- **Opportunity ID:** {opportunity['opportunity_id']}",
        f"- **Client:** {account['name']} ({account['account_id']})",
        f"- **Client industry:** {account['industry']}",
        f"- **Client region:** {account['region']}",
        f"- **Client status:** {account['status']}",
        f"- **Sales representative:** {rep['name']} ({rep['sales_rep_id']})",
        f"- **Sales representative region:** {rep['region']}",
        f"- **Technology:** {opportunity['technology']}",
        f"- **Service:** {opportunity['service']}",
        f"- **Deal value:** {money(opportunity['deal_value'])}",
        f"- **Opportunity status:** {opportunity['status']}",
        f"- **Stage:** {opportunity['stage']}",
        f"- **Created date:** {opportunity['created_date']}",
        f"- **Close date:** {opportunity['close_date']}",
    ]
    if loss_reason:
        lines.append(f"- **Loss reason:** {loss_reason}")

    summary = (
        f"{opportunity['title']} is a {opportunity['service']} opportunity for "
        f"{account['name']} using {opportunity['technology']}. The deal value is "
        f"{money(opportunity['deal_value'])}. The opportunity is "
        f"{opportunity['status'].lower()} and was handled by {rep['name']}."
    )
    if loss_reason:
        summary += f" The recorded loss reason is {loss_reason}."
    lines += ["", "## Summary", "", summary]

    path = OPPORTUNITIES_DIR / f"{opportunity['opportunity_id']}_{slug(opportunity['title'])}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

account_lines = ["# Client Account Directory", ""]
for account in accounts:
    account_lines += [
        f"## {account['name']}",
        "",
        f"- **Account ID:** {account['account_id']}",
        f"- **Industry:** {account['industry']}",
        f"- **Region:** {account['region']}",
        f"- **Status:** {account['status']}",
        "",
    ]
(REFERENCE_DIR / "accounts_directory.md").write_text(
    "\n".join(account_lines).rstrip() + "\n", encoding="utf-8"
)

rep_lines = ["# Sales Team Directory", ""]
for rep in sales_reps:
    rep_lines += [
        f"## {rep['name']}",
        "",
        f"- **Sales representative ID:** {rep['sales_rep_id']}",
        f"- **Region:** {rep['region']}",
        "",
    ]
(REFERENCE_DIR / "sales_team.md").write_text(
    "\n".join(rep_lines).rstrip() + "\n", encoding="utf-8"
)

quarters = {}
for row in revenue:
    quarters.setdefault(row["quarter"], []).append(row)

revenue_lines = ["# Revenue Report", ""]
for quarter in sorted(quarters):
    revenue_lines += [f"## {quarter}", ""]
    total = 0
    for row in quarters[quarter]:
        value = int(row["revenue"])
        total += value
        revenue_lines.append(f"- **{row['industry']}:** {money(value)}")
    revenue_lines += [f"- **Quarter total:** {money(total)}", ""]

industry_rows = {}
for row in revenue:
    industry_rows.setdefault(row["industry"], {})[row["quarter"]] = int(row["revenue"])

revenue_lines += ["## Revenue by industry across quarters", ""]
for industry in sorted(industry_rows):
    values = industry_rows[industry]
    revenue_lines.append(
        f"- **{industry}:** " +
        "; ".join(f"{q}: {money(values[q])}" for q in sorted(values))
    )

(REFERENCE_DIR / "revenue_report.md").write_text(
    "\n".join(revenue_lines).rstrip() + "\n", encoding="utf-8"
)

print("Knowledge documents generated successfully.")
