# anvil-t-ecdsa

Coordinates:

```text
org.exploit.anvil:t-ecdsa:0.3.1
```

Java package:

```text
org.exploit.tss.gg20
```

`t-ecdsa` contains the GG20 threshold ECDSA client and supporting protocol
components: MtA runners, commitments, Chaum-Pedersen proof handling, integrity
checks, partial signature calculation, and signature aggregation.

## Primary API

| Area | Types |
| --- | --- |
| Client | `GG20Client` |
| Context | `GG20Context`, `CryptoContext`, `InitContext`, `MtAContext`, `SignatureContext`, `IntegrityContext`, `SignatureAggregatorContext` |
| In-memory contexts | `InMemoryCryptoContext`, `InMemoryInitContext`, `InMemoryMtAInitiatorContext`, `InMemoryMtARespondentContext`, `InMemorySignatureContext`, `InMemoryIntegrityContext`, `InMemoryAggregatorContext` |
| Commitments | `GG20CommitmentGenerator`, `CommitmentResult`, `GammaCommitment`, `ChaumPedersenCommitment`, `ChaumPedersenCommitmentWithValue` |
| MtA | `MtAProtocolRunner`, `MtAInitiatorProtocolRunner`, `MtARespondentProtocolRunner`, `MtAResponse` |
| Signing | `PartialSignatureCalculator`, `SignaturePartAggregator`, `SignatureBuilder` |
| Integrity | `IntegrityChecker`, `IdentifiableAbortException` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.3.1")
    implementation "org.exploit.anvil:t-ecdsa"
    implementation "org.exploit.anvil:ecc-secp256k1"
}
```

```java
import org.exploit.tss.gg20.GG20Client;

try (var client = new GG20Client<>(
    executor,
    context,
    commitmentGenerator,
    signatureBuilder
)) {
    client.init();
    var mta = client.mta();
    var partial = client.signature().computePartialS();
    var signature = client.aggregator().calculateSignature();
}
```

## Integration Model

The module exposes protocol state through context interfaces and Java model
types. It does not define a network transport. Integrations are expected to
persist and exchange the message objects required by each GG20 phase.

`IdentifiableAbortException` carries a participant id for aborts where the
code can identify the peer.

When a phase needs both respondent operations, use
`client.mta().asRespondent().respond(initiatorId, publicKey, message)`.
It verifies the initiator's range, BiPrime, and NoSmallFactor proofs once for
this request, then returns `MtAResponse.gamma()` and `MtAResponse.lagrange()`.
Each operation generates its own mask and encryption randomness. The additive
shares are stored together only after both operations succeed. Verification
results are not cached between requests.

The existing `compute(type, initiatorId, publicKey, message)` API still verifies
each request independently. Custom `MtARespondentContext` implementations must
implement atomic `storeShares` to use `respond`; its default implementation
rejects the operation without storing shares.

The default in-memory crypto context generates local auxiliary CRT secrets for
incoming proof verification. Only `crypto().zkSetup()` is exchanged with peers;
`crypto().zkSetupSecrets()` must remain local and must never be serialized.
An explicitly supplied public-only `ZKSetup` continues to work without CRT.

After all MtA responses have been produced and all received GAMMA/LAGRANGE
results have been verified and stored, stop accepting MtA work and call
`client.context().crypto().destroyZKSetupSecrets()`. This destroys the native
factor/inverse buffers while preserving the public setup. The call waits for
active CRT operations. `client.close()` also destroys these secrets on success,
abort, or timeout. Borrowed CRT verifiers reject use after destruction.

For TKeeper, the coordinator completes the MtA round before collecting the
offline phase. The early-erasure call belongs immediately after
`GG20OfflinePhaseHandler.broadcast` enters the offline phase, once that MtA
round has completed successfully. Do not erase on the first received MtA result
or an incoming offline message: other MtA calls may still be active.

## Dependencies

This module depends on `ecc-spi`, `paillier`, `bigint`, and `zk-dlog`.
Concrete curve support is supplied by curve modules such as `ecc-secp256k1` or
`ecc-p256`.
