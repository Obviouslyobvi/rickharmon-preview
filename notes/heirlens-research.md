# HeirLens — research brief

Source: "Fwd: Curative Curiousity" — Rick Harmon forwarded a cold email
from Alex Capozzolo, 2026-08-27.

## What it is

Heir Lens (heirlens.com). You give it a property address. It resolves the
parcel and recorded owners, checks whether those owners are living, finds
and verifies obituaries, assembles surviving family into a tree, applies
that state's intestate succession law to compute each person's share, skip
traces the heirs, and scores the lead. Bulk CSV upload. Under a minute per
address; bulk runs queue in the background.

Sells to investors and wholesalers working probate and inherited-property
leads, and to the VAs who do their research. The pitch is time: heir
research by hand is 2-4 hours per property across five websites.

## Pricing

- Starter  $175/mo    25 searches   ($7.00/search)
- Pro      $450/mo    75 searches   ($6.00/search)
- Team   $1,000/mo   200 searches   ($5.00/search)

Month to month, Stripe, no setup fee. Searches do not roll over. Research
pauses at the cap instead of billing overages. One search = researching one
address; viewing, editing trees, recalculating shares are free.

**The FAQ says there is no free trial.** Alex's email offers "10 free pulls
in the free trial." So the 10 pulls are a hand comp, not a product feature.
Get it in writing before handing over a card.

## Who is behind it

Alex Capozzolo is real and easy to verify. Co-founder of Brotherly Love
Real Estate (Philadelphia, founded 2018 with Jon Sanborn, childhood friends,
100+ flips) and SD House Guys (San Diego). Licensed California realtor.
Prolific real estate content writer with bylines at Realtor.com, Yahoo News,
Landlord Studio, TechBullion. He handles tech, acquisitions, and internal
systems at SD House Guys. He says he has been doing curative title deals in
PA since 2024, which matches the Philadelphia operation.

So: an operator who built a tool for his own shop and is now selling it.
Not a stranger, not a scam.

## But the product is brand new

- heirlens.com is a Next.js app on Vercel. Nothing else.
- Zero web presence. No press, no reviews, no forum mentions, no directory
  listings, no G2, nothing. It does not exist outside its own domain.
- No /about, /privacy, /terms, /blog. The site links a privacy policy in
  the FAQ; the page 404s.
- Personalized cold email, plus "planning to hit up Tim soon to see if he's
  cool with me posting in the actual FB groups." That is founder-led sales
  at day one, not a company with customers.

Read it as a pre-launch beta being validated on strangers. Which is fine,
as long as nobody treats the output as verified.

## The accuracy claim

Email: "on a bulk test of 100 leads, it got 92/100 correct, in 10 minutes."

Site: "accuracy is measured continuously against a fixed set of fifty real
properties whose correct heir lists were confirmed by a human researcher."

Two different benchmarks, both self-reported, both graded by the vendor.
And "correct" is never defined. Correct on heir count? On every named heir?
On the computed shares? On the skip trace hits? Those are four different
numbers and they are not close to each other.

To its credit the methodology is conservative in the ways that matter:
unconfirmable relationships get flagged as candidates with no share assigned
rather than quietly folded in, unsolvable properties get an explicit "needs
human deep dive" flag, every heir carries a link back to the obituary or
record it came from, and results are frozen and replayed so they do not
drift between sessions. That is a defensible design. It is still an
estimate, and the site says so: not legal advice, not a title search, not a
substitute for probate counsel.

One more limit worth naming: intestate succession only applies when there is
no valid will. If a will exists, it controls and the computed shares are
wrong. The tool cannot see wills.

## The California problem

This is the finding that matters for Rick.

Fully modeled states: **Pennsylvania, Texas, Florida, Georgia, North
Carolina, Ohio.** Everything else falls back to "a general per-stirpes
model," which the vendor itself labels an estimate. Property data is
nationwide; the succession math is not.

California is not on the list. And California is not a state where a generic
per-stirpes model gets you close, because California is a community property
state. Under Probate Code 6401-6402 the surviving spouse takes all of the
community property, and the separate property splits differently depending
on whether there is one child, multiple children, or no issue. A generic
model will hand back wrong spousal shares on exactly the estates Rick lends
against.

Rick's book is California. The state law engine, which is the actual
differentiated part of this product, does not cover his market.

## Does Rick have a use for it

Rick is not the buyer this was built for. HeirLens is a lead-generation tool
for investors hunting pre-probate deals. Rick is a lender whose deal flow
arrives from probate and trust attorneys and from administrators, after a
filing already exists. He does not need a family tree to find the lead. The
lead calls him.

Three honest possibilities, best to worst:

1. **Heir buyout sizing.** Rick's loans often exist so one heir can buy out
   the others. Heir count and share math is the deal. A fast first-pass map
   of who is on title and how many people have to be cashed out would be a
   real pre-qualification aid. Blocked by the California gap above, and the
   attorney of record usually has this information already.

2. **Content and authority.** The underlying subject, how many heirs stand
   between an estate and a closing, is good material for the CloseProbate
   audience. Rick does not need a subscription to write about it.

3. **Origination prospecting.** Pull California inherited properties with
   multiple heirs and solicit. This is the use with the worst risk profile.
   Skip-traced heir contact data plus outbound solicitation puts a licensed
   mortgage originator into DNC and FCRA-adjacent territory, and consumer
   report data cannot be used for eligibility decisions. Not worth it.

## Recommendation

Take the 10 free pulls. Cost is zero and the skip traces alone have salvage
value, which is Alex's own framing.

Run them as a test, not as production: pick California properties where Rick
already knows the correct answer from a closed file, and grade the output
against the truth. That tests the exact thing the vendor has not tested,
which is how the fallback model performs outside its six modeled states.

Do not subscribe. $175/mo is not the objection; the objection is that the
state law engine does not cover Rick's state and Rick is not the customer
this was built for.

Reply value is on the relationship side, not the software side. Alex is a
real operator with a Philadelphia flip business and a curative title
practice. Rick sells to California probate and trust attorneys. There is a
referral conversation there that is worth more than the tool.

## Note for Palmer

Separate from Rick, this is worth a look as a product model. A single
operator built a narrow AI research tool for a pain he had, priced it at
$175-1,000/mo, and is selling it direct by cold email to people he found in
a Facebook group. That is the shape of thing this shop sells. The execution
detail worth stealing is the conservative posture: flag what you cannot
confirm, cite every claim, freeze results so they do not drift. That is what
makes an AI research tool sellable to people whose money is on the line.
