#!/usr/bin/env python3
"""
AI Agency Client NPS Survey Analyzer & Feedback Intelligence Tool
A zero-dependency Python CLI tool for analyzing NPS survey data,
generating client feedback intelligence, and producing actionable
retention improvement plans.

Usage:
  python ai_client_nps_analyzer.py analyze --input sample_nps_data.csv
  python ai_client_nps_analyzer.py report --format html
  python ai_client_nps_analyzer.py trends --months 6
  python ai_client_nps_analyzer.py action-plan --segment detractors
"""

import csv
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from textwrap import dedent

# ─── Configuration ───────────────────────────────────────────────────────────

VERSION = "1.0.0"
PRODUCT_NAME = "AI Agency NPS Survey Analyzer & Feedback Intelligence Tool"
STANDALONE_PRICE = "$14"
BUNDLE_PRICE = "$37"
AGENCY_PRICE = "$97"

# NPS Framework categories
NPS_CATEGORIES = {
    "promoters": {"range": (9, 10), "label": "Promoters", "color": "green"},
    "passives": {"range": (7, 8), "label": "Passives", "color": "amber"},
    "detractors": {"range": (0, 6), "label": "Detractors", "color": "red"},
}

# 12 feedback dimensions for analysis
FEEDBACK_DIMENSIONS = [
    "communication", "quality", "timeliness", "value", "support",
    "expertise", "proactiveness", "reporting", "onboarding", "innovation",
    "partnership", "roi"
]

# Improvement recommendation templates per dimension
IMPROVEMENT_TEMPLATES = {
    "communication": [
        "Establish a regular communication cadence (weekly status calls, monthly business reviews)",
        "Create a client communication playbook with response time SLAs",
        "Implement a client portal for real-time project visibility",
        "Assign a dedicated account manager for high-value clients",
    ],
    "quality": [
        "Implement peer review processes before client delivery",
        "Create quality checklists for each service deliverable",
        "Conduct quarterly service quality audits with client input",
        "Establish quality metrics and track them per project",
    ],
    "timeliness": [
        "Review project scoping and timeline estimation process",
        "Implement project management tools with automated deadline tracking",
        "Build buffer time into project estimates",
        "Create escalation protocols for at-risk deadlines",
    ],
    "value": [
        "Document and share ROI metrics with clients quarterly",
        "Create case studies showing tangible results from your work",
        "Conduct quarterly business reviews highlighting value delivered",
        "Create value scorecards mapped to client KPIs",
    ],
    "support": [
        "Extend support hours or establish urgency-based response tiers",
        "Create a knowledge base for common client questions",
        "Implement a ticketing system with SLA tracking",
        "Assign backup team members for continuity",
    ],
    "expertise": [
        "Invest in team certifications and training programs",
        "Create thought leadership content in client industries",
        "Share industry insights and trends proactively with clients",
        "Invite clients to exclusive workshops and training sessions",
    ],
    "proactiveness": [
        "Conduct quarterly account planning sessions",
        "Set up automated alerts for client health indicators",
        "Create a proactive recommendation cadence",
        "Monitor industry changes and suggest relevant improvements",
    ],
    "reporting": [
        "Standardize client reporting templates and cadence",
        "Create automated dashboards for key client metrics",
        "Include forward-looking insights in reports, not just historical data",
        "Provide executive summaries for stakeholder communication",
    ],
    "onboarding": [
        "Create a structured 30-60-90 day onboarding program",
        "Assign onboarding specialists for new clients",
        "Create an onboarding checklist with milestones and deliverables",
        "Collect feedback at each onboarding stage",
    ],
    "innovation": [
        "Dedicate innovation time to improving client solutions",
        "Share emerging technology trends relevant to client industry",
        "Propose quarterly improvement initiatives for each client",
        "Create a client innovation advisory board",
    ],
    "partnership": [
        "Schedule quarterly strategic alignment meetings",
        "Create a joint roadmap with key clients",
        "Offer exclusive beta access to new features/services",
        "Establish a client advisory council",
    ],
    "roi": [
        "Create ROI measurement frameworks aligned with client goals",
        "Document and communicate quantifiable results monthly",
        "Build ROI calculators for each service offering",
        "Share industry benchmark data for context",
    ],
}

# Sample client industries
INDUSTRIES = [
    "SaaS", "E-Commerce", "Healthcare", "Real Estate", "Financial Services",
    "Education", "Professional Services", "Manufacturing", "Nonprofit", "Legal"
]

# Sample client names for demo
SAMPLE_CLIENTS = [
    ("Acme Corp", "SaaS"),
    ("BrightPath Health", "Healthcare"),
    ("Capital Ventures", "Financial Services"),
    ("DataFlow Inc", "SaaS"),
    ("EcoBuild Partners", "Real Estate"),
    ("FreshCart Online", "E-Commerce"),
    ("GlobalEd Solutions", "Education"),
    ("Harbor Legal Group", "Legal"),
    ("InnovateTech", "SaaS"),
    ("Junction Media", "Professional Services"),
    ("Kensington Advisors", "Financial Services"),
    ("Lakeside Manufacturing", "Manufacturing"),
    ("Meridian Health Systems", "Healthcare"),
    ("NorthStar Nonprofit", "Nonprofit"),
    ("Oxford Learning Institute", "Education"),
    ("Pacific Retail Group", "E-Commerce"),
    ("Quantum Analytics", "Professional Services"),
    ("Riverside Properties", "Real Estate"),
    ("Summit Legal Partners", "Legal"),
    ("Twin Oaks Manufacturing", "Manufacturing"),
    ("Urban Commerce Co", "E-Commerce"),
    ("Vertex Construction", "Real Estate"),
    ("WestBridge Nonprofit", "Nonprofit"),
    ("Xenith Technologies", "SaaS"),
]

SAMPLE_VERBATIM_COMMENTS = [
    "Great team, very responsive to our needs",
    "Quality has been inconsistent lately",
    "They really understand our business",
    "Communication could be more proactive",
    "Outstanding results, exceeded our expectations",
    "Slow response times when we need help urgently",
    "Very professional and knowledgeable team",
    "Would like more strategic guidance rather than just execution",
    "Excellent partnership, feels like an extension of our team",
    "Pricing feels high for the value delivered",
    "The reporting needs improvement - too much data, not enough insights",
    "Love the proactive suggestions for improvement",
    "Onboarding was smooth and well-organized",
    "Some projects have gone over timeline",
    "Their expertise in our industry really shows",
    "Would appreciate more frequent check-ins",
    "The ROI has been clear and measurable",
    "Support team is excellent - always helpful",
    "Need more innovation in our solutions",
    "Overall great experience, minor room for improvement",
    "They helped us achieve 40% efficiency gain",
    "Sometimes feel like just another account",
    "The quarterly reviews are very valuable",
    "Documentation could be better organized",
]


# ─── Core Classes ────────────────────────────────────────────────────────────

class NPSScore:
    """Represents an individual NPS survey response."""

    def __init__(self, score, client_name="", industry="", date=None,
                 comments="", segment="", account_manager=""):
        self.score = max(0, min(10, score))
        self.client_name = client_name
        self.industry = industry
        self.date = date or datetime.now()
        self.comments = comments
        self.segment = segment
        self.account_manager = account_manager

    @property
    def category(self):
        if self.score >= 9:
            return "promoters"
        elif self.score >= 7:
            return "passives"
        return "detractors"

    @property
    def category_label(self):
        return NPS_CATEGORIES[self.category]["label"]

    @property
    def category_color(self):
        return NPS_CATEGORIES[self.category]["color"]

    def __repr__(self):
        return f"NPSScore({self.score}, {self.client_name})"


class NPSDataset:
    """Collection of NPS survey responses with analysis methods."""

    def __init__(self, responses=None):
        self.responses = responses or []

    def add(self, response):
        self.responses.append(response)

    @property
    def total(self):
        return len(self.responses)

    @property
    def promoters(self):
        return [r for r in self.responses if r.category == "promoters"]

    @property
    def passives(self):
        return [r for r in self.responses if r.category == "passives"]

    @property
    def detractors(self):
        return [r for r in self.responses if r.category == "detractors"]

    @property
    def promoter_count(self):
        return len(self.promoters)

    @property
    def passive_count(self):
        return len(self.passives)

    @property
    def detractor_count(self):
        return len(self.detractors)

    @property
    def score_distribution(self):
        dist = Counter()
        for r in self.responses:
            dist[r.score] += 1
        return dist

    @property
    def average_score(self):
        if not self.responses:
            return 0
        scores = [r.score for r in self.responses if r.score is not None]
        return sum(scores) / len(scores) if scores else 0

    @property
    def nps_score(self):
        """Calculates Net Promoter Score: %Promoters - %Detractors, range -100 to 100"""
        if self.total == 0:
            return 0
        pct_promoters = (self.promoter_count / self.total) * 100
        pct_detractors = (self.detractor_count / self.total) * 100
        return round(pct_promoters - pct_detractors)

    @property
    def nps_rating(self):
        score = self.nps_score
        if score >= 70:
            return "Excellent"
        elif score >= 50:
            return "Great"
        elif score >= 30:
            return "Good"
        elif score >= 0:
            return "Needs Improvement"
        else:
            return "Critical"

    @property
    def nps_color(self):
        score = self.nps_score
        if score >= 50:
            return "green"
        elif score >= 0:
            return "amber"
        return "red"

    def by_industry(self):
        groups = defaultdict(list)
        for r in self.responses:
            groups[r.industry].append(r)
        return dict(groups)

    def by_account_manager(self):
        groups = defaultdict(list)
        for r in self.responses:
            groups[r.account_manager or "Unassigned"].append(r)
        return dict(groups)

    def by_month(self):
        groups = defaultdict(list)
        for r in self.responses:
            key = r.date.strftime("%Y-%m")
            groups[key].append(r)
        return dict(groups)

    def industry_analysis(self):
        results = {}
        for industry, responses in self.by_industry().items():
            ds = NPSDataset(responses)
            results[industry] = {
                "count": ds.total,
                "nps": ds.nps_score,
                "avg_score": round(ds.average_score, 1),
                "promoters": ds.promoter_count,
                "passives": ds.passive_count,
                "detractors": ds.detractor_count,
                "rating": ds.nps_rating,
            }
        return results

    def trend_data(self):
        trends = {}
        for month, responses in sorted(self.by_month().items()):
            ds = NPSDataset(responses)
            trends[month] = {
                "count": ds.total,
                "nps": ds.nps_score,
                "avg_score": round(ds.average_score, 1),
            }
        return trends

    def response_rate(self, total_sent):
        """Calculate response rate given total surveys sent."""
        if total_sent <= 0:
            return 0
        return round((self.total / total_sent) * 100, 1)

    def top_complaints(self, limit=10):
        """Extract common themes from detractor comments."""
        keywords = [
            "slow", "expensive", "communication", "quality", "timeliness",
            "support", "response", "value", "inconsistent", "unclear",
            "confusing", "difficult", "complex", "bureaucratic", "disorganized"
        ]
        complaints = Counter()
        for r in self.detractors:
            if r.comments:
                text = r.comments.lower()
                for kw in keywords:
                    if kw in text:
                        complaints[kw] += 1
        return complaints.most_common(limit)

    def sentiment_summary(self):
        positive = sum(1 for r in self.responses if r.score >= 8)
        neutral = sum(1 for r in self.responses if 5 <= r.score <= 7)
        negative = sum(1 for r in self.responses if r.score < 5)
        return {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "positive_pct": round(positive / self.total * 100, 1) if self.total else 0,
            "neutral_pct": round(neutral / self.total * 100, 1) if self.total else 0,
            "negative_pct": round(negative / self.total * 100, 1) if self.total else 0,
        }

    def generate_action_plan(self, segment="all"):
        """Generate targeted improvement recommendations."""
        if segment == "detractors":
            target = self.detractors
        elif segment == "passives":
            target = self.passives
        elif segment == "promoters":
            target = self.promoters
        else:
            target = self.responses

        # Analyze comments to find weak dimensions
        dimension_scores = {d: [] for d in FEEDBACK_DIMENSIONS}
        for r in target:
            if r.comments:
                text = r.comments.lower()
                for dim in FEEDBACK_DIMENSIONS:
                    if dim in text:
                        dimension_scores[dim].append(r.score)

        # Score dimensions (higher = better)
        dim_avg = {}
        for dim, scores in dimension_scores.items():
            dim_avg[dim] = sum(scores) / len(scores) if scores else 7.0

        # Sort by weakness (lowest scores first)
        sorted_dims = sorted(dim_avg.items(), key=lambda x: x[1])

        # Generate recommendations
        recommendations = []
        for dim, avg_score in sorted_dims:
            if avg_score < 7:
                templates = IMPROVEMENT_TEMPLATES.get(dim, [])
                for t in templates[:2]:
                    recommendations.append({
                        "dimension": dim,
                        "current_score": round(avg_score, 1),
                        "priority": "high" if avg_score < 5 else "medium",
                        "recommendation": t,
                    })

        return recommendations


# ─── Data Generators ─────────────────────────────────────────────────────────

def generate_sample_data(count=100, multi_month=True):
    """Generate realistic synthetic NPS survey data for demonstration."""
    dataset = NPSDataset()
    base_date = datetime.now() - timedelta(days=180)

    # Score distribution weights for realism
    score_weights = [0.02, 0.01, 0.02, 0.03, 0.05, 0.07, 0.12, 0.18, 0.20, 0.15, 0.15]

    managers = [
        "Sarah Chen", "Marcus Johnson", "Emily Rodriguez", "David Kim",
        "Jessica Patel", "Andrew Thompson", "Rachel Green", "Michael Torres"
    ]

    for i in range(count):
        # Weight score toward higher values for realism
        score = random.choices(range(11), weights=score_weights, k=1)[0]

        client, industry = random.choice(SAMPLE_CLIENTS)
        date_offset = random.randint(0, 180) if multi_month else random.randint(0, 30)
        survey_date = base_date + timedelta(days=date_offset)

        comments = random.choice(SAMPLE_VERBATIM_COMMENTS) if random.random() > 0.4 else ""

        dataset.add(NPSScore(
            score=score,
            client_name=client,
            industry=industry,
            date=survey_date,
            comments=comments,
            segment=client.split()[0].lower(),
            account_manager=random.choice(managers),
        ))

    return dataset


# ─── Report Generators ──────────────────────────────────────────────────────

def generate_html_report(dataset, filename="nps_analysis_report.html"):
    """Generate a professional HTML report with inline CSS."""
    nps = dataset.nps_score
    rating = dataset.nps_rating
    color = dataset.nps_color

    # Industry breakdown
    industry_rows = ""
    for industry, info in sorted(dataset.industry_analysis().items(), key=lambda x: -x[1]["nps"]):
        bar_color = "green" if info["nps"] >= 50 else ("amber" if info["nps"] >= 0 else "red")
        bar_width = max(10, (info["nps"] + 100) / 2)
        industry_rows += f"""
        <tr>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;font-weight:600;">{industry}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">{info['count']}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">
                <span style="color:{'#22c55e' if info['nps']>=50 else ('#f59e0b' if info['nps']>=0 else '#ef4444')};font-weight:700;">{info['nps']}</span>
            </td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">
                <div style="background:#374151;border-radius:4px;height:20px;width:100%;">
                    <div style="background:{'#22c55e' if info['nps']>=50 else ('#f59e0b' if info['nps']>=0 else '#ef4444')};width:{bar_width}%;height:20px;border-radius:4px;"></div>
                </div>
            </td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">{info['rating']}</td>
        </tr>"""

    # Trend data
    trend_rows = ""
    for month, data in sorted(dataset.trend_data().items()):
        trend_rows += f"""
        <tr>
            <td style="padding:6px 12px;border-bottom:1px solid #2a2a2a;">{month}</td>
            <td style="padding:6px 12px;border-bottom:1px solid #2a2a2a;">{data['count']}</td>
            <td style="padding:6px 12px;border-bottom:1px solid #2a2a2a;color:{'#22c55e' if data['nps']>=50 else ('#f59e0b' if data['nps']>=0 else '#ef4444')};font-weight:700;">{data['nps']}</td>
            <td style="padding:6px 12px;border-bottom:1px solid #2a2a2a;">{data['avg_score']}</td>
        </tr>"""

    # Action recommendations
    recommendations = dataset.generate_action_plan("detractors")
    action_items = ""
    for rec in recommendations[:8]:
        priority_badge = f'<span style="background:{ "#ef4444" if rec["priority"]=="high" else "#f59e0b" };color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">{rec["priority"].upper()}</span>'
        action_items += f"""
        <div style="background:#1e293b;border-radius:8px;padding:12px 16px;margin-bottom:8px;border-left:3px solid {'#ef4444' if rec['priority']=='high' else '#f59e0b'};">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                <strong style="text-transform:capitalize;color:#e2e8f0;">{rec['dimension']}</strong>
                {priority_badge}
            </div>
            <p style="margin:4px 0 0;color:#94a3b8;font-size:13px;">Score: {rec['current_score']}/10</p>
            <p style="margin:4px 0 0;color:#cbd5e1;font-size:14px;">{rec['recommendation']}</p>
        </div>"""

    # Verbatim comments
    comment_items = ""
    for r in random.sample(dataset.responses, min(10, dataset.total)):
        emoji = "🟢" if r.category == "promoters" else ("🟡" if r.category == "passives" else "🔴")
        comment_items += f"""
        <div style="background:#1e293b;border-radius:8px;padding:12px 16px;margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span><strong style="color:#e2e8f0;">{r.client_name}</strong> <span style="color:#64748b;">({r.industry})</span></span>
                <span>{emoji} <strong>{r.score}/10</strong></span>
            </div>
            {f'<p style="margin:4px 0 0;color:#94a3b8;font-style:italic;">"{r.comments}"</p>' if r.comments else ''}
        </div>"""

    # Build full HTML
    # (score bar color handling)
    nps_bar_pct = max(5, (nps + 100) / 2)
    nps_bar_bg = {"green": "#22c55e", "amber": "#f59e0b", "red": "#ef4444"}[color]

    sentiment = dataset.sentiment_summary()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NPS Client Feedback Intelligence Report</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#0f172a; color:#e2e8f0; line-height:1.6; }}
.container {{ max-width:1000px; margin:0 auto; padding:40px 20px; }}
.header {{ text-align:center; margin-bottom:40px; }}
.header h1 {{ font-size:2em; background:linear-gradient(135deg,#818cf8,#22c55e); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:8px; }}
.header p {{ color:#64748b; }}
.card {{ background:#1e293b; border-radius:12px; padding:24px; margin-bottom:20px; }}
.card h2 {{ color:#818cf8; margin-bottom:16px; font-size:1.3em; }}
.stat-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:16px; margin-bottom:20px; }}
.stat {{ text-align:center; padding:16px; background:#334155; border-radius:8px; }}
.stat .value {{ font-size:2em; font-weight:700; }}
.stat .label {{ color:#94a3b8; font-size:13px; margin-top:4px; }}
.nps-meter {{ text-align:center; padding:24px; background:#334155; border-radius:12px; margin-bottom:20px; }}
.nps-meter .score {{ font-size:4em; font-weight:800; }}
.nps-meter .rating {{ font-size:1.1em; }}
.nps-bar {{ background:#374151; border-radius:6px; height:24px; margin:16px 0; overflow:hidden; }}
.nps-bar-fill {{ height:24px; border-radius:6px; transition:width 0.5s ease; }}
table {{ width:100%; border-collapse:collapse; }}
th {{ padding:8px 12px; text-align:left; border-bottom:2px solid #334155; color:#94a3b8; font-size:12px; text-transform:uppercase; letter-spacing:1px; }}
td {{ padding:8px 12px; border-bottom:1px solid #2a2a2a; }}
.footer {{ text-align:center; color:#64748b; font-size:12px; margin-top:40px; padding-top:20px; border-top:1px solid #1e293b; }}
@media print {{
    body {{ background:#fff; color:#1e293b; }}
    .card {{ background:#f8fafc; border:1px solid #e2e8f0; }}
    .stat {{ background:#f1f5f9; }}
    .nps-meter {{ background:#f1f5f9; }}
    .header h1 {{ -webkit-text-fill-color:#6366f1; }}
}}
</style>
</head>
<body>
<div class="container">

<!-- HEADER -->
<div class="header">
    <h1>📊 NPS Client Feedback Intelligence</h1>
    <p>Generated {datetime.now().strftime("%B %d, %Y")} | {dataset.total} responses across {len(dataset.by_industry())} industries</p>
</div>

<!-- NPS METER -->
<div class="nps-meter">
    <div class="score" style="color:{nps_bar_bg};">{nps}</div>
    <div class="rating" style="color:{nps_bar_bg};font-weight:600;">{rating}</div>
    <div class="nps-bar">
        <div class="nps-bar-fill" style="width:{nps_bar_pct}%;background:{nps_bar_bg};"></div>
    </div>
</div>

<!-- KEY STATS -->
<div class="stat-grid">
    <div class="stat">
        <div class="value" style="color:#22c55e;">{dataset.promoter_count}</div>
        <div class="label">Promoters</div>
        <div style="font-size:11px;color:#64748b;">Scores 9-10</div>
    </div>
    <div class="stat">
        <div class="value" style="color:#f59e0b;">{dataset.passive_count}</div>
        <div class="label">Passives</div>
        <div style="font-size:11px;color:#64748b;">Scores 7-8</div>
    </div>
    <div class="stat">
        <div class="value" style="color:#ef4444;">{dataset.detractor_count}</div>
        <div class="label">Detractors</div>
        <div style="font-size:11px;color:#64748b;">Scores 0-6</div>
    </div>
    <div class="stat">
        <div class="value" style="color:#818cf8;">{round(dataset.average_score,1)}</div>
        <div class="label">Avg Score</div>
        <div style="font-size:11px;color:#64748b;">/10</div>
    </div>
    <div class="stat">
        <div class="value" style="color:#818cf8;">{sentiment['positive']}</div>
        <div class="label">Positive</div>
        <div style="font-size:11px;color:#64748b;">Score 8-10</div>
    </div>
    <div class="stat">
        <div class="value" style="color:#818cf8;">{sentiment['negative']}</div>
        <div class="label">Negative</div>
        <div style="font-size:11px;color:#64748b;">Score 0-4</div>
    </div>
</div>

<!-- SENTIMENT BREAKDOWN -->
<div class="card">
    <h2>📈 Sentiment Distribution</h2>
    <div style="display:flex;gap:8px;margin-bottom:16px;">
        <div style="flex:{sentiment['positive_pct']};background:#22c55e;height:40px;border-radius:6px;display:flex;align-items:center;justify-content:center;min-width:40px;font-weight:700;font-size:14px;">{sentiment['positive_pct']}%</div>
        <div style="flex:{sentiment['neutral_pct']};background:#f59e0b;height:40px;border-radius:6px;display:flex;align-items:center;justify-content:center;min-width:40px;font-weight:700;font-size:14px;">{sentiment['neutral_pct']}%</div>
        <div style="flex:{sentiment['negative_pct']};background:#ef4444;height:40px;border-radius:6px;display:flex;align-items:center;justify-content:center;min-width:40px;font-weight:700;font-size:14px;">{sentiment['negative_pct']}%</div>
    </div>
    <div style="display:flex;gap:16px;font-size:13px;color:#94a3b8;">
        <span>🟢 Positive ({sentiment['positive_pct']}%)</span>
        <span>🟡 Neutral ({sentiment['neutral_pct']}%)</span>
        <span>🔴 Negative ({sentiment['negative_pct']}%)</span>
    </div>
</div>

<!-- TREND -->
<div class="card">
    <h2>📅 NPS Trend (Last {len(dataset.trend_data())} Months)</h2>
    <table>
        <tr><th>Month</th><th>Responses</th><th>NPS</th><th>Avg Score</th></tr>
        {trend_rows}
    </table>
</div>

<!-- INDUSTRY BREAKDOWN -->
<div class="card">
    <h2>🏢 Industry Breakdown</h2>
    <table>
        <tr><th>Industry</th><th>Responses</th><th>NPS</th><th>Bar</th><th>Rating</th></tr>
        {industry_rows}
    </table>
</div>

<!-- ACTIONABLE RECOMMENDATIONS -->
<div class="card">
    <h2>🎯 Priority Improvement Actions</h2>
    <p style="color:#94a3b8;font-size:14px;margin-bottom:12px;">Targeted recommendations based on detractor feedback analysis</p>
    {action_items}
</div>

<!-- VERBATIM FEEDBACK -->
<div class="card">
    <h2>💬 Client Verbatim Feedback (Sample)</h2>
    {comment_items}
</div>

<!-- SCORE DISTRIBUTION -->
<div class="card">
    <h2>📊 Score Distribution</h2>
    <table>
        <tr><th>Score</th><th>Count</th><th>Distribution</th></tr>
"""
    for score in range(10, -1, -1):
        count = dataset.score_distribution.get(score, 0)
        bar_width = (count / max(dataset.total, 1)) * 100
        s_color = "22c55e" if score >= 9 else ("f59e0b" if score >= 7 else "ef4444")
        html += f"""
        <tr>
            <td style="padding:4px 12px;border-bottom:1px solid #2a2a2a;font-weight:600;color:#{s_color};">{score}</td>
            <td style="padding:4px 12px;border-bottom:1px solid #2a2a2a;">{count}</td>
            <td style="padding:4px 12px;border-bottom:1px solid #2a2a2a;">
                <div style="background:#374151;border-radius:4px;height:16px;width:100%;">
                    <div style="background:#{s_color};width:{bar_width}%;height:16px;border-radius:4px;"></div>
                </div>
            </td>
        </tr>"""

    html += f"""
    </table>
</div>

<!-- FOOTER -->
<div class="footer">
    <p>Generated by {PRODUCT_NAME} v{VERSION}</p>
    <p>Standalone: {STANDALONE_PRICE} | Bundle: {BUNDLE_PRICE} | Agency: {AGENCY_PRICE}</p>
    <p style="margin-top:8px;">AI Agency Revenue Toolkit — <a href="https://tennie321.github.io/ai-revenue-toolkit/" style="color:#818cf8;">tennie321.github.io/ai-revenue-toolkit</a></p>
</div>

</div>
</body>
</html>"""
    return html


def generate_markdown_report(dataset):
    """Generate markdown report."""
    lines = []
    lines.append("# 📊 NPS Client Feedback Intelligence Report")
    lines.append(f"")
    lines.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y')}")
    lines.append(f"**Total Responses:** {dataset.total}")
    lines.append(f"")
    lines.append("## NPS Score Meter")
    lines.append(f"")
    lines.append(f"**NPS Score: {dataset.nps_score}** — {dataset.nps_rating}")
    lines.append(f"")
    lines.append("| Category | Count | Percentage |")
    lines.append("|----------|-------|------------|")
    lines.append(f"| 🟢 Promoters (9-10) | {dataset.promoter_count} | {round(dataset.promoter_count/dataset.total*100) if dataset.total else 0}% |")
    lines.append(f"| 🟡 Passives (7-8) | {dataset.passive_count} | {round(dataset.passive_count/dataset.total*100) if dataset.total else 0}% |")
    lines.append(f"| 🔴 Detractors (0-6) | {dataset.detractor_count} | {round(dataset.detractor_count/dataset.total*100) if dataset.total else 0}% |")
    lines.append(f"")
    lines.append(f"**Average Score:** {round(dataset.average_score, 1)}/10")
    lines.append(f"")

    # Industry breakdown
    lines.append("## Industry Breakdown")
    lines.append("")
    lines.append("| Industry | NPS | Count | Rating |")
    lines.append("|----------|-----|-------|--------|")
    for industry, info in sorted(dataset.industry_analysis().items(), key=lambda x: -x[1]["nps"]):
        lines.append(f"| {industry} | {info['nps']} | {info['count']} | {info['rating']} |")
    lines.append("")

    # Trend
    lines.append("## NPS Trend")
    lines.append("")
    lines.append("| Month | Responses | NPS | Avg Score |")
    lines.append("|-------|-----------|-----|-----------|")
    for month, data in sorted(dataset.trend_data().items()):
        lines.append(f"| {month} | {data['count']} | {data['nps']} | {data['avg_score']} |")
    lines.append("")

    # Recommendations
    lines.append("## 🎯 Priority Action Recommendations")
    lines.append("")
    recs = dataset.generate_action_plan("detractors")
    for i, rec in enumerate(recs[:10], 1):
        priority = f"[{rec['priority'].upper()}]" if rec['priority'] else ""
        lines.append(f"{i}. **{rec['dimension'].title()}** {priority} — Score: {rec['current_score']}/10")
        lines.append(f"   → {rec['recommendation']}")
        lines.append("")

    # Top complaints
    lines.append("## Top Detractor Themes")
    lines.append("")
    for kw, count in dataset.top_complaints(5):
        lines.append(f"- **{kw.title()}** mentioned {count} times")
    lines.append("")

    lines.append("---")
    lines.append(f"*Generated by {PRODUCT_NAME} v{VERSION}*")
    lines.append(f"*Standalone: {STANDALONE_PRICE} | Bundle: {BUNDLE_PRICE} | Agency: {AGENCY_PRICE}*")
    return "\n".join(lines)


# ─── CLI Interface ──────────────────────────────────────────────────────────

def cmd_analyze(args):
    """Analyze NPS survey data from CSV file or generate sample."""
    if args.input and os.path.exists(args.input):
        dataset = load_csv(args.input)
        print(f"📊 Loaded {dataset.total} responses from {args.input}")
    else:
        count = args.sample or 100
        dataset = generate_sample_data(count)
        print(f"📊 Generated {dataset.total} sample NPS responses")

    print(f"\n{'='*50}")
    print(f"NPS Score: {dataset.nps_score} — {dataset.nps_rating}")
    print(f"{'='*50}")
    print(f"Promoters:  {dataset.promoter_count} ({round(dataset.promoter_count/dataset.total*100)}%)")
    print(f"Passives:   {dataset.passive_count} ({round(dataset.passive_count/dataset.total*100)}%)")
    print(f"Detractors: {dataset.detractor_count} ({round(dataset.detractor_count/dataset.total*100)}%)")
    print(f"Avg Score:  {round(dataset.average_score, 1)}/10")
    print(f"\nTop Industries by NPS:")
    for industry, info in sorted(dataset.industry_analysis().items(), key=lambda x: -x[1]["nps"])[:5]:
        print(f"  {industry}: {info['nps']} ({info['count']} responses)")
    print(f"\nTop Detractor Themes:")
    for kw, count in dataset.top_complaints(5):
        print(f"  - {kw}: {count} mentions")

    print(f"\n💡 Run with --report to generate a full report")
    return dataset


def cmd_report(args):
    """Generate professional report in HTML and/or Markdown."""
    if args.input and os.path.exists(args.input):
        dataset = load_csv(args.input)
    else:
        count = args.sample or 100
        dataset = generate_sample_data(count)

    output_format = args.format or "both"

    if output_format in ("html", "both"):
        html = generate_html_report(dataset)
        html_file = args.output or "nps_analysis_report.html"
        if not html_file.endswith(".html"):
            html_file += ".html"
        with open(html_file, "w") as f:
            f.write(html)
        print(f"✅ HTML report generated: {html_file}")

    if output_format in ("md", "markdown", "both"):
        md = generate_markdown_report(dataset)
        md_file = (args.output.replace(".html", ".md") if args.output and ".html" in args.output
                   else (args.output + ".md" if args.output else "nps_analysis_report.md"))
        if not md_file.endswith(".md"):
            md_file += ".md"
        with open(md_file, "w") as f:
            f.write(md)
        print(f"✅ Markdown report generated: {md_file}")

    print(f"\n📊 NPS Score: {dataset.nps_score} — {dataset.nps_rating}")


def cmd_sample(args):
    """Generate sample NPS data CSV file."""
    count = args.count or 100
    output = args.output or "sample_nps_data.csv"
    dataset = generate_sample_data(count)
    save_csv(dataset, output)
    print(f"✅ Generated {count} sample NPS responses → {output}")
    print(f"   NPS Score: {dataset.nps_score} — {dataset.nps_rating}")


def cmd_trends(args):
    """Show NPS trends over time."""
    if args.input and os.path.exists(args.input):
        dataset = load_csv(args.input)
    else:
        dataset = generate_sample_data(200, multi_month=True)

    months = args.months or 6
    trends = dataset.trend_data()
    recent_months = list(trends.keys())[-months:]

    print(f"\n📈 NPS Trend (Last {len(recent_months)} months)")
    print(f"{'='*50}")
    print(f"{'Month':<12} {'Resp':>5} {'NPS':>6} {'Avg':>6} {'Bar':<20}")
    print(f"{'-'*12} {'-'*5} {'-'*6} {'-'*6} {'-'*20}")
    for month in recent_months:
        data = trends[month]
        bar = "█" * max(1, (data["nps"] + 100) // 10)
        print(f"{month:<12} {data['count']:>5} {data['nps']:>6} {data['avg_score']:>6} {bar:<20}")

    # Direction
    if len(recent_months) >= 2:
        first = trends[recent_months[0]]["nps"]
        last = trends[recent_months[-1]]["nps"]
        direction = "📈 Upward" if last > first else ("📉 Downward" if last < first else "➡️ Stable")
        print(f"\nDirection: {direction} ({first} → {last})")
        delta = last - first
        if delta > 0:
            print(f"✅ NPS improved by {delta} points")
        elif delta < 0:
            print(f"⚠️  NPS declined by {abs(delta)} points — investigate")
        else:
            print(f"No change in NPS")


def cmd_action_plan(args):
    """Generate targeted action plan for a segment."""
    if args.input and os.path.exists(args.input):
        dataset = load_csv(args.input)
    else:
        dataset = generate_sample_data(100)

    segment = args.segment or "detractors"
    recs = dataset.generate_action_plan(segment)

    segment_label = {"all": "All Clients", "detractors": "Detractors",
                     "passives": "Passives", "promoters": "Promoters"}

    print(f"\n🎯 Action Plan for: {segment_label.get(segment, segment)}")
    print(f"{'='*60}")
    for i, rec in enumerate(recs, 1):
        priority = f"[{rec['priority'].upper()}]" if rec.get("priority") else ""
        print(f"\n{i}. {rec['dimension'].title()} {priority}")
        print(f"   Current Score: {rec['current_score']}/10")
        print(f"   → {rec['recommendation']}")

    if not recs:
        print(f"\n✅ No critical recommendations for this segment!")


def cmd_export_csv(args):
    """Export current dataset to CSV."""
    if args.input and os.path.exists(args.input):
        dataset = load_csv(args.input)
    else:
        print("❌ No input file specified")
        return 1

    output = args.output or "nps_export.csv"
    save_csv(dataset, output)
    print(f"✅ Exported {dataset.total} responses → {output}")


def load_csv(filepath):
    """Load NPS data from CSV file."""
    dataset = NPSDataset()
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                score = int(row.get("score", 0))
                date_str = row.get("date", "")
                date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
                dataset.add(NPSScore(
                    score=score,
                    client_name=row.get("client_name", row.get("client", "")),
                    industry=row.get("industry", ""),
                    date=date,
                    comments=row.get("comments", row.get("feedback", row.get("verbatim", ""))),
                    segment=row.get("segment", ""),
                    account_manager=row.get("account_manager", row.get("manager", "")),
                ))
            except (ValueError, KeyError) as e:
                print(f"⚠️  Skipping row: {e}")
    return dataset


def save_csv(dataset, filepath):
    """Save NPS dataset to CSV."""
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["client_name", "industry", "score", "date", "comments",
                         "category", "account_manager"])
        for r in dataset.responses:
            writer.writerow([
                r.client_name, r.industry, r.score,
                r.date.strftime("%Y-%m-%d"), r.comments,
                r.category_label, r.account_manager,
            ])


# ─── Main CLI ────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=f"{PRODUCT_NAME} v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(f"""
Examples:
  python {sys.argv[0]} analyze --sample 100
  python {sys.argv[0]} analyze --input sample_nps_data.csv
  python {sys.argv[0]} report --format html --sample 150
  python {sys.argv[0]} report --format md --input data.csv
  python {sys.argv[0]} trends --months 12
  python {sys.argv[0]} action-plan --segment detractors
  python {sys.argv[0]} sample --count 200 --output my_data.csv

Pricing:
  Standalone: {STANDALONE_PRICE}  |  Bundle: {BUNDLE_PRICE}  |  Agency: {AGENCY_PRICE}
        """)
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze NPS survey data")
    p_analyze.add_argument("--input", "-i", help="CSV file with NPS data (columns: score, client_name, industry, date, comments)")
    p_analyze.add_argument("--sample", "-s", type=int, default=100, help="Generate N sample responses if no input")

    # report
    p_report = subparsers.add_parser("report", help="Generate professional NPS report")
    p_report.add_argument("--format", "-f", choices=["html", "md", "markdown", "both"], default="both", help="Output format")
    p_report.add_argument("--input", "-i", help="CSV input file")
    p_report.add_argument("--sample", "-s", type=int, help="Sample size if no input")
    p_report.add_argument("--output", "-o", default="nps_analysis_report", help="Output filename (without extension)")

    # sample
    p_sample = subparsers.add_parser("sample", help="Generate sample NPS data CSV")
    p_sample.add_argument("--count", "-c", type=int, default=100, help="Number of sample responses")
    p_sample.add_argument("--output", "-o", default="sample_nps_data.csv", help="Output CSV filename")

    # trends
    p_trends = subparsers.add_parser("trends", help="Show NPS trends over time")
    p_trends.add_argument("--input", "-i", help="CSV input file")
    p_trends.add_argument("--months", "-m", type=int, default=6, help="Number of months to show")

    # action-plan
    p_action = subparsers.add_parser("action-plan", help="Generate targeted improvement action plan")
    p_action.add_argument("--segment", "-s", choices=["all", "promoters", "passives", "detractors"], default="detractors", help="Client segment to target")
    p_action.add_argument("--input", "-i", help="CSV input file")

    # export
    p_export = subparsers.add_parser("export", help="Export dataset to CSV")
    p_export.add_argument("--input", "-i", required=True, help="Input CSV file")
    p_export.add_argument("--output", "-o", default="nps_export.csv", help="Output CSV filename")

    # Version
    parser.add_argument("--version", "-v", action="version", version=f"v{VERSION}")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "analyze": cmd_analyze,
        "report": cmd_report,
        "sample": cmd_sample,
        "trends": cmd_trends,
        "action-plan": cmd_action_plan,
        "export": cmd_export_csv,
    }

    cmd = commands.get(args.command)
    if cmd:
        cmd(args)


if __name__ == "__main__":
    main()