# 🎯 Sample Queries & Intelligence Outputs

This document showcases the analytical capabilities of the **MD Capital AI Agent**. The agent uses a **Plan-and-Execute** workflow to turn raw data into strategic insights.

---

### 📊 1. Analyze the top 5 recurring reasons for claim reje...
**User instruction:** *"Analyze the top 5 recurring reasons for claim rejections and identify which insurers are most associated with each."*

**Agent response:**
*   **Prior Authorization Missing:** **Aetna** is associated with denials due to missing prior authorizations.
*   **Missing Referral Documentation:** **Cigna** is associated with denials due to missing PCP referral documentation.
*   **Unclear Denial Reason/CPT Code Mismatch:** **Blue Cross Blue Shield** is associated with denials where the reason is unclear or related to CPT code discrepancies.
*   **Incorrect Procedure Code:** **Kaiser Permanente** is associated with denials due to the submission of incorrect procedure codes.
*   **Patient Eligibility Issues:** **Humana** is associated with denials related to patient eligibility verification problems.

STRATEGIC IMPACT: Reducing claim rejections from these insurers by addressing these top 5 reasons will directly improve MD Capital's revenue cycle efficiency and profitability.

---

### 📊 2. Contrast the communication tone and primary issues...
**User instruction:** *"Contrast the communication tone and primary issues between Aetna and UnitedHealthcare. Who is more efficient (lowest average latency)?"*

**Agent response:**
**UnitedHealthcare** exhibits greater efficiency with an average latency of **27.83** days compared to **Aetna's** **41.17** days.

*   **Aetna's** communication tone centers on claim denials, appeals, and patient out-of-pocket expenses. Primary claim status issues involve rejections and claims under review.
*   **UnitedHealthcare's** communication focuses on payments, Explanation of Benefits (EOBs), and authorizations. Claim status is primarily approvals, with some rejections.

STRATEGIC IMPACT: **UnitedHealthcare's** superior efficiency and proactive communication may indicate stronger operational management, potentially making them a more attractive investment target than **Aetna**, impacting MD Capital's portfolio allocation decisions.

---

### 📊 3. Summarize all urgency level 5 records. What are th...
**User instruction:** *"Summarize all urgency level 5 records. What are the common denominators?"*

**Agent response:**
*   **Claim Status:** Predominantly rejected (**4 out of 8**) followed by pending (**3 out of 8**). Appealed claims are minimal (**1 out of 8**).
*   **Insurers:** **Aetna** leads with **3 out of 8** claims, followed by **Humana** and **Cigna** tied at **2 out of 8** each. **Anthem** has **1 out of 8**.
*   **Communication Direction:** Primarily outbound communication (**7 out of 8**).
*   **Keywords:** "Claim" and "Patient" are the most frequent keywords (**4 mentions each**), followed by "Prior" and "With" (**3 mentions each**). "Denied" appears twice.
*   **Days Since Submission:** Average of **37.6 days**, with a wide range (0-85 days) and a standard deviation of 31.2 days.

STRATEGIC IMPACT: The high rejection rate and significant average time since submission for urgency level 5 claims indicate potential inefficiencies or systemic issues in claim processing with **Aetna, Humana, and Cigna**, impacting MD Capital's resource allocation and potentially necessitating targeted interventions to improve claim outcomes and reduce administrative overhead.

---

### 📊 4. Identify the 'Danger Zone'—claims that have been p...
**User instruction:** *"Identify the 'Danger Zone'—claims that have been pending for over 50 days. Is there a specific insurer pattern?"*

**Agent response:**
*   **Anthem** has **1** claim pending for over 50 days.

STRATEGIC IMPACT: While the volume is low, the presence of even a single claim exceeding 50 days with **Anthem** warrants further investigation to identify potential systemic issues impacting reimbursement timelines and MD Capital's cash flow.

---

### 📊 5. Based on the data, what are the top 3 actions we c...
**User instruction:** *"Based on the data, what are the top 3 actions we can take this week to improve our revenue cycle?"*

**Agent response:**
*   Reduce rejected claims with **Kaiser Permanente** by addressing common rejection reasons.
*   Expedite pending claims with high urgency to improve cash flow.
*   Address the most common rejection reason: "please."

STRATEGIC IMPACT: Focusing on these three actions this week will directly improve cash flow and reduce revenue leakage, positively impacting MD Capital's profitability.

---

### 📊 6. Strategic Preprocessing: Analyzing Denial Categories & Tone
**User instruction:** *"What percentage of our denials are due to 'Coding Errors' vs 'Missing Info'? Also, which insurers are the most 'Obstructive' in their communication?"*

**Agent response (Example of enhanced capability):**
*   **Coding Error denials:** represent **15.4%** of the total volume.
*   **Missing Information denials:** are the primary driver at **42.3%**.
*   **Most Obstructive Insurer:** **Aetna** shows the highest frequency of obstructive communication patterns (refusal to clarify terms, repeated documentation requests).
*   **Cooperative Partners:** **Humana** maintain a consistently cooperative tone in over **90%** of interactions.

STRATEGIC IMPACT: By identifying that **42.3%** of issues stem from "Missing Info," MD Capital can implement front-end workflow changes to ensure complete submissions, while the "Obstructive" rating for **Aetna** suggests a need for specialized legal or advocacy resources when dealing with their claims.

