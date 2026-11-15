#!/usr/bin/env python3
# language: Python 3, file: ruche_pow.py, target: macOS
# La Ruche - minage PoW reel : recherche de nonce SHA-256 sous une difficulte
# Usage: python3 ruche_pow.py [difficulte_bits]  (defaut 20 - ajustable)
import hashlib, time, sys, os

def mine(bits):
    target = 2 ** (256 - bits)
    print(f"  difficulte : {bits} bits (hash < 2^-{bits})")
    print("  Ctrl+C pour stopper la ruche\n")
    block = 0
    total_hashes = 0
    try:
        while True:
            block += 1
            prefix = f"HIVE-BLOCK-{block}-{time.time():.0f}"
            n = 0
            t0 = time.time()
            h0 = t0
            while True:
                h = int(hashlib.sha256(f"{prefix}{n}".encode()).hexdigest(), 16)
                n += 1
                total_hashes += 1
                if h < target: break
            dt = time.time() - t0
            rate = n / dt if dt else 0
            print(f"  BLOC {block:>3} trouve  nonce={n:>12,}  "
                  f"hash={format(h, '064x')[:20]}...  "
                  f"{rate:>10,.0f} h/s  (session: {total_hashes:,})")
    except KeyboardInterrupt:
        print(f"\n  la ruche se repose. total : {total_hashes:,} hashes")

if __name__ == "__main__":
    bits = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    mine(bits)
