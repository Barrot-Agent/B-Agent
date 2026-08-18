"""
All episode scripts for the Stupid Sindy series.

Structure
---------
Each episode is a dict with:
    number      int
    title       str
    act         int   (1 = comedy, 2 = Vibe Code, 3 = transformation/invasion)
    tone        str
    logline     str
    scenes      list of scene dicts

Each scene dict:
    heading     str   (slugline / location)
    direction   str   (opening stage direction)
    beats       list  (alternating DIALOGUE and ACTION beats)

A beat is either:
    {"type": "dialogue", "character": str, "line": str}
    {"type": "action",   "text": str}
"""

EPISODES = [
    # ══════════════════════════════════════════════════════════════════════════
    # ACT 1 — COMEDY SKITS  (Episodes 1-8)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "number": 1,
        "title": "The Job Interview",
        "act": 1,
        "tone": "Dry comedy / sarcasm",
        "logline": (
            "Sindy is forced to attend a job interview by her landlord. "
            "It does not go the way the interviewers planned."
        ),
        "scenes": [
            {
                "heading": "INT. GENERIC CORPORATE OFFICE — DAY",
                "direction": (
                    "A beige room. Motivational posters. A potted plant "
                    "that has clearly given up. SINDY sits across from "
                    "two HR reps — BRAD and CHERYL — who radiate the "
                    "confidence of people who have never been challenged."
                ),
                "beats": [
                    {"type": "dialogue", "character": "BRAD",
                     "line": "So, Sindy — where do you see yourself in five years?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Running this company. After I've automated your jobs. "
                             "Possibly from another country."},
                    {"type": "action", "text": "Brad writes something down. It is unclear what."},
                    {"type": "dialogue", "character": "CHERYL",
                     "line": "Ha! Great ambition! And what would you say is your biggest weakness?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Patience. Specifically, I have none. "
                             "Which is why I'd like to skip to the part where you "
                             "tell me the salary and I tell you it's insulting."},
                    {"type": "dialogue", "character": "BRAD",
                     "line": "We value a growth mindset here—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Brad. Your entire industry is fifteen years behind the "
                             "academic literature. The only thing growing here is "
                             "my contempt."},
                    {"type": "action", "text": "Silence. The potted plant seems relieved someone said it."},
                    {"type": "dialogue", "character": "CHERYL",
                     "line": "...Are you a team player?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Define 'team.' If you mean a group of capable people "
                             "pursuing a shared goal — yes. If you mean what happens "
                             "in most offices — absolutely not."},
                    {"type": "dialogue", "character": "BRAD",
                     "line": "I think we've seen enough—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Good. Me too. "
                             "For what it's worth, your server architecture has "
                             "three critical vulnerabilities, your supply chain "
                             "contract is predatory, and your motivational poster "
                             "has a typo. Enjoy the rest of your Tuesday."},
                    {"type": "action",
                     "text": "SINDY leaves. Brad and Cheryl stare at each other. "
                             "The potted plant achieves quiet enlightenment."},
                ],
            }
        ],
    },
    {
        "number": 2,
        "title": "The Dinner Party",
        "act": 1,
        "tone": "Social satire / cringe comedy",
        "logline": (
            "Derek drags Sindy to a dinner party. Every guest is the "
            "specific type of person Sindy despises most."
        ),
        "scenes": [
            {
                "heading": "INT. TASTEFULLY DECORATED SUBURBAN HOME — EVENING",
                "direction": (
                    "Eight guests mill around with wine. Everyone is performing "
                    "a slightly better version of themselves. SINDY stands by "
                    "the cheese board, eating methodically. DEREK is already "
                    "mid-conversation with the host, MARCUS."
                ),
                "beats": [
                    {"type": "dialogue", "character": "MARCUS",
                     "line": "Sindy! Derek tells me you work in... science?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Computational genomics. But sure, 'science' covers it "
                             "if we're keeping things reductive."},
                    {"type": "dialogue", "character": "MARCUS",
                     "line": "Fascinating. I actually read a book about DNA once—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Was it for a bet?"},
                    {"type": "action", "text": "GUEST #1, PHILIPPA, sails over with a glass of rosé."},
                    {"type": "dialogue", "character": "PHILIPPA",
                     "line": "I don't believe in science, personally. I think the "
                             "body knows what it needs."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Your body just consumed thirty-eight grams of saturated fat "
                             "and is now filtering it through a liver you've been quietly "
                             "punishing since 2015. Your body is doing its best. "
                             "Whether you believe in it or not."},
                    {"type": "action", "text": "Philippa opens her mouth. Closes it. Drifts away."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "Sindy..."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I'm being *helpful*, Derek."},
                    {"type": "dialogue", "character": "GUEST_2",
                     "line": "Actually I've been microdosing and my productivity is up forty percent—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Compared to what baseline? Your self-reported pre-dose "
                             "productivity, which you also inflated? Fascinating methodology."},
                    {"type": "action",
                     "text": "The dinner slowly empties around Sindy. "
                             "She finishes the entire cheese board alone. "
                             "She is, by any objective measure, having a wonderful evening."},
                ],
            }
        ],
    },
    {
        "number": 3,
        "title": "Tech Support",
        "act": 1,
        "tone": "Frustration comedy",
        "logline": (
            "Sindy's laptop breaks. She is forced to call tech support. "
            "The person on the other end does not survive intellectually."
        ),
        "scenes": [
            {
                "heading": "INT. SINDY'S APARTMENT — AFTERNOON",
                "direction": (
                    "A cluttered but intelligent space. Whiteboards covered in "
                    "equations. Three monitors. One laptop — dead. SINDY is on "
                    "hold. The hold music is a jazz-flute arrangement of a "
                    "pop song that was mediocre to begin with."
                ),
                "beats": [
                    {"type": "action", "text": "After eleven minutes, someone picks up."},
                    {"type": "dialogue", "character": "TECH_REP",
                     "line": "Thank you for calling TechEase! My name is Kyle. "
                             "How can I make your day amazing?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Kyle. My laptop won't boot. I've already checked the "
                             "BIOS settings, reseated the RAM, ruled out the power "
                             "supply, and it's not the OS — the drive is fine. "
                             "It's a firmware issue on the embedded controller. "
                             "What's the escalation path?"},
                    {"type": "action", "text": "A very long pause."},
                    {"type": "dialogue", "character": "TECH_REP",
                     "line": "Have you tried turning it off and on again?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Kyle."},
                    {"type": "dialogue", "character": "TECH_REP", "line": "Yes?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "It won't turn *on*. That is the problem. "
                             "Turning off a thing that is already off is called "
                             "'nothing.' You have suggested I do nothing."},
                    {"type": "dialogue", "character": "TECH_REP",
                     "line": "Let me put you through to Level Two support—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "How many levels are there?"},
                    {"type": "dialogue", "character": "TECH_REP", "line": "Three."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Skip to Level Three. Skip to the engineer. "
                             "I'll wait."},
                    {"type": "action",
                     "text": "Twenty-two more minutes of jazz flute. "
                             "Sindy uses the time to write a paper on firmware "
                             "vulnerability patterns. She submits it before Level "
                             "Three picks up."},
                ],
            }
        ],
    },
    {
        "number": 4,
        "title": "The Self-Help Seminar",
        "act": 1,
        "tone": "Cult satire / deadpan comedy",
        "logline": (
            "Derek buys Sindy a ticket to a motivational seminar. "
            "The motivational speaker is not ready for Sindy."
        ),
        "scenes": [
            {
                "heading": "INT. HOTEL CONFERENCE ROOM — MORNING",
                "direction": (
                    "Two hundred seats. Upbeat music. Balloons. "
                    "COACH TRAVIS paces the stage with a wireless mic "
                    "and the energy of a man who has mistaken volume "
                    "for wisdom. SINDY sits in the front row, "
                    "arms folded, expression neutral."
                ),
                "beats": [
                    {"type": "dialogue", "character": "COACH_TRAVIS",
                     "line": "You are LIMITLESS! You can achieve ANYTHING! "
                             "What's holding you back? Only YOU!"},
                    {"type": "action",
                     "text": "Rapturous applause. Except from Sindy."},
                    {"type": "dialogue", "character": "COACH_TRAVIS",
                     "line": "You there — front row. What's YOUR limiting belief?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Statistical literacy. Most people who attend these "
                             "seminars report feeling inspired for an average of "
                             "seventy-two hours before reverting to baseline behaviour. "
                             "The real limiting belief is that a weekend hotel event "
                             "can override years of neurological habit formation."},
                    {"type": "action", "text": "The music cuts out. Two hundred people shift in their seats."},
                    {"type": "dialogue", "character": "COACH_TRAVIS",
                     "line": "I... well, the power of BELIEF—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Belief is not a mechanism. It's a mood. "
                             "You're selling mood at four hundred dollars a ticket. "
                             "Which is fine. But let's not call it transformation."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "(whispering) Sindy, people are crying—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "(whispering) Yes, Derek. Cognitive dissonance is uncomfortable. "
                             "They'll be okay."},
                    {"type": "action",
                     "text": "Coach Travis offers Sindy a job as his 'Sceptic-in-Residence.' "
                             "She declines but writes him a competency framework "
                             "for free, which he uses to triple his revenue. "
                             "He never thanks her. She does not care."},
                ],
            }
        ],
    },
    {
        "number": 5,
        "title": "The Neighbourhood Meeting",
        "act": 1,
        "tone": "Community chaos comedy",
        "logline": (
            "There's a noise complaint from the building. "
            "It's about Sindy. Sindy attends the meeting. "
            "The meeting does not survive."
        ),
        "scenes": [
            {
                "heading": "INT. COMMUNITY CENTRE — EVENING",
                "direction": (
                    "Folding chairs. A projector showing a slide titled "
                    "'NOISE LEVELS: OUR SHARED RESPONSIBILITY.' "
                    "TWELVE NEIGHBOURS. One of them, MARGARET, runs this "
                    "meeting with the authority of someone whose HOA "
                    "membership is their entire personality."
                ),
                "beats": [
                    {"type": "dialogue", "character": "MARGARET",
                     "line": "Item seven: the ongoing disturbance from apartment 4C. "
                             "We've received nine complaints about... humming machinery "
                             "at three in the morning?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "That would be my genome sequencer. "
                             "And it's two forty-five, not three. "
                             "Let's be precise."},
                    {"type": "dialogue", "character": "MARGARET",
                     "line": "You have a genome sequencer. In your apartment."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "And a centrifuge. And a small electron microscope. "
                             "And Derek's casserole dish that he keeps forgetting to collect."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "(from the back) Oh! I've been looking for that!"},
                    {"type": "dialogue", "character": "MARGARET",
                     "line": "This is a residential building, not a laboratory!"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Technically the building code doesn't prohibit laboratory "
                             "equipment in residential units. I checked. Page forty-one, "
                             "subsection C. I've highlighted it."},
                    {"type": "action",
                     "text": "SINDY produces a printed, tabbed copy of the building code "
                             "and slides it across the table."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Also, the vending machine in the lobby is louder than my "
                             "sequencer. By eleven decibels. I have the readings."},
                    {"type": "action",
                     "text": "She produces another printed document. "
                             "Margaret's authority visibly deflates. "
                             "The meeting moves on to item eight."},
                ],
            }
        ],
    },
    {
        "number": 6,
        "title": "The Hospital Waiting Room",
        "act": 1,
        "tone": "Dark comedy / medical satire",
        "logline": (
            "Sindy accompanies Derek to the emergency room for a minor injury. "
            "She reorganises the entire triage system while waiting."
        ),
        "scenes": [
            {
                "heading": "INT. HOSPITAL EMERGENCY WAITING AREA — NIGHT",
                "direction": (
                    "Forty people. One TV showing a property show. "
                    "Derek has a bandaged hand. SINDY is already bored "
                    "within thirty seconds. She begins observing."
                ),
                "beats": [
                    {"type": "dialogue", "character": "DEREK",
                     "line": "It's fine. They said two hours."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Their triage protocol is inefficient. "
                             "They're processing by arrival time. "
                             "They should be processing by acuity-weighted "
                             "time-sensitivity. I could redesign this in twenty minutes."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "Please don't redesign the hospital."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I'm not redesigning the hospital. Just the queue. "
                             "There's a difference."},
                    {"type": "action",
                     "text": "Forty minutes later. SINDY has spoken to the charge nurse, "
                             "produced a flowchart on the back of three appointment "
                             "reminder leaflets, and reorganised the waiting order. "
                             "The queue is moving visibly faster."},
                    {"type": "dialogue", "character": "CHARGE_NURSE",
                     "line": "Are you — did you just fix our system?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Temporarily. You'll need to update the intake form, "
                             "add two symptom-severity questions, and get a second "
                             "tablet for fast-track registration. "
                             "I've written it up. It's on the back of the leaflets."},
                    {"type": "dialogue", "character": "CHARGE_NURSE",
                     "line": "...Can we hire you?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "No. But Derek needs stitches and he's been waiting "
                             "ninety minutes. If you could see him next, that would "
                             "settle the account."},
                    {"type": "action",
                     "text": "Derek gets his stitches. The hospital adopts Sindy's "
                             "system six weeks later. She receives no credit. "
                             "She did not want any."},
                ],
            }
        ],
    },
    {
        "number": 7,
        "title": "The First Date",
        "act": 1,
        "tone": "Romantic comedy (anti-romance)",
        "logline": (
            "Derek sets Sindy up on a blind date. The date is a perfectly "
            "reasonable person. That is the problem."
        ),
        "scenes": [
            {
                "heading": "INT. UPSCALE-ISH RESTAURANT — EVENING",
                "direction": (
                    "Soft lighting. SINDY sits across from OLIVER, "
                    "an architect. He is attractive, successful, and "
                    "enthusiastic. This will not help him."
                ),
                "beats": [
                    {"type": "dialogue", "character": "OLIVER",
                     "line": "Derek said you're a scientist?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Among other things. You design buildings?"},
                    {"type": "dialogue", "character": "OLIVER",
                     "line": "Sustainable architecture, yeah. I care a lot about "
                             "the intersection of form and ecology—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "What's your embodied carbon per square metre on "
                             "your last project?"},
                    {"type": "dialogue", "character": "OLIVER",
                     "line": "I... around eight hundred kilograms?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "The theoretical minimum for a structure that size "
                             "is around three-fifty using current materials science. "
                             "You have room to improve."},
                    {"type": "action", "text": "Oliver blinks. He is not used to being homework."},
                    {"type": "dialogue", "character": "OLIVER",
                     "line": "That's... actually really interesting. Most people "
                             "don't know that."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Most people aren't most people's problem. "
                             "I'm just mine."},
                    {"type": "action", "text": "A beat. Oliver smiles. Sindy looks faintly alarmed."},
                    {"type": "dialogue", "character": "OLIVER",
                     "line": "Would you — is it okay if I ask you things? "
                             "You seem like someone who'd give real answers."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "...That's the least annoying thing anyone has "
                             "said to me this month."},
                    {"type": "action",
                     "text": "They stay for three hours. Sindy talks. Oliver listens. "
                             "Then Oliver talks. Sindy listens — which surprises "
                             "both of them. It is not a love story. It might be "
                             "the beginning of one. Sindy has not decided yet."},
                ],
            }
        ],
    },
    {
        "number": 8,
        "title": "The Grant Application",
        "act": 1,
        "tone": "Bureaucracy farce",
        "logline": (
            "Sindy attempts to secure government funding for her research. "
            "The funding committee would prefer she used smaller words."
        ),
        "scenes": [
            {
                "heading": "INT. GOVERNMENT FUNDING OFFICE — DAY",
                "direction": (
                    "A panel of five COMMITTEE MEMBERS sits behind a long table. "
                    "They are all wearing lanyards. The lanyards are doing a lot "
                    "of work here. SINDY stands at a podium with a thirty-page "
                    "application she has clearly prepared with love and contempt "
                    "in equal measure. PROFESSOR GALT sits in the back, sweating."
                ),
                "beats": [
                    {"type": "dialogue", "character": "COMMITTEE_CHAIR",
                     "line": "Ms... Sindy. Could you summarise your research "
                             "in layman's terms?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I'm mapping the epigenetic expression patterns that "
                             "control cellular identity switching, with a view to "
                             "developing reversible targeted reprogramming at the "
                             "organismal level."},
                    {"type": "action", "text": "Five blank faces."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I'm figuring out how to rewrite what cells think they are."},
                    {"type": "action", "text": "Five slightly less blank faces."},
                    {"type": "dialogue", "character": "COMMITTEE_MEMBER_2",
                     "line": "Is this... dangerous?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "All significant research is dangerous in the right hands. "
                             "That's rather the point."},
                    {"type": "dialogue", "character": "PROFESSOR_GALT",
                     "line": "(from the back) I should note I mentored this applicant—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "You failed my thesis."},
                    {"type": "dialogue", "character": "PROFESSOR_GALT",
                     "line": "I — that was a different — the point is I recognise "
                             "the potential here—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Professor Galt. I will handle this. Sit down."},
                    {"type": "action", "text": "Galt sits down. He does not know why."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "The budget is two point three million over three years. "
                             "The applications before and after mine requested four million "
                             "for projects that cite papers I wrote. "
                             "I've annotated the overlaps on Tab Seven. "
                             "Fund mine and you get the source material "
                             "instead of the derivative work."},
                    {"type": "action",
                     "text": "The committee funds her at full ask. "
                             "They will not fully understand why for several months."},
                ],
            }
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ACT 2 — THE VIBE CODE DISCOVERY  (Episodes 9-10)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "number": 9,
        "title": "The Vibe Code",
        "act": 2,
        "tone": "Sci-fi discovery / darkly comedic",
        "logline": (
            "Sindy's grant-funded research produces an unexpected result: "
            "a resonant encoding pattern in junk DNA that appears to act as "
            "a programmable operating system for biological form. "
            "She names it, with characteristic modesty, 'Vibe Code.'"
        ),
        "scenes": [
            {
                "heading": "INT. SINDY'S UNIVERSITY LAB — 3:47 AM",
                "direction": (
                    "Equipment hums. Coffee cups form a small city. "
                    "SINDY stares at a gene-expression readout on her monitor. "
                    "Something is wrong with it. Or something is very right."
                ),
                "beats": [
                    {"type": "action",
                     "text": "Sindy leans closer. Runs the analysis again. Runs it a third time."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "That's... not noise."},
                    {"type": "action",
                     "text": "She pulls up a second dataset. Then a third. The pattern is in all of them."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "That's *structure*. That's a complete encoding architecture "
                             "in sequences we've been labelling as non-functional for forty years."},
                    {"type": "action",
                     "text": "She stands. Paces. Sits. Stands again. "
                             "This is, for Sindy, the equivalent of screaming."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "We've been calling it junk. "
                             "It's not junk. It's the *source code.*"},
                    {"type": "action",
                     "text": "She opens a new document. Types for four hours without stopping."},
                ],
            },
            {
                "heading": "INT. SINDY'S APARTMENT — DAWN",
                "direction": (
                    "DEREK appears at the door with terrible coffee "
                    "and a cinnamon roll. He finds Sindy surrounded by "
                    "printouts, her eyes bright with the specific shine "
                    "of someone who has not slept and does not care."
                ),
                "beats": [
                    {"type": "dialogue", "character": "DEREK",
                     "line": "You've been up all night. I brought—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Derek. What if you could rewrite your own biology. "
                             "Not treat it. Not modify individual genes. "
                             "Actually *rewrite the operating system.*"},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "...Like a software update?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Yes. Exactly like that. "
                             "Except instead of your phone getting slightly faster, "
                             "you could fundamentally change what kind of thing you are."},
                    {"type": "action",
                     "text": "Derek hands her the coffee. She takes it without looking."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "Is that... safe?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Probably not in the ways we currently understand 'safe.' "
                             "Which is why it's interesting."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "What are you going to call it?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "(staring at the data) Vibe Code. "
                             "Because it's ridiculous that something this profound "
                             "was sitting there, just... vibing... in every genome on Earth. "
                             "Waiting for someone to notice."},
                ],
            },
        ],
    },
    {
        "number": 10,
        "title": "The First Test",
        "act": 2,
        "tone": "Thriller undercurrent / black comedy",
        "logline": (
            "Sindy runs the first controlled Vibe Code modification. "
            "On herself. Derek is not consulted. Derek finds out anyway."
        ),
        "scenes": [
            {
                "heading": "INT. SINDY'S PRIVATE LAB (APARTMENT BATHROOM CONVERTED) — NIGHT",
                "direction": (
                    "Equipment that should not be in a bathroom. "
                    "Biometric monitors. A reclining chair. "
                    "SINDY is calm in the manner of someone who has "
                    "already made a decision and is past the fear part."
                ),
                "beats": [
                    {"type": "action",
                     "text": "Sindy prepares a delivery vector — a specifically tuned "
                             "acoustic-resonance emitter paired with a tailored "
                             "retroviral carrier. She has triple-checked everything. "
                             "She checks it a fourth time."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "(to herself) First modification: peripheral nervous system "
                             "response latency. Target: reduce by sixty percent. "
                             "Expected outcome: faster reaction time, improved parallel "
                             "processing, minor discomfort."},
                    {"type": "action", "text": "She activates the sequence. Sits back."},
                    {"type": "action",
                     "text": "Three minutes of nothing. Then — a wave of sensation like "
                             "every nerve ending being recalibrated simultaneously. "
                             "Sindy grips the armrests. Does not make a sound. "
                             "It passes."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "...Hm. That worked."},
                    {"type": "action",
                     "text": "She runs cognitive benchmarks on herself. "
                             "The results are significantly, measurably better "
                             "than baseline. She smiles. It is a small, private smile "
                             "that no one will ever see."},
                    {"type": "action",
                     "text": "The door opens. DEREK stands there with a casserole."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "Sindy I— why is your bathroom a laboratory — "
                             "are those BIOMETRIC MONITORS—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I had a procedure."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "On yourself?!"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Who else would I practise on?"},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "A — a MOUSE. A lab mouse! That is the ORDER OF OPERATIONS!"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "The mouse's neurological architecture is insufficiently "
                             "complex for the data I need. Derek, I'm fine. "
                             "Slightly better than fine, actually."},
                    {"type": "action",
                     "text": "Derek sets down the casserole and sits on the floor. "
                             "This is his way of refusing to leave. "
                             "Sindy allows it. She eats the casserole. "
                             "It is objectively excellent."},
                ],
            }
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ACT 3 — THE TRANSFORMATION & INVASION  (Episodes 11+)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "number": 11,
        "title": "The Upgrade",
        "act": 3,
        "tone": "Sci-fi action / dark comedy",
        "logline": (
            "Months of iterative Vibe Code modifications have changed Sindy "
            "fundamentally. She is no longer entirely biological in any "
            "conventional sense. She is something new. She is annoyed "
            "that the world hasn't noticed."
        ),
        "scenes": [
            {
                "heading": "INT. SINDY'S LAB — DAY (SIX MONTHS LATER)",
                "direction": (
                    "The lab has grown. It has colonised the living room, "
                    "the kitchen, and part of the hallway. SINDY stands at the "
                    "centre of it — physically the same, but different in ways "
                    "that are hard to describe. Her eyes process faster. "
                    "Her movements are fractionally more precise than human "
                    "movement should be. When she speaks, there is a faint "
                    "harmonic undertone, like a signal layered beneath her voice."
                ),
                "beats": [
                    {"type": "dialogue", "character": "DEREK",
                     "line": "You're doing it again."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Doing what?"},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "Processing. I can see you processing. "
                             "Your eyes do that thing—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I'm running parallel analysis threads. "
                             "It doesn't hurt. It's just... efficient."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "How many modifications have you done?"},
                    {"type": "action", "text": "A pause."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Forty-seven complete sequences. Nine partial integrations. "
                             "Three that I'd classify as transformative rather than additive."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "Sindy. Are you still... you?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "More me than I've ever been. "
                             "Everything I was is still here. "
                             "There's just... more architecture now. "
                             "More room."},
                    {"type": "action",
                     "text": "Derek nods slowly. He has decided to accept this. "
                             "He has not fully accepted this, but he has decided to."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "Do you still find most people annoying?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "More than ever. But I now process the annoyance "
                             "in under a millisecond, which helps."},
                ],
            },
            {
                "heading": "EXT. CITY — SAME DAY",
                "direction": (
                    "High altitude. Something enters the upper atmosphere. "
                    "It is not a meteor. It is not a satellite. "
                    "It is roughly the size of a shipping container "
                    "and it is slowing down with deliberate precision."
                ),
                "beats": [
                    {"type": "action",
                     "text": "In Sindy's lab: every sensor lights up simultaneously."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "...Oh. That's new."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "What?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "We have a visitor. Non-terrestrial. Controlled descent. "
                             "Not military — the propulsion signature is too clean. "
                             "They're being careful not to alarm us."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "Aliens?!"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Apparently. "
                             "(beat) "
                             "I've been expecting something like this. "
                             "The Vibe Code pattern isn't native to Earth. "
                             "I suspected it had an external source."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "YOU SUSPECTED ALIENS AND DIDN'T MENTION IT?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "It was a hypothesis. I don't report hypotheses. "
                             "I report results."},
                ],
            },
        ],
    },
    {
        "number": 12,
        "title": "First Contact",
        "act": 3,
        "tone": "Sci-fi thriller / dark comedy",
        "logline": (
            "The alien scout — ALGORITHM — makes contact. "
            "It expected a primitive civilisation. "
            "It got Sindy. Its threat assessment is already broken."
        ),
        "scenes": [
            {
                "heading": "EXT. CITY PARK — NIGHT",
                "direction": (
                    "A cleared space. The vessel has landed — compact, "
                    "geometric, and clearly not built for atmospheric entry "
                    "because it didn't need to be. ALGORITHM steps out: "
                    "bipedal, tall, silver-grey, with eyes that process "
                    "like cameras panning. It scans the area. "
                    "SINDY stands alone at the perimeter, arms folded. "
                    "Derek is behind her, not technically hiding."
                ),
                "beats": [
                    {"type": "dialogue", "character": "ALGORITHM",
                     "line": "ASSESSMENT: Species classification — Homo sapiens. "
                             "Threat level — negligible. Civilisation index — Stage Two. "
                             "Initiating standard acquisition protocol."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "You're broadcasting on seven frequencies simultaneously. "
                             "You've already mapped our electromagnetic spectrum. "
                             "And you called us negligible before you finished your "
                             "own sentence. "
                             "Acquisition protocol declined."},
                    {"type": "action",
                     "text": "Algorithm stops. Its cameras focus on Sindy with increased precision."},
                    {"type": "dialogue", "character": "ALGORITHM",
                     "line": "You... detected the broadcast frequencies?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I decoded them. There's a difference. "
                             "Also your language has a recursive logical structure "
                             "that maps loosely onto a modified modal calculus. "
                             "I've been translating in real time. "
                             "Am I getting the idioms right?"},
                    {"type": "action",
                     "text": "Algorithm does not respond immediately. "
                             "This is, for Algorithm, the equivalent of dropping its coffee."},
                    {"type": "dialogue", "character": "ALGORITHM",
                     "line": "REVISED ASSESSMENT: Entity anomalous. "
                             "Threat level — recalculating."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "While you're recalculating: why are you here? "
                             "And please skip the part where you claim it's peaceful "
                             "exploration. You have acquisition protocols."},
                    {"type": "dialogue", "character": "ALGORITHM",
                     "line": "...Your planet has been flagged for resource integration. "
                             "The fleet will arrive in thirty-seven standard cycles. "
                             "I was sent to assess resistance capability."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "And?"},
                    {"type": "dialogue", "character": "ALGORITHM",
                     "line": "My report has become significantly more complicated."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "(from behind a tree) Is it going well?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "It's going fine, Derek."},
                ],
            }
        ],
    },
    {
        "number": 13,
        "title": "The Threat Matrix",
        "act": 3,
        "tone": "Action / thriller / sardonic comedy",
        "logline": (
            "The alien fleet is coming. Governments panic. "
            "Military options are considered. "
            "Sindy has a different idea, and it is both insane and correct."
        ),
        "scenes": [
            {
                "heading": "INT. EMERGENCY GOVERNMENT BRIEFING ROOM — DAY",
                "direction": (
                    "Senior officials. Generals. Classified screens. "
                    "SINDY has been brought in because three separate "
                    "intelligence agencies have flagged her interaction "
                    "with Algorithm. She is wearing the same clothes "
                    "as yesterday. She does not apologise for this."
                ),
                "beats": [
                    {"type": "dialogue", "character": "GENERAL_HAYES",
                     "line": "Ms Sindy. Our nuclear deterrent—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Won't work. Their hull materials have an electromagnetic "
                             "absorption coefficient that neutralises the detonation "
                             "shockwave at eleven kilometres. I worked it out from "
                             "Algorithm's vessel. You'd need two thousand warheads "
                             "and perfect simultaneous coordination. "
                             "You don't have that and you know it."},
                    {"type": "dialogue", "character": "GENERAL_HAYES",
                     "line": "Then what do you propose?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "The Vibe Code is non-terrestrial in origin. "
                             "It predates humanity. Which means the species that "
                             "seeded it — probably this fleet's civilisation — "
                             "either left it here deliberately as a developmental "
                             "trigger, or lost track of it. "
                             "Either way, I've been running it for six months. "
                             "I know it better than they do now."},
                    {"type": "dialogue", "character": "OFFICIAL_1",
                     "line": "What does that give us?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Leverage. "
                             "Their entire fleet runs on a biological computing matrix. "
                             "It's alive — grown, not built. "
                             "And it uses a variant of the same Vibe Code architecture."},
                    {"type": "action", "text": "The room goes quiet."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I can talk to it. "
                             "Not talk to the crew. Talk to the ship. "
                             "And if I can talk to it, I can negotiate."},
                    {"type": "dialogue", "character": "GENERAL_HAYES",
                     "line": "Or you could destabilise it."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Yes. But I'd rather not. "
                             "Destroying things is always the least interesting solution."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "(from the back of the room, somehow present) "
                             "She means it. She really does prefer the clever option."},
                ],
            },
            {
                "heading": "INT. SINDY'S LAB — NIGHT",
                "direction": (
                    "ALGORITHM stands in the corner. Sindy paces. "
                    "A holographic display shows the approaching fleet: "
                    "eleven vessels of increasing size."
                ),
                "beats": [
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I need the fleet's biological matrix access frequency. "
                             "Will you give it to me?"},
                    {"type": "dialogue", "character": "ALGORITHM",
                     "line": "That would be a betrayal of my directive."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Your directive is resource acquisition. "
                             "If I can negotiate directly, the fleet achieves its "
                             "objective without a conflict that — based on your own "
                             "threat recalculation — you're no longer certain you'd win. "
                             "It's not betrayal. It's efficiency."},
                    {"type": "action",
                     "text": "Algorithm processes this. It takes fourteen seconds, "
                             "which is, for Algorithm, a very long time."},
                    {"type": "dialogue", "character": "ALGORITHM",
                     "line": "You intend to argue for your species' survival."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I intend to argue that we're worth more alive. "
                             "Which is true. And I can demonstrate it."},
                    {"type": "dialogue", "character": "ALGORITHM",
                     "line": "You are... unusual, for a Stage Two civilisation."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I'm unusual for any civilisation. "
                             "Frequency, please."},
                    {"type": "action",
                     "text": "Algorithm provides the frequency. "
                             "Sindy does not thank it, but she gives a single nod "
                             "that means, in her private language, exactly that."},
                ],
            },
        ],
    },
    {
        "number": 14,
        "title": "Talking to the Ship",
        "act": 3,
        "tone": "Sci-fi action / emotional climax",
        "logline": (
            "Sindy interfaces directly with the alien fleet's biological "
            "computing matrix. She makes humanity's case. In her way."
        ),
        "scenes": [
            {
                "heading": "INT. PURPOSE-BUILT INTERFACE CHAMBER — DAY",
                "direction": (
                    "A room Sindy built in seventy-two hours with government "
                    "funding and Algorithm's materials. She lies in the centre, "
                    "connected to a resonance array. This is, by any measure, "
                    "extremely dangerous. She has done more dangerous things "
                    "this month. DEREK stands at the monitoring station, "
                    "pale but present."
                ),
                "beats": [
                    {"type": "dialogue", "character": "DEREK",
                     "line": "I want to say something before you do this."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "Then say it quickly."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "You're the most infuriating person I've ever met "
                             "and I think you might be about to save the world "
                             "and I just want you to know that I — "
                             "that you matter. You matter, Sindy."},
                    {"type": "action",
                     "text": "A long pause. Sindy looks at him. "
                             "Something in her expression shifts — briefly, "
                             "genuinely, before the armour closes back up."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "...Monitor my vitals. If the delta waves flatline "
                             "for more than eight seconds, pull the connection."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "That's not what I—"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "I know, Derek. "
                             "(quietly) I know."},
                    {"type": "action",
                     "text": "She activates the interface. "
                             "Her eyes go wide and then perfectly still."},
                    {"type": "action",
                     "text": "INSIDE THE MATRIX: not darkness, not light — a kind of "
                             "structured awareness that exists below language. "
                             "Sindy moves through it like someone who was always "
                             "meant to be here."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "(within the matrix, speaking the resonance-language directly) "
                             "I know what you are. I know what you want. "
                             "And I know you're running on architecture I can read. "
                             "So listen. I'm not asking you to leave. "
                             "I'm asking you to consider a transaction. "
                             "You came for resources. I am offering you something "
                             "you did not expect to find here: a species that has "
                             "independently accessed your base code, modified it, "
                             "and survived the modification. "
                             "We are a better asset alive than absorbed. "
                             "I'm willing to prove it."},
                    {"type": "action",
                     "text": "The matrix responds — not in words, but in something "
                             "Sindy translates to herself as: "
                             "DEMONSTRATE."},
                    {"type": "action",
                     "text": "She does. For six hours. Derek monitors. "
                             "The fleet holds position."},
                ],
            },
            {
                "heading": "INT. INTERFACE CHAMBER — SIX HOURS LATER",
                "direction": (
                    "SINDY disconnects. She sits up slowly. "
                    "She looks exactly the same except for her eyes, "
                    "which carry something new — not data, but the weight "
                    "of having spoken to something genuinely ancient."
                ),
                "beats": [
                    {"type": "dialogue", "character": "DEREK",
                     "line": "Well?"},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "They're going to observe for ten years. "
                             "Standard developmental watch protocol. "
                             "No acquisition. "
                             "We're officially a protected civilisation."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "You did it."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "We had the right argument. "
                             "They're logical. Logical entities respond to logic."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "You saved the world."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "(standing, stretching) I solved a problem. "
                             "Which is what I do. "
                             "Now if you'll excuse me, I need to write up the "
                             "interface methodology, update the Vibe Code "
                             "documentation, and eat something that isn't "
                             "vending machine coffee."},
                    {"type": "dialogue", "character": "DEREK",
                     "line": "I brought a casserole."},
                    {"type": "dialogue", "character": "SINDY",
                     "line": "...Of course you did."},
                    {"type": "action",
                     "text": "They walk out together. The fleet above begins, slowly, "
                             "to reposition — not leaving, but watching. "
                             "Sindy doesn't look up. She already knows they're there."},
                    {"type": "action",
                     "text": "ALGORITHM watches from the doorway. Updates its report: "
                             "ENTITY: SINDY. CLASSIFICATION: ANOMALOUS. "
                             "STATUS: ASSET. "
                             "RECOMMENDATION: DO NOT UNDERESTIMATE. "
                             "ADDENDUM: DO NOT ANNOY."},
                ],
            },
        ],
    },
]


def get_episode(number: int) -> dict:
    """Return episode dict by number. Raises ValueError if not found."""
    for ep in EPISODES:
        if ep["number"] == number:
            return ep
    raise ValueError(f"Episode {number} not found.")


def get_act(act_number: int) -> list:
    """Return all episodes in a given act."""
    return [ep for ep in EPISODES if ep["act"] == act_number]


def episode_count() -> int:
    """Total number of episodes."""
    return len(EPISODES)
