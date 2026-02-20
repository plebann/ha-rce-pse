# RCE Prices Integration for Home Assistant - API v2 ready

[![hacs_badge](https://img.shields.io/badge/HACS-Default-blue.svg?style=for-the-badge)](https://github.com/hacs/integration)
![GitHub Release](https://img.shields.io/github/v/release/plebann/ha-rce-pse?style=for-the-badge)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/plebann/ha-rce-pse/tests.yml?style=for-the-badge)
[![hacs_downloads](https://img.shields.io/github/downloads/plebann/ha-rce-pse/latest/total?style=for-the-badge)](https://github.com/plebann/ha-rce-pse/releases/latest)
![GitHub License](https://img.shields.io/github/license/plebann/ha-rce-pse?style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/plebann/ha-rce-pse?style=for-the-badge)
![Maintenance](https://img.shields.io/maintenance/yes/2025?style=for-the-badge)


## Rynkowa Cena Energii

A Home Assistant integration for monitoring Polish electricity market prices (RCE - Rynkowa Cena Energii) from PSE (Polskie Sieci Elektroenergetyczne).

> This project is a fork of [lewa-reka/ha-rce-pse](https://github.com/lewa-reka/ha-rce-pse), developed independently as **RCE Prices** (`rce_prices`).

Instalation & Presentation: https://youtu.be/6N71uXgf9yc

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=plebann&repository=ha-rce-pse&category=integration)

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Search for **"RCE Prices"**
3. DOWNLOAD the integration
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/rce_prices` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

### Initial Setup

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=rce_prices)

1. Go to **Settings** > **Integrations**
2. Click **Add Integration** and search for "RCE Prices"
3. Configure the source price settings (see below)
4. Click **Submit** to complete the setup

## Usage Examples

Here are two ready-to-use dashboard card configurations that showcase different ways to display energy price data:

### 1. Advanced Charts with ApexCharts (Additional Dependencies Required)

This card provides advanced charting capabilities with professional-looking graphs and real-time price analysis. Perfect for users who want detailed visual analytics.

![ApexCharts Analysis Card](examples/images/card2_apexcharts.png)

**Configuration file**: [`PL: examples/pl/card2_apexcharts_analysis.yaml`](examples/pl/card2_apexcharts_analysis.yaml) [`EN: examples/en/card2_apexcharts_analysis.yaml`](examples/en/card2_apexcharts_analysis.yaml)


**Requirements:**
- `apexcharts-card` - Install via HACS → "ApexCharts Card"

### 2. Basic Overview (No Dependencies Required)

This card provides a comprehensive overview of current energy prices using standard Home Assistant entities. It's perfect for users who want a clean, simple display without additional dependencies.

![Basic Overview Card](examples/images/card1_basic.png)

**Configuration file**: [`PL: examples/pl/card1_basic_overview.yaml`](examples/pl/card1_basic_overview.yaml) [`EN: examples/en/card1_basic_overview.yaml`](examples/en/card1_basic_overview.yaml)


Both cards can be easily customized to match your dashboard theme and specific needs. Simply copy the YAML configuration from the respective files and paste them into your Home Assistant dashboard in edit mode.

## Features

- **Real-time price monitoring** - Current electricity price with 15-minute precision
- **Daily statistics** - Comprehensive price analysis (average, min, max, median)
- **Tomorrow's data** - Next day pricing available after 14:00 CET
- **Price comparison** - Today vs tomorrow percentage differences
- **Optimal time windows** - Automatic detection of cheapest and most expensive periods
- **Smart scheduling** - Built-in morning/evening best-price indicators
- **Peak avoidance** - Built-in high-cost window detection
- **Time range display** - Easy-to-read time ranges (e.g., "23:00 - 01:00")
- **Hourly price averaging** - Optional hourly price calculation for net-billing settlements
- **Automatic updates** - Data refreshed every 30 minutes from official PSE API

## Configuration

After installing the integration, you can configure it through the Home Assistant UI.

### Configuration Options

The integration provides configuration options for handling source prices:

#### Hourly Prices Option

This advanced option is useful for net-billing settlements due to prosumer metering with hourly accuracy despite 15-minute prices. When enabled, the integration calculates average prices for each hour from the published quarter-hour prices.

- **Use Hourly Prices** (true/false): Enable hourly price averaging
  - *Default*: false (uses original 15-minute prices)
  - *When enabled*: Calculates average price for each hour from 15-minute intervals
  - *Use case*: Net-billing settlements according to Art. 4b sec. 11 of the Ustawa o OZE

**How it works:**
- When disabled: Uses original 15-minute price data from PSE API
- When enabled: Calculates hourly averages and applies the same price to all 15-minute intervals within each hour
- Example: If hour 0 has prices [300, 320, 340, 360] PLN, all four 15-minute intervals will show 330 PLN (average)

### Reconfiguring Settings

You can modify these settings at any time:

1. Go to **Configuration** > **Integrations**
2. Find "RCE Prices" in your integrations list
3. Click **Configure** 
4. Adjust the settings as needed
5. Click **Submit** to apply changes

The integration will automatically reload with your new settings.

## Sensors

### Main Sensors
- **Price** - Current electricity price (with all daily prices as attributes)
- **Tomorrow Price** - Tomorrow's price (available after 14:00 CET) (with all prices for the next day as attributes)

### Today's Statistics
- **Today Average Price** - Average price for today
- **Today Maximum Price** - Highest price today
- **Today Minimum Price** - Lowest price today
- **Today Median Price** - Median price for today
- **Today Current vs Average** - Percentage difference between current and average price

### Tomorrow's Statistics (available after 14:00 CET)
- **Tomorrow Average Price** - Average price for tomorrow
- **Tomorrow Maximum Price** - Highest price tomorrow
- **Tomorrow Minimum Price** - Lowest price tomorrow
- **Tomorrow Median Price** - Median price for tomorrow
- **Tomorrow vs Today Average** - Percentage difference between tomorrow and today average

### Price Hours & Time Ranges
- **Today Max Price Hour Start/End** - When the highest price period starts/ends today
- **Today Min Price Hour Start/End** - When the lowest price period starts/ends today
- **Today Max Price Range** - Time range of highest price period (e.g., "17:00 - 18:00")
- **Today Min Price Range** - Time range of lowest price period (e.g., "02:00 - 03:00")
- **Tomorrow Max Price Hour Start/End** - When the highest price period starts/ends tomorrow
- **Tomorrow Min Price Hour Start/End** - When the lowest price period starts/ends tomorrow
- **Tomorrow Max Price Range** - Time range of highest price period tomorrow
- **Tomorrow Min Price Range** - Time range of lowest price period tomorrow

### Best Time Windows
- **Today Morning Best Price** - Lowest price in morning best window
- **Today Morning 2nd Best Price** - Second-lowest price in morning best window
- **Today Evening Best Price** - Lowest price in evening best window
- **Today Evening 2nd Best Price** - Second-lowest price in evening best window

## Binary Sensors

The integration provides binary sensors that indicate when you are currently within specific price windows. These sensors are perfect for automation triggers and dashboard indicators.

### Today's Price Window Binary Sensors

These sensors indicate whether you are currently within the most expensive or cheapest price periods for today:

- **Today Min Price Window Active** - `true` when currently within the lowest price period of the day
- **Today Max Price Window Active** - `true` when currently within the highest price period of the day

## Debugging

To enable debug logging for the RCE Prices integration, add the following to your Home Assistant `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.rce_prices: debug
```

This will enable detailed logging for:
- Integration setup and configuration
- API requests and responses 
- Data fetching and processing
- Sensor creation and updates
- Error handling and troubleshooting

After adding this configuration, restart Home Assistant and check the logs in:
- **Configuration** > **Logs** in the Home Assistant UI
- Or directly in the `home-assistant.log` file

Debug logs include:
- PSE API request URLs and parameters
- API response status and data counts
- Configuration flow steps
- Sensor setup progress
- Coordinator data updates

## Data Source

This integration fetches data from the official PSE API:
- **API**: `https://api.raporty.pse.pl/api` - API v2
- **Update Interval**: 30 minutes
- **Data Availability**: Tomorrow's prices are available after 14:00 CET

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Apache 2.0 License

Copyright 2025 Lewa-Reka and RCE PSE Integration Contributors (original work)
Copyright 2026 plebann (fork modifications)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate and ensure your code follows the project's coding standards. 
