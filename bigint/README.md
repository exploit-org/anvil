# anvil-bigint

Coordinates:

```text
org.exploit.anvil:bigint:0.1.2
```

Java packages:

```text
org.exploit.bigint
org.exploit.bigint.util
org.exploit.bigint.model
```

`bigint` provides a GMP-backed `BigInt` type used by the rest of Anvil for
scalar arithmetic, modular arithmetic, prime generation, and native-size integer
serialization.

## Primary API

| Type | Purpose |
| --- | --- |
| `BigInt` | Mutable native GMP integer wrapped as a Java object with arithmetic, modular arithmetic, conversion, comparison, and destruction methods. |
| `LibGMP` | Native loader for GMP. |
| `CSPRNG` | Shared `SecureRandom` provider using `SecureRandom.getInstanceStrong()` when available. |
| `PrimeNumberGenerator` | Parallel prime, Blum prime, and Blum-pair generation. |
| `BlumPair` | Pair of generated Blum primes. |

## Usage

```groovy
dependencies {
    implementation platform("org.exploit.anvil:bom:0.1.2")
    implementation "org.exploit.anvil:bigint"
}
```

```java
import org.exploit.bigint.BigInt;
import org.exploit.bigint.util.PrimeNumberGenerator;

try (var x = BigInt.valueOf(42);
     var y = BigInt.valueOf(17);
     var n = PrimeNumberGenerator.generate(256);
     var z = x.multiply(y).mod(n)) {
    byte[] encoded = z.toUnsignedByteArray(32);
}
```

## Arithmetic Surface

`BigInt` includes:

```text
add, subtract, multiply, divide, remainder
pow, modPow, modPowSec
mod, modInverse, modInverseSec
gcd, jacobi, isProbablePrime
shiftLeft, shiftRight, testBit, bitLength
modMul, modMulSec
multiExp2, multiExp2Sec, multiExp2Signed
toByteArray, toUnsignedByteArray, toJavaInt
destroy, close, isDestroyed
```

Methods with `Sec` in the name call GMP secure-operation variants or secure
helpers where the wrapper implements them.

## Runtime

`LibGMP.load()` is called by `BigInt` static initialization. The loader tries a
bundled resource path under `natives/{os}-{arch}/` first, then falls back to
`System.loadLibrary("gmp")`.

Applications that use this module through the class path should launch with:

```bash
--enable-native-access=ALL-UNNAMED
```

`BigInt` implements `Destroyable` and `AutoCloseable`. Close or destroy
temporary values that hold secret material.
