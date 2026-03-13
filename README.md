# Harvest Pie CLI

A command-line utility that displays a high-contrast, colorblind-friendly pie chart of your weekly hours from Harvest and Forecast.

## Features

-   **Three-Metric Tracking**: Monitors **Worked** hours (Harvest), **Forecast** hours (Planned), and your personal **Target** hours.
-   **Intelligent Logic**:
    -   **Success**: When your Worked or Forecast hours meet your Target.
    -   **Remaining**: Shows hours planned in Forecast that you haven't worked yet.
    -   **Under Target**: Flags any gap between your Target and your planned/worked workload with a vibrant alert color.
-   **Colorblind Friendly**: Uses the **Wong Palette** (Sky Blue, Reddish Purple, Orange) by default for maximum accessibility and visual "pop".
-   **Local Configuration**: All API keys and preferences are stored locally in `config.json` (git-ignored).
-   **Testing Modes**: Pass forced values on the command line to test scenarios without hitting the APIs.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package and project management.

1.  Clone this repository.
2.  Install dependencies and set up the environment:
    ```bash
    uv sync
    ```

## Configuration

Run the configuration command to set up your Harvest and Forecast API access:
```bash
uv run harvest-pie config [OPTIONS]
```

### Configuration Options
-   `--token`: Harvest Personal Access Token ([Generate here](https://id.getharvest.com/developers)).
-   `--account`: Harvest Account ID.
-   `--forecast-account`: Harvest Forecast Account ID.
-   `--forecast-token`: (Optional) Forecast Access Token if different from Harvest.
-   `--target-hours`: Your weekly goal in hours (Default: **30**).
-   `--default-capacity`: Fallback weekly capacity if no Forecast/Manual data exists (Default: **30**).
-   `--scheduled-hours`: Manual override for "Scheduled" hours (bypasses Forecast).
-   `--color-worked`: Hex color for worked hours (Default: Sky Blue `#56B4E9`).
-   `--color-remaining`: Hex color for remaining hours (Default: Reddish Purple `#CC79A7`).
-   `--color-under-target`: Hex color for "Under Target" alerts (Default: Orange `#E69F00`).

Example:
```bash
uv run harvest-pie config --target 35 --forecast-account 592300
```

## Usage

Simply run the tool to see your current weekly progress (Monday-Sunday):
```bash
uv run harvest-pie
```

### Testing and Overrides
You can bypass API calls by forcing values directly on the command line:
-   `--force-worked [hours]`: Skips Harvest API and uses this value.
-   `--force-forecast [hours]`: Skips Forecast API and uses this value.

Example:
```bash
uv run harvest-pie --force-worked 35 --force-forecast 35
```

### Visual Summary
-   **Green Status Lines**: In the text summary, the **Forecast** and **Target** lines turn green once your worked hours meet or exceed them.
-   **Pie Chart**:
    -   **Sky Blue**: Hours already worked.
    -   **Reddish Purple**: Hours remaining to work (Forecast - Worked).
    -   **Orange**: The "Under Target" gap (Target - Forecast).
