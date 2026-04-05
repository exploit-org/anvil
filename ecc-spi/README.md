# anvil-ecc-spi

Coordinates:

```text
org.exploit.anvil:ecc-spi:0.1.0
```

Java packages:

```text
org.exploit.ecc.spi
org.exploit.ecc.util
```

`ecc-spi` defines the common elliptic-curve interfaces shared by curve modules,
threshold protocols, and zero-knowledge proof modules.

## Primary API

| Area | Types |
| --- | --- |
| Keys | `ECKey`, `ECPrivateKey`, `ECPublicKey`, `ECKeyPair`, `ECKeyFactory` |
| Curves | `EllipticCurveParams`, `RecoverableCurveParams`, `WeierstrassCurveParams` |
| Points | `PointOps`, `WeierstrassPointOps`, `AffinePointView`, `FpPoint` |
| Signatures | `ECSignature`, `ECDSASignature`, `RecoverableSignature`, `SchnorrSignature`, `EdDSASignature` |
| Signing | `ECSigner`, `ECVerifier` |
| Mapping | `HashToCurve`, `ExpandMessageXmd` |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.1.0")
    implementation "org.exploit.anvil:ecc-spi"
}
```

```java
import org.exploit.ecc.spi.point.PointOps;
import org.exploit.ecc.spi.params.EllipticCurveParams;

static <P extends PointOps<P>> P multiplyBase(EllipticCurveParams<P> curve, org.exploit.bigint.BigInt k) {
    return curve.getG().mul(k);
}
```

## Contracts

`PointOps` exposes immutable-style point operations:

```text
add, dbl, mul, sub, normalize, negate, isValid, encode
```

Private keys implement `Destroyable`. Concrete modules decide how scalar bytes,
point encodings, signatures, and hash-to-curve suites are represented.
