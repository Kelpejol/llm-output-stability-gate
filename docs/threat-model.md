# Threat Model

## Threats

- Hallucinated responses
- Contradictory outputs
- Overconfidence in unstable generations

## Mitigations

- Multi-sample uncertainty quantification
- Threshold-based rejection
- No silent acceptance

## Assumptions

- Sampling captures model variance
- Thresholds are domain-specific

## Non-Goals

- Guaranteeing correctness
- Adversarial prompt defense
