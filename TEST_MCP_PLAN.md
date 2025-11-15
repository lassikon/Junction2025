# MCP Integration Testing Plan

## Phase 1: Local Testing ✅ (Done)
- [x] MCP server standalone test
- [x] MCP client connectivity test
- [x] Financial calculator middleware test

## Phase 2: Docker Integration (Next)
1. Rebuild Docker container with MCP SDK
2. Start containers: `docker-compose up --build`
3. Check logs: `docker logs hackathon-backend`
4. Verify MCP server starts without errors

## Phase 3: API Testing
1. Test onboarding flow (no MCP involved yet)
2. Make first decision with investment option
3. Verify console logs show:
   - "🧮 Calculating effects via MCP financial server..."
   - "[MCP] Connected to financial calculator server"
   - Transaction validation messages
4. Check response has correct financial effects

## Phase 4: Validation
1. Make multiple investment decisions
2. Verify balance sheet integrity:
   - money_change + investment_change = net gain/loss
   - No money created from nothing
3. Check passive income calculated correctly
4. Verify random multipliers (not fixed values)

## Phase 5: Edge Cases
1. Test major_loss scenario
2. Test insufficient funds
3. Test expense-only changes
4. Test mixed scenarios

## Expected Behavior
- LLM returns: `{"narrative": "...", "outcome": {"action_type": "investment", "investment_details": {"principal": 1000, "asset_type": "index_fund", "result_quality": "gain"}}}`
- MCP calculates actual numbers with small random variation
- Balance sheet validated before applying
- All calculations deterministic except for small random ranges

## Success Criteria
✅ No crashes or errors
✅ Financial effects are consistent
✅ Balance sheet always valid
✅ Passive income correlates with investments
✅ Random multipliers working (test multiple times, get different values)
