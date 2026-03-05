# Product Concept: AI-Enhanced Incident Management Communications

## Background & Context

At Abnormal Security, we treat every customer-impacting incident with urgency, transparency, and professionalism. External customer communications are typically managed via Abnormal's product status page.

Our Incident Management process includes engineering response coordination, severity classification, and the creation of external communications that keep customers informed and reassured.

These are manual tasks typically owned by a mix of Technical Support and Engineers who serve as incident commanders. These messages must strike the right balance of clarity, brevity, and technical accuracy while omitting irrelevant internal details.

As a result, this process is time-intensive, error-prone under pressure, and inconsistent in tone and quality depending on the author:
- Delays in communication due to bottlenecks in drafting and review
- Inconsistencies in message tone and structure across incidents
- Potential for over-sharing or under-communicating key customer impacts
- Cognitive overhead for engineering teams during high-severity incidents

## Task Assignment

Your goal is to define an AI-native workflow that assists in generating succinct, accurate, and customer-appropriate incident communications. This solution should aim to:
- Reduce manual effort and response time during incidents
- Ensure consistent, on-brand, and compliant messaging
- Improve clarity around customer impact while minimizing internal noise
- Integrate seamlessly into our existing incident response workflows

The output of this initiative should improve operational efficiency, reduce communication risk during incidents, and reinforce customer trust through high-quality, timely updates.

## Anonymized Incident Data

To help you build a realistic prototype, we've provided anonymized incident data from a real production incident via Google Drive:

**[TBD - Google Drive Link]**

This includes raw technical data from multiple sources (logs, metrics, deployments, alerts, Slack conversations). Your prototype should process this real data to generate customer-appropriate communications - not just be a static demo.

## Please create:

### 1. A Product Requirements Document (~2-3 pages) that includes:
- Your key assumptions about the current process and stakeholders
- North star vision and scope for the AI-native solution
- High-level user experience and user stories
- Implementation approach and technical design thinking
- Phased rollout plan (crawl, walk, run)
- Success metrics and evaluation framework for measuring AI output quality

### 2. A working prototype that demonstrates a key part of your proposed workflow.
This should be a functional proof-of-concept that validates your core technical approach. Focus on building the most critical component that proves your solution can work.

**The prototype should be accessible via web browser for our review.**

**Important**: Your prototype must process the provided anonymized incident data to generate customer-facing communications. This demonstrates your ability to work with real data sources and translate technical signals into appropriate external messaging.

### 3. A ~5 minute video recording walking through your approach.
Please describe:
- How AI is utilized in your proposed solution
- A demo of your working prototype
- How you leveraged AI tools during your development process

## Important Notes

**Time Investment**: We recommend spending approximately 1 day on this assignment. Focus your energy on demonstrating your technical building capabilities while showing solid product thinking in your documentation.

**Prototype Scope**: Your prototype should be working and functional for the specific workflow component you choose to build, but it doesn't need to implement every feature described in your PRD. Think of this as building the minimal viable proof-of-concept that validates your technical approach and AI integration strategy.

**Technical Focus**: As an AI Product Engineer, we want to see your ability to rapidly build and ship functional solutions. Prioritize demonstrating your technical execution skills alongside your product reasoning.

**Evaluation Criteria**: We'll assess your submission based on:
- Quality of technical execution and AI integration
- Soundness of product strategy and user-centric thinking
- Ability to scope appropriately and deliver a working solution
- Clear communication of your approach and technical decisions
