# Course template

## Title formula

`[Tool or Skill] for [Audience]: from [Starting state] to [End state]`
Every module must map to a test the learner can pass at the end. If a module has no
test, it is a lecture, not a course.

## Pricing table

| Tier | Price | Access |
|---|---|---|
| Self-paced | 49-99 | videos, exercises, no support |
| Guided | 149-299 | plus review of two submissions |
| Team | 499-999 | five seats, one live session |

## Outline

1. Module 1: setup, with a pass/fail environment check
2. Module 2: the smallest working example, built live
3. Module 3: the failure modes, one per lesson
4. Module 4: the production version
5. Module 5: measurement, so the learner can prove it worked
6. Capstone with a rubric

Each lesson: objective, 3-8 minute script, exercise, quiz question, expected result.
Quiz questions are graded automatically; only the capstone is graded by hand.

## Deliverables checklist

- [ ] course outline with minutes per lesson
- [ ] scripts written before recording
- [ ] one repository per module that runs
- [ ] quiz bank with answers and explanations
- [ ] capstone rubric with three score bands
- [ ] caption files
- [ ] refund and access policy

## Sales page copy structure

1. Headline: end state
2. Who this is for and the prerequisite, stated as a test
3. Module list with minutes
4. What the learner builds, shown as artifacts
5. Price and access length
6. Refund sentence
7. FAQ: prerequisites, tools, time per week

## File structure

```
course-slug/
  outline.md
  modules/01-setup/script.md
  modules/01-setup/exercise/
  quizzes/01.json
  capstone/rubric.md
  sales/COPY.md
```
