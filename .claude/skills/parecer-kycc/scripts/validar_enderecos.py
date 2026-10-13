#!/usr/bin/env python3
"""Valida formato e checksum de endereços de carteira e detecta homóglifos.

Uso:
    python validar_enderecos.py ENDERECO [ENDERECO ...]
    python validar_enderecos.py --arquivo lista.txt     (um por linha)
    python validar_enderecos.py --extrair texto.txt     (procura endereços num texto)
    python validar_enderecos.py --rotulo "UrbanСrypto"  (só homóglifos, para nomes de entidade/tags)

Cobertura:
  - TRON (T..., 34 caracteres): Base58Check, prefixo 0x41
  - EVM (0x + 40 hex: Ethereum, Polygon, Base, BSC, Arbitrum...): EIP-55
    (endereço todo minúsculo ou todo maiúsculo é válido, mas sem checksum)
  - Bitcoin legado (1..., 3...): Base58Check
  - Bitcoin bech32/bech32m (bc1...)
  - Solana (32–44 caracteres base58, decodifica para 32 bytes) — sem checksum

Sai com código 1 se algum endereço for inválido.
"""
import hashlib
import re
import sys
import unicodedata

B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


# ------------------------------------------------------------ keccak-256 (EIP-55)
def _keccak256(data: bytes) -> bytes:
    RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
          0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
          0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
          0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
          0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
          0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
    ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
    M = (1 << 64) - 1
    rotl = lambda v, n: ((v << n) | (v >> (64 - n))) & M if n else v
    rate = 136
    msg = bytearray(data) + b"\x01"
    while len(msg) % rate:
        msg.append(0)
    msg[-1] |= 0x80
    A = [[0] * 5 for _ in range(5)]
    for off in range(0, len(msg), rate):
        for i in range(rate // 8):
            A[i % 5][i // 5] ^= int.from_bytes(msg[off + 8 * i: off + 8 * i + 8], "little")
        for rnd in range(24):
            C = [A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4] for x in range(5)]
            D = [C[(x - 1) % 5] ^ rotl(C[(x + 1) % 5], 1) for x in range(5)]
            A = [[A[x][y] ^ D[x] for y in range(5)] for x in range(5)]
            B = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    B[y][(2 * x + 3 * y) % 5] = rotl(A[x][y], ROT[x][y])
            A = [[B[x][y] ^ ((~B[(x + 1) % 5][y]) & B[(x + 2) % 5][y]) for y in range(5)] for x in range(5)]
            A[0][0] ^= RC[rnd]
    out = b"".join(A[i % 5][i // 5].to_bytes(8, "little") for i in range(rate // 8))
    return out[:32]


assert _keccak256(b"").hex() == "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"


def _b58decode(s):
    n = 0
    for ch in s:
        n = n * 58 + B58.index(ch)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    return b"\x00" * (len(s) - len(s.lstrip("1"))) + raw


def _b58check(s):
    raw = _b58decode(s)
    if len(raw) < 5:
        return None
    body, chk = raw[:-4], raw[-4:]
    ok = hashlib.sha256(hashlib.sha256(body).digest()).digest()[:4] == chk
    return body if ok else None


def _bech32_ok(addr):
    CH = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    a = addr.lower()
    if addr != a and addr != addr.upper():
        return False, "caixa mista"
    pos = a.rfind("1")
    hrp, data = a[:pos], a[pos + 1:]
    if any(c not in CH for c in data) or len(data) < 6:
        return False, "caractere inválido"
    def polymod(v):
        G = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
        chk = 1
        for x in v:
            b = chk >> 25
            chk = (chk & 0x1ffffff) << 5 ^ x
            for i in range(5):
                chk ^= G[i] if (b >> i) & 1 else 0
        return chk
    vals = [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp] + [CH.index(c) for c in data]
    pm = polymod(vals)
    if pm == 1:
        return True, "bech32 (SegWit v0)"
    if pm == 0x2bc830a3:
        return True, "bech32m (Taproot)"
    return False, "checksum bech32 inválido"


def homoglifos(addr):
    alertas = []
    if any(ord(c) > 127 for c in addr):
        nomes = {c: unicodedata.name(c, "?") for c in addr if ord(c) > 127}
        alertas.append("caracteres não-ASCII: " + ", ".join(f"{c}={n}" for c, n in nomes.items()))
    if addr != addr.strip() or any(c.isspace() for c in addr):
        alertas.append("espaço/invisível no endereço")
    return alertas


def validar(addr):
    a = addr.strip()
    h = homoglifos(addr)
    if h:
        return False, "?", "; ".join(h)
    if re.fullmatch(r"0x[0-9a-fA-F]{40}", a):
        hexpart = a[2:]
        if hexpart == hexpart.lower() or hexpart == hexpart.upper():
            return True, "EVM", "formato válido, sem checksum EIP-55 (todo minúsculo/maiúsculo)"
        hh = _keccak256(hexpart.lower().encode()).hex()
        esperado = "".join(c.upper() if int(hh[i], 16) >= 8 else c for i, c in enumerate(hexpart.lower()))
        return (esperado == hexpart, "EVM",
                "checksum EIP-55 válido" if esperado == hexpart else f"EIP-55 INVÁLIDO (esperado 0x{esperado})")
    if a.startswith("T") and len(a) == 34:
        if any(c not in B58 for c in a):
            return False, "TRON", "caractere fora do Base58 (0, O, I ou l)"
        body = _b58check(a)
        if body is None:
            return False, "TRON", "Base58Check INVÁLIDO"
        return (body[0] == 0x41 and len(body) == 21, "TRON",
                "Base58Check válido" if body[0] == 0x41 else "prefixo diferente de 0x41")
    if a.lower().startswith(("bc1", "tb1")):
        ok, msg = _bech32_ok(a)
        return ok, "BTC", msg
    if a[:1] in "13" and 26 <= len(a) <= 35 and all(c in B58 for c in a):
        body = _b58check(a)
        return (body is not None, "BTC", "Base58Check válido" if body is not None else "Base58Check INVÁLIDO")
    if 32 <= len(a) <= 44 and all(c in B58 for c in a):
        try:
            ok = len(_b58decode(a)) == 32
        except ValueError:
            ok = False
        return ok, "Solana?", "32 bytes em base58 (Solana não tem checksum)" if ok else "não decodifica para 32 bytes"
    return False, "desconhecido", "formato não reconhecido"


PADRAO = re.compile(r"\b(0x[0-9a-fA-F]{40}|T[1-9A-HJ-NP-Za-km-z]{33}|bc1[02-9ac-hj-np-z]{11,71}|[13][1-9A-HJ-NP-Za-km-z]{25,34})\b")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--rotulo":
        falhou = False
        for r in args[1:]:
            h = homoglifos(r)
            falhou |= bool(h)
            print(f"{'ERRO' if h else 'OK '} | rótulo | {r} | {'; '.join(h) or 'só ASCII'}")
        sys.exit(1 if falhou else 0)
    if args[0] == "--arquivo":
        enderecos = [l.strip() for l in open(args[1], encoding="utf-8") if l.strip()]
    elif args[0] == "--extrair":
        enderecos = sorted(set(PADRAO.findall(open(args[1], encoding="utf-8", errors="replace").read())))
    else:
        enderecos = args
    falhou = False
    for e in enderecos:
        ok, rede, msg = validar(e)
        falhou |= not ok
        print(f"{'OK ' if ok else 'ERRO'} | {rede:<12} | {e} | {msg}")
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
