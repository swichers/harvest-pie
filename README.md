# Harvest Pie CLI

A command-line utility that displays a pie chart of hours worked vs. hours scheduled from the Harvest API.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package and project management.

1.  Clone this repository.
2.  Install dependencies and set up the environment:
    ```bash
    uv sync
    ```

## Configuration

Run the configuration command to set up your Harvest API keys:
```bash
uv run harvest-pie config
```
You will be prompted for:
-   **Harvest Personal Access Token**: Generate one at [Harvest Developers](https://id.getharvest.com/developers).
-   **Harvest Account ID**: Found on the same page.
-   **Scheduled Hours (Optional)**: If you want to override the weekly capacity set in Harvest.

Configuration is stored in `config.json` in the project root.

## Usage

Simply run:
```bash
uv run harvest-pie
```

The tool will fetch your time entries for the current week (Monday-Sunday) and display a pie chart comparing them to your weekly capacity (scheduled hours).

### Colors
-   **Worked Hours**: Brighter pastel (Baby Blue: `#89cff0`).
-   **Missing Hours**: Darker pastel (Dark Blue Gray: `#4b5d67`).
