# FalconX Acceptance Checklist

## 1) Delivery Completeness
- [ ] Full source code delivered
- [ ] No critical files missing
- [ ] Installation steps included
- [ ] Dependencies clearly defined
- [ ] Config/example env files included

## 2) Project Structure
- [ ] Clear folder structure
- [ ] Core modules separated logically
- [ ] No duplicate or confusing run files
- [ ] No random temporary/debug files
- [ ] Naming is clean and understandable

## 3) Core Trading Pipeline
- [ ] Market data ingestion exists
- [ ] Signal generation exists
- [ ] Risk management exists
- [ ] Position management exists
- [ ] Execution layer exists
- [ ] Logging/reporting exists
- [ ] Main run path is clear

## 4) Exchange Integration
- [ ] OKX integration exists
- [ ] API config is clean
- [ ] Testnet/paper/live mode is clear
- [ ] Order placement path is identifiable
- [ ] Balance retrieval exists
- [ ] Position retrieval exists
- [ ] Error handling for exchange responses exists

## 5) Risk & Protection
- [ ] Position sizing logic exists
- [ ] Stop loss logic exists
- [ ] Take profit logic exists
- [ ] Max drawdown protection exists
- [ ] Consecutive loss protection exists
- [ ] Kill switch or emergency stop exists

## 6) Engineering Quality
- [ ] Code is readable
- [ ] Modules are reusable
- [ ] Hardcoded secrets are absent
- [ ] Basic exception handling exists
- [ ] No obvious broken imports
- [ ] No obvious placeholder-only architecture

## 7) Operational Readiness
- [ ] Can run locally/VPS
- [ ] Has clear startup command
- [ ] Has logs
- [ ] Has config separation
- [ ] Can be tested safely before live mode

## 8) Decision
- [ ] Accept as strong base
- [ ] Accept with required revisions
- [ ] Reject and request major fixes

## Notes
- Delivery should be evaluated as a system, not as scattered files.
- Any missing core layer should be treated as a structural weakness.
- FalconX target is institutional-grade architecture, not a toy bot.