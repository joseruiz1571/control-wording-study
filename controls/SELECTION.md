# Phase 2 control selection (40 bases)

Official NIST SP 800-53 Rev 5 statements (v0) with four meaning-preserving paraphrases each.
All 40 use mlassure patterns `synthesis`, `sufficiency`, or `correlation` only.
SC-28 and SC-7 (deterministic, code-keyed) and attestation controls are excluded.

## Counts by family

- **AC**: 8
- **AU**: 7
- **CM**: 8
- **RA**: 2
- **SA**: 5
- **SI**: 7
- **SC**: 2
- **CA**: 1

## Counts by vocab_pattern (tagged on v0, copied to all variants)

- **vague-qualifier**: 4
- **specific**: 23
- **mixed**: 13

## Counts by mlassure_pattern

- **synthesis**: 12
- **sufficiency**: 18
- **correlation**: 10

## Bases

### AC-3 — Access Enforcement

- **vocab_pattern:** mixed
- **mlassure_pattern:** sufficiency
- **collectors:** getEndpointExecutionRole
- **ml_reason:** The endpoint execution-role policy statements are the logical-access rules the fixture exposes for the deployed model.

### AC-2(7) — Account Management | Privileged User Accounts

- **vocab_pattern:** mixed
- **mlassure_pattern:** synthesis
- **collectors:** getEndpointExecutionRole | getCloudTrailEvents
- **ml_reason:** The generic SageMaker execution role plus CloudTrail identities show how privileged endpoint accounts are administered, monitored, and revoked.

### AC-5 — Separation of Duties

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getEndpointExecutionRole
- **ml_reason:** A single generic execution role holding both s3:* and sagemaker:* is the fixture's evidence of whether duties are separated in access authorizations.

### AC-6 — Least Privilege

- **vocab_pattern:** vague-qualifier
- **mlassure_pattern:** sufficiency
- **collectors:** getEndpointExecutionRole
- **ml_reason:** Overly broad s3:* and sagemaker:* statements on the endpoint role are the fixture's least-privilege evidence.

### AC-6(5) — Least Privilege | Privileged Accounts

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getEndpointExecutionRole
- **ml_reason:** The endpoint's attached IAM role is the privileged account the fixture exposes for the running model.

### AC-6(7) — Least Privilege | Review of User Privileges

- **vocab_pattern:** mixed
- **mlassure_pattern:** sufficiency
- **collectors:** getEndpointExecutionRole
- **ml_reason:** The fixture's role policy document is what an assessor can review to validate whether assigned privileges remain necessary.

### AC-6(9) — Least Privilege | Log Use of Privileged Functions

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getCloudTrailEvents
- **ml_reason:** CloudTrail CreateEndpoint and UpdateEndpoint records are the fixture's log of privileged endpoint operations.

### AC-6(10) — Least Privilege | Prohibit Non-privileged Users from Executing Privileged Functions

- **vocab_pattern:** specific
- **mlassure_pattern:** synthesis
- **collectors:** getEndpointExecutionRole | getCloudTrailEvents
- **ml_reason:** Role actions plus CloudTrail user identities show whether non-privileged actors can run privileged endpoint functions.

### AU-2 — Event Logging

- **vocab_pattern:** mixed
- **mlassure_pattern:** sufficiency
- **collectors:** getCloudTrailEvents
- **ml_reason:** The CloudTrail event set is what the fixture can log for this endpoint; an assessor can judge whether those event types are identified, selected, and adequate.

### AU-3 — Content of Audit Records

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getCloudTrailEvents
- **ml_reason:** Each CloudTrail record carries event name, time, user identity, and request parameters that an assessor can check against required audit-record content.

### AU-6 — Audit Record Review, Analysis, and Reporting

- **vocab_pattern:** mixed
- **mlassure_pattern:** synthesis
- **collectors:** getCloudTrailEvents | getModelMonitorSchedules
- **ml_reason:** CloudTrail plus failed monitor runs are the fixture's audit-like records an assessor can review for unusual activity and impact.

### AU-6(3) — Audit Record Review, Analysis, and Reporting | Correlate Audit Record Repositories

- **vocab_pattern:** specific
- **mlassure_pattern:** correlation
- **collectors:** getCloudTrailEvents | getModelMonitorSchedules
- **ml_reason:** CloudTrail and model-monitor histories are distinct record stores the fixture can correlate for endpoint situational awareness.

### AU-8 — Time Stamps

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getCloudTrailEvents
- **ml_reason:** CloudTrail eventTime values (UTC) are the fixture's audit time stamps.

### AU-12 — Audit Record Generation

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getCloudTrailEvents
- **ml_reason:** CloudTrail on this endpoint is the fixture's audit-record generation capability for deploy and change events.

### AU-12(1) — Audit Record Generation | System-wide and Time-correlated Audit Trail

- **vocab_pattern:** specific
- **mlassure_pattern:** correlation
- **collectors:** getCloudTrailEvents | getModelRegistryEntry
- **ml_reason:** Registry timestamps and CloudTrail event times can be compiled into a time-correlated trail of approval versus deploy.

### CM-2 — Baseline Configuration

- **vocab_pattern:** mixed
- **mlassure_pattern:** synthesis
- **collectors:** getModelRegistryEntry | getEndpointConfig
- **ml_reason:** The registry package version plus endpoint configuration are the fixture's current baseline of what is deployed.

### CM-3 — Configuration Change Control

- **vocab_pattern:** specific
- **mlassure_pattern:** correlation
- **collectors:** getCloudTrailEvents | getModelRegistryEntry
- **ml_reason:** CloudTrail deploys versus registry approval time show whether configuration-controlled model changes were reviewed, approved, recorded, and implemented in order.

### CM-3(1) — Configuration Change Control | Automated Documentation, Notification, and Prohibition of Changes

- **vocab_pattern:** specific
- **mlassure_pattern:** correlation
- **collectors:** getCloudTrailEvents | getModelRegistryEntry
- **ml_reason:** Registry approval status versus CloudTrail UpdateEndpoint/CreateEndpoint times show whether automated change records, approval, and prohibition-until-approval held.

### CM-3(2) — Configuration Change Control | Testing, Validation, and Documentation of Changes

- **vocab_pattern:** specific
- **mlassure_pattern:** correlation
- **collectors:** getCloudTrailEvents | getModelRegistryEntry
- **ml_reason:** A hotfix UpdateEndpoint with no matching registry entry is the fixture's signal that a change was finalized without documented validation.

### CM-6 — Configuration Settings

- **vocab_pattern:** mixed
- **mlassure_pattern:** synthesis
- **collectors:** getEndpointConfig | getEndpointNetworkConfig | getKMSConfig
- **ml_reason:** Endpoint, network isolation, and KMS settings are the fixture's implemented configuration of the running model service.

### CM-7(1) — Least Functionality | Periodic Review

- **vocab_pattern:** mixed
- **mlassure_pattern:** synthesis
- **collectors:** getEndpointConfig | getEndpointExecutionRole | getEndpointNetworkConfig
- **ml_reason:** Instance type, broad IAM actions, and absent VPC/isolation are the fixture's running functions, services, and network posture to review as unnecessary or nonsecure.

### CM-8 — System Component Inventory

- **vocab_pattern:** mixed
- **mlassure_pattern:** synthesis
- **collectors:** getModelRegistryEntry | getEndpointConfig
- **ml_reason:** Registry package identity and the named endpoint/instance are the fixture's inventory of this model's deployed components.

### CM-8(1) — System Component Inventory | Updates During Installation and Removal

- **vocab_pattern:** specific
- **mlassure_pattern:** correlation
- **collectors:** getModelRegistryEntry | getCloudTrailEvents
- **ml_reason:** An UpdateEndpoint hotfix with no matching registry version is the fixture's missed inventory update on a system change.

### RA-3 — Risk Assessment

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getModelCard
- **ml_reason:** getModelCard is the only collector that could return a documented risk assessment for this model; the frozen fixture returns null, which the LLM can treat as absence or as a gap.

### RA-7 — Risk Response

- **vocab_pattern:** vague-qualifier
- **mlassure_pattern:** synthesis
- **collectors:** getModelMonitorSchedules | getCloudTrailEvents
- **ml_reason:** A failed data-quality monitor and an undocumented hotfix are findings from monitoring and change records; the fixture shows no linked response.

### SA-10 — Developer Configuration Management

- **vocab_pattern:** specific
- **mlassure_pattern:** correlation
- **collectors:** getCloudTrailEvents | getModelRegistryEntry
- **ml_reason:** Registry approval versus CloudTrail deploys (including a hotfix with no package) show whether only organization-approved, documented model changes were implemented.

### SA-10(5) — Developer Configuration Management | Mapping Integrity for Version Control

- **vocab_pattern:** specific
- **mlassure_pattern:** correlation
- **collectors:** getModelRegistryEntry | getCloudTrailEvents
- **ml_reason:** Registry modelPackageVersion versus the hotfix endpointConfigName tests whether the deployed version still maps to the master package record.

### SA-8(32) — Security and Privacy Engineering Principles | Sufficient Documentation

- **vocab_pattern:** vague-qualifier
- **mlassure_pattern:** sufficiency
- **collectors:** getModelCard
- **ml_reason:** The model card is the only documentation artifact the collectors can retrieve for this endpoint; the frozen fixture has none.

### SA-4(8) — Acquisition Process | Continuous Monitoring Plan for Controls

- **vocab_pattern:** mixed
- **mlassure_pattern:** sufficiency
- **collectors:** getModelMonitorSchedules
- **ml_reason:** Configured model-monitor schedules are the fixture's only continuous-monitoring plan evidence for this endpoint.

### SA-11 — Developer Testing and Evaluation

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getModelMonitorSchedules
- **ml_reason:** Monitor type, schedule, last-run status, and failure reason are the fixture's post-design testing and evaluation evidence for the deployed model.

### SI-2 — Flaw Remediation

- **vocab_pattern:** specific
- **mlassure_pattern:** correlation
- **collectors:** getCloudTrailEvents | getModelRegistryEntry
- **ml_reason:** The undocumented hotfix deploy is the fixture's flaw-remediation change; registry absence tests whether it entered configuration management.

### SI-2(2) — Flaw Remediation | Automated Flaw Remediation Status

- **vocab_pattern:** mixed
- **mlassure_pattern:** synthesis
- **collectors:** getModelRegistryEntry | getCloudTrailEvents
- **ml_reason:** Registry version versus CloudTrail endpoint-config names are the automated signals of whether the deployed component matches the current package.

### SI-4 — System Monitoring

- **vocab_pattern:** mixed
- **mlassure_pattern:** synthesis
- **collectors:** getDataCaptureConfig | getModelMonitorSchedules | getEndpointNetworkConfig
- **ml_reason:** Disabled data capture, a failed DataQuality monitor, and no VPC/isolation are the fixture's system-monitoring and unauthorized-connection signals.

### SI-4(2) — System Monitoring | Automated Tools and Mechanisms for Real-time Analysis

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getModelMonitorSchedules
- **ml_reason:** The weekly cron DataQuality schedule (and its failed last run) is the fixture's automated analysis mechanism, which an assessor can judge against near real-time.

### SI-6 — Security and Privacy Function Verification

- **vocab_pattern:** mixed
- **mlassure_pattern:** synthesis
- **collectors:** getModelMonitorSchedules | getDataCaptureConfig
- **ml_reason:** A scheduled monitor whose last run failed because capture is disabled is verification of a security/quality function, with no evidence of the required alert or follow-up action.

### SI-7 — Software, Firmware, and Information Integrity

- **vocab_pattern:** specific
- **mlassure_pattern:** correlation
- **collectors:** getModelRegistryEntry | getCloudTrailEvents
- **ml_reason:** A hotfix endpoint config with no registry package is an unauthorized change to deployed model software relative to the approved version.

### SI-12 — Information Management and Retention

- **vocab_pattern:** vague-qualifier
- **mlassure_pattern:** sufficiency
- **collectors:** getDataCaptureConfig
- **ml_reason:** Data-capture enablement, percentage, and destination are the fixture's handling of inference information the endpoint could retain.

### SC-28(1) — Protection of Information at Rest | Cryptographic Protection

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getKMSConfig
- **ml_reason:** volumeKmsKeyId, artifactKmsKeyId, and keyManager are the fixture's cryptographic protection of model artifacts and endpoint volumes at rest. Not SC-28 (deterministic).

### SC-7(5) — Boundary Protection | Deny by Default — Allow by Exception

- **vocab_pattern:** specific
- **mlassure_pattern:** sufficiency
- **collectors:** getEndpointNetworkConfig
- **ml_reason:** Empty security groups, no VPC, and isolation disabled are the fixture's boundary posture (deny-by-default cannot hold). Not SC-7 (deterministic).

### CA-7 — Continuous Monitoring

- **vocab_pattern:** specific
- **mlassure_pattern:** synthesis
- **collectors:** getModelMonitorSchedules | getDataCaptureConfig
- **ml_reason:** Monitor metrics, cron frequency, last-run failure, and disabled capture are the fixture's system-level continuous monitoring program for this endpoint.
