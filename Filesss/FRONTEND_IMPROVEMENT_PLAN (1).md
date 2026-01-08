# Risk Management Workflow System - Frontend Design Improvement Plan

## Executive Summary

This plan outlines the design and implementation of a modern, user-friendly frontend for the Risk Management Workflow System. The frontend will provide an intuitive interface for risk managers (FRM/CFA) to interact with the 7-phase risk management workflow, from document intake through execution tracking.

## Current State

- **Backend**: Complete FastAPI implementation with all 7 phases
- **Frontend**: None (API-only system)
- **API Endpoints**: Fully functional REST API on port 8002
- **Technology Stack**: Python/FastAPI backend ready for frontend integration

## Design Principles

### 1. Decision-First Design
- Every screen answers: "What decision does the user need to make?"
- Information hierarchy: Decision → Context → Details
- Remove cognitive load: Show only what's needed, when it's needed

### 2. Risk Manager Workflow Alignment
- Match the mental model of FRM/CFA professionals
- Use risk management terminology (tail risk, ruin gates, stress testing)
- Visualize risk concepts (scenario trees, confidence bands, kill switches)

### 3. Phase-Driven Navigation
- Clear workflow progression through 7 phases
- Visual indicators of current phase and status
- Ability to review past phases while in current phase

### 4. Human-in-the-Loop Emphasis
- Prominent approval/rejection controls
- Clear confidence indicators
- Audit trail visibility

### 5. Print-Friendly & Documentation-Ready
- All critical information printable
- Professional report generation
- PDF export capabilities

## Technology Stack

### Core Framework
- **Next.js 14** (App Router) - React framework with server-side rendering
- **TypeScript** - Type safety
- **TailwindCSS** - Utility-first styling
- **Shadcn/ui** or **Radix UI** - Accessible component library

### Key Libraries
- **React Query / TanStack Query** - API state management
- **Zustand** or **Jotai** - Client state management
- **React Hook Form** - Form handling
- **Recharts** or **Chart.js** - Data visualization
- **React PDF** - PDF generation
- **Zod** - Schema validation (matches backend Pydantic)

### Development Tools
- **ESLint** - Code quality
- **Prettier** - Code formatting
- **Vitest** - Testing framework

## Page Structure & User Journey

### Page 1: Dashboard / Home
**Purpose**: System overview and workflow entry point

**Key Sections**:
1. **System Status Banner**
   - API health check indicator
   - Active workflows count
   - Recent activity summary

2. **Quick Actions**
   - "Start New Risk Assessment" (primary CTA)
   - "View Active Workflows"
   - "Review Pending Approvals"

3. **Recent Workflows Table**
   - Workflow ID, document name, current phase, status
   - Click to navigate to workflow detail

4. **Statistics Cards**
   - Total assessments completed
   - Average processing time
   - Ruin gate stops (safety metrics)

**API Integration**:
- `GET /api/workflow/status/{workflow_id}` - List all workflows
- `GET /health` - System health

---

### Page 2: Workflow Detail / Phase Navigator
**Purpose**: Main workflow interface showing current phase and allowing navigation

**Layout**:
- **Left Sidebar**: Phase navigation (7 phases, visual progress)
- **Main Content**: Current phase interface
- **Right Sidebar**: Quick reference (assumptions, key risks, decisions)

**Phase Indicators**:
- ✅ Completed (green checkmark)
- 🔄 In Progress (spinning indicator)
- ⏸️ Paused/Waiting (yellow pause icon)
- ❌ Stopped (red X)
- ⏭️ Not Started (gray)

**Phase Navigation**:
1. **Phase 1: Intake & Framing** - Document upload, assumptions
2. **Phase 2: Risk Scan** - Tail risk, incentives, regulatory
3. **Phase 3: Modeling** - Bounds, scenarios, stress tests
4. **Phase 4: Memory** - Historical context, near misses
5. **Phase 5: Ruin Gates** - Kill switch evaluation
6. **Phase 6: Human Judgment** - Review and approval
7. **Phase 7: Execution** - Tracking and monitoring

**API Integration**:
- `GET /api/workflow/status/{workflow_id}` - Workflow state
- `GET /api/intake/status/{document_id}` - Phase 1 data
- `GET /api/workflow/*` - Phase-specific endpoints

---

### Page 3: Phase 1 - Intake & Framing Interface
**Purpose**: Document upload and assumption extraction

**Components**:
1. **Document Upload Zone**
   - Drag-and-drop file upload
   - Supported formats: PDF, TXT, DOCX
   - File preview and validation

2. **Processing Status**
   - Real-time progress indicator
   - "Extracting assumptions..." status messages

3. **Assumptions Display**
   - **Explicit Assumptions** (extracted via pattern matching)
     - List with confidence indicators
     - Source sentence highlighting
   - **Hidden Assumptions** (LLM-identified)
     - Expandable cards showing:
       - Assumption statement
       - Why it's hidden
       - Required conditions
       - Violation consequences

4. **Failure-First Analysis Summary**
   - Collapsible sections:
     - Failure modes
     - Black swan events
     - Tail risks
     - Fragility points
     - Antifragility opportunities

5. **Action Buttons**
   - "Proceed to Risk Scan" (when complete)
   - "Add Manual Assumptions"
   - "Review Academic Context" (if available)

**API Integration**:
- `POST /api/intake/upload` - File upload
- `POST /api/intake/process` - Trigger processing
- `GET /api/intake/status/{document_id}` - Get results

---

### Page 4: Phase 2 - Risk Scan Results
**Purpose**: Display AI-powered risk analysis results

**Layout**: Three-column view for three scan types

**Column 1: Tail Risk Scan**
- Black swan events (expandable cards)
- Fat tail exposures (risk matrix visualization)
- Tail risk scenarios (scenario list)

**Column 2: Incentive Analysis**
- Skin-in-game assessment (who has exposure?)
- Moral hazards (risk indicators)
- Principal-agent problems (conflict areas)

**Column 3: Regulatory/Political Scan**
- Regulatory risks (compliance, rule changes)
- Political risks (policy changes, opposition)
- Jurisdictional risks (cross-border issues)

**Visualizations**:
- Risk heatmap (severity × probability)
- Network diagram (stakeholder relationships)
- Timeline view (regulatory/political events)

**Action Buttons**:
- "Proceed to Modeling"
- "Flag Risk for Review"
- "Export Risk Report"

**API Integration**:
- `GET /api/risk_scan/{document_id}` - Get scan results
- `POST /api/risk_scan/flag` - Flag specific risks

---

### Page 5: Phase 3 - Modeling Dashboard
**Purpose**: Display quantitative risk modeling results

**Components**:

1. **Bounds Calculator Results**
   - Three scenario cards:
     - Worst Case (red theme)
     - Expected Case (yellow theme)
     - Best Case (green theme)
   - Each showing: probability, impact, description

2. **Scenario Tree Visualization**
   - Interactive tree diagram
   - Click nodes to see details
   - Probability paths highlighted

3. **Stress Test Results**
   - Table of stress scenarios
   - Impact assessment
   - Comparison to historical data

4. **Optionality Check**
   - Optionality score (0-1)
   - Upside preservation indicator
   - Visual gauge/chart

**Visualizations**:
- Probability distribution curves
- Scenario tree (D3.js or similar)
- Stress test comparison charts

**Action Buttons**:
- "Proceed to Ruin Gates"
- "Adjust Model Parameters"
- "Export Model Report"

**API Integration**:
- `GET /api/modeling/{workflow_id}` - Get modeling results
- `POST /api/modeling/adjust` - Adjust parameters

---

### Page 6: Phase 5 - Ruin Gates Dashboard
**Purpose**: Critical safety check interface (most important phase visually)

**Design**: High-visibility, attention-grabbing design

**Components**:

1. **Three Gate Cards** (large, prominent)
   - **Gate 1: Ruin Possible?**
     - Large YES/NO indicator
     - Red background if YES (STOP)
     - Green background if NO (PROCEED)
   - **Gate 2: Downside Capped?**
     - Same YES/NO design
   - **Gate 3: Redundancy Exists?**
     - Same YES/NO design

2. **Overall Status Banner**
   - **STOP / REDESIGN** (if any gate fails) - Red, large text
   - **PROCEED** (if all gates pass) - Green, large text

3. **Gate Details**
   - Expandable sections for each gate
   - Reasoning and evidence
   - Risk factors identified

4. **Action Buttons**
   - If STOP: "Review Redesign Options", "Export Stop Report"
   - If PROCEED: "Continue to Human Review"

**Visual Design**:
- Traffic light metaphor (red/yellow/green)
- Large, bold typography for STOP/PROCEED
- Cannot be missed - most prominent page

**API Integration**:
- `GET /api/ruin_gates/{workflow_id}` - Get gate evaluation
- `POST /api/ruin_gates/override` - Manual override (with audit log)

---

### Page 7: Phase 6 - Human Judgment Interface
**Purpose**: Professional review and approval workflow

**Components**:

1. **Confidence Classification Banner**
   - High/Medium/Low confidence indicator
   - Color-coded (green/yellow/red)
   - Reasoning displayed

2. **Review Checklist**
   - All phases reviewed
   - Key assumptions verified
   - Risk assessments validated
   - Modeling assumptions checked

3. **Professional Review Section**
   - Reviewer name/credentials
   - Review comments (rich text editor)
   - Approval/rejection decision

4. **Context Review Section**
   - Audience fit assessment
   - Tone appropriateness
   - Political sensitivity check

5. **Decision Log Preview**
   - Shows what will be logged
   - Audit trail information

**Action Buttons**:
- "Approve & Release" (green, primary)
- "Request Revisions" (yellow)
- "Reject" (red)
- "Save Draft Review"

**API Integration**:
- `GET /api/judgment/{workflow_id}` - Get review data
- `POST /api/judgment/approve` - Approve workflow
- `POST /api/judgment/reject` - Reject workflow
- `POST /api/judgment/review` - Save review comments

---

### Page 8: Phase 7 - Execution & Monitoring
**Purpose**: Track real-world outcomes and model updates

**Components**:

1. **Execution Tracker**
   - Timeline of execution milestones
   - Status indicators
   - Outcome tracking

2. **Monitoring Dashboard**
   - Real-time monitoring (if applicable)
   - Alert system
   - Status updates

3. **Model Updates Section**
   - Learning outcomes
   - Model adjustments made
   - Performance metrics

4. **Historical Comparison**
   - Compare to similar past assessments
   - Accuracy metrics
   - Lessons learned

**Visualizations**:
- Timeline view
- Performance charts
- Comparison tables

**API Integration**:
- `GET /api/execution/{workflow_id}` - Get execution data
- `POST /api/execution/update` - Update execution status
- `GET /api/execution/monitor` - Get monitoring data

---

## Component Library

### Reusable Components

1. **PhaseProgressIndicator**
   - Visual progress bar through 7 phases
   - Clickable phase markers
   - Status indicators

2. **RiskCard**
   - Standardized risk display
   - Severity × probability matrix
   - Expandable details

3. **AssumptionCard**
   - Assumption statement
   - Confidence indicator
   - Source reference
   - Edit/flag actions

4. **GateStatusCard**
   - Large YES/NO indicator
   - Color-coded (red/green)
   - Reasoning display

5. **ConfidenceBadge**
   - High/Medium/Low indicator
   - Color-coded
   - Tooltip with details

6. **WorkflowStatusBadge**
   - Current phase indicator
   - Status (in progress, paused, stopped)
   - Time elapsed

7. **DocumentUploadZone**
   - Drag-and-drop interface
   - File preview
   - Validation feedback

8. **ScenarioTreeVisualization**
   - Interactive tree diagram
   - Probability paths
   - Node details on click

9. **RiskHeatmap**
   - Severity × probability matrix
   - Color-coded cells
   - Hover details

10. **ApprovalWorkflow**
    - Review checklist
    - Comment sections
    - Approval/rejection controls
    - Audit trail preview

## Design System

### Color Palette

**Status Colors**:
- **Success/Proceed**: Green (#10B981)
- **Warning/Pause**: Yellow (#F59E0B)
- **Error/Stop**: Red (#EF4444)
- **Info/In Progress**: Blue (#3B82F6)
- **Neutral/Not Started**: Gray (#6B7280)

**Risk Severity Colors**:
- **Critical**: Dark Red (#DC2626)
- **High**: Red (#EF4444)
- **Medium**: Yellow (#F59E0B)
- **Low**: Green (#10B981)

**Phase Colors** (distinct for each phase):
- Phase 1 (Intake): Blue
- Phase 2 (Risk Scan): Purple
- Phase 3 (Modeling): Orange
- Phase 4 (Memory): Teal
- Phase 5 (Ruin Gates): Red (most prominent)
- Phase 6 (Judgment): Amber
- Phase 7 (Execution): Green

### Typography

- **Headings**: Inter or System UI (sans-serif)
- **Body**: Inter or System UI
- **Code/Technical**: JetBrains Mono or Consolas
- **Hierarchy**: Clear size differentiation (h1: 2.5rem, h2: 2rem, h3: 1.5rem)

### Spacing

- Consistent 8px grid system
- Generous whitespace for readability
- Card-based layouts with padding

### Icons

- **Lucide React** or **Heroicons** - Consistent icon set
- Phase-specific icons for navigation
- Status icons (check, pause, stop, play)

## Responsive Design

### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Mobile Considerations
- Collapsible sidebars
- Stacked layouts
- Touch-friendly controls
- Simplified navigation

## Accessibility

### Requirements
- **WCAG 2.1 AA compliance**
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus indicators
- ARIA labels

### Implementation
- Semantic HTML
- Proper heading hierarchy
- Alt text for images
- Form labels
- Error announcements

## Performance

### Optimization
- **Code splitting** - Route-based
- **Lazy loading** - Images and heavy components
- **API caching** - React Query caching
- **Debouncing** - Search and filter inputs
- **Virtual scrolling** - Long lists

### Metrics
- First Contentful Paint < 1.5s
- Time to Interactive < 3s
- Lighthouse score > 90

## Testing Strategy

### Unit Tests
- Component rendering
- User interactions
- Form validation
- API integration mocks

### Integration Tests
- Workflow progression
- Phase transitions
- API calls
- State management

### E2E Tests
- Complete workflow from upload to approval
- Error handling
- User journey validation

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Next.js setup with TypeScript
- TailwindCSS configuration
- Component library setup (Shadcn/ui)
- API client setup (React Query)
- Basic routing structure

### Phase 2: Core Pages (Week 3-4)
- Dashboard page
- Workflow detail page
- Phase 1 (Intake) interface
- Phase 2 (Risk Scan) interface
- Basic navigation

### Phase 3: Advanced Features (Week 5-6)
- Phase 3 (Modeling) with visualizations
- Phase 5 (Ruin Gates) - critical design
- Phase 6 (Human Judgment) interface
- Phase 7 (Execution) dashboard

### Phase 4: Polish & Testing (Week 7-8)
- Responsive design refinement
- Accessibility audit
- Performance optimization
- Testing suite
- Documentation

## Success Metrics

### User Experience
- Time to complete workflow < 30 minutes
- User satisfaction score > 4/5
- Error rate < 5%
- Support tickets < 10/month

### Technical
- Page load time < 2s
- API response time < 500ms
- Zero critical bugs
- 95%+ test coverage

## Future Enhancements

1. **Real-time Collaboration**
   - Multiple reviewers
   - Live comments
   - Shared workspaces

2. **Advanced Visualizations**
   - 3D scenario trees
   - Interactive risk maps
   - Custom chart builder

3. **Mobile App**
   - Native iOS/Android apps
   - Push notifications
   - Offline capability

4. **AI-Assisted Review**
   - LLM-powered review suggestions
   - Automated risk flagging
   - Smart recommendations

5. **Integration Hub**
   - Connect to external risk systems
   - Data import/export
   - API marketplace

## Deliverables

1. **Working Frontend Application**
   - All 7 phases implemented
   - Responsive design
   - Accessible interface

2. **Component Library**
   - Reusable components
   - Storybook documentation
   - Usage examples

3. **API Integration**
   - Complete API client
   - Error handling
   - Loading states

4. **Documentation**
   - User guide
   - Developer documentation
   - API integration guide

5. **Testing Suite**
   - Unit tests
   - Integration tests
   - E2E tests

---

## ChatGPT Prompt Template

Use this prompt with ChatGPT to get detailed implementation guidance:

```
I'm building a frontend for a Risk Management Workflow System. The backend is a FastAPI application with 7 phases:

1. Intake & Framing - Document upload, assumption extraction
2. Risk Scan - AI-powered tail risk, incentive, regulatory analysis
3. Modeling - Quantitative bounds, scenarios, stress testing
4. Memory - Historical data and learning
5. Ruin Gates - Critical safety checks (kill switches)
6. Human Judgment - Professional review and approval
7. Execution - Real-world tracking and monitoring

Technology stack: Next.js 14, TypeScript, TailwindCSS, React Query, Shadcn/ui

Key requirements:
- Decision-first design (every screen answers "what decision does the user need to make?")
- Phase-driven navigation with clear progress indicators
- Prominent ruin gate interface (most critical phase)
- Professional, print-friendly design
- Accessible (WCAG 2.1 AA)
- Responsive (mobile, tablet, desktop)

Please provide:
1. Detailed component specifications for [specific phase/page]
2. API integration patterns
3. State management approach
4. Visualization recommendations
5. Code examples for key components
```

---

**End of Plan**
