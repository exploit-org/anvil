# Threshold Signature Scheme: Threat Model

---

## 1. System Overview

This document describes the threat model for three threshold cryptographic scheme implementations designed for security-critical financial infrastructure (custody, payments, distributed signing).

### 1.1 Protocol Implementations

**FROST (Flexible Round-Optimized Schnorr Threshold Signatures)**

- RFC 9591 compliant, two-round Schnorr threshold signing.
- Ciphersuites: FROST(Ed25519, SHA-512), FROST(secp256k1, SHA-256), FROST(P-256, SHA-256).
- Bitcoin-specific variants: BIP-340 Schnorr and BIP-341 Taproot key-path spending (secp256k1 only).
- Nonce generation hedged against bad RNG via H3(random_bytes(32) ‖ SerializeScalar(sk_i)).

**GG20 (Gennaro–Goldfeder 2020 Threshold ECDSA)**

- One-round online threshold ECDSA with identifiable abort.
- Hardened with zero-knowledge proofs from CGGMP21/24.
- Paillier-based multiplicative-to-additive (MtA) sub-protocol.
- Supported curves: secp256k1, secp256r1 (P-256).

**Verifiable Threshold ElGamal Decryption**

- Non-interactive ElGamal KEM encryption; threshold decryption via Lagrange interpolation.
- Each participant produces a partial decrypt `dᵢ = [skᵢ]R` with a DLEQ proof.
- Coordinator verifies all DLEQ proofs before combining; aborts with identifiable participant index on failure.
- Supported curves: secp256k1, secp256r1 (P-256).
- KDF: HKDF-SHA-384 with domain separation; symmetric layer: AES-256-GCM or ChaCha20-Poly1305.

### 1.2 Deployment Context

- Runtime: Java 25 with the Foreign Function and Memory (FFM) API for native-backed primitives.
- Native artifacts are built from `tkeeper-org/tss4j/native` and distributed as `tss4j-natives` JAR resources under `natives/{os}-{arch}/`.
- Native loaders prefer bundled `tss4j-natives` artifacts and fall back to system libraries only when the bundled artifact for the current platform is unavailable.
- Deployments using native-backed modules must enable native access for the application modules, e.g. `--enable-native-access=ALL-UNNAMED` for unnamed-module launches.
- Participants are distributed across independent trust domains.
- Communication channels are authenticated and reliable (but not necessarily confidential).
- Threshold configuration: t-of-n where t ≥ 2.
- Target security level: 128-bit (secp256k1, P-256, Ed25519).

---

## 2. Assets

| Asset                                              | Description                                                           | Confidentiality | Integrity | Availability     |
|----------------------------------------------------|-----------------------------------------------------------------------|-----------------|-----------|------------------|
| Group signing key s                                | Shamir-shared across participants; never reconstructed in production  | CRITICAL        | CRITICAL  | HIGH             |
| Key shares x_i                                     | Per-participant secret share of s                                     | CRITICAL        | CRITICAL  | HIGH             |
| ECIES key shares sk_i                              | Per-participant share of the ECIES master decryption key              | CRITICAL        | CRITICAL  | HIGH             |
| Signing nonces (d_i, e_i / k_i, γ_i)               | Ephemeral per-session secrets                                         | CRITICAL        | CRITICAL  | N/A (single-use) |
| Paillier private keys (p, q)                       | Per-participant; used in MtA homomorphic operations (GG20 only)       | CRITICAL        | CRITICAL  | HIGH             |
| Partial decrypts d_i = [sk_i]R                     | Per-participant ECIES decryption outputs                              | LOW             | CRITICAL  | HIGH             |
| Partial signatures / signature shares              | Per-participant outputs of round two                                  | LOW             | CRITICAL  | HIGH             |
| Final aggregate signature (R, z)                   | Public output                                                         | PUBLIC          | CRITICAL  | HIGH             |
| Group public key PK                                | Public; used for verification                                         | PUBLIC          | CRITICAL  | HIGH             |
| ZK proof auxiliary data (Ring-Pedersen parameters) | Used in range proofs and factor proofs (GG20 only)                    | LOW             | CRITICAL  | HIGH             |
| Session context / AAD                              | Binds FROST/GG20 operations to a specific session; prevents replay    | LOW             | CRITICAL  | HIGH             |
| Native library artifacts                           | GMP, secp256k1, libsodium binaries loaded through Java 25 FFM         | PUBLIC          | CRITICAL  | HIGH             |

---

## 3. Trust Model and Assumptions

### 3.1 Adversary Model

- **Dishonest majority not tolerated.** Security holds if strictly fewer than t participants are corrupted.
- The Coordinator (FROST) or any single participant (GG20, ECIES) may be corrupted, but cannot compromise the signing or decryption key alone.
- Adversary is computationally bounded (PPT) under the Discrete Logarithm assumption (all protocols) and the composite residuosity / DDH assumptions (GG20).
- Adversary has full control over corrupted participants: can deviate arbitrarily from the protocol, send malformed messages, and collude.

### 3.2 Network Assumptions

- Authenticated channels between all participants (attacker cannot impersonate).
- Reliable delivery (attacker cannot selectively drop messages without detection).
- Confidentiality of channels is NOT required for protocol security but RECOMMENDED to prevent metadata leakage.

### 3.3 Cryptographic Assumptions

| Assumption                       | Protocol                                        | Basis                                |
|----------------------------------|-------------------------------------------------|--------------------------------------|
| Discrete Logarithm Problem (DLP) | FROST, GG20, ECIES                              | secp256k1, P-256, Ed25519            |
| Random Oracle Model              | FROST (H1–H5), GG20 (Fiat-Shamir), ECIES (HKDF) | SHA-512, SHA-256, SHA-384            |
| Decisional Composite Residuosity | GG20                                            | Paillier encryption                  |
| Strong RSA                       | GG20                                            | Ring-Pedersen commitments            |
| Computational Diffie-Hellman     | GG20, ECIES                                     | MtA EC-binding proof; DLEQ soundness |

---

## 4. Threat Catalog

### 4.1 Key Extraction Attacks

#### T-4.1.1: Nonce Reuse (FROST)

- **Attack:** If a participant reuses a nonce pair (d_i, e_i) across two signing sessions, an attacker can algebraically recover x_i.
- **Mitigation:** Nonces generated via H3(random_bytes(32) ‖ SerializeScalar(sk_i)) per RFC 9591 §4.1. This hedges against bad RNG by mixing fresh entropy with the secret key. Each nonce pair is bound to a unique operation ID by the embedding application.
- **Residual risk:** Negligible (2⁻¹²⁸) assuming CSPRNG provides at least 128 bits of entropy per call and no more than 2⁶⁴ signatures are produced per participant.

#### T-4.1.2: BitForge: Malicious Paillier Modulus (GG20)

- **Attack (CVE-2023-33241):** A malicious participant constructs a Paillier modulus N with small prime factors. Through repeated MtA signing sessions, the attacker extracts other participants' key shares via CRT-based recovery. Full key extraction in as few as 16 signatures.
- **Mitigation:**
    - **Paillier-Blum Modulus Proof** validates N = p·q where p ≡ q ≡ 3 (mod 4), with Jacobi symbol verification J(w, N) = −1 (addresses CVE-2025-66016).
    - **No Small Factors Proof** (CGGMP21 §C.5) proves p, q > 2²⁵⁶, parameterized with ℓ = 256 bits.
    - Both proofs verified before any MtA computation proceeds.
- **Residual risk:** Negligible under Strong RSA assumption and correct proof verification.

#### T-4.1.3: Alpha-Rays: MtA Range Proof Exploitation (GG20)

- **Attack:** Attacker selects adversarial k_i values near N in MtA, causing information leakage about peer shares through the range proof gap.
- **Mitigation:**
    - Range proof with β-parameter q² on prover side, verified against q³ bound.
    - EC-point binding in MtAwc (LAGRANGE path): respondent proves that b_j corresponds to dlog(W_j = [λ_j]Y_j) via G·s₁ = V_ec + [e]W_j in the respondent proof.
    - Paillier key size validated: N ≥ q⁸.
- **Residual risk:** Low. Full Π_{aff-g} style proof (CGGMP21) provides tighter binding; current construction provides equivalent security for the LAGRANGE path through the integrated EC check.

#### T-4.1.4: Presignature + Raw Signing Forgery (GG20)

- **Attack (CVE-2025-66017):** When presignatures (precomputed R) are combined with raw signing, an attacker who knows R can craft a substitute hash h' and transform the resulting signature into a valid signature for an arbitrary message.
- **Mitigation:** Architecture does not use presignatures. All signing sessions execute the full interactive protocol where R is computed fresh. API does not expose a presignature mode.
- **Residual risk:** None: attack vector does not exist in current architecture.

#### T-4.1.5: Invalid DLEQ Proof in Partial Decryption (ECIES)

- **Attack:** Malicious participant submits a crafted `dᵢ = [skᵢ']R` with a forged or omitted DLEQ proof, biasing the reconstructed shared secret S and either corrupting decryption or leaking information about honest shares via the Lagrange combination.
- **Mitigation:** Coordinator verifies DLEQ proof for every partial decrypt before combining: checks `[r]G = A₁ + [e]Yᵢ` and `[r]R = A₂ + [e]dᵢ` with a Fiat-Shamir challenge. Any failure raises `IdentifiableAbortException(idx)`. `Yᵢ` must be derived from DKG transcript, not from the incoming message.
- **Residual risk:** Negligible under DLP assumption. Dependent on correct `Yᵢ` sourcing: see operational recommendations.

### 4.2 Signature Forgery Attacks

#### T-4.2.1: Share Substitution in MtA (GG20)

- **Attack:** Malicious respondent in MtAwc substitutes an arbitrary value for b_j instead of their true Lagrange-weighted share w_j = λ_j · x_j. Without EC-point binding, the initiator cannot detect this substitution.
- **Mitigation:** Respondent proof includes EC commitment V_ec = [α]G. Verifier checks [s₁]G = V_ec + [e]W_j where W_j = [λ_j]Y_j is computed independently from group info established during DKG. Prover cannot satisfy this equation without knowledge of dlog(W_j).
- **Residual risk:** Negligible under CDH assumption.

#### T-4.2.2: Rogue Commitment in FROST

- **Attack:** Malicious participant crafts commitment (D_i, E_i) as a function of other participants' commitments to bias the aggregate nonce R, potentially enabling forgery.
- **Mitigation:** FROST's binding factor mechanism (RFC 9591 §4.4) computes per-participant binding factors ρ_i = H1(group_pk ‖ H4(msg) ‖ H5(commitment_list) ‖ SerializeScalar(i)). The commitment list is hashed before binding factors are derived, preventing adaptive commitment selection. Commitment list is sorted and deterministic.
- **Residual risk:** None under Random Oracle Model.

### 4.3 Denial of Service / Protocol Disruption

#### T-4.3.1: Malformed Signature Shares

- **Attack:** Corrupted participant produces invalid signature share to cause signature verification failure.
- **Mitigation:**
    - **FROST:** Coordinator verifies each signature share via verify_signature_share (RFC 9591 §5.3): [z_i]G = comm_share_i + [c·λ_i]Y_i.
    - **GG20:** Identifiable abort via delta/sigma commitment verification and Lagrange product consistency check (`assertLambdaProductMatchesDelta`).
- **Residual risk:** DoS is possible (misbehaving participant identified and excluded), but no security compromise.

#### T-4.3.2: GAMMA MtA Response Manipulation (GG20)

- **Attack:** Malicious respondent in MtA(k, γ) sends c_j = Enc(0) instead of the correctly computed ciphertext. Initiator computes incorrect α, leading to an invalid signature.
- **Mitigation:** By design per GG20: γ is ephemeral and MtA(k, γ) does not require MtAwc. Invalid response detected at signature aggregation via delta consistency check. Misbehaving participant identified through identifiable abort.
- **Residual risk:** DoS only; no key material exposure.

#### T-4.3.3: Invalid Partial Decrypt in ECIES

- **Attack:** Malicious participant submits a partial decrypt with an invalid DLEQ proof to abort decryption without revealing their key share.
- **Mitigation:** Identifiable abort: `IdentifiableAbortException` exposes the participant index. Coordinator can retry with a different quorum excluding the identified participant.
- **Residual risk:** DoS possible with any single corrupted participant in a threshold-1-of-n setup. Mitigated by quorum redundancy (n > t).

### 4.4 Side-Channel Attacks

#### T-4.4.1: Timing Leakage on Secret Operations

- **Attack:** Variable-time scalar multiplication or modular exponentiation leaks bits of secret values through timing observations.
- **Mitigation:**
    - Secret-dependent modular exponentiations use `modPowSec` (GMP `mpz_powm_sec`).
    - Secret-dependent multiplications use `multiplySec` (GMP `mpn_sec_mul`).
    - Paillier decryption and CRT operations use constant-time primitives.
    - FROST scalar serialization avoids data-dependent branching.
- **Residual risk:** Implementation-dependent. Underlying GMP library operations should be audited for constant-time guarantees on deployment platform.

#### T-4.4.2: Native Library Substitution / FFM Boundary Abuse

- **Attack:** Attacker influences the native library selected at runtime, tampers with bundled native resources, or exploits an ABI/signature mismatch across the Java 25 FFM boundary.
- **Mitigation:**
    - Native libraries are built in the controlled `tkeeper-org/tss4j/native` pipeline and packaged as `tss4j-natives` resources.
    - Runtime loading prefers bundled `tss4j-natives` artifacts; system library fallback is only acceptable when the bundled artifact is absent and the deployment explicitly trusts the host library path.
    - Application classpath/module path is trusted and not attacker-writable.
    - FFM downcall bindings are generated and version-pinned against the native headers used by the bundled artifacts.
    - Deployments record the resolved native library name/path at startup for auditability.
- **Residual risk:** Medium operational risk. Native artifact integrity, classpath integrity, and runtime flags are deployment responsibilities.

## 5. Zero-Knowledge Proof Inventory

### 5.1 GG20 Proof Suite

| Proof                                                | Purpose                                                      | Generator                          | Verifier                           | Security Property                                                         |
|------------------------------------------------------|--------------------------------------------------------------|------------------------------------|------------------------------------|---------------------------------------------------------------------------|
| Paillier-Blum Modulus (Π_{mod})                      | N is a Blum integer (p·q, both ≡ 3 mod 4)                    | `BiPrimeProver`                    | `BiPrimeVerifier`                  | Soundness: malicious prover cannot forge for composite N with > 2 factors |
| No Small Factors (Π_{fac})                           | p, q have no small prime factors under CGGMP parameters      | `NoSmallFactorProver`              | `NoSmallFactorVerifier`            | Prevents BitForge-class key extraction via MtA                            |
| Paillier Range Proof (Π_{range})                     | MtA plaintext witness is in the allowed protocol range       | `PaillierRangeProver`              | `PaillierRangeVerifier`            | Prevents over-sized MtA inputs; binds to exact ciphertext                 |
| Paillier Respondent Proof (Π_{resp}) with EC binding | Correct MtA homomorphic evaluation AND b_j = dlog(W_j)       | `PaillierRespondentProver`         | `PaillierRespondentVerifier`       | Prevents share substitution; binds ciphertext to EC public key            |

### 5.2 ECIES / Threshold Decryption Proof Suite

| Proof                | Purpose                                                                                 | Generator                     | Verifier                      | Security Property                                                |
|----------------------|-----------------------------------------------------------------------------------------|-------------------------------|-------------------------------|------------------------------------------------------------------|
| DLEQ Proof           | Proves dᵢ = [skᵢ]R and Yᵢ = [skᵢ]G (same skᵢ) without revealing skᵢ                     | `DleqProver`                  | `DleqVerifier`                | Soundness under DLP; prevents invalid partial decrypt submission |
| Chaum-Pedersen Proof | Proves knowledge of x such that T = [x]G + [t]H (used in ZK setup / commitment binding) | `ChaumPedersenProver`         | `ChaumPedersenVerifier`       | Sigma protocol with Fiat-Shamir; soundness under DLP             |

### 5.3 FROST Hash Functions (RFC 9591)

| Function | Ed25519 Instantiation                             | secp256k1 / P-256 Instantiation   | Purpose                                    |
|----------|---------------------------------------------------|-----------------------------------|--------------------------------------------|
| H1       | SHA-512(ctx ‖ "rho" ‖ m) mod q                    | hash_to_field(m, DST=ctx‖"rho")   | Binding factor derivation                  |
| H2       | SHA-512(m) mod q (no domain sep: RFC 8032 compat) | hash_to_field(m, DST=ctx‖"chal")  | Signature challenge                        |
| H3       | SHA-512(ctx ‖ "nonce" ‖ m) mod q                  | hash_to_field(m, DST=ctx‖"nonce") | Hedged nonce generation                    |
| H4       | SHA-512(ctx ‖ "msg" ‖ m)                          | SHA-256(ctx ‖ "msg" ‖ m)          | Message pre-hashing for binding factor     |
| H5       | SHA-512(ctx ‖ "com" ‖ m)                          | SHA-256(ctx ‖ "com" ‖ m)          | Commitment list hashing for binding factor |

---

## 6. Known Vulnerabilities Addressed

| CVE / Reference                   | Description                                                         | Status    | Mitigation                                                   |
|-----------------------------------|---------------------------------------------------------------------|-----------|--------------------------------------------------------------|
| CVE-2023-33241 (BitForge)         | GG18/GG20 Paillier key with small factors enables key extraction    | MITIGATED | Π_{mod} + Π_{fac} proofs                                     |
| CVE-2025-66016                    | Missing J(w,N)=−1 check in Paillier-Blum proof allows proof forgery | MITIGATED | Jacobi symbol check in `BiPrimeVerifier.basicChecks()` |
| Alpha-Rays (2021/1621)            | MtA range proof exploitation for key share bit leakage              | MITIGATED | Range proofs + EC-point binding in MtAwc                     |
| Nonce reuse / deterministic nonce | Multi-party nonce reuse enables full key recovery                   | MITIGATED | H3-hedged nonce generation per RFC 9591                      |

---

## 7. Protocol-Specific Security Properties

### 7.1 FROST

| Property                             | Guarantee                                        | Condition                            |
|--------------------------------------|--------------------------------------------------|--------------------------------------|
| Existential Unforgeability (EUF-CMA) | Adversary cannot forge signatures                | < t participants corrupted           |
| Robustness                           | NOT provided (by design)                         | Misbehaving participant causes abort |
| Identifiable Abort                   | Coordinator can identify misbehaving participant | Authenticated channel                |
| Non-deterministic Nonces             | Required for multi-party security                | H3 hedging + CSPRNG                  |
| BIP-340/341 Compatibility            | Schnorr/Taproot signatures verifiable on Bitcoin | secp256k1 BIP schemes only           |

### 7.2 GG20

| Property                             | Guarantee                                                 | Condition                                                        |
|--------------------------------------|-----------------------------------------------------------|------------------------------------------------------------------|
| Existential Unforgeability (EUF-CMA) | Adversary cannot forge signatures                         | < t participants corrupted; Paillier keys validated              |
| Identifiable Abort                   | Misbehaving participant identified via share verification | All ZK proofs verified                                           |
| UC Security                          | NOT provided (standalone model)                           | Sequential composition safe; parallel requires session isolation |

### 7.3 Threshold ECIES

| Property                      | Guarantee                                                                             | Condition                                                          |
|-------------------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| IND-CCA2 (encryption)         | Ciphertext indistinguishable under chosen-ciphertext attack                           | HKDF domain separation; AEAD tag verification                      |
| Verifiable Partial Decryption | Each dᵢ is provably correct before combination                                        | All DLEQ proofs verified; Yᵢ sourced from authenticated DKG output |
| Identifiable Abort            | Faulty participant index exposed on DLEQ failure                                      | Authenticated channel                                              |
| Long-term Key Compromise      | Past ciphertexts remain safe only while fewer than t ECIES key shares are compromised | Threshold decryption key remains below threshold                   |


## 8. Limitations and Future Work

1. **GG20 UC Security:** Current implementation is proven secure in the standalone model. Migration to CGGMP24-style UC-secure protocol is planned to support safe parallel execution.
2. **Post-Quantum:** FROST, GG20, and Threshold ECIES all rely on DLP/CDH hardness. We already work on threshold post-quantum signature schemes, first ML-DSA is in our roadmap.
3. **Constant-Time Guarantees:** While secret-dependent operations use `*Sec` variants, a formal audit of the underlying native (GMP) library for constant-time behavior on all target platforms is recommended.
