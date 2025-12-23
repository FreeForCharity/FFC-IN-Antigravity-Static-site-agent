# FFC Static Site Agent

This repository contains the "brain" and "tools" for the Free For Charity (FFC) Antigravity Agent, specifically focused on **Static Site Conversions**.

## Included Workflows

### `/convert-site`
This command allows the agent to:
1. **Identify** the source site technology (e.g., WordPress).
2. **Scrape** the site into a static structure.
3. **Repair** assets, CSS, and video embeds for static hosting.
4. **Deploy** the result to a new GitHub repository with GitHub Pages enabled.

## How to use this Agent
To use these workflows in another project:
1. Open this repository in your workspace alongside your target project.
2. Ask Antigravity to run `/convert-site`.

## Structure
- `.agent/workflows/`: High-level instructions for the agent.
- `scripts/`: Supporting Node.js and Python scripts.
