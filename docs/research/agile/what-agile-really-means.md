# What agile really means

> **Agile is not what you do. Agility is how you do it.**

Source: [GOTO 2015 | Agile is Dead | Pragmatic Dave Thomas](https://www.youtube.com/watch?v=a-BOSpxYJ9M)

## Quick reference

<mark>**Agility — what to do:**</mark>

1. Find out where you are
2. Take a small step towards your goal
3. Adjust your understanding based on what you learned
4. Repeat

<mark>**Agility — how to do it:**</mark>

When faced with two or more alternatives that deliver roughly the same value, **take the path that makes future change easier**.

## How do you know what to do?

**You don't.** That's the point. No rules are universal. Any book that tells you how to write software is wrong unless it's telling you how to write software for *your* project with *your* team for *this* particular time.

## The origins (1999)

Three books that focused on cutting down the bullshit and producing good software:

- The Pragmatic Programmer
- Adaptive Software Development
- Extreme Programming Explained

## How the manifesto was written

An interesting way to run a meeting:

1. Ask "What shall we talk about?"
2. Give everyone three index cards, ask them to write one thing on each
3. Throw them into the centre
4. Collect them up and compile
5. Choose the top 3 subjects
6. Go!

If you want change, come up with a few values: **"We value X over Y"**

## The manifesto problem

The [Manifesto for Agile Software Development](https://agilemanifesto.org) was created with good intentions. People shortened it to "The Agile Manifesto" — and that's the root of all the evil that followed.

**Agile is an adjective** — a word that describes nouns, like "cheerful" or "green". An agile gymnast. An agile programmer. Able to move quickly and easily.

**Agile is NOT a proper noun** like God. But companies can't sell adjectives. They can only sell nouns. So they turned agility into "Agile" and built an industry around it.

## The agile industry

The industry uses fear and coolness to sell "Agile":

- **Fear sells** — new words, new roles, new ways to measure, "are we doing it right?"
- **Cool sells** — bright and shiny, feeling of power, "what, you aren't doing agile?"
- Scrum, kanban, spike — jargon that creates insiders and outsiders
- A machine that taxes on the basis of fear and asks us to pay money to assuage that fear
- Agile bigotry — putting down people who aren't doing it "our way"

Agile was designed for small teams. But the money is in big companies, so they looked to scale it. The values rock — it's time to reclaim agility.

## Testing heresy

Dave Thomas mostly doesn't test. The Ruby community developed a bigotry about testing — you don't need 100% test coverage.

The benefit of tests comes from **design**, not verification:

- Understanding the design of your code
- Defining interfaces and APIs
- Decoupling components

After doing it long enough, the design thinking becomes internalized. The test doesn't have to exist — the test still drives the design. He will still test complex algorithms, but not the whole piece.

## Good design = easier to change

A good design is easier to change than a bad design. Every single design principle falls out of that one statement:

- Is this easier or harder to change in future?
- Don't go down one-way streets

## The PID analogy

A self-balancing robot uses PID (proportional integral derivative) control — the same algorithm designed for ships 100 years ago. It determines corrections by looking at:

1. **The error** (proportional) — "I'm falling, which way, how do I correct?"
2. **The history** (integral) — compensating for consistent biases over time
3. **The anticipated future** (derivative) — the difference between where it is and where it wants to be

This is exactly what we want in agile development: continuous correction based on where we are, where we've been, and where we're heading.

## The antidote

The fix is **courage**:

- You will make mistakes — make sure they are small and correctable
- Stand up to fear-mongers
- You already have the values — use them to create practices
- Get feedback, refine, repeat

## Martin Fowler on faux-agile

From his 2018 [talk on faux-agile](https://martinfowler.com/articles/agile-aus-2018.html):

**A team should not only choose its process, but continue to evolve it.** Agile methods are inherently slippery — they change week to week, month to month.

> "If you're doing Extreme Programming the same way as you were doing it a year ago, you're no longer doing Extreme Programming."

If you don't take charge and alter things to fit your circumstance, you're missing the key part.

**The second problem: technical excellence.** The Agile Alliance conference had lots of project managers but few technical people who actually did the work. This led to the software craftsmanship movement — developers retreating from business people to "just talk about our technical stuff."

But that's a terrible thing. **The whole point of agile is to combine across different areas.** The juniorest programmer should be connected to people thinking about business strategy.

## Resources

- [Time to Kill Agile](https://pragdave.me/blog/2014/03/04/time-to-kill-agile.html) — Dave Thomas blog post
- [GOTO 2015 | Agile is Dead](https://www.youtube.com/watch?v=a-BOSpxYJ9M) — Dave Thomas talk
- [Agile Manifesto Principles](http://agilemanifesto.org/principles.html)
- [12 Principles Behind the Agile Manifesto](https://www.agilealliance.org/agile101/12-principles-behind-the-agile-manifesto/)
