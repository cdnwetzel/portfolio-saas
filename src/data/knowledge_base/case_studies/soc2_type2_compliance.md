# SOC2 Type II: Evidence-Based Compliance & 90-Day Rolling Audit

## Overview

Achieved and maintained SOC2 Type II certification for a 25-person MSP within 90 days, establishing a framework where **every action is logged, every policy is documented, and auditors verify actual compliance through evidence** — not checkbox exercises.

SOC2 Type II differs fundamentally from SOC2 Type I: it requires **continuous operational evidence** that controls are actually working over a minimum 90-day observation period. This is not a snapshot audit; it's proof of sustained compliance through logs, monitoring, and corrective action.

## The 90-Day Rolling Lookback Model

### What "90-Day Rolling" Means

Auditors review a continuous 90-day window of evidence:
- **Month 1 (Days 1-30)**: Initial audit preparation, control baseline
- **Month 2 (Days 31-60)**: Controls operating, evidence accumulating
- **Month 3 (Days 61-90)**: Full 90-day window available for audit sampling

After the initial 90 days:
- Each new day adds to the audit window
- Each day that falls outside 90 days is dropped
- Auditors continuously sample from the rolling window
- Any control failure must be detected and corrected within 90 days (not retroactively)

**Critical implication:** You cannot fix a control failure that occurred 91 days ago. The control must work consistently throughout the audit period.

### Audit Frequency & Continuity

For this MSP:
- Annual formal audit (detailed review of full 12 months)
- Continuous sampling within rolling 90-day window
- Quarterly checkpoints (ensure no drift)
- Monthly internal compliance reviews
- Weekly evidence collection and validation

## Core Principle: Logged, Auditable, Provable

### Every Action is Tracked

SOC2 requires evidence that controls are operating. This means:

**Access Control Logging:**
- Every user login (successful and failed)
- Every permission grant/revoke
- Every privilege escalation
- Every access to sensitive data
- Every administrative action

**Change Management Logging:**
- Every system configuration change (add/edit/delete)
- Every software deployment
- Every access rule modification
- Every firewall rule update
- Every user account creation/modification/deletion
- Every policy change

**Monitoring & Alerting:**
- Every security event detected
- Every vulnerability discovered
- Every corrective action initiated
- Every incident investigation
- Every remediation verification

**Example: Adding a new user to the MSP**
```
[Admin action logged]
- User: john.doe@msp.com
- Action: Create user account
- User ID: newuser@client.com
- Permissions: Support Technician role
- Systems: Ticketing system, RDP gateway, Client portal
- Timestamp: 2024-06-15 09:23:14 UTC
- Approver: manager@msp.com (via change ticket CT-2847)
- Justification: "New hire, replacing departed technician"
- Audit trail: All created with correct group memberships, firewall rules updated to allow access, MFA enforced

[Quarterly audit check]
- User still has correct permissions? Yes
- User still employed? Yes
- Access still justified? Yes
- No unauthorized actions? Confirmed
```

### Policies Drive Evidence

Every control requires a documented policy, and auditors verify compliance by sampling evidence:

**Example: Password Policy**
- Policy states: "Passwords must be ≥14 characters, changed every 90 days, no reuse of last 5 passwords"
- Evidence auditors check:
  - System enforces password length? (screenshot of Active Directory settings)
  - Password expiration logs? (sample of 10 users, all changed within 90 days)
  - Password history enforced? (sample of change attempts, old passwords rejected)
  - MFA enabled? (audit log showing MFA enforcement for all accounts)

**Example: Firewall Rule Management**
- Policy states: "Firewall rules reviewed monthly, unused ports closed, principle of least privilege enforced"
- Evidence auditors check:
  - Monthly review documentation? (signed firewall audit reports for last 12 months)
  - Change logs for rule modifications? (who changed what, when, why)
  - Internal testing results? (penetration test findings, corrective actions taken)
  - Current rule set matches policy? (comparison of documented rules vs actual configuration)

## Implementation Journey: 25-Person MSP

### Starting State

The MSP had:
- Basic security practices (firewalls, antivirus)
- Limited logging (logs written locally, not centralized)
- No formal change management (changes made ad-hoc)
- No evidence collection system
- No regular testing (internal or external)
- Policies existed in people's heads, not documentation

**Major gaps for SOC2:**
- No proof of control operation
- No audit trail for changes
- No centralized monitoring
- No incident response procedures documented
- No access control reviews
- No segregation of duties

### Phase 1: Foundation (Weeks 1-4)

**Logging Infrastructure:**
- Deployed centralized syslog (rsyslog/ELK) for all systems
- Configured log forwarding from: firewalls, switches, servers, identity systems, applications
- Set 90+ day retention (meets SOC2 lookback requirement)
- Implemented log parsing and basic alerting

**Policy Documentation:**
- Drafted 25+ formal policies covering:
  - Access control and authentication
  - Change management
  - Incident response
  - Data classification and handling
  - Business continuity and disaster recovery
  - Personnel security
  - Supplier management
  - Monitoring and logging
- Got executive sign-off and staff training

**Evidence Collection Process:**
- Built evidence management spreadsheet (documented which evidence proves which controls)
- Identified who owns each control
- Scheduled monthly evidence review meetings

**Effort:** ~2-3 weeks implementation, 1 week staff training and policy adoption

### Phase 2: Control Implementation (Weeks 5-8)

**Access Control:**
- Enabled MFA company-wide (time-based OTP + hardware keys for admins)
- Implemented role-based access control (RBAC) in all systems
- Removed default accounts and credentials
- Locked down privileged access with PAM (Privileged Access Management)
- Enabled detailed logging of all privilege escalations

**Change Management:**
- Implemented formal change ticket system (tied to audit logging)
- Required approval for all production changes
- Mandated testing before deployment
- Logged all approvals, deployments, rollbacks
- Created change windows (Monday-Thursday, 9am-5pm, not on-call hours)

**Network Security:**
- Disabled weak TLS versions (1.0, 1.1), enabled only 1.2+
- Disabled weak cipher suites, enforced strong encryption
- Reviewed and locked down firewall rules (closed unused ports)
- Configured Network Access Control (NAC) to enforce device compliance
- Enabled detailed firewall logging for all blocked connections

**Monitoring & Alerting:**
- Set up security alerts for: failed logins, privilege escalations, failed change approvals, exposed credentials
- Configured daily log review and investigation procedures
- Established incident response team and procedures
- Created incident documentation and investigation templates

**Effort:** ~3-4 weeks implementation, continuous staff training

### Phase 3: Testing & Validation (Weeks 9-12)

**Monthly Internal Penetration Testing:**
- Hired internal tester (or trained staff member)
- Ran monthly pen tests targeting: web applications, network, infrastructure
- Documented all findings in standardized format
- Assigned corrective actions with deadlines

**Vulnerability Scanning:**
- Implemented automated vulnerability scanning (Nessus, OpenVAS)
- Weekly scans of all systems
- Prioritized critical/high findings for immediate remediation
- Tracked remediation progress and re-testing

**Compliance Validation:**
- Reviewed all logs for evidence of control operation
- Verified every policy was being followed (sampling)
- Validated all corrective actions were completed
- Prepared audit evidence documentation
- Conducted mock audit internally

**Effort:** ~3 weeks setup, 1 week intensive audit prep

## Key Controls: Evidence Requirements

### Access Control

**Control:** Only authorized personnel can access systems and data

**Evidence auditors verified:**
- Current user access list (who has what permissions)
- New user approval forms (justification for each account)
- Access reviews (quarterly verification of who needs what)
- Failed login logs (unauthorized attempts blocked)
- Privilege escalation logs (when admin rights were used, why)
- Account termination procedures (departed employees removed promptly)
- MFA enforcement (logs showing all multi-factor authentications)

**Example finding during testing:**
```
Vulnerability: Service account with permanent password
Corrective action: 
  1. Changed to managed service account with automatic password rotation
  2. Enabled privileged access logging
  3. Removed standing access, switched to just-in-time (JIT) escalation
  4. Re-tested in next month's pen test
```

### Change Management

**Control:** All changes are approved, tested, logged, and can be rolled back

**Evidence auditors verified:**
- Change ticket system (every change has ticket, approval, timeline)
- Approval logs (manager/security review documented)
- Testing results (changes tested before production)
- Deployment logs (when deployed, by whom)
- Rollback procedures documented (and tested)
- Change history (can rebuild any system from logs)

**Example:** Firewall rule change
```
Change Ticket: CHG-4521
Date: 2024-06-20
Change: Add firewall rule to allow monitoring traffic on port 5514
Justification: New syslog server deployment
Risk Assessment: Low (new inbound rule, monitoring only)
Approval: security@msp.com (2024-06-19)
Testing: Tested in staging environment, confirmed syslog receiving
Deployment: 2024-06-20 22:00 UTC (change window)
Logs: Rule added via API, logged in firewall audit trail
Verification: Confirmed rule active, monitoring traffic flowing
Rollback plan: If monitoring fails, delete rule and revert to previous config
```

### Monitoring & Logging

**Control:** All security-relevant events are logged, analyzed, and responded to

**Evidence auditors verified:**
- Logging enabled on all systems (screenshots of configurations)
- Logs contain required data (timestamps, users, actions, results)
- Logs retained 90+ days (and backed up)
- Logs reviewed regularly (automated alerts + manual review)
- Incidents detected and responded to (incident logs)
- Corrective actions tracked (vulnerability remediation logs)

**Example logging requirement:**
```
All system logs must include:
- Timestamp (to second precision, UTC)
- User/source (who performed the action)
- Action (what was done: login, file access, configuration change)
- Resource (what was accessed: filename, service, setting)
- Result (success/failure)
- Additional context (client ID, IP address, reason)

Sample log entry:
2024-06-20T14:23:45Z user=john.doe action=login resource=vpn result=success mfa=passed source_ip=203.0.113.45
2024-06-20T14:24:12Z user=john.doe action=file_access resource=/var/log/sensitive.log result=success access_level=admin
2024-06-20T14:25:33Z user=john.doe action=privilege_escalation resource=sudo result=success justification="emergency server restart"
```

## Operational Discipline: What It Really Means

### Monthly Internal Pen Testing

**Process:**
1. Schedule pen test for specific day each month
2. Tester given same access as attacker would have (from perimeter)
3. Tester documents all findings (even minor ones)
4. Findings categorized: critical, high, medium, low
5. Critical/high findings must have corrective action within 2 weeks
6. All findings tested for remediation in next month's test

**Example findings from actual monthly tests:**
```
Month 1:
- Weak SSH cipher suite on mail server (CRITICAL)
  Action: Disabled weak ciphers, enabled only chacha20+poly1305, aes-256-gcm
  Verification: Tested in Month 2, confirmed fixed

- Expired SSL certificate on web portal (HIGH)
  Action: Renewed certificate with 60-day renewal reminder
  Verification: Confirmed current, monitoring expiration

- Unused port 8080 exposed on web server (MEDIUM)
  Action: Closed port in firewall, disabled on web server
  Verification: Port scan in Month 2 showed closed

- Missing HSTS header on web application (MEDIUM)
  Action: Added "Strict-Transport-Security: max-age=31536000" header
  Verification: Browser testing confirmed HSTS enforced
```

### Quarterly Compliance Review

**What we verified:**
- All logging systems still running (checked log volume, no gaps)
- All policies still being followed (sampled 10% of access changes, verified approval trail)
- No drift in security configurations (scanned all systems, compared to baseline)
- No new vulnerabilities introduced (vulnerability scan results)
- All staff still trained (confirmation on file for all 25 people)
- All evidence still collected and organized (audit folder review)

**If we found issues:**
- Root cause analysis
- Corrective action implementation
- Re-testing
- Documentation for audit trail

## The Biggest Challenges

### 1. Staff Adoption

**Problem:** People resisted the rigor. "Why do we need to log everything? Why approval for every change?"

**Solution:**
- Showed real incident examples (compromised account led to data breach at competitor)
- Explained that SOC2 protects them (proof they didn't cause the breach)
- Positioned compliance as professional standard (like building codes for infrastructure)
- Made processes as frictionless as possible (automated approvals where safe, fast ticketing)

**Result:** After 2-3 months, staff accepted that "this is how we do things" and compliance became normal

### 2. Log Volume & Management

**Problem:** Systems generated gigabytes of logs daily. Storage costs exploded, searching logs was slow.

**Solution:**
- Implemented log retention tiers: hot storage (30 days, fast), warm storage (60 days, slower), archive (90+ days)
- Configured log parsing to extract only security-relevant events (dropped routine application logs)
- Set up automated log compression and archival
- Implemented Elasticsearch for fast searching

**Result:** 90-day retention was manageable cost (~$500/month), auditors could search logs quickly

### 3. Proving the Negative

**Problem:** Auditors asked "How do you know you caught all breaches?" Hard to prove you *didn't* get hacked.

**Solution:**
- Showed complete audit trail (every login logged, every change logged)
- Demonstrated monitoring (alerts for suspicious activity)
- Showed incident response process (if breach detected, here's what we do)
- Conducted tabletop exercises (response procedures documented and tested)

**Result:** Auditors accepted that comprehensive logging + monitoring = high confidence in detection

## Ongoing Maintenance: The 90-Day Rolling Model

After initial certification, compliance became operational:

**Weekly:**
- Review security alerts (5-10 minutes)
- Check log volume (ensure no gaps)

**Monthly:**
- Internal penetration test (1-2 days effort)
- Log review and analysis (4 hours)
- Evidence collection and organization (2 hours)
- Staff compliance check (verify policies followed in sample of actions)

**Quarterly:**
- Full compliance review (8-10 hours)
- Vulnerability scan and remediation (4-6 hours)
- Policy updates as needed (2-4 hours)
- Staff retraining (if needed)

**Annually:**
- External audit (3-5 days of auditor time)
- Full evidence binder review (10-15 hours prep)
- Policy refresh and distribution
- Staff training refresh

**Total ongoing effort:** ~20-25 hours/month for 25-person MSP

## Why SOC2 Type II Matters

SOC2 Type II proves:
- **Controls actually work** (not just documented)
- **Compliance is sustained** (not one-time)
- **You detect and respond to incidents** (logs prove it)
- **Staff are trained and follow procedures** (evidence-based)

For service organizations, it's the gold standard. Customers trust you because auditors verified your claims.

---

*This document synthesizes experience implementing SOC2 Type II for a 25-person MSP, achieving certification within 90 days and maintaining rolling compliance through evidence-based control operation, comprehensive logging, and continuous testing.*
