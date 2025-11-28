# Mission and Conviction

Testing produces conviction: justified belief that software fulfills its mission.

- Mission: what must be true for the software to achieve its purpose
- Oracle: mechanism that determines whether a property holds
- Conviction: earned when oracles confirm mission properties

## Mission

Mission decomposes into properties. A property is a testable claim about the system.

Properties divide by scope:
- Process properties: what must hold during execution
- Product properties: what must hold of the result

Both are invariants. Process invariants are checked throughout. Product invariants are checked at termination.

### Well-Specified Mission

A mission is well-specified when:
- Every property is oracle-constructible
- Every property is necessary for purpose
- All properties together are sufficient for purpose
- No property assumes implementation

Decompose until testable:

```text
"Produce usable imagery"
  -> too vague, no oracle

"Geometric accuracy under 20m CE90"
  -> how measured?

"CE90 under 20m against surveyed GCPs on test scene"
  -> oracle: compare output coordinates to GCP survey
  -> testable
```

Stop when you can name the oracle.

### Property Criteria

A property is well-specified when:
- Testable: an oracle can be constructed
- Atomic: single concern per property
- Necessary: removal would mean mission unfulfilled
- Purpose-anchored: traces to why the system exists

```text
Bad:  "System shall be reliable"
Good: "System shall complete within 180s for inputs up to 1500x22000"

Bad:  "System shall produce accurate, timely, well-formatted output"
Good: Three separate properties for accuracy, timing, format

Bad:  "Function X shall return type Y" (implementation)
Good: "Output shall be usable by downstream processing" (purpose)
```

## Oracle

An oracle answers: does this property hold?

### Oracle Types

| Type | Source | Strength |
| ---- | ------ | -------- |
| Specified | Predetermined correct answer | High on covered cases |
| Derived | Reference implementation | High, inherits reference bugs |
| Relational | Invariant across transformations | Moderate, proves property not value |
| Implicit | Plausibility bounds | Low, proves validity not correctness |

### Well-Specified Oracle

An oracle is well-specified when:
- Deterministic: same input yields same verdict
- Constructible: can be built with available resources
- Validated: provenance establishes trustworthiness
- Scoped: clear about what it covers

```text
Bad:  "Output looks correct" (subjective)
Good: "Output matches reference within 0.5 dB RMS"

Bad:  "Output equals what a perfect processor would produce"
Good: "Output matches SNAP processor within tolerance on test vectors"
```

### Oracle Construction

Decision tree for oracle selection:

```text
Do you have ground truth for specific inputs?
  -> Yes: Specified oracle (Known Answer Test)
  -> No: Do you have a trusted reference implementation?
    -> Yes: Derived oracle (reference comparison)
    -> No: Do you have invariant properties?
      -> Yes: Relational oracle (metamorphic testing)
      -> No: Do you have validity bounds?
        -> Yes: Implicit oracle (plausibility check)
        -> No: No oracle exists. Property is untestable.
```

If no oracle exists, the property is untestable. Untestable properties provide zero conviction. Either find an oracle, find a proxy property with an oracle, or acknowledge the gap.

### Relational Oracle Patterns

Common metamorphic relations:

| Pattern | Relation | Example |
| ------- | -------- | ------- |
| Symmetry | f(T(x)) = T(f(x)) | Transform invariance |
| Conservation | measure(out) = measure(in) | Energy preservation |
| Monotonicity | x < y implies f(x) <= f(y) | Order preservation |
| Roundtrip | inverse(f(x)) = x | Encode/decode |
| Subset | filter(f(x)) subset f(x) | Refinement |

## Conviction

Conviction level depends on oracle quality.

### Conviction Levels

| Level | Oracle | Claim |
| ----- | ------ | ----- |
| 0 | None | Executes |
| 1 | Implicit | Output plausible |
| 2 | Specified | Correct on known cases |
| 3 | Derived | Matches reference |
| 4 | Relational | Properties hold universally |

Conviction for a property equals its oracle level.
Conviction for the mission equals minimum conviction across critical properties.

### Required Conviction

Match conviction to consequence:

| Failure consequence | Minimum conviction |
| ------------------- | ------------------ |
| Inconvenience | L1 |
| Data loss | L2 |
| Financial loss | L2 + L4 |
| Mission loss | L3 + L4 |
| Safety risk | L3 + L4 + qualification |

## Tests

A test is an oracle applied to an execution.

```text
Test = Execute(input) -> Output
       Oracle(input, output) -> {pass, fail}
       Pass -> evidence for property
       Fail -> evidence against property
```

A test provides conviction when:
- It exercises a mission property
- It uses a valid oracle
- It runs under representative conditions

Tests without oracles are not tests. They are executions.

### Anti-Patterns

| Pattern | Problem | Fix |
| ------- | ------- | --- |
| Golden master | Proves unchanged, not correct | Add specified oracle |
| Plausibility bounds | Proves valid, not accurate | Add specified oracle |
| Loose tolerance | Proves bounded, not conserved | Tighten to spec |
| Toy data | Proves nothing about scale | Representative size |
| Circular oracle | Tests system against itself | Independent oracle |

## Gaps

A gap exists when a mission property lacks sufficient conviction.

### Audit Protocol

1. List mission properties
2. For each: what oracle? what level?
3. For each: does level meet required conviction?
4. Gap = property where level < required

### Gap Closure

Close gaps by:
- Constructing stronger oracles
- Finding proxy properties with oracles
- Accepting and documenting the risk

## Validation Questions

Before claiming conviction, answer:

For each property:
- What is the oracle?
- Where did it come from?
- What does it cover?
- What could it miss?

For the mission:
- Are all critical properties covered?
- Is the weakest oracle strong enough?
- What would remain uncertain after all tests pass?

For deployment:
- If all tests pass, would you deploy?
- If not, what is missing?
- If yes, what are you betting on?

Conviction is not certainty. It is justified belief given available evidence. The framework makes the justification explicit and the gaps visible.

## Test Marking

Mark mission-critical tests to enable extraction and analysis of mission property validation.

### Framework Markers

Use framework-native markers to tag tests that validate mission properties:

```python
# pytest
@pytest.mark.mission
def test_geometric_accuracy_within_ce90():
    """Oracle: Specified. Property: CE90 under 20m against GCPs."""
    ...

# pytest with property classification
@pytest.mark.mission
@pytest.mark.process_property
def test_memory_stays_below_4gb():
    """Oracle: Implicit. Property: Peak memory under hardware constraint."""
    ...

@pytest.mark.mission
@pytest.mark.product_property
def test_output_radiometric_calibration():
    """Oracle: Derived. Property: Calibration matches reference."""
    ...
```

```javascript
// Jest/Vitest
describe('mission', () => {
  test('processing completes within orbital window', () => {
    // Oracle: Specified. Property: Timing constraint.
  })
})
```

```go
// Go testing
func TestMission(t *testing.T) {
    t.Run("mission:timing_constraint", func(t *testing.T) {
        // Oracle: Specified. Property: Completion within window.
    })
}
```

### Test Documentation

Document oracle type and property in test docstring or comment:

```python
@pytest.mark.mission
def test_range_compression_energy_conservation():
    """
    Property: Range compression preserves signal energy (process invariant)
    Oracle: Relational (conservation law)
    Conviction: L4
    """
    signal = generate_chirp()
    compressed = compress_range(signal)
    assert energy_ratio(compressed, signal) in (0.95, 1.05)
```

Structure: Property -> Oracle -> Conviction level

### Extraction

Run mission tests and extract results for analysis:

```sh
# pytest: run only mission tests
pytest -m mission

# Generate report with conviction analysis
pytest -m mission --tb=short -v > mission-report.txt

# Extract by property type
pytest -m "mission and process_property"
pytest -m "mission and product_property"
```

### Analysis

Map test results to mission properties:

```python
def analyze_mission_validation(test_results: list) -> dict:
    """Analyze which mission properties have conviction and at what level."""
    properties = extract_properties(test_results)

    return {
        "total_properties": len(properties),
        "conviction_levels": {
            prop: oracle_level(prop)
            for prop in properties
        },
        "gaps": [
            prop for prop in properties
            if oracle_level(prop) < required_level(prop)
        ],
        "minimum_conviction": min(oracle_level(p) for p in properties)
    }
```

### Naming Convention

Encode mission context in test names:

```text
test_mission_{property}_{oracle_type}

Examples:
- test_mission_timing_constraint_specified
- test_mission_energy_conservation_relational
- test_mission_output_format_derived
```

### Mission Test Criteria

A test earns the mission marker when:
- It validates a documented mission property
- It uses a well-specified oracle (documented type)
- Oracle level meets required conviction for that property
- Test runs under representative conditions

Do not mark:
- Implementation details unrelated to mission
- Tests without clear oracles
- Tests that only prove execution (conviction L0)

### Reporting

Generate conviction reports mapping to mission framework:

```text
Mission Validation Report
========================

Critical Properties: 12
Covered: 11 (91.7%)
Minimum Conviction: L2

By Property Type:
  Process properties: 7/7 (L2-L4)
  Product properties: 4/5 (L2-L3)

By Oracle Type:
  Specified: 5 tests (L2)
  Derived: 3 tests (L3)
  Relational: 3 tests (L4)
  Implicit: 0 tests

Gaps:
  Property: Absolute radiometric accuracy
    Required: L3 (matches reference)
    Current: none (untestable - no reference available)
    Status: Gap documented, risk accepted

Overall Mission Conviction: L2
Recommendation: Sufficient for deployment given failure consequences
```
