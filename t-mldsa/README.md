# anvil-t-mldsa

Coordinates:

```text
org.exploit.anvil:t-mldsa:0.1.2
```

Java package:

```text
org.exploit.mldsa
```

`t-mldsa` contains ML-DSA key, signature, signing, verification, and threshold
ML-DSA protocol utilities. Plain ML-DSA keys and signatures implement the
protocol-agnostic `crypto-spi` asymmetric contracts.

## Primary API

| Area | Types |
| --- | --- |
| Parameters | `MLDSAParameters`, `ThresholdMLDSAParameters` |
| Plain keys | `MLDSAKeyFactory`, `MLDSAKeyPair`, `MLDSAPrivateKey`, `MLDSAPublicKey` |
| Plain signing | `MLDSASigner`, `MLDSAVerifier`, `MLDSASignature` |
| Threshold keys | `ThresholdMLDSAKeyGen`, `ThresholdMLDSAKeyGenerator`, `ThresholdKeyPair`, `ThresholdPartyKey`, `ThresholdPublicKey` |
| Threshold signing | `ThresholdMLDSAClient`, `ThresholdMLDSACoordinator`, `ThresholdSigning`, `ThresholdCombine`, `ThresholdVerify` |
| Protocol storage | `ThresholdMLDSAContext`, `RoundStore`, `InMemoryRoundStore`, `ThresholdSignatureContext`, `InMemoryThresholdSignatureContext` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.1.2")
    implementation "org.exploit.anvil:t-mldsa"
}
```

```java
import org.exploit.mldsa.constant.MLDSAParameters;
import org.exploit.mldsa.factory.MLDSAKeyFactory;
import org.exploit.mldsa.signer.MLDSASigner;
import org.exploit.mldsa.signer.MLDSAVerifier;

var factory = new MLDSAKeyFactory(MLDSAParameters.ML_DSA_44);
var keyPair = factory.generate();

var signature = new MLDSASigner().sign(message, keyPair.privateKey());
var ok = new MLDSAVerifier().verify(message, signature, keyPair.publicKey());
```

## Integration Model

Threshold ML-DSA is interactive. The module exposes Java protocol messages and
state holders, but does not define networking or durable storage.

For threshold signing, each party runs a `ThresholdMLDSAClient` with a
party-local `RoundStore`. The store contains ephemeral signing state between
rounds and can be replaced by a backend implementation. The signing coordinator
uses `ThresholdSignatureContext` to collect commitments, reveals, and partial
signatures; `InMemoryThresholdSignatureContext` is only the default local
implementation. `ThresholdMLDSAContext` groups these storage interfaces for
integrations that prefer a single context object.

Signing sessions support additional authenticated data through `aad`
(`additionalContext`/`ctx` are aliases for the same byte string). The AAD is the
ML-DSA context byte string used during signing and verification, so all parties
and the coordinator must use the same value.

Session-owned objects are destroyable. `ThresholdMLDSAClient`,
`ThresholdMLDSACoordinator`, `ThresholdMLDSAContext`, `RoundStore`, and
`ThresholdSignatureContext` clear their transient state on `destroy()`. Long
lived keys such as `ThresholdPartyKey` are destroyable separately and are not
destroyed implicitly when a signing session is closed.

For DKG, `ThresholdMLDSAKeyGenerator` is a stateful per-party DKG participant.
It returns explicit transport values (`Round1Broadcast`, `DirectMessage`,
`Round2Output`, `Round3Output`, `Round4Output`, `DkgResult`) and expects the
backend to route broadcast and direct messages. The generator keeps secret
per-party state locally across DKG rounds; backend integrations should persist
or pin that participant state according to their own session model.

Plain ML-DSA signing and verification use Bouncy Castle's ML-DSA primitives
with Anvil-owned key and signature value types. `MLDSAParameters` also exposes
Java 25 `NamedParameterSpec` constants for integrations that use JCA surfaces.

## Dependencies

This module depends on `crypto-spi` and Bouncy Castle `bcprov-jdk18on`.
