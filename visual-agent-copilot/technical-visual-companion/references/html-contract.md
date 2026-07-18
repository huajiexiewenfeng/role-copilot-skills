# Offline HTML Contract

The user-facing deliverable is one self-contained UTF-8 HTML file that works without a network connection.

## Validation Command

```text
validate_html.py --html PATH --required-term TERM --required-term TERM [--max-bytes 2000000]
```

`--required-term` is repeatable. Required terms come from the confirmed visual fact model for the task. The default size ceiling is 2 MB (`2000000` bytes).

The validator writes one UTF-8 JSON report with `overall`, `errors`, and `metrics`. Exit code `0` means passed; exit code `1` means failed.

## Rules and Error Codes

| Rule | Error code |
|---|---|
| UTF-8 without a byte-order mark | `utf8-bom`, `invalid-utf8` |
| Exactly one HTML doctype | `doctype-count` |
| Exactly one HTML root | `html-root-count` |
| At least one semantic section | `section-missing` |
| At least one inline SVG relational diagram | `svg-missing` |
| Every SVG has `role="img"`, `title`, and `desc` | `svg-accessibility-incomplete` |
| No script or iframe | `script-forbidden`, `iframe-forbidden` |
| No HTTP(S) or protocol-relative resource attributes | `external-resource-forbidden` |
| No HTTP(S), CSS import, fetch, XMLHttpRequest, or WebSocket reference | `network-reference-forbidden` |
| A narrow-screen media rule exists | `responsive-rule-missing` |
| A reduced-motion rule exists | `reduced-motion-rule-missing` |
| A dark color-scheme rule exists | `color-scheme-rule-missing` |
| File is within the configured size ceiling | `size-limit-exceeded` |
| Every required fact-model term is present | `required-term-missing:<term>` |

## Scope Limit

Structural validation cannot prove visual quality, mobile readability, diagram correctness, or factual accuracy. Desktop and 390px visual review remain mandatory, and the required terms must be derived from confirmed facts rather than used as a substitute for factual review.
