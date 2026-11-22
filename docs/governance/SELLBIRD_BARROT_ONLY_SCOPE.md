# Sellbird operating scope: Barrot technology only

**Status:** Active user-directed restriction  
**Applies to:** Sellbird prospect discovery, qualification, outreach preparation, and campaign execution in the Barrot ecosystem.

## Purpose

Use [Sellbird](https://github.com/ethanplusai/sellbird), the open-source AI sales prospecting and outreach project formerly called Harvey, only to acquire prospective customers and collaborators for Barrot technology.

Sellbird is a customer-acquisition tool. It is not the Barrot persistent execution, approval, queue, or orchestration framework.

## Allowed prospect categories

- Organizations that could become paying Barrot technology customers.
- Organizations suitable for a bounded Barrot pilot or technical evaluation.
- Research collaborators and institutional research partners.
- Technology and integration partners.
- Potential sponsors or funders of Barrot development, where the proposal is evidence-based and clearly scoped.
- Open-source adopters whose use can validate real Barrot capabilities.

## Qualification requirements

Every target segment and offer must map to a capability that is implemented and verified in the current Barrot repository or a reproducible execution record. For each campaign, document:

1. Ideal customer profile and buyer roles.
2. Specific problem the verified Barrot capability addresses.
3. Evidence that the capability exists and works.
4. Buying signals and qualification criteria.
5. Proposed pilot or offer, scope, success measures, and support burden.
6. Pricing hypothesis and conversion action.
7. Prospect/contact provenance and estimated data-acquisition cost.

Do not claim production readiness, security certification, customer adoption, integrations, performance, or revenue without evidence.

## Explicit exclusions

Until the user changes this instruction, Sellbird must not prospect for, promote, or send outreach about:

- Music tracks or music production services.
- Background vocals, songwriting, or other music services.
- TrekFlex clothing or apparel.
- Any other separate user product or venture.

The readiness constraints are explicit: music must not be marketed until finished tracks exist; TrekFlex must not be marketed until physical clothing has been manufactured. Do not imply finished inventory or deliverables exist.

## Outreach and privacy controls

- Prospect discovery and qualification may proceed without sending messages.
- Keep sending paused until the user explicitly approves the campaign's audience, offer, message, and sending setup.
- Verify mailbox authentication, domain health, sender identity, suppression lists, opt-out handling, personalization, and applicable legal/privacy requirements before sending.
- Respect provider terms, anti-spam rules, privacy obligations, and contact preferences.
- Do not fabricate personalization, buying signals, identities, contact details, customer references, or outcomes.
- Do not enable unattended sending or autonomous follow-up without explicit authorization.
- Track each lead through discovered, qualified, approved, sent, replied, meeting-booked, proposal, and revenue-collected states. These states must not be conflated.

## Automatic implementation of verified Barrot gaps

When Barrot research or prospect qualification exposes a concrete technology gap, do not merely add it to a recommendation list. If the gap is in scope and the implementation path is compatible, licensed, secure, bounded, and testable, proceed through the governed engineering loop:

1. Map existing Barrot capability and avoid duplication.
2. Define measurable acceptance criteria.
3. Select the smallest compatible implementation.
4. Implement in an isolated branch or sandbox.
5. Run focused tests and the relevant full suite.
6. Evaluate security, licensing, resource cost, and regressions.
7. Integrate through one coherent change and existing review/CI/branch-protection gates.

Do not install or integrate a tool speculatively. User authorization to implement ready repository changes does not waive independent review, protected-branch checks, or approval for deployment, credential changes, external communications, financial actions, or irreversible side effects.

## Reporting

Every commercial report must state:

- The Barrot capability being offered and its verification evidence.
- Target segment and why it qualifies.
- Number of discovered and qualified prospects, with provenance.
- Paid lookup or infrastructure costs.
- Whether outreach is paused, approved, sent, or replied to.
- Meetings, proposals, and revenue only when supported by records.
- The next concrete conversion action and any blocker.

Never claim that prospecting has generated income until payment or collected revenue is verified.
