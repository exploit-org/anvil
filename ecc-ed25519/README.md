# anvil-ecc-ed25519

Coordinates:

```text
org.exploit.anvil:ecc-ed25519:0.1.0
```

Java package:

```text
org.exploit.ecc.ed25519
```

`ecc-ed25519` provides Ed25519 key generation, public-key derivation, point
operations, EdDSA signatures, and direct libsodium-backed Ed25519 operations.

## Primary API

| Area | Types |
| --- | --- |
| Low-level Ed25519 | `Ed25519` |
| Keys | `Ed25519KeyFactory`, `Ed25519PrivateKey`, `Ed25519PublicKey`, `Ed25519KeyPair` |
| Curve and points | `Ed25519CurveParams`, `Ed25519PointOps` |
| Signatures | `Ed25519Signer`, `Ed25519Verifier`, `Ed25519Signature` |
| Scalars | `Ed25519Clamp` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.1.0")
    implementation "org.exploit.anvil:ecc-ed25519"
}
```

```java
import org.exploit.ecc.ed25519.factory.Ed25519KeyFactory;
import org.exploit.ecc.ed25519.signer.Ed25519Signer;
import org.exploit.ecc.ed25519.signer.Ed25519Verifier;

var keys = new Ed25519KeyFactory().generate();
var signer = new Ed25519Signer();
var verifier = new Ed25519Verifier();

byte[] message = "message".getBytes(java.nio.charset.StandardCharsets.UTF_8);
var signature = signer.sign(message, keys.privateKey());
boolean ok = verifier.verify(message, signature, keys.publicKey());
```

## Encoding

`Ed25519PrivateKey` stores a 32-byte seed. Public keys and points encode to
32-byte Ed25519 compressed point bytes. `Ed25519Signature.encode()` returns the
64-byte Ed25519 signature form.

## Runtime

The module uses libsodium through Java FFM bindings. The loader tries
`System.loadLibrary("sodium")`, `System.loadLibrary("libsodium")`, and then a
bundled `natives/{os}-{arch}/` resource if present.

Applications that use this module through the class path should launch with:

```bash
--enable-native-access=ALL-UNNAMED
```
