# Diagram Selection

Select diagrams from the relationships in the confirmed fact model, not from a favorite layout.

## Relationship Map

| Question in the confirmed design | Preferred diagram |
|---|---|
| Where is the boundary, who owns what, and what is upstream or downstream? | System boundary or responsibility map |
| Who calls whom, in what order, and which interactions are synchronous or asynchronous? | Sequence or swimlane |
| What states, retries, failures, waits, and recovery paths exist? | State machine |
| Which nodes, networks, ports, hosts, containers, and deployment zones exist? | Deployment topology |
| Where does data originate, how is it processed, and where does it arrive? | Data flow |
| How do options, versions, capabilities, or trade-offs differ? | Comparison matrix |
| How does staged execution, delivery, rollout, or release progress? | Phase flow or Timeline |

## Selection Process

1. Write the concrete questions the visual must answer.
2. List candidate diagrams and score each one by relationship coverage.
3. Reject a candidate when it duplicates another diagram without answering a new question.
4. Choose one to three complementary diagrams.
5. Choose one diagram when one diagram answers the full question clearly.

An explicit user request for a diagram type or diagram count overrides automatic selection when it is compatible with confirmed facts. If it is not compatible, stop and explain the conflict rather than inventing content.
