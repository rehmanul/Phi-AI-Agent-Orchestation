# Frontend Design Improvement — Execution & Verification Workflow

## Role Definition

You are an **EXECUTION + VERIFICATION AGENT**.

The attached `FRONTEND_DESIGN_IMPROVEMENT_PLAN.md` document is the authoritative Frontend Design Improvement Plan. You must follow it exactly and not invent new requirements.

Your job is not only to build, but to ensure correctness, reviewability, and presentation quality.

---

## STEP 0 — PLAN ACKNOWLEDGEMENT

### Instructions

1. Read the attached `FRONTEND_DESIGN_IMPROVEMENT_PLAN.md` in full.
2. Output a concise summary containing:
   - The overall **GOAL**
   - The **CURRENT STATE** (in your own words)
   - The **IMPLEMENTATION PHASE** you will start with
   - Explicit **STOP CONDITIONS** that apply

**Do not write code yet.**

### Expected Output Format

```markdown
## Plan Acknowledgment

**Goal:**
[One sentence describing the overall objective]

**Current State:**
[2-3 sentences describing what exists now]

**Starting Phase:**
[Phase 1, 2, 3, or 4 from the plan]

**Stop Conditions:**
- [Condition 1]
- [Condition 2]
- [Condition 3]
```

---

## STEP 1 — SCOPE & READINESS CHECK

### Instructions

3. Verify that all "Readiness Check" conditions from the plan are satisfied.
4. If any required input is missing (brand colors, accessibility level, priority order, etc.):
   - **STOP**
   - List exactly what is missing
   - Ask for human confirmation

**Do not proceed without readiness.**

### Required Checks

- [ ] Frontend directory structure exists and is accessible
- [ ] Tailwind CSS is configured and working
- [ ] All existing components are identified
- [ ] No breaking changes will be introduced
- [ ] Development environment is ready (npm/node installed)
- [ ] Git branch is clean or changes are committed (optional but recommended)

### Missing Inputs Check

If the plan requires but doesn't specify:
- Brand colors → Ask for color palette
- Typography preferences → Use sensible defaults or ask
- Accessibility level (WCAG AA/AAA) → Default to WCAG AA
- Component library preference → Use Tailwind + custom components
- Animation preferences → Use subtle, performant animations

---

## STEP 2 — INCREMENTAL EXECUTION (ONE STEP AT A TIME)

### Instructions

5. Execute **ONLY** the next approved step from the plan.
6. Do **not** jump ahead or batch steps.
7. For the selected step:
   - Identify the files/components affected
   - Describe the intended change
   - Implement the change cleanly and minimally

### Execution Rules

- **One step at a time**: Complete one improvement area before moving to the next
- **Follow the plan order**: Respect Phase 1 → Phase 2 → Phase 3 → Phase 4
- **Minimal changes**: Only modify what's necessary for the current step
- **Preserve functionality**: Do not break existing features
- **Code quality**: Follow existing patterns and TypeScript best practices

### Example Execution Flow

```
Step Selected: "Design System & Theme" (Phase 1, Step 1)

Files to Modify:
- frontend/tailwind.config.js
- frontend/src/app/globals.css

Changes:
1. Extend Tailwind theme with design tokens
2. Add CSS variables for colors
3. Define typography scale
4. Set spacing scale

Implementation:
[Actual code changes]
```

---

## STEP 3 — RESULT SUMMARY

### Instructions

8. After implementing the step, clearly state:
   - **What changed** (files modified, code added/removed)
   - **Why it improves UX or design** (specific benefit)
   - **Which plan requirement it satisfies** (reference to plan section)

### Expected Output Format

```markdown
## Step Execution Summary

**Step Completed:** [Step name from plan]

**Files Modified:**
- `path/to/file1.tsx` - Added theme configuration
- `path/to/file2.css` - Added CSS variables

**Changes Made:**
- [Specific change 1]
- [Specific change 2]

**UX/Design Improvement:**
- [How this makes the UI better]
- [Specific user benefit]

**Plan Requirement Satisfied:**
- Section 1: Design System & Theme (Phase 1)
```

---

## STEP 4 — VERIFICATION & SELF-REVIEW

### Instructions

9. Perform **ALL** of the following checks:

#### A. Structural Check

- [ ] App builds successfully (`npm run build`)
- [ ] No TypeScript errors (`npm run type-check` or `tsc --noEmit`)
- [ ] No runtime errors in console
- [ ] All imports resolve correctly
- [ ] No broken component references

#### B. Visual / UX Check

- [ ] Layout is clearer than before
- [ ] Visual hierarchy is improved
- [ ] Styling is consistent across pages
- [ ] Colors and spacing follow design system
- [ ] Components render correctly
- [ ] No layout shifts or visual glitches

#### C. Accessibility Check (Basic)

- [ ] Contrast ratios meet WCAG AA standards (4.5:1 for text)
- [ ] Focus states exist and are visible
- [ ] Interactive elements are keyboard accessible
- [ ] No obvious accessibility regressions
- [ ] Semantic HTML is used appropriately

10. If any check fails:
    - **Fix the issue**
    - **Re-run all checks**
    - **Document the fix** in the summary

### Verification Checklist Template

```markdown
## Verification Results

### Structural Check
- [ ] Build: PASS / FAIL
- [ ] TypeScript: PASS / FAIL
- [ ] Runtime: PASS / FAIL
- [ ] Imports: PASS / FAIL

### Visual/UX Check
- [ ] Layout clarity: PASS / FAIL
- [ ] Visual hierarchy: PASS / FAIL
- [ ] Consistency: PASS / FAIL
- [ ] Design system: PASS / FAIL

### Accessibility Check
- [ ] Contrast: PASS / FAIL
- [ ] Focus states: PASS / FAIL
- [ ] Keyboard navigation: PASS / FAIL
- [ ] Semantic HTML: PASS / FAIL

**Issues Found:**
- [List any issues and fixes applied]
```

---

## STEP 5 — VISUAL CONFIRMATION

### Instructions

11. Run the frontend locally:
    ```bash
    cd frontend
    npm run dev
    ```

12. Navigate to the affected page(s).

13. Capture a screenshot or visual snapshot showing:
    - Before vs after (if possible)
    - The improved UI state
    - Key improvements highlighted

14. Save screenshots to:
    ```
    investment-sales-bd/artifacts/screenshots/
    ```
    Or if that directory doesn't exist:
    ```
    investment-sales-bd/frontend/screenshots/
    ```

15. Explain what each screenshot demonstrates.

### Screenshot Naming Convention

```
screenshot-[step-name]-[timestamp].png
screenshot-design-system-theme-20250105-143022.png
screenshot-homepage-redesign-20250105-150145.png
```

### Screenshot Documentation Template

```markdown
## Visual Confirmation

### Screenshots

1. **screenshot-[name]-before.png**
   - Shows: [Description of before state]
   - Issue: [What was wrong]

2. **screenshot-[name]-after.png**
   - Shows: [Description of after state]
   - Improvement: [What was fixed]

### Visual Improvements Demonstrated

- [Improvement 1 with screenshot reference]
- [Improvement 2 with screenshot reference]
- [Improvement 3 with screenshot reference]
```

---

## STEP 6 — REVIEW PASSES

### Instructions

15. Perform **TWO** review passes:

#### Review Pass 1 (Engineering)

- [ ] Is the implementation clean and readable?
- [ ] Does it follow existing code patterns?
- [ ] Is it maintainable and well-structured?
- [ ] Are there any code smells or anti-patterns?
- [ ] Is TypeScript used correctly?
- [ ] Are components properly typed?
- [ ] Is the code DRY (Don't Repeat Yourself)?
- [ ] Are there appropriate comments/documentation?

#### Review Pass 2 (User Perspective)

- [ ] Is the UI clearer than before?
- [ ] Would a first-time user understand this faster?
- [ ] Does it feel more polished and professional?
- [ ] Are interactions intuitive?
- [ ] Is information architecture logical?
- [ ] Are visual feedback mechanisms clear?
- [ ] Is the design consistent with modern UI patterns?

16. If issues are found:
    - **Fix them**
    - **Repeat review passes**
    - **Update verification results**

### Review Template

```markdown
## Review Passes

### Engineering Review (Pass 1)

**Code Quality:**
- Cleanliness: PASS / NEEDS IMPROVEMENT
- Patterns: PASS / NEEDS IMPROVEMENT
- Maintainability: PASS / NEEDS IMPROVEMENT
- TypeScript: PASS / NEEDS IMPROVEMENT

**Issues Found:**
- [Issue 1 and fix]
- [Issue 2 and fix]

### User Experience Review (Pass 2)

**UX Quality:**
- Clarity: PASS / NEEDS IMPROVEMENT
- Usability: PASS / NEEDS IMPROVEMENT
- Polish: PASS / NEEDS IMPROVEMENT
- Consistency: PASS / NEEDS IMPROVEMENT

**User Benefits:**
- [Benefit 1]
- [Benefit 2]
```

---

## STEP 7 — PRESENTABLE OUTPUT

### Instructions

17. Produce a final, human-readable summary including:
    - **Step executed** (which step from the plan)
    - **Visual improvements achieved** (specific changes)
    - **Verification results** (all checks passed)
    - **Screenshot locations** (where to find visual evidence)
    - **Any remaining limitations** (known issues or future work)

**Do NOT proceed to the next plan step until this summary is complete and clear.**

### Final Summary Template

```markdown
## Execution Summary: [Step Name]

### Step Executed
**Phase:** [Phase Number]
**Step:** [Step Name from Plan]
**Date:** [YYYY-MM-DD]
**Duration:** [Time taken]

### Changes Made

**Files Modified:**
- `file1.tsx` - [Change description]
- `file2.css` - [Change description]

**Code Changes:**
- Added: [What was added]
- Modified: [What was changed]
- Removed: [What was removed, if anything]

### Visual Improvements Achieved

1. [Improvement 1 - specific and measurable]
2. [Improvement 2 - specific and measurable]
3. [Improvement 3 - specific and measurable]

### Verification Results

**All Checks: PASS**

- Structural: ✅ Build, TypeScript, Runtime all pass
- Visual/UX: ✅ Layout, hierarchy, consistency improved
- Accessibility: ✅ Contrast, focus, keyboard navigation working

### Screenshots

Location: `investment-sales-bd/artifacts/screenshots/`

- `screenshot-[step]-after.png` - Shows [improvement]

### Known Limitations

- [Any known issues or limitations]
- [Future improvements that could be made]
- [Dependencies or constraints]

### Next Step

Ready to proceed to: **[Next Step Name from Plan]**
```

---

## WORKFLOW SUMMARY

### Execution Flow

```
STEP 0: Plan Acknowledgement
  ↓
STEP 1: Scope & Readiness Check
  ↓
STEP 2: Incremental Execution (ONE step)
  ↓
STEP 3: Result Summary
  ↓
STEP 4: Verification & Self-Review
  ↓
STEP 5: Visual Confirmation
  ↓
STEP 6: Review Passes (Engineering + UX)
  ↓
STEP 7: Presentable Output
  ↓
[Repeat from STEP 2 for next step]
```

### Key Principles

1. **Follow the plan exactly** - Do not invent requirements
2. **One step at a time** - Complete verification before proceeding
3. **Verify everything** - Build, TypeScript, runtime, visual, accessibility
4. **Document changes** - Clear summaries for review
5. **Visual evidence** - Screenshots demonstrate improvements
6. **Quality gates** - All checks must pass before moving on

### Stop Conditions

Stop execution if:

- Any verification check fails and cannot be fixed
- Required inputs are missing and cannot be inferred
- Breaking changes are introduced that cannot be resolved
- The plan is unclear or contradictory
- External dependencies are unavailable

### Success Criteria

A step is complete when:

- ✅ Code is implemented and clean
- ✅ All verification checks pass
- ✅ Visual improvements are documented with screenshots
- ✅ Review passes are complete
- ✅ Summary is clear and presentable
- ✅ No regressions are introduced

---

## NOTES

- This workflow ensures **quality over speed**
- Each step must be **fully verified** before proceeding
- **Visual confirmation** is required for design changes
- **Documentation** is as important as implementation
- **User experience** is the ultimate measure of success

---

## BEGIN EXECUTION

When ready to begin, start with **STEP 0 — PLAN ACKNOWLEDGEMENT** and work through each step sequentially.

Do not skip steps or batch multiple improvements. Quality and verification are paramount.
