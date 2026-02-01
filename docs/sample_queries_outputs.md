# 🎯 Sample Queries & Intelligence Outputs

This document showcases the analytical capabilities of the **MD Capital AI Agent**. The agent performs real-time synthesis of insurer communication logs, turning raw text and metadata into strategic insights.

---

### 📊 1. Pattern Recognition: Denial Root Causes
**User instruction:** *"Analyze the top 5 recurring reasons for claim rejections and identify which insurers are most associated with each."*

**Agent response:**
> Based on a comprehensive review of the 41 communication records, here are the primary drivers of claim denials:
>
> 1.  **Administrative & Prior Authorization (PA)**: This is the leading cause. **Aetna** and **Humana** frequently deny claims due to missing or expired authorizations.
> 2.  **Coding Accuracy**: Errors in CPT codes (e.g., 99214 vs 99213) are common with **Aetna** and **Kaiser Permanente**.
> 3.  **Documentation Gaps**: **Cigna** and **Anthem** often cite missing clinical notes or PCP referrals.
> 4.  **Verification Failures**: **Humana** shows a pattern of eligibility verification issues (e.g., Member ID mismatches).
> 5.  **Coordination of Benefits (COB)**: **UnitedHealthcare** is the primary insurer requiring primary EOBs before processing.

---

### 🏢 2. Competitive Benchmarking: Aetna vs. UnitedHealthcare
**User instruction:** *"Contrast the communication tone and primary issues between Aetna and UnitedHealthcare. Who is more efficient?"*

**Agent response:**
> **Aetna Communications**: Characterized by a "Corrective" tone. Issues are heavily documentation-focused (Itemized bills, PA-7 forms). Aetna also shows the highest average latency at **43.4 days**, indicating a more complex turnaround process.
>
> **UnitedHealthcare Communications**: More "Process-Oriented". While they have COB issues, their communications often confirm payment processing and EFT status. They demonstrate higher efficiency with an average turnaround of **29.8 days**.
>
> **Strategic Insight**: Redirect documentation heavy-loads away from Aetna's manual review process to reduce the 40+ day lag.

---

### ⚡ 3. High-Urgency Analysis
**User instruction:** *"Summarize all urgency level 5 records. What are the common denominators?"*

**Agent response:**
> Urgency Level 5 records represent **Critical Risk** scenarios. The common denominators across these records are:
>
> *   **Hard Deadlines**: Timely filing limits (5 days remaining) and Appeal windows (3 days remaining).
> *   **Clinical Severity**: Life-threatening situations (Air Ambulances) or urgent surgical requirements.
> *   **Financial Exposure**: Cases where out-of-pocket maximums have been reached, necessitating immediate full coverage.
> *   **Operational Blocks**: Expired authorizations for critical medication refills.

---

### ⏱️ 4. Latency & Performance Metrics
**User instruction:** *"Identify the 'Danger Zone'—claims that have been pending for over 50 days. Is there a specific insurer pattern?"*

**Agent response:**
> There are **6 records** in the "Danger Zone" (>50 days):
>
> *   **Anthem**: 85 days (Timely filing risk).
> *   **Aetna**: 90 days (External review stage) and 60 days (Partially denied).
> *   **Cigna**: 57 days (Appealed) and 55 days (Air ambulance denial).
> *   **UnitedHealthcare**: 52 days (Approved, but auditing payment).
>
> **Pattern**: Claims that cross the 50-day mark typically graduate from "Pending" to "Appealed" or face "Final Denial" stages, specifically with **Aetna** and **Anthem**.

---

### 💡 5. Proactive Recommendations
**User instruction:** *"Based on the data, what are the top 3 actions we can take this week to improve our revenue cycle?"*

**Agent response:**
> 1.  **Expedite Cigna Appeals**: Address the level 2 appeals for Cigna (currently at 75 days) to unlock aging receivables.
> 2.  **Audit PA Workflow for Aetna**: Aetna's 30-day "Prior Auth not on file" denials are preventable. Implement a pre-submission PA check.
> 3.  **Standardize Modifier 25 with Anthem**: Recurring denials for Modifier 25 suggest a systematic billing error that can be fixed via global template updates.
