# Architecture Decision Records (ADRs)

## ADR Template

Each Architecture Decision Record follows this template:

- **Status**: Proposed, Accepted, Superseded, Deprecated
- **Date**: Decision date
- **Context**: Situation and forces that led to this decision
- **Decision**: The decision made
- **Consequences**: Positive and negative outcomes

---

## ADR-001: Modular Monolith Architecture Pattern

**Status**: Accepted  
**Date**: 2024-08-01  
**Deciders**: Development Team  

### Context

Finance Bro needed an architectural pattern that balances:
- Rapid development and deployment for a small team
- Clear separation of concerns for maintainability
- Future scalability options
- Operational simplicity

Options considered:
1. **Traditional Monolith**: Single codebase, tightly coupled
2. **Modular Monolith**: Single deployment, clear internal boundaries
3. **Microservices**: Distributed services, independent deployment

### Decision

We chose a **Modular Monolith** architecture pattern with:
- Clear service boundaries within a single deployable unit
- Function-first approach over object-oriented design
- Separation by feature (pages, services, components, core)
- Prepared for future microservices extraction if needed

### Consequences

**Positive**:
- Faster development cycles with single deployment unit
- Shared data access and session state management
- Simplified operational overhead (single container)
- Clear internal boundaries prevent tight coupling
- Easy refactoring and code organization

**Negative**:
- Potential scaling limitations for high-load scenarios
- Single point of failure for entire application
- Shared database/cache layer coupling
- May require architectural changes for extreme scale

---

## ADR-002: Streamlit as Web Framework

**Status**: Accepted  
**Date**: 2024-08-01  
**Deciders**: Development Team  

### Context

Finance Bro needed a web framework for rapid prototyping and deployment of financial analysis tools. Requirements:
- Rapid development for data-heavy applications
- Built-in components for charts and data visualization
- Python-native development environment
- Easy deployment and hosting options

Options considered:
1. **Flask/Django**: Traditional web frameworks with full control
2. **Streamlit**: Python-native framework for data applications
3. **Dash**: Plotly-based framework for analytical applications
4. **Jupyter Notebooks**: Notebook-based interface

### Decision

We chose **Streamlit 1.47.0** as the web framework because:
- Native Python development with minimal web development overhead
- Built-in support for data visualizations and interactive components
- Excellent integration with pandas, AI libraries, and financial data tools
- Multi-page application support for complex workflows
- Built-in session state management and caching
- Easy authentication integration with Google OAuth

### Consequences

**Positive**:
- Extremely rapid development cycles for data applications
- Native integration with pandas, charts, and AI libraries
- Built-in session management and caching mechanisms
- Easy deployment with containerization
- Active community and regular updates

**Negative**:
- Limited customization compared to traditional web frameworks
- Session state tied to server instance (scaling challenges)
- Less control over HTML/CSS compared to traditional frameworks
- Potential performance limitations for complex interactive features

---

## ADR-003: Fixed Python and Dependency Versions

**Status**: Accepted  
**Date**: 2024-08-01  
**Deciders**: Development Team  

### Context

Finance Bro requires stable, predictable behavior with financial data analysis libraries. The AI/ML ecosystem has complex dependency relationships that can break with version updates.

Key constraints:
- PandasAI 2.3.0 requires specific pandas version compatibility
- QuantStats library version conflicts with newer pandas versions
- Financial data integrity requires consistent library behavior
- Production deployments need reproducible builds

### Decision

We implemented **strict version locking** for critical dependencies:
- **Python**: Exactly 3.10.11 (no newer versions)
- **PandasAI**: 2.3.0 (stable, proven version)
- **Pandas**: 1.5.3 (compatible with PandasAI 2.x)
- **QuantStats**: 0.0.59 (last version compatible with pandas 1.5.3)
- **UV**: Package manager for faster, deterministic dependency resolution

### Consequences

**Positive**:
- Guaranteed reproducible builds across environments
- Stable behavior for financial calculations and AI analysis
- No unexpected breaking changes from dependency updates
- Clear compatibility matrix for all components

**Negative**:
- Missing latest features and security updates from newer versions
- Technical debt accumulation requiring eventual major upgrades
- Potential security vulnerabilities in older dependencies
- Developer experience limitations from older tool versions

---

## ADR-004: Multi-Agent AI Architecture with CrewAI

**Status**: Accepted  
**Date**: 2024-08-15  
**Deciders**: Development Team  

### Context

Finance Bro needed enhanced AI capabilities beyond simple natural language queries. Complex financial analysis requires:
- Multiple specialized perspectives (analyst, data scientist, writer)
- Collaborative analysis workflows
- Comprehensive report generation
- Domain expertise in financial analysis

Options considered:
1. **Single OpenAI Agent**: Simple but limited perspective
2. **Custom Multi-Agent Framework**: Full control but high development overhead
3. **CrewAI Framework**: Specialized for collaborative AI workflows
4. **LangChain Agents**: General-purpose but complex setup

### Decision

We implemented **CrewAI** for multi-agent financial analysis:
- Specialized agents: Financial Analyst, Data Analyst, Report Writer
- Sequential task execution with collaborative handoffs
- YAML-based configuration for agent roles and tasks
- Integration with existing OpenAI infrastructure

### Consequences

**Positive**:
- Comprehensive financial analysis from multiple expert perspectives
- Structured, professional report generation
- Collaborative AI workflow with task specialization
- Easy configuration and modification of agent behaviors
- Enhanced value proposition for financial health analysis

**Negative**:
- Increased OpenAI API usage and costs
- Additional complexity in system architecture
- Longer processing times for multi-agent analysis
- Dependency on external CrewAI framework evolution

---

## ADR-005: Function-First Design Over Object-Oriented

**Status**: Accepted  
**Date**: 2024-08-01  
**Deciders**: Development Team  

### Context

Finance Bro needed a programming paradigm that optimizes for:
- Rapid development and prototyping
- Data transformation and analysis workflows
- Streamlit compatibility and integration
- Team productivity with varying OOP experience

Options considered:
1. **Object-Oriented Design**: Classes, inheritance, encapsulation
2. **Function-First Design**: Pure functions, composition, minimal state
3. **Hybrid Approach**: Mix of functions and classes where appropriate

### Decision

We adopted a **Function-First Design** approach:
- Prioritize pure functions for data transformations
- Use functions with Streamlit caching decorators
- Minimize mutable state and complex class hierarchies
- Use classes only for stateful components (managers, coordinators)

### Consequences

**Positive**:
- Simpler code that's easier to understand and test
- Better compatibility with Streamlit's function-based caching
- Faster development cycles with less boilerplate
- Easier debugging and troubleshooting
- More predictable behavior with immutable data flows

**Negative**:
- Less encapsulation compared to OOP design
- Potential code duplication without careful organization
- May not scale well for very complex domain models
- Less familiar pattern for developers with strong OOP background

---

## ADR-006: Local File System Caching Strategy

**Status**: Accepted  
**Date**: 2024-08-01  
**Deciders**: Development Team  

### Context

Finance Bro needed caching strategy for:
- Expensive API calls to VnStock and OpenAI
- Generated charts and visualizations
- Session state persistence
- Performance optimization

Options considered:
1. **In-Memory Caching**: Fast but lost on restart
2. **Local File System**: Persistent, simple, no external dependencies
3. **Redis**: Fast, distributed, but adds operational complexity
4. **Database Caching**: Persistent, queryable, but overhead for simple caching

### Decision

We implemented **Local File System Caching** with:
- Streamlit's `@st.cache_data` for function-level caching
- File system cache in `cache/` directory for persistence
- TTL-based expiration policies
- Chart exports to `exports/charts/` directory

### Consequences

**Positive**:
- Simple implementation with no external dependencies
- Persistent across application restarts
- Easy to understand and debug
- Low operational overhead
- Works well for single-instance deployment

**Negative**:
- Not shared across multiple application instances
- Limited by local disk space
- Manual cache cleanup required
- Not suitable for horizontal scaling
- Potential I/O bottlenecks for high-frequency access

---

## ADR-007: Google OAuth for Authentication

**Status**: Accepted  
**Date**: 2024-08-01  
**Deciders**: Development Team  

### Context

Finance Bro needed user authentication that:
- Provides secure user identification
- Minimizes password management overhead
- Integrates well with Streamlit
- Offers good user experience

Options considered:
1. **Custom Authentication**: Full control but security complexity
2. **Google OAuth**: Widely adopted, secure, easy integration
3. **Auth0**: Comprehensive but adds service dependency
4. **No Authentication**: Simple but no user personalization

### Decision

We implemented **Google OAuth 2.0** authentication:
- Leverages Streamlit's native OAuth support
- No password storage or management required
- Uses standard OAuth 2.0 security practices
- Minimal user data collection (email, name only)

### Consequences

**Positive**:
- High security with industry-standard OAuth 2.0
- No password management overhead
- Easy user onboarding with existing Google accounts
- Reduced security liability for user credentials
- Built-in multi-factor authentication support

**Negative**:
- Dependency on Google's service availability
- Users without Google accounts excluded
- Limited control over authentication flow
- Privacy concerns for users hesitant about Google integration

---

## ADR-008: Vietnamese Market Data Specialization

**Status**: Accepted  
**Date**: 2024-08-01  
**Deciders**: Development Team  

### Context

Finance Bro needed to choose market scope and data sources:
- Global market data (expensive, complex licensing)
- US market focus (competitive market)
- Vietnamese market specialization (underserved market)
- Multiple market support (development complexity)

Vietnamese market characteristics:
- Growing retail investor base
- Limited specialized analysis tools
- VnStock provides comprehensive free data access
- Opportunity for market-specific features

### Decision

We focused exclusively on **Vietnamese Stock Market** with:
- VnStock API as primary and secondary data source
- Vietnamese investment fund analysis
- Market-specific features (VCI/TCBS data sources)
- Vietnamese business practices and regulations consideration

### Consequences

**Positive**:
- Clear market focus with specialized features
- Comprehensive coverage of Vietnamese market
- Free, reliable data access through VnStock
- Opportunity to serve underserved market segment
- Simplified data licensing and compliance

**Negative**:
- Limited addressable market compared to global scope
- Dependency on Vietnamese market data availability
- Potential growth limitations without market expansion
- Currency and regulatory restrictions for international users

---

## ADR-009: Chart Generation and Export Strategy

**Status**: Accepted  
**Date**: 2024-08-01  
**Deciders**: Development Team  

### Context

Finance Bro needed chart generation capabilities for:
- AI-generated visualizations from PandasAI
- Technical analysis charts with indicators
- Interactive data exploration
- Export capabilities for user workflows

Options considered:
1. **Matplotlib/Seaborn**: Static charts, full control
2. **Plotly**: Interactive charts, web-native
3. **Altair**: Grammar of graphics, Streamlit integration
4. **Mixed Approach**: Different libraries for different use cases

### Decision

We implemented a **Mixed Chart Strategy**:
- **PandasAI + Matplotlib**: AI-generated charts with export capability
- **Altair**: Interactive statistical visualizations
- **mplfinance**: Specialized candlestick and technical analysis charts
- **Consistent Export**: All charts exportable to PNG with unified styling

### Consequences

**Positive**:
- Optimal tool selection for each chart type
- Consistent theming across different chart libraries
- AI integration with automatic chart generation
- Professional financial chart capabilities
- Flexible export options for user workflows

**Negative**:
- Multiple charting dependencies to maintain
- Potential styling inconsistencies across libraries
- Increased bundle size and complexity
- Learning curve for different chart APIs

---

## ADR-010: Error Handling and User Experience Strategy

**Status**: Accepted  
**Date**: 2024-08-01  
**Deciders**: Development Team  

### Context

Finance Bro needed robust error handling for:
- External API failures (VnStock, OpenAI)
- Data validation and user input errors
- Graceful degradation when services unavailable
- Clear user communication about system status

Options considered:
1. **Fail Fast**: Stop execution on any error
2. **Silent Failure**: Continue with degraded functionality
3. **Graceful Degradation**: Fallback strategies with user notification
4. **Circuit Breaker**: Automatic service protection with recovery

### Decision

We implemented **Graceful Degradation** with user-friendly error handling:
- Clear error messages with actionable guidance
- Fallback to cached data when APIs unavailable
- Progressive functionality degradation rather than complete failure
- User notifications about service status and limitations

### Consequences

**Positive**:
- Better user experience during service disruptions
- Clear communication about system limitations
- Maintains partial functionality during outages
- Reduces user frustration with informative error messages

**Negative**:
- Increased complexity in error handling logic
- Potential user confusion about available features
- More code paths to test and maintain
- Cache management complexity for fallback scenarios

---

## ADR-011: DuPont Analysis Financial Formatting System

**Status**: Accepted  
**Date**: 2025-08-18  
**Deciders**: Development Team  

### Context

Finance Bro needed consistent financial data formatting across all analysis pages:
- DuPont Analysis tab required professional financial metrics display
- Users needed flexible display options (billions, millions, original VND)
- Code duplication existed between different financial analysis components
- Inconsistent formatting affected user experience

Options considered:
1. **Page-Specific Formatting**: Individual formatting logic per page
2. **Centralized Helper Functions**: Shared formatting utilities
3. **Component-Based System**: Reusable UI components with formatting
4. **Configuration-Driven Approach**: Constants-based formatting system

### Decision

We implemented a **Comprehensive Financial Formatting System** with:
- **Centralized Helper Functions**: `format_financial_display()` and `convert_dataframe_for_display()` in `src/services/data.py`
- **Reusable UI Components**: `render_financial_display_options()` in `src/components/ui_components.py`
- **Configuration Constants**: `FINANCIAL_DISPLAY_OPTIONS` and `DEFAULT_FINANCIAL_DISPLAY` in `src/core/config.py`
- **Consistent Session State**: Unique session keys for display preferences across components

### Consequences

**Positive**:
- Eliminated code duplication across financial analysis pages
- Consistent professional formatting throughout application
- User-controlled display preferences with persistence
- Easy maintenance through centralized formatting logic
- Comprehensive test coverage for financial formatting functions

**Negative**:
- Additional abstraction layer increases initial complexity
- Requires coordination between configuration, services, and components
- Breaking changes to formatting affect multiple pages simultaneously

---

## ADR-012: Comprehensive Testing Strategy Implementation

**Status**: Accepted  
**Date**: 2025-08-22  
**Deciders**: Development Team  

### Context

Finance Bro required robust testing infrastructure for:
- Financial calculation accuracy and reliability
- Complex data transformation and formatting logic
- Integration testing for multi-component workflows
- Regression testing for critical financial analysis features

Testing needs included:
- Unit tests for individual functions and calculations
- Integration tests for data flow between services
- Edge case handling for financial data validation
- Test fixtures for consistent test data across modules

Options considered:
1. **Minimal Testing**: Basic tests for critical functions only
2. **Focused Unit Testing**: Comprehensive unit tests with limited integration
3. **Comprehensive Test Suite**: Full unit, integration, and edge case coverage
4. **Test-Driven Development**: Write tests before implementation

### Decision

We implemented a **Comprehensive Testing Strategy** with:
- **Extensive Unit Test Coverage**: Individual function testing for all financial calculations
- **Test Fixtures and Data**: Realistic sample data in `conftest.py` for consistent testing
- **Edge Case Testing**: Comprehensive handling of invalid inputs, NaN values, and edge cases
- **Integration Testing**: Cross-component workflow validation
- **Financial Accuracy Testing**: Specific tests for financial formatting, DuPont analysis, and portfolio optimization

### Consequences

**Positive**:
- High confidence in financial calculation accuracy
- Early detection of regressions during development
- Comprehensive documentation through test cases
- Reliable behavior for edge cases and error conditions
- Foundation for continuous integration and quality assurance

**Negative**:
- Increased development time for comprehensive test writing
- Test maintenance overhead as codebase evolves
- Additional complexity in test data management
- Potential over-testing of simple utility functions

---

## ADR-013: Smart Data Loading Architecture with Progressive Feedback

**Status**: Accepted  
**Date**: 2025-01-15  
**Deciders**: Development Team  

### Context

Finance Bro required enhanced data loading capabilities to address user experience issues:
- Pages had complex dependencies requiring specific visitation orders
- Users experienced confusion when data wasn't pre-loaded
- Loading processes lacked progress feedback and status updates
- Multiple pages performed redundant data loading operations
- Cache management was inconsistent across different data types

Key problems identified:
- Valuation page required visiting "Stock Analysis" page first for proper data loading
- Users encountered incomplete data without clear error messages
- No real-time feedback during long-running data operations
- Session state management was scattered across multiple pages

### Decision

We implemented a **Smart Data Loading Architecture** with:
- **Centralized Session State Service**: `src/services/session_state.py` for intelligent dependency resolution
- **Financial Data Service**: `src/services/financial_data.py` for comprehensive data loading
- **Progressive Loading Patterns**: Multi-stage loading with progress bars and status updates
- **Enhanced Valuation Flow**: Pre-loading system with "Load & Analyze Valuation" button
- **Intelligent Cache Management**: Cache key generation and invalidation strategies
- **Error Handling with Fallback**: Graceful degradation with informative error messages

### Consequences

**Positive**:
- Eliminated page dependencies - any page can be accessed directly
- Improved user experience with real-time progress feedback
- Reduced redundant API calls through intelligent caching
- Enhanced error handling with clear user communication
- Centralized data loading logic for better maintainability
- Consistent session state management across all pages
- Better performance through cache optimization

**Negative**:
- Increased architectural complexity with additional service layer
- More complex session state management logic
- Additional memory usage for cached data and progress tracking
- Potential race conditions in parallel data loading scenarios
- Higher initial development effort for implementation

**Technical Implementation Details**:
- Progressive loading breaks complex data requirements into stages (60% financial, 40% price data)
- Smart dependency resolution automatically loads prerequisite data
- Cache keys generated based on symbol, period, source, and company source parameters
- Real-time progress indicators with status messages improve perceived performance
- Comprehensive error handling provides fallback strategies when services fail

---

## ADR-014: CrewAI Streaming Architecture with Thread-Safe Data Bridge

**Status**: Accepted
**Date**: 2026-02-26
**Deciders**: Development Team

### Context

Finance Bro's CrewAI Financial Health Report runs a multi-agent pipeline via `kickoff()`, which is a blocking call — no UI updates are possible while it executes. This created a poor user experience where users saw only a spinner for 30–60 seconds with no indication of progress.

Key technical constraints:
- CrewAI `kickoff()` is blocking — the main thread cannot update Streamlit UI during execution
- Streamlit batches UI updates per script run, so callbacks within `kickoff()` cannot update `st.status` mid-execution
- `st.session_state` is thread-local in Streamlit — inaccessible from child threads
- Financial dataframes stored in session state need to be available to CrewAI tools running in background threads

Options considered:
1. **Blocking with spinner**: Simple but no progress feedback during 30–60 second execution
2. **Threading + Queue**: Background thread runs `kickoff()`, communicates progress via `queue.Queue` to main thread
3. **Async execution**: Not supported by CrewAI's synchronous `kickoff()` API

### Decision

We implemented a **Threading + Queue** architecture with a module-level data bridge:
- **Background thread** runs `kickoff()` with `task_callback`, posts progress updates to a `queue.Queue`
- **Main thread** polls the queue in a loop, updating `st.status` containers as each agent completes its task
- **Module-level `_shared_dataframes`** in `financial_analysis_tool.py` bridges session state data from the main thread to the background thread, bypassing Streamlit's thread-local session state limitation
- **Typewriter streaming** via `st.write_stream()` with a word-by-word generator for the final report output
- **Backward compatible** — the non-streaming `run_financial_health_analysis()` function remains available as fallback

### Consequences

**Positive**:
- Real-time per-agent progress feedback improves perceived performance
- Typewriter effect for final report creates engaging user experience
- Backward compatible with existing non-streaming analysis function
- Clean separation between streaming orchestration (`crewai_streaming.py`) and core crew logic (`crewai.py`)
- Queue-based communication is thread-safe and well-understood

**Negative**:
- Threading adds complexity to error handling and debugging
- Module-level `_shared_dataframes` is global mutable state — requires careful lifecycle management
- Streaming results cannot be cached by Streamlit's `@st.cache_data` (each run re-executes)
- Queue polling loop requires timeout handling to prevent infinite waits
- Two code paths (streaming vs non-streaming) increase maintenance surface

**Technical Implementation Details**:
- `src/services/crewai_streaming.py` — Streaming orchestration with `run_financial_health_analysis_streaming()`
- `src/financial_health_crew/tools/financial_analysis_tool.py` — `_shared_dataframes` module-level dict with `set_shared_dataframes()` / `get_shared_dataframes()` accessor functions
- `pages/Financial_Health_Report.py` — UI integration with `st.status` containers and `st.write_stream()`
- Thread lifecycle: main thread sets shared data → spawns worker thread → polls queue → collects result

---

## Decision Status Summary

| ADR | Title | Status | Impact |
|-----|-------|--------|---------|
| ADR-001 | Modular Monolith Architecture | ✅ Accepted | High |
| ADR-002 | Streamlit Web Framework | ✅ Accepted | High |
| ADR-003 | Fixed Python Dependencies | ✅ Accepted | Medium |
| ADR-004 | CrewAI Multi-Agent Architecture | ✅ Accepted | Medium |
| ADR-005 | Function-First Design | ✅ Accepted | Medium |
| ADR-006 | Local File System Caching | ✅ Accepted | Medium |
| ADR-007 | Google OAuth Authentication | ✅ Accepted | Medium |
| ADR-008 | Vietnamese Market Specialization | ✅ Accepted | High |
| ADR-009 | Mixed Chart Generation Strategy | ✅ Accepted | Low |
| ADR-010 | Graceful Error Handling | ✅ Accepted | Medium |
| ADR-011 | DuPont Analysis Financial Formatting | ✅ Accepted | Medium |
| ADR-012 | Comprehensive Testing Strategy | ✅ Accepted | Medium |
| ADR-013 | Smart Data Loading Architecture | ✅ Accepted | High |
| ADR-014 | CrewAI Streaming with Thread-Safe Data Bridge | ✅ Accepted | Medium |

## Decision Review Process

### Quarterly Review Schedule

**Q1 Review Topics**:
- Dependency version updates and compatibility
- Performance optimization opportunities
- Security enhancement requirements

**Q2 Review Topics**:
- Architecture scalability assessment
- Technology stack evolution evaluation
- User experience improvement opportunities

**Q3 Review Topics**:
- Market expansion possibilities
- Feature architecture decisions
- Integration enhancement opportunities

**Q4 Review Topics**:
- Annual architecture health assessment
- Technical debt reduction planning
- Strategic technology decisions for next year

### Decision Change Process

1. **Identify Need**: Performance issues, new requirements, technology evolution
2. **Impact Assessment**: Analyze affected components, migration effort, risk
3. **Stakeholder Consultation**: Development team, users, business stakeholders
4. **Decision Documentation**: Update or supersede existing ADR
5. **Migration Planning**: Implementation timeline, testing strategy, rollback plan
6. **Implementation**: Gradual migration with monitoring and validation
7. **Review**: Post-implementation assessment and lessons learned

### Future Architectural Considerations

**Short-term (6 months)**:
- Enhanced caching strategies for better performance
- Additional AI model integration options
- Mobile-responsive UI improvements

**Medium-term (12 months)**:
- Horizontal scaling preparation and implementation
- Advanced security enhancements
- Real-time market data streaming capabilities

**Long-term (18+ months)**:
- Microservices extraction for high-load components
- Multi-market expansion architecture
- Advanced analytics and machine learning integration

## ADR Maintenance Guidelines

### Creating New ADRs

1. **Use the standard template** for consistency
2. **Include context and alternatives** considered
3. **Document consequences** both positive and negative
4. **Assign unique sequential numbers** (ADR-XXX)
5. **Get team review** before marking as "Accepted"

### Updating Existing ADRs

1. **Never modify accepted ADRs** - create new ones that supersede
2. **Link related decisions** with clear references
3. **Update status appropriately** (Superseded, Deprecated)
4. **Maintain decision history** for audit trail

### ADR Quality Checklist

- [ ] Clear problem statement and context
- [ ] Alternatives considered and evaluated
- [ ] Decision rationale clearly explained
- [ ] Consequences (positive and negative) documented
- [ ] Implementation implications addressed
- [ ] Review and approval process followed
- [ ] Linked to related ADRs where applicable

This ADR documentation provides a comprehensive record of architectural decisions that shape Finance Bro's design and implementation, ensuring transparency and enabling informed future evolution of the system.