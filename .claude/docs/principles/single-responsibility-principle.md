# Single responsibility principle

The Single Responsibility Principle is foundational to writing maintainable code. It's deceptively simple to state but surprisingly hard to apply consistently. Understanding it deeply changes how you think about class and method design.

## The core principle

A **function** or **method** should do one thing and only one thing.\
A **class** should do the smallest possible useful thing.\
A **module** should group together things that change for the same reason.

Different framings, same underlying principle: **one reason to change**.

If every entity only does one thing, there is only one reason ever to change it: if the way in which it does that thing must change. Robert C. Martin captured this as:

> There should never be more than one reason for a class to change.

This lens helps you spot problems. Ask <mark>what can change and how those changes affect your class</mark>:

- If the database changes, does your class need to change?
- If the output device changes (screen, mobile, printer), does your class need to change?
- If your class needs to change because of changes from many different directions, it has too many responsibilities.

**Gather together the things that change for the same reasons.** Separate those things that change for different reasons.

Martin later clarified that a "reason to change" often comes from a specific *role* or *actor*. While one person might wear multiple hats, the role of an accountant is different from a database administrator. Each module should be responsible to one role. If the accountant needs a change, it shouldn't affect the DBA's code.

## One thing vs one responsibility

"Do one thing" is easy to misunderstand. It sounds like a class should have one method, or a function should have one line. That's not what it means.

**Doing one thing** — a single action, a single step, a single operation.

**Having one responsibility** — owning all the tasks required to achieve one result.

A `Wheel` class might have `diameter`, `circumference`, and `rotation_speed` methods. That's three things, but one responsibility: wheel measurements. They all change for the same reason — if the wheel's geometry changes.

A `ReportGenerator` class with `fetch_data`, `format_report`, and `send_email` methods is doing three things *and* has three responsibilities. Data fetching, formatting, and email delivery change for different reasons and at different times.

The test isn't "how many methods?" — it's **"how many reasons to change?"**

This same distinction applies to commits. An atomic commit should check in one cluster of related changes — not one file, but all the files needed to achieve one result. A commit that fixes a bug, adds a feature, and refactors some unrelated code has three responsibilities. Split it into three commits.

## Beck's framing: change pressure

Kent Beck means something narrower and more practical than the textbook version. Where Martin asks "how many reasons to change?", Beck asks **when and why do changes actually collide?**

> "If two changes tend to happen at different times, they should probably be in different places."

### Responsibility is a decision, not a feature

Not "this class handles users" — but "this class changes when pricing rules change." A responsibility maps to a kind of decision. When you can name the decision, you can see the boundary.

### Changes come from people

SRP is violated when different people (or roles) want to change the same thing for different reasons. The accountant's change shouldn't collide with the DBA's change. If it does, the code is coupling two audiences.

### Change pressure is the signal

<mark>If two unrelated changes keep colliding in the same file, SRP is broken — even if the code looks tidy.</mark> You don't need a design diagram to spot this. Your version control history shows you where the pressure is. Files that change for multiple reasons show up as merge conflicts, surprising breakages, and "while I was in there" commits.

### It's contextual

What counts as "one responsibility" depends on:

- **Team size** — a solo developer can tolerate more coupling than a team of ten
- **Volatility** — code that never changes can safely hold more than code that changes weekly
- **Cost of mistakes** — payment processing needs stricter separation than a prototype

<mark>SRP is a living judgement call, not a mechanical rule. The same code might be fine today and a violation tomorrow when the change pressure shifts.</mark>

### Beck vs Martin

| | Martin's framing | Beck's framing |
|:--|:-----------------|:---------------|
| **Unit of analysis** | Class or module | Any code that changes together |
| **Key question** | How many reasons to change? | Do changes collide in practice? |
| **Source of truth** | Roles and actors | Version history and change frequency |
| **When to split** | When you can name two responsibilities | When two unrelated changes keep touching the same code |

Both framings lead to the same moves. Beck's is more empirical — look at where changes actually collide rather than where you predict they might.

## Why the Single Responsibility Principle ("SRP") matters

Applying SRP allows you to modify code without triggering cascading changes throughout your application. Like replacing your phone's screen without having to rewire the battery, reconfigure the motherboard, and reinstall the operating system.

**Classes that do one thing:**

- Isolate that thing from the rest of your application
- Allow change without consequence
- Enable reuse without duplication
- Are pluggable units of well-defined behaviour with few entanglements
- Are easier to test — when a class does one thing, you can test that thing in isolation

An application that is easy to change is like a box of building blocks — you can select just the pieces you need and assemble them in *unanticipated* ways.

**A class with multiple responsibilities:**

- Has various responsibilities entangled within it
- Makes it impossible to reuse only the behaviour you need
- Has many reasons to change, increasing the chance of breaking dependent code
- Forces you to either duplicate code or accept unwanted dependencies

Each responsibility is an *axis of change*. When requirements change, that change will be manifest through a change in responsibility. If a class has more than one responsibility, those responsibilities become coupled. Changes to one may impair or inhibit the class's ability to meet the others. This coupling leads to *fragile designs* that break in unexpected ways when changed.

When you depend on a class that does too much, it may change for a reason unrelated to your use of it — and each time it changes, there's a possibility of breaking your code.

## Detecting SRP violations

### The "and" test

If describing a function or class requires the word **"and"**, it likely has more than one responsibility. If it uses **"or"**, the responsibilities aren't even related. One dead giveaway is the word "and" in a function's name.

### Ask reasonable questions

Rephrase each method as a question to the class. Imagine a `Gear` class that calculates bicycle gear ratios:

- "Mr. Gear, what is your ratio?" — reasonable
- "Mr. Gear, what is your tire size?" — the class is doing too much

When everything in a class is related to its central purpose, the class is said to be *highly cohesive*.

### Describe it in one sentence

A class should do the smallest possible useful thing. That thing ought to be simple to describe in one sentence without conjunctions.

## Example: Gear and Wheel

Consider a bicycle gear calculator. Each class has a single, focused responsibility:

```python
import math

class Wheel:
    """Calculates wheel measurements."""

    def __init__(self, rim: float, tire: float):
        self.rim = rim
        self.tire = tire

    @property
    def diameter(self) -> float:
        return self.rim + (self.tire * 2)

    @property
    def circumference(self) -> float:
        return self.diameter * math.pi

class Gear:
    """Calculates gear ratios."""

    def __init__(self, chainring: int, cog: int, wheel: Wheel):
        self.chainring = chainring
        self.cog = cog
        self.wheel = wheel

    @property
    def ratio(self) -> float:
        return self.chainring / self.cog

    @property
    def gear_inches(self) -> float:
        return self.ratio * self.wheel.diameter
```

Usage:

```python
wheel = Wheel(rim=26, tire=1.5)
gear = Gear(chainring=52, cog=11, wheel=wheel)

print(wheel.circumference)  # 91.106...
print(gear.ratio)           # 4.727...
print(gear.gear_inches)     # 137.09...
```

Each class answers reasonable questions:

- "Wheel, what is your diameter?" — yes
- "Wheel, what is your circumference?" — yes
- "Gear, what is your ratio?" — yes
- "Gear, what is your tire size?" — no, that belongs to Wheel

## Applies to methods too

Methods, like classes, should have a single responsibility. The same design techniques work:

- Ask what the method does
- Describe its responsibility in a single sentence
- Extract bits that need comments into separate methods

**Benefits of single-responsibility methods:**

- Expose previously hidden qualities
- Avoid the need for comments (method names replace them)
- Encourage reuse — small methods propagate healthy coding patterns
- Are easy to move to another class

When every function does one thing, it becomes clear when a function can be deleted: when changes elsewhere reveal its responsibility is no longer needed, simply remove it.

## Practical guidelines

### Hide data behind behaviour

Wrap instance variables in properties so the knowledge of what that data means lives in one place. If a variable is referenced ten times and suddenly needs adjustment, wrapping it in a property means **changing code in just one place**:

```python
@property
def cog(self) -> int:
    adjustment = self.bar_adjustment if self.foo else self.baz_adjustment
    return self._cog * adjustment
```

This transforms `cog` from data (referenced everywhere) to behaviour (defined once). DRY code tolerates change because any change in behaviour can be made in just one place.

### Hide complex data structures

Sometimes you can't control your input — an external API sends you nested arrays, a CSV parser hands you rows of values. **Don't let that messy structure leak** into your code.

```python
from dataclasses import dataclass

@dataclass
class WheelData:
    rim: float
    tire: float

class WheelCollection:
    """Isolates knowledge of raw data structure."""

    def __init__(self, data: list[list[float]]):
        self.wheels = [WheelData(rim=row[0], tire=row[1]) for row in data]

    def diameters(self) -> list[float]:
        return [w.rim + (w.tire * 2) for w in self.wheels]
```

The `diameters` method has no knowledge of the incoming array structure — it just knows `wheels` is iterable and each item has `rim` and `tire`. If the input format changes (say, the API swaps column order), only the constructor changes.

### Postpone decisions

Your goal is to preserve single responsibility while making the **fewest design commitments possible**. Any decision you make in advance of an explicit requirement is just a guess. Don't decide; **preserve your ability to make a decision later** when you must.

When the future cost of doing nothing equals the current cost, postpone the decision. **Wait for a new requirement** — it supplies the exact information you need to make the next design decision.

If a class has no dependencies and changes to it have no consequences, it doesn't matter if it's imperfect. When it acquires dependencies, those dependencies will supply the information you need to make good design decisions.

### It doesn't need to be perfect

It just needs to allow for change. <mark>Design is more the art of preserving changeability than it is the act of achieving perfection.</mark>

## SRP applies to files too

SRP isn't just about classes and methods — it applies to files and modules. A file that grows too large is a sign that multiple responsibilities have accumulated.

### Example: Python module to package

You start with `bindata.py` to fetch crypto data from Binance. It works. Then you add price alerts, historical data caching, portfolio tracking, and WebSocket streaming. Before you know it, `bindata.py` is 1,200 lines.

Don't try to predict this upfront — that's *premature abstraction*. Instead, let the code tell you what needs to be grouped. Look for clumps of related ideas:

```text
bindata.py (1,200 lines)
├── API client code (authentication, rate limiting, requests)
├── Price alert logic (thresholds, notifications)
├── Historical data (caching, aggregation)
├── Portfolio tracking (positions, P&L calculations)
└── WebSocket streaming (connections, message handling)
```

Extract each clump into its own module, then convert `bindata.py` into a package:

```text
bindata/
├── __init__.py              # Exposes public API from submodules
├── api.py                   # API client, authentication, rate limiting
├── alerts.py                # Price alert thresholds and notifications
├── fetch_historical.py      # Historical kline data retrieval
├── fetch_recent.py          # Recent kline data retrieval
├── fetch_snapshot.py        # Current market snapshot
├── aggregate_klines.py      # Kline aggregation and rollups
├── fill_kline_gaps.py       # Gap detection and filling
├── portfolio.py             # Position tracking, P&L calculations
└── streaming.py             # WebSocket connections and handlers
```

The `__init__.py` re-exports what consumers need:

```python
from bindata.client import BinanceClient
from bindata.alerts import PriceAlert
from bindata.portfolio import Portfolio
```

Existing code that did `from bindata import BinanceClient` still works.

### Example: React components in a single file

Vibe coding a React app, you build everything in `Dashboard.tsx`. It starts as one component, then grows to include charts, tables, filters, modals, and loading states. Now it's 800 lines with six components tangled together.

```text
Dashboard.tsx (800 lines)
├── Dashboard (main layout)
├── PriceChart (candlestick visualisation)
├── VolumeChart (bar chart)
├── TradesTable (recent trades list)
├── FilterBar (date range, symbol selector)
└── TradeModal (trade details popup)
```

Group related components and extract them:

```text
dashboard/
├── index.tsx           # Dashboard component, re-exports
├── charts/
│   ├── index.ts        # Exports PriceChart, VolumeChart
│   ├── PriceChart.tsx
│   └── VolumeChart.tsx
├── TradesTable.tsx
├── FilterBar.tsx
└── TradeModal.tsx
```

The charts live together because they change together — new chart types, shared axis formatting, common tooltip styles. `TradesTable`, `FilterBar`, and `TradeModal` are independent enough to stand alone.

### The pattern

1. **Start simple** — one file is fine
2. **Let it grow** — don't prematurely split
3. **Notice the clumps** — related code clusters together
4. **Extract when it hurts** — when the file becomes hard to navigate
5. **Name the responsibility** — the new file/folder name should describe what changes together

Don't be afraid of a single responsibility expanding until it becomes more than one. That's just life. Code grows, requirements change, features accumulate. The discipline isn't in preventing growth — it's in doing the work to simplify when you notice it. Extract, rename, reorganise, and restore single responsibility again.

<mark>SRP is a living, breathing principle — not a rule in stone that limits you.</mark>

## Beware of God classes

Classes and modules often start with a single responsibility, but as you add features they can evolve into *God classes* that span hundreds or thousands of lines. At this point, break them into smaller classes. Look for commonality and overlap — come up with names when you group things together.

## Origin

The Single Responsibility Principle is the "S" in SOLID, coined by Michael Feathers and popularised by Robert C. Martin. It's based on the principle of cohesion described by Tom DeMarco and Meilir Page-Jones.

> The SRP is one of the simplest of the principles, and one of the hardest to get right. Conjoining responsibilities is something that we do naturally. Finding and separating those responsibilities from one another is much of what software design is really about.
> — Robert C. Martin

## Sources

- [C2 Wiki — SingleResponsibilityPrinciple](https://wiki.c2.com/?SingleResponsibilityPrinciple) — the original wiki's community discussion on SRP, with contributions from Ward Cunningham and others
- Robert C. Martin, *Agile Software Development: Principles, Patterns, and Practices*
- Sandi Metz, *Practical Object-Oriented Design in Ruby*
