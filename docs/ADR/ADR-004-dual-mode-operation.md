# ADR-004: Dual-Mode Operation (Interactive and Batch)

**Status**: Specified (Not Yet Implemented)  
**Date**: 2026-02-10  
**Decision Makers**: Repository Owner (implicit)

## Context

The PIM Activity Audit Agent needs to serve two distinct use cases:

1. **Ad-hoc Investigation**: Security team member investigates specific PIM activations
2. **Automated Monitoring**: Scheduled scanning for compliance/alerting

These use cases have different interaction models:
- Interactive: User-driven questions, context-aware conversation
- Automated: Single execution, predefined output format

## Decision

The application implements **dual-mode operation**:

1. **Interactive Chat Mode** (default):
   - Command-line interface with natural language input
   - Context-aware conversation (maintains chat history)
   - User-driven workflow: scan, query, investigate
   - Human-readable formatted output

2. **Batch Mode** (triggered by `--mode batch`):
   - Single execution, no user input
   - Scans last 24 hours automatically
   - Generates complete Markdown report
   - Suitable for cron jobs or scheduled Azure Functions

### Evidence from Specification

From `/README.md`:

**Interactive Mode Example**:
```
> scan
📊 Scanning for PIM activations in last 24 hours...
Found 2 elevated users...

> What did john.doe@contoso.com do?
📋 Activities for john.doe@contoso.com during elevation:
[activity list]

> exit
👋 Goodbye!
```

**Batch Mode Example**:
```bash
python main.py --mode batch
```
Output: "List of all PIM activations in last 24 hours, Complete activity timeline for each elevated user, Markdown-formatted report suitable for logging/alerting"

## Rationale

### Advantages

1. **Flexibility**: Same tool serves both investigation and monitoring
2. **Code Reuse**: Core detection and analysis logic shared between modes
3. **Operational Efficiency**: One tool to deploy and maintain
4. **Natural Workflow**: Interactive for investigations, batch for compliance

### Trade-offs

1. **Complexity**: Supporting two interaction models increases code complexity
2. **Testing Burden**: Must test both modes and their transitions
3. **Configuration**: Needs mode-specific settings (e.g., output format, time ranges)
4. **User Experience**: Two different ways to use the same tool (learning curve)

## Consequences

### Positive

- **Interactive Mode Benefits**:
  - Exploratory analysis: "What happened?"
  - Follow-up questions: "Show me more details"
  - Context preservation: Agent remembers previous queries
  - Immediate feedback for security investigations

- **Batch Mode Benefits**:
  - Automated compliance scanning
  - Integration with monitoring systems (Azure Monitor Action Groups)
  - Scheduled reports (daily/weekly summaries)
  - No human interaction required

### Negative

- State management differs between modes (stateful vs. stateless)
- Output formatting requirements differ (human vs. machine-readable)
- Error handling differs (interactive retry vs. batch failure)
- Performance expectations differ (interactive = fast response, batch = complete coverage)

### Implementation Complexity

The code must handle:

1. **Mode Detection**: Parse `--mode` flag, default to interactive
2. **Input Source**: 
   - Interactive: `input()` or CLI library
   - Batch: Predefined scan parameters
3. **Output Format**:
   - Interactive: Console with emoji/formatting
   - Batch: Markdown report
4. **Error Handling**:
   - Interactive: Display error, allow retry
   - Batch: Log error, exit with status code
5. **Context Management**:
   - Interactive: Maintain conversation history
   - Batch: Single execution context

## Architectural Implications

### Suggested Code Structure

```
/src
  /core
    pim_detector.py         # Shared: PIM detection logic
    activity_correlator.py  # Shared: Activity querying
    risk_assessor.py        # Shared: Alignment analysis
  /interfaces
    interactive_cli.py      # Interactive mode entry point
    batch_runner.py         # Batch mode entry point
  /reporting
    console_formatter.py    # Interactive output
    markdown_generator.py   # Batch output
  main.py                   # Mode router
```

### Configuration Requirements

Must support:
- `--mode` flag: `interactive` (default) or `batch`
- Time range: Default 24 hours, should be configurable
- Output destination: stdout (default) or file path (batch mode)
- Log level: Different verbosity for different modes

## Use Case Mapping

### Interactive Mode Use Cases

1. **Emergency Investigation**: User gets alert, opens tool, scans for suspicious activations
2. **Deep Dive**: User investigates specific user's complete activity timeline
3. **Alignment Verification**: User asks if activities match stated reasons
4. **Learning**: User explores PIM data to understand patterns

### Batch Mode Use Cases

1. **Daily Compliance Report**: Scheduled run at end of each day
2. **Real-Time Alerting**: Triggered every hour, sends report to action group if misalignment detected
3. **Audit Trail**: Automated logging of all PIM activities
4. **Dashboard Integration**: Generates data for monitoring dashboards

## Testing Considerations

### Interactive Mode Testing

- Mock user input/output
- Test conversation context preservation
- Test command parsing (scan, exit, natural language queries)
- Test error recovery and retry logic

### Batch Mode Testing

- Test non-interactive execution
- Validate Markdown output format
- Test exit codes (success/failure)
- Test complete workflow (scan → correlate → assess → report)

### Shared Logic Testing

- PIM detection: Same tests for both modes
- Activity correlation: Same tests for both modes
- Risk assessment: Same tests for both modes

## Alternative Considered

**Separate Tools**: Build two separate applications (one CLI tool, one batch script).

**Rejected because**:
- Code duplication (core logic would be identical)
- Deployment complexity (two tools to maintain)
- Harder to keep feature parity
- Specification clearly describes single tool with two modes

## Future Extensions

Possible future modes (not in current specification):
- **Web UI Mode**: Browser-based interface
- **API Mode**: REST API for integration
- **Streaming Mode**: Real-time monitoring with continuous output

## References

- `/README.md`: Features section describes "Interactive Chat Interface" and "Batch Mode"
- `/README.md`: Usage examples show both `python main.py` (interactive) and `python main.py --mode batch`
- Non-functional requirement #5: "Must be designed to run both interactively (chat mode) and non-interactively (batch mode)"
