# Data Pipeline Engineering Interview - Part 3

### Business Requirements

**Client Need**: European gas market participants need a unified platform that provides:
- Real-time supply-demand balance forecasts
- LNG cargo tracking and terminal analytics  
- Storage levels monitoring with alerts
- Interactive dashboards for decision-making
- 3x daily updates (05:00, 12:00, 16:00 UTC) for critical market windows


### Data Sources & Complexity

**Premium External APIs** 
1. **Kpler** - LNG vessel tracking, cargo flows, terminal data
2. **Energy Aspects** - Long-term supply forecasts, storage analytics  
3. **Commodity Essentials** - European gas infrastructure, pipeline flows


**Technical Constraints**:
- Different data frequencies: real-time, daily, weekly, monthly

---

## Interview Challenge

**Scenario**: The existing infrastructure is basic: PostgreSQL database, Python environment.
---

## Question 1: Database Schema & Data Modeling (5 minutes)

**Context**: Draw the database schema for storing LNG cargo data from Kpler API.

**Specific Requirements:**
- LNG cargos have: vessel_name, departure_port, arrival_port, departure_date, arrival_date, volume_m3
- Ports belong to countries and regions (Europe, Asia, etc.)
- Vessels have capacity and current status
- Track cargo status changes over time

**What to assess:**
1. Table structure and relationships
2. Primary/foreign key choices
3. Indexing strategy for time-series queries
4. How to handle data updates and corrections


## Question 2: Incremental vs Historical Data Fetching (3 minutes)

**Scenario**: You need to optimize this data ingestion pattern from our system:

```python
def ingest_ce_gasbulk(ce_client, engine, logger, schema_name, 
                      run_historical=False):
    if run_historical:
        # Fetch all data from 2014 to present (10+ years)
        fetch_data_range(start_date=2014, end_date=today())
    else:
        # Get last upload timestamp from database
        max_timestamp = get_max_timestamp(engine, table_name)
        # Fetch only updates since last run
        fetch_data_since(timestamp=max_timestamp)
```

**Problems with current approach:**
- New data sources require full historical fetch (expensive)
- Cold starts take hours to populate
- No handling of late-arriving data corrections

**What to assess:**
- Strategy for identifying missing vs existing data
- Hybrid approach combining incremental + selective historical
- Handling data corrections and backfill scenarios
- Performance optimization for large historical datasets

---

## Question 3: Complex Dashboard State Management (4 minutes)

**Scenario**: Build a supply-demand balance dashboard with interconnected components:

1. **Date range picker** (affects all charts)
2. **Regional filter** (Europe, Asia) (affects supply & demand charts)
3. **Supply chart** - shows pipeline flows by source
4. **Demand chart** - shows consumption by country
5. **Balance indicator** - real-time supply minus demand
6. **LNG cargo table** - filtered by selected date range and region

**Challenge**: User interactions must update multiple components efficiently without redundant database calls.

**Complex Requirements:**
- When region changes: update supply chart, demand chart, balance calculation, cargo table
- When date range changes: all components refresh
- Balance calculation needs live data from both supply and demand charts
- Cargo table pagination must persist through filter changes

**What to assess:**
- Callback dependency design
- State management strategy
- Data sharing between components
- Prevention of circular callback triggers

---

## Question 4: Data Quality Validation (3 minutes)

**Scenario**: Your LNG cargo ingestion just received this data from Kpler API:

```json
[
  {"vessel": "Arctic Aurora", "departure_port": "Hammerfest", "arrival_port": "Gate Terminal", 
   "departure_date": "2024-12-15", "arrival_date": "2024-12-10", "volume_m3": 145000},
  {"vessel": "Pacific Pioneer", "departure_port": "Freeport", "arrival_port": "Dunkirk", 
   "departure_date": "2024-12-16", "arrival_date": "2024-12-28", "volume_m3": -85000},
  {"vessel": "", "departure_port": "Qatar", "arrival_port": "Zeebrugge", 
   "departure_date": "2024-12-17", "arrival_date": "2024-12-30", "volume_m3": 165000}
]
```

**What to assess:**
- Identify data quality issues in the sample
- Design validation rules for LNG cargo data
- Error handling strategy (reject, flag, auto-correct)
- How to prevent invalid data from reaching dashboards

---

## Question 5: System Architecture Trade-offs (1 minute)

**Scenario**: Your pipeline currently runs as a single Python script that:
1. Fetches data from 4 APIs sequentially (2 hours total)
2. Processes all transformations in memory 
3. Updates dashboard data once complete

**Business pressure**: Users want data refreshed every 30 minutes instead of daily.

**What to assess:**
- Identify current architecture bottlenecks
- Propose microservices vs monolith trade-offs
- Incremental processing vs full refresh strategy
- Cost-performance optimization decisions

---

## Evaluation Criteria

### Technical Excellence (40%)
- **System Design**: Scalable, maintainable architecture
- **SQL Proficiency**: Efficient schema design and query optimization  
- **Python Engineering**: Clean, testable code patterns
- **Performance**: Understanding of bottlenecks and optimization strategies

### Business Understanding (25%)
- **Domain Knowledge**: Understanding of energy market requirements
- **Stakeholder Management**: Balancing technical and business needs
- **Value Creation**: Focus on business impact and ROI

### Operational Maturity (20%)
- **Production Readiness**: Monitoring, logging, error handling
- **Data Quality**: Validation, testing, and quality assurance
- **DevOps Practices**: CI/CD, infrastructure as code

### Problem-Solving (15%)
- **Trade-off Analysis**: Understanding of technical trade-offs
- **Innovation**: Creative solutions to complex problems
- **Communication**: Clear explanation of technical concepts

---

## Expected Architecture Components

Candidates should demonstrate understanding of:

**Data Layer:**
- Data lake vs. data warehouse trade-offs
- Real-time and batch processing patterns
- Change data capture and event streaming
- Data quality and validation frameworks

**Processing Layer:**
- Workflow orchestration (Airflow, Prefect, etc.)
- Distributed computing for large datasets
- Business logic separation and configuration
- Testing strategies for data pipelines

**Application Layer:**
- API design for data access
- Caching strategies for performance
- Real-time dashboard architecture
- Security and authentication

**Infrastructure:**
- Container orchestration
- Auto-scaling and load balancing  
- Monitoring and observability
- Disaster recovery and backup

---

## Time Allocation Guidance

- **Total: 15 minutes**
- Question 1: Database Schema (5 minutes)
- Question 2: Pipeline Orchestration (3 minutes) 
- Question 3: Dashboard State Management (4 minutes)
- Question 4: Data Quality (3 minutes)
- Question 5: Architecture Trade-offs (1 minute)

**Interview Style**: Fast-paced technical assessment. Focus on specific implementation details rather than high-level concepts.

**Success Indicators:**
- Draws clear, logical database schemas
- Understands callback dependencies and state management
- Identifies data quality issues quickly
- Makes practical architecture decisions under time pressure