# AI Agency NPS Survey Analyzer &amp; Feedback Intelligence Tool

A zero-dependency Python CLI tool for analyzing NPS survey data, generating 
client feedback intelligence, and producing actionable retention improvement plans.

## Features

- **NPS Analysis**: Calculate NPS scores, category breakdowns, and statistical summaries
- **Industry Benchmarking**: Compare NPS across industries and client segments
- **Trend Tracking**: Monitor NPS trends over time with direction analysis
- **Sentiment Analysis**: Classify feedback sentiment (positive/neutral/negative)
- **Action Plan Generator**: Targeted improvement recommendations based on detractor feedback
- **Verbatim Analysis**: Extract common themes from client comments
- **Professional Reports**: Beautiful HTML reports with inline CSS + Markdown exports
- **CSV Import/Export**: Compatible with any survey tool export

## Quick Start

```bash
# Generate 100 sample responses & analyze
python ai_client_nps_analyzer.py analyze --sample 100

# Generate a professional HTML report
python ai_client_nps_analyzer.py report --format html --sample 150

# Show NPS trends over 6 months
python ai_client_nps_analyzer.py trends --months 6

# Generate targeted action plan for detractors
python ai_client_nps_analyzer.py action-plan --segment detractors

# Load real CSV data
python ai_client_nps_analyzer.py analyze --input my_survey_data.csv
```

## CSV Format

Expected columns: `score`, `client_name`, `industry`, `date` (YYYY-MM-DD), `comments`

## Pricing

| Tier | Price | What's Included |
|------|-------|-----------------|
| **Standalone** | **$14** | Tool + docs + sample data |
| **Bundle** | **$37** | All 18+ AI agency tools (36% off $58) |
| **Agency** | **$97** | Bundle + white-label rights + priority updates |

## Framework

The tool uses a proprietary **F.E.E.D.B.A.C.K.** analysis framework:
- **F**ind patterns in verbatim feedback
- **E**valuate sentiment distribution
- **E**xamine industry-specific trends
- **D**iagnose detractor pain points
- **B**uild targeted improvement plans
- **A**nalyze score distribution
- **C**ompare across segments/managers
- **K**ey metrics dashboard

## Technical

- Zero external dependencies (stdlib only: csv, json, random, datetime)
- Python 3.8+ compatible
- HTML reports are self-contained (inline CSS, no CDN)
- ~42KB total footprint

## AI Revenue Toolkit

This tool is part of the **AI Revenue Toolkit** — a suite of 18+ agency operations 
tools. Get the full bundle at:
[https://tennie321.github.io/ai-revenue-toolkit/](https://tennie321.github.io/ai-revenue-toolkit/)