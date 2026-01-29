# Sample Queries & Outputs

Below are examples of how the MD Capital AI Agent handles various management questions based on the provided dataset.

---

### 1. Rejection Analysis
**Question**: "What are the top 5 reasons claims are being denied?"
**Agent Response**:
> Based on the communication analysis, the top 5 reasons for claim denials are:
> 1. **Prior Authorization Issues**: Claims denied because authorization was not on file or expired (e.g., Aetna, Humana).
> 2. **Missing Documentation**: Specifically missing referral documentation from PCP or itemized bill breakdowns (e.g., Cigna, Aetna).
> 3. **Coding Errors**: Incorrect procedure codes (CPT 99214 vs 99213) or missing modifiers (Modifier 25).
> 4. **Medical Necessity**: Claims under review or denied for medical necessity requiring additional clinical notes (e.g., Anthem).
> 5. **Eligibility/Coordination of Benefits**: Issues verifying patient eligibility or needing primary insurance EOB (e.g., Humana, UnitedHealthcare).

---

### 2. Insurer-Specific Insights
**Question**: "Compare Aetna vs. UnitedHealthcare on denial reasons."
**Agent Response**:
> **Aetna** denials are primarily driven by **administrative and documentation issues**, such as missing prior authorizations and requests for itemized bill breakdowns. They also show a pattern of denying emergency room claims as non-emergency.
>
> **UnitedHealthcare**, on the other hand, shows more **process-oriented issues**, such as coordination of benefits (COB) requirements and bundled payment issues where services are included in a global period. However, they also have positive communications regarding approved EFT payments.

---

### 3. Operational Patterns
**Question**: "What characterizes urgency level 5 communications?"
**Agent Response**:
> Urgency level 5 communications are characterized by **critical time-sensitive issues** and **high-stakes medical situations**:
> - **Deadlines**: Approaching appeal deadlines (3-5 days) or timely filing limits.
> - **Clinical Urgency**: Patients requiring urgent surgery or life-threatening situations (e.g., air ambulance transport).
> - **Financial Thresholds**: Patients reaching out-of-pocket maximums.
> - **Expired Auths**: Urgent medication refills where prior authorization has expired.

---

### 4. Quantitative Analysis
**Question**: "Which insurer has the slowest response times?"
**Agent Response**:
> Based on the `days_since_submission` field:
> - **Aetna** has the highest average pending time at **43.4 days**, with some appeals reaching **90 days**.
> - **Anthem** follows closely with an average of **32.3 days**.
> - **Cigna** averages **46.0 days** for pending/appealed claims.
> *Note: UnitedHealthcare appears to be the most efficient with an average of 29.8 days.*
