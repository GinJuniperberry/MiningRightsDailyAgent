"""mining-news-mcp Mock 兜底数据

当真实 RSS 抓取失败或返回空时，使用这些样例数据保证 demo 可运行。
"""

MOCK_NEWS_ITEMS = [
    {
        "title": "Pilbara Minerals announces record lithium production in Q2 2026",
        "url": "https://www.mining.com/pilbara-minerals-q2-2026-record-production",
        "source": "mining.com",
        "published_at": "2026-07-09",
        "summary": "Pilbara Minerals reported record spodumene concentrate production of 210kt in Q2 2026, "
                   "exceeding guidance. The company attributed the result to improved plant throughput "
                   "and optimized processing operations at Pilgangoora.",
        "score": 0.92
    },
    {
        "title": "Lithium prices stabilize as demand from EV sector recovers",
        "url": "https://www.mining-journal.com/lithium-prices-stabilize-2026",
        "source": "mining-journal.com",
        "published_at": "2026-07-08",
        "summary": "Spot lithium carbonate prices have stabilized above 100,000 CNY/t as downstream "
                   "battery manufacturers restock inventories. Analysts expect prices to remain firm "
                   "in Q3 2026 supported by seasonal demand.",
        "score": 0.85
    },
    {
        "title": "Pilbara Minerals approves expansion of Pilgangoora operation",
        "url": "https://www.reuters.com/pilbara-minerals-pilgangoora-expansion",
        "source": "reuters.com",
        "published_at": "2026-07-07",
        "summary": "Pilbara Minerals has approved a expansion project to increase Pilgangoora's nameplate "
                   "capacity to 1.0 Mtpa. First production from the expanded operation is targeted for "
                   "H2 2027, subject to regulatory approvals and final investment decision.",
        "score": 0.80
    },
    {
        "title": "Australia imposes new export reporting requirements for critical minerals",
        "url": "https://www.mining.com/australia-critical-minerals-export-reporting",
        "source": "mining.com",
        "published_at": "2026-07-06",
        "summary": "The Australian government announced new quarterly reporting requirements for "
                   "critical minerals exporters including lithium, aimed at improving supply chain "
                   "transparency. The new rules take effect from Q1 2027.",
        "score": 0.75
    },
    {
        "title": "Global lithium demand forecast revised upward to 1.5 Mt LCE by 2030",
        "url": "https://www.mining-journal.com/global-lithium-demand-forecast-2030",
        "source": "mining-journal.com",
        "published_at": "2026-07-05",
        "summary": "Major forecasters revised global lithium demand projections upward, driven by "
                   "accelerating EV adoption and grid-scale energy storage deployment. Demand is "
                   "now expected to reach 1.5 Mt LCE by 2030, up from previous 1.3 Mt estimates.",
        "score": 0.78
    }
]

MOCK_ARTICLE = {
    "url": "https://www.mining.com/pilbara-minerals-q2-2026-record-production",
    "title": "Pilbara Minerals announces record lithium production in Q2 2026",
    "published_at": "2026-07-09",
    "source": "mining.com",
    "content": (
        "Pilbara Minerals Limited (ASX: PLS) today announced record spodumene concentrate "
        "production of 210kt for the June 2026 quarter, exceeding the upper end of guidance. "
        "The result was driven by improved plant throughput, optimized processing operations, "
        "and higher feed grades at the Pilgangoora Lithium Project in Western Australia.\n\n"
        "Key highlights for Q2 FY2026:\n"
        "- Spodumene concentrate production: 210kt (up 15% QoQ)\n"
        "- Ore processed: 4.2 Mt at 1.25% Li2O grade\n"
        "- Recovery rate: 68%, up from 65% in the previous quarter\n"
        "- Shipments: 205kt at average price of US$1,420/t CIF\n\n"
        "Managing Director and CEO Dale Henderson said: 'We are pleased to deliver record "
        "production this quarter, demonstrating the operational improvements we have implemented "
        "at Pilgangoora. Our team has done an outstanding job in optimizing plant performance "
        "and we remain on track to meet our full-year guidance.'\n\n"
        "The company maintained its full-year production guidance of 800-850kt and confirmed "
        "that the P680 expansion project remains on schedule for first production in Q1 2027."
    ),
    "citations": [
        "https://www.pilbaraminerals.com.au",
        "https://www.asx.com.au"
    ]
}
