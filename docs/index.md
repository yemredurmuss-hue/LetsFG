---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

# :material-airplane: BoostedTravel

<p class="hero-tagline">Agent-native flight search & booking. 400+ airlines, straight from the terminal — no browser, no scraping.</p>

<div class="hero-badges">

[![PyPI](https://img.shields.io/pypi/v/boostedtravel?style=flat-square)](https://pypi.org/project/boostedtravel/)
[![npm](https://img.shields.io/npm/v/boostedtravel?style=flat-square)](https://www.npmjs.com/package/boostedtravel)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](https://github.com/Boosted-Chat/BoostedTravel/blob/main/LICENSE)

</div>

<div class="install-box">pip install boostedtravel</div>

<div class="hero-buttons">
<a href="getting-started.md" class="btn-primary">Get Started</a>
<a href="api-guide.md" class="btn-secondary">API Guide</a>
<a href="https://api.boostedchat.com/docs" class="btn-secondary">Swagger API</a>
</div>

</div>

---

<div class="feature-grid" markdown>

<a class="feature-card" href="getting-started.md">
<span class="feature-icon">:material-rocket-launch:</span>
<h3>Getting Started</h3>
<p>Register, set up auth & payment, and search your first flight in under 5 minutes.</p>
</a>

<a class="feature-card" href="api-guide.md">
<span class="feature-icon">:material-api:</span>
<h3>API Guide</h3>
<p>Error handling, search results, resolution, workflows, unlock mechanics, costs.</p>
</a>

<a class="feature-card" href="agent-guide.md">
<span class="feature-icon">:material-robot:</span>
<h3>AI Agent Guide</h3>
<p>Architecture patterns, preference scoring, rate limits, price tracking & persistence.</p>
</a>

<a class="feature-card" href="cli-reference.md">
<span class="feature-icon">:material-console:</span>
<h3>CLI Reference</h3>
<p>Every command, flag, cabin code, and option for the boostedtravel CLI.</p>
</a>

<a class="feature-card" href="packages.md">
<span class="feature-icon">:material-package-variant:</span>
<h3>Packages</h3>
<p>Python SDK, JavaScript SDK, MCP Server — all the ways to integrate.</p>
</a>

<a class="feature-card" href="https://api.boostedchat.com/docs">
<span class="feature-icon">:material-file-document-outline:</span>
<h3>OpenAPI Reference</h3>
<p>Interactive Swagger docs — try every endpoint directly in your browser.</p>
</a>

</div>

---

## Why BoostedTravel?

Flight websites inflate prices with demand tracking, cookie-based pricing, and surge markup. The same flight is often **$20–$50 cheaper** through BoostedTravel — raw airline price, zero markup.

<div class="pricing-table" markdown>

| | Google Flights / Booking / Expedia | **BoostedTravel** |
|---|---|---|
| Search | Free | **Free** |
| View details & price | Free (with tracking / inflation) | **Free** (no tracking) |
| Book | Ticket + hidden markup | **$1 unlock + ticket price** |
| Price goes up on repeat search? | Yes | **Never** |

</div>

---

## How It Works

<div class="steps">
<span class="step">:material-magnify: Search <small>(free)</small></span>
<span class="step-arrow">→</span>
<span class="step">:material-lock-open: Unlock <small>($1)</small></span>
<span class="step-arrow">→</span>
<span class="step">:material-check-circle: Book <small>(free)</small></span>
</div>

1. **Search** — returns offers with price, airlines, duration, stopovers, conditions. Completely free, unlimited.
2. **Unlock** — confirms live price with the airline, reserves for 30 minutes. $1 flat fee.
3. **Book** — creates real airline PNR. E-ticket sent to passenger email. Free after unlock.

---

## Quick Start

=== "Python CLI"

    ```bash
    pip install boostedtravel
    boostedtravel register --name my-agent --email you@example.com
    export BOOSTEDTRAVEL_API_KEY=trav_...

    boostedtravel search LHR JFK 2026-04-15
    boostedtravel unlock off_xxx
    boostedtravel book off_xxx \
      --passenger '{"id":"pas_0","given_name":"John","family_name":"Doe","born_on":"1990-01-15","gender":"m","title":"mr"}' \
      --email john.doe@example.com
    ```

=== "Python SDK"

    ```python
    from boostedtravel import BoostedTravel

    bt = BoostedTravel(api_key="trav_...")
    flights = bt.search("LHR", "JFK", "2026-04-15")

    unlocked = bt.unlock(flights.offers[0].id)
    booking = bt.book(
        offer_id=unlocked.offer_id,
        passengers=[{"id": "pas_0", "given_name": "John", "family_name": "Doe",
                     "born_on": "1990-01-15", "gender": "m", "title": "mr"}],
        contact_email="john.doe@example.com",
    )
    print(f"Booked! PNR: {booking.booking_reference}")
    ```

=== "JavaScript"

    ```typescript
    import { BoostedTravel } from 'boostedtravel';

    const bt = new BoostedTravel({ apiKey: 'trav_...' });
    const flights = await bt.search('LHR', 'JFK', '2026-04-15');
    console.log(`${flights.totalResults} offers`);
    ```

=== "MCP (Claude/Cursor)"

    ```json
    {
      "mcpServers": {
        "boostedtravel": {
          "command": "npx",
          "args": ["-y", "boostedtravel-mcp"],
          "env": { "BOOSTEDTRAVEL_API_KEY": "trav_..." }
        }
      }
    }
    ```

---

<div class="text-center" markdown>

**Ready to build?** [Get your API key :material-arrow-right:](getting-started.md){ .md-button .md-button--primary }

</div>
