# AI provider update review — 2026-11-17

This note separates official vendor announcements from XPiX integration decisions. A model appearing in a vendor announcement does not mean it is configured, enabled, benchmarked, or available under the project's current API credentials.

## Anthropic / Claude

Official sources:
- https://www.anthropic.com/news
- https://platform.claude.com/docs/en/release-notes/overview
- https://claude.com/resources/product-updates

Recent items:
- **Nov 9, 2026:** Claude Fable 5.2 launched for demanding reasoning and long-horizon agentic work. Anthropic lists a 1M-token context window and 128k max output. Claude Mythos 5.2 is restricted to verified organizations/programs; do not design the default product around Mythos access.
- **Nov 12, 2026:** self-hosted Claude Managed Agents launched for eligible customers; agents, sessions, and history can be hosted inside the customer's infrastructure. Access is by request, so it is not assumed available to XPiX.
- **Nov 12, 2026:** Claude Meetings beta announced for Team and Enterprise.
- **Nov 16, 2026 Platform release notes:** text watermarking details were added for supported Claude model/platform combinations. This is not a reason to change XPiX inference settings.

XPiX recommendation:
- Keep Claude as an optional high-reasoning/reviewer provider behind server-side configuration.
- Evaluate Fable 5.2 on bounded tasks (multi-file code review, architecture reasoning, source reconciliation) before changing defaults.
- Do not assume Mythos access or self-hosted Managed Agents access.
- Keep API keys server-side and retain usage caps, short context, caching, and provider fallback.

## Google / Gemini

Official sources:
- https://blog.google/products-and-platforms/products/gemini/
- https://blog.google/feed/
- https://ai.google.dev/gemini-api/docs/models
- https://ai.google.dev/gemini-api/docs/latest-model

Recent items:
- **Nov 12, 2026:** Gemini 4 Hydrogen rolled into Google Search with stronger multi-part intent handling, simultaneous query expansion, and more visual/structured responses. This is a Search product update; do not treat it as proof that an API model ID is available to XPiX.
- **Nov 16, 2026:** Google announced 66 additional regional voices rolling out in the Gemini app. This is an app/voice rollout, not automatically an API voice-model upgrade.
- **Nov 16, 2026:** Gemini app history/training controls were updated; rollout is gradual. This concerns consumer app privacy controls, not the server API's data policy.
- Current Gemini API model documentation lists Gemini 3.8 Flash for long-horizon software engineering and autonomous agent workflows, and Gemini 3.8 Live / Live Extended Thinking for low-latency or higher-reasoning voice interactions.

XPiX recommendation:
- Keep the existing Gemini integration as the fast/default fallback until a measured API test is run.
- Test documented API model IDs in a separate staging configuration; never copy app-only labels such as Hydrogen into the API model setting without API documentation.
- Use Live models only for the voice path if the Live API contract and cost/latency tests pass.
- Preserve explicit provider/model selection, daily caps, cache, token budget, and offline fallback.

## XPiX provider architecture decisions

1. A single provider adapter contract should expose provider, model, latency_ms, input_tokens, output_tokens (when supplied), cost_estimate, status, and fallback_reason.
2. Secrets remain server-side. The browser must never receive Anthropic or Gemini server API keys.
3. Provider fallback must be explicit and visible; never silently imply that a premium model answered when the fallback handled the request.
4. Add a small, non-market-data evaluation set for Arabic dashboard explanations, code review, JSON/schema reliability, and multi-step tool plans.
5. Compare quality, latency, error rate, and estimated cost before promoting a model. No model change is made in this staging-preparation commit.
6. Never send broker credentials, private trading account details, or raw private user records to an AI provider by default.

## Scope and status
- Research/documentation only.
- No model IDs, API calls, secrets, or production settings changed.
- Vendor announcements and API documentation must be rechecked at implementation time because availability, model IDs, and pricing can change.
