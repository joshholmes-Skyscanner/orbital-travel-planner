# Intentional Issues Reference

This document catalogues all intentional bugs, vulnerabilities, and anti-patterns in the codebase. These are learning opportunities for workshop participants.

---

## Booking API ([app/api/bookings.py](app/api/bookings.py))

### 1. No Duplicate Detection
**Location:** `create_booking()` function
**Issue:** Users can book the same plan multiple times simultaneously
**Impact:** Overselling, inventory conflicts
**Fix Strategy:** Add unique constraint or check existing bookings before creating

### 2. No Seat Availability Check
**Location:** `create_booking()` function
**Issue:** Creates booking without verifying seat availability via MCP
**Impact:** Booking confirmed but no seats available
**Fix Strategy:** Call `availability.check` MCP tool before creating booking

### 3. No Hold Expiry Enforcement
**Location:** `confirm_booking()` function, lines ~182-184 (commented out)
**Issue:** Can confirm booking after 5-minute hold expires
**Impact:** Business logic violation, inventory management issues
**Fix Strategy:** Uncomment the hold expiry check

### 4. No Authorization
**Location:** All booking endpoints
**Issue:** Anyone can view/cancel any booking with just the ID
**Impact:** Privacy violation, unauthorized cancellations
**Fix Strategy:** Add user authentication, check booking ownership

### 5. Verbose Error Messages
**Location:** `get_booking()` function, line ~168
**Issue:** Error message exposes internal database structure
**Impact:** Information disclosure, aids attackers
**Fix Strategy:** Return generic "Booking not found" message

```python
# Current (bad):
detail=f"Booking {booking_id} not found in database table 'bookings'"

# Should be:
detail="Booking not found"
```

### 6. No Idempotency
**Location:** `confirm_booking()` function
**Issue:** Calling confirm multiple times creates multiple payment records
**Impact:** Duplicate charges, audit trail corruption
**Fix Strategy:** Check current status, return existing confirmation if already confirmed

### 7. Mock Payment Always Succeeds
**Location:** `confirm_booking()` function, lines ~201-210
**Issue:** Payment never fails, no error handling
**Impact:** Unrealistic testing, no failure recovery paths
**Fix Strategy:** Add random payment failures, integrate with validation MCP tool

---

## Database Models ([app/db_models.py](app/db_models.py))

### 8. Seat Race Condition
**Location:** `Seat` model, line ~93 comment
**Issue:** No database constraint on status transitions, allows concurrent booking of same seat
**Impact:** Double-booking, data corruption
**Fix Strategy:** Use database row locking (SELECT FOR UPDATE) or unique constraints

### 9. No Indexes on Frequent Queries
**Location:** Throughout models
**Issue:** Missing indexes on `user_id`, `status`, `timestamp` fields
**Impact:** Slow queries as data grows
**Fix Strategy:** Add indexes to frequently filtered/joined columns

### 10. No Connection Pooling Tuning
**Location:** [app/database.py](app/database.py), line ~11
**Issue:** Using default connection pool settings
**Impact:** Connection exhaustion under load
**Fix Strategy:** Configure `pool_size`, `max_overflow`, `pool_timeout`

---

## MCP Server ([mcp/server.py](mcp/server.py))

### 11. Negative Prices (Chaos Mode)
**Location:** `pricing.calculate()`, lines ~76-83
**Issue:** Returns negative total price
**Impact:** Invalid business data, breaks downstream logic
**Fix Strategy:** Add validation in API layer or MCP client

### 12. Risk Score Out of Bounds (Chaos Mode)
**Location:** `risk.assess()`, lines ~135-141
**Issue:** Returns risk_score > 1.0 or < 0.0
**Impact:** Violates invariant (risk should be 0..1)
**Fix Strategy:** Validate risk score before using in calculations

### 13. Missing Required Fields (Chaos Mode)
**Location:** Multiple tools
**Issue:** Returns responses missing required fields
**Impact:** Breaks Pydantic validation, crashes clients
**Fix Strategy:** Add response validation with graceful degradation

### 14. Random Timeouts
**Location:** Multiple tools with `time.sleep()`
**Issue:** Simulates slow/unresponsive providers
**Impact:** Request timeouts, poor user experience
**Fix Strategy:** Add timeout handling, retry logic, circuit breakers

---

## Middleware ([app/middleware.py](app/middleware.py))

### 15. Logs Sensitive Data
**Location:** `AuditMiddleware.dispatch()`, lines ~31-36
**Issue:** Logs request body containing passenger data, payment info
**Impact:** Compliance violation (GDPR, PCI-DSS), security risk
**Fix Strategy:** Redact sensitive fields before logging

### 16. No Log Rotation
**Location:** `configure_logging()`, line ~107
**Issue:** Writes to `api_audit.log` indefinitely
**Impact:** Disk fills up, application crashes
**Fix Strategy:** Use RotatingFileHandler or external log management

### 17. Hardcoded API Keys
**Location:** `AuthMiddleware.VALID_API_KEYS`, lines ~67-70
**Issue:** API keys in source code
**Impact:** Security violation, leaked credentials
**Fix Strategy:** Store in environment variables or secrets manager

### 18. Verbose Auth Error Messages
**Location:** `AuthMiddleware.dispatch()`, lines ~91-97
**Issue:** Error message reveals valid API key format
**Impact:** Aids brute force attacks
**Fix Strategy:** Return generic "Invalid credentials" message

### 19. No Key Rotation
**Location:** `AuthMiddleware`
**Issue:** No mechanism to expire or rotate API keys
**Impact:** Compromised keys remain valid indefinitely
**Fix Strategy:** Add key expiry, rotation mechanism

---

## API Layer

### 20. No Pagination
**Location:** `list_bookings()` function
**Issue:** Returns all bookings matching filter
**Impact:** Memory exhaustion, slow response times
**Fix Strategy:** Add limit/offset or cursor-based pagination

### 21. No Rate Limiting per API Key
**Location:** Middleware configuration
**Issue:** Rate limit by IP only, not by authenticated user
**Impact:** Single user can exhaust API quota
**Fix Strategy:** Rate limit per API key when authenticated

### 22. No Request Validation Logging
**Location:** Throughout API
**Issue:** Validation failures not logged for analysis
**Impact:** Can't identify malicious probing or common errors
**Fix Strategy:** Log validation failures with request context

---

## Frontend ([app/static/app.js](app/static/app.js))

### 23. No Input Sanitization Beyond Basic Escaping
**Location:** Throughout JavaScript
**Issue:** Relies only on `escapeHtml()` for XSS prevention
**Impact:** Potential XSS if `escapeHtml()` has bugs
**Fix Strategy:** Use a well-tested sanitization library, CSP headers

### 24. No Loading States
**Location:** All async functions
**Issue:** No visual feedback during long-running operations
**Impact:** Poor UX, users may click multiple times
**Fix Strategy:** Show spinners, disable buttons during requests

### 25. No Retry Logic
**Location:** All `fetch()` calls
**Issue:** Single request failure = permanent failure
**Impact:** Transient network errors break user flow
**Fix Strategy:** Add exponential backoff retry for failed requests

### 26. No Error Recovery
**Location:** Throughout
**Issue:** Errors displayed but no way to retry
**Impact:** User must reload page to recover
**Fix Strategy:** Add retry buttons, clear error states

---

## Testing Gaps

### 27. No Concurrency Tests
**Location:** Missing from test suite
**Issue:** Race conditions not tested
**Impact:** Production bugs not caught in testing
**Fix Strategy:** Add tests that create concurrent bookings for same seat

### 28. No Chaos Testing
**Location:** Missing from test suite
**Issue:** MCP failures not systematically tested
**Impact:** Poor resilience to provider failures
**Fix Strategy:** Add tests with MCP_CHAOS=1, verify graceful degradation

### 29. No Property-Based Tests for Validation
**Location:** Minimal in `tests/properties/`
**Issue:** Edge cases not explored systematically
**Impact:** Validation bugs with unexpected inputs
**Fix Strategy:** Use Hypothesis to generate test cases

---

## How to Use This Document

### For Workshop Participants:
1. Pick an issue category matching your current stage
2. Use Claude Code to find the issue in the codebase
3. Design a fix (may involve multiple files)
4. Implement and verify with tests
5. Reflect: Why was this pattern used? What's the proper solution?

### For Workshop Facilitators:
- Use this as a checklist of issues discovered
- Track which issues each team has found/fixed
- Discuss tradeoffs in solutions
- Add your own issues for advanced participants

---

## Severity Levels

- 🔴 **Critical**: Security vulnerability or data corruption risk
- 🟠 **High**: Business logic violation or significant UX issue
- 🟡 **Medium**: Performance or observability issue
- 🟢 **Low**: Code quality or minor UX issue

### Critical Issues:
- #4: No Authorization
- #8: Seat Race Condition
- #17: Hardcoded API Keys

### High Issues:
- #1: No Duplicate Detection
- #2: No Seat Availability Check
- #5: Verbose Error Messages
- #15: Logs Sensitive Data
- #18: Verbose Auth Errors

### Medium Issues:
- #3: No Hold Expiry Enforcement
- #9: No Indexes
- #11-14: MCP Chaos Issues
- #20: No Pagination
- #27-29: Testing Gaps

### Low Issues:
- #16: No Log Rotation
- #23-26: Frontend UX Issues

---

## Workshop Exercise Ideas

1. **Stage 2**: Build `/validate-api` skill that finds issues #11-14
2. **Stage 3**: Build `/chaos-test` skill that exploits issue #8
3. **Stage 4**: Build `/debt-audit` skill that catalogs all issues
4. **Stage 5**: Build MCP validation server that catches issues #11-13

Participants will discover many of these organically through the exercises!
