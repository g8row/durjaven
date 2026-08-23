"""Minimal TrueType/TTC table reader — just enough to invert a font's `cmap`.

Word's PDF export writes the mathematics of an OMML equation as glyphs of a
*subsetted* Cambria Math whose `ToUnicode` CMap covers only the Cyrillic and
punctuation runs. Every math glyph therefore extracts as U+0020 and the whole
formula reads as a run of spaces (see scripts/extract_math.py).

The way back is that the subset is written with `/Encoding /Identity-H` and
`/CIDToGIDMap /Identity`, and Word keeps the *original* glyph ids. So a CID in
the content stream is a glyph id in the full Cambria Math, and one reversed
`cmap` from the full font decodes every subset in the corpus.

Only `cmap` formats 4 and 12 are handled; that covers Cambria Math and the
embedded subsets, which also retain a usable `cmap` of their own as a fallback.
"""
import struct


def _tables(b, off=0):
    _, num = struct.unpack(">IH", b[off:off + 6])
    t = {}
    for i in range(num):
        p = off + 12 + 16 * i
        tag = b[p:p + 4].decode("latin1")
        o, ln = struct.unpack(">II", b[p + 8:p + 16])
        t[tag] = (o, ln)
    return t


def ttc_offset(b, index):
    """Byte offset of font `index` inside a TrueType Collection."""
    if b[:4] != b"ttcf":
        return 0
    n = struct.unpack(">I", b[8:12])[0]
    if index >= n:
        raise IndexError("TTC has %d fonts, asked for %d" % (n, index))
    return struct.unpack(">I", b[12 + 4 * index:16 + 4 * index])[0]


def font_name(b, off=0):
    t = _tables(b, off)
    if "name" not in t:
        return ""
    no, _ = t["name"]
    _, cnt, so = struct.unpack(">HHH", b[no:no + 6])
    for j in range(cnt):
        p = no + 6 + 12 * j
        pid, _eid, _lid, nid, ln, o2 = struct.unpack(">HHHHHH", b[p:p + 12])
        if nid == 4 and pid == 3:
            return b[no + so + o2:no + so + o2 + ln].decode("utf-16-be", "replace")
    return ""


def gid_to_unicode(b, off=0):
    """Reverse a font's `cmap` into {glyph_id: codepoint}.

    A glyph reachable from several codepoints keeps the first one seen, which
    for Cambria Math is the plain character rather than a presentation form.
    """
    t = _tables(b, off)
    if "cmap" not in t:
        return {}
    co, _ = t["cmap"]
    _, n = struct.unpack(">HH", b[co:co + 4])
    best = None
    for i in range(n):
        _pid, _eid, o2 = struct.unpack(">HHI", b[co + 4 + 8 * i:co + 12 + 8 * i])
        fmt = struct.unpack(">H", b[co + o2:co + o2 + 2])[0]
        # Prefer format 12: it reaches beyond the BMP, where the Mathematical
        # Alphanumeric Symbols (U+1D400..) that Word uses for italic maths live.
        if fmt == 12:
            best = (12, co + o2)
        elif fmt == 4 and best is None:
            best = (4, co + o2)
    if best is None:
        return {}
    fmt, o = best
    g2u = {}
    if fmt == 4:
        seg_x2 = struct.unpack(">H", b[o + 6:o + 8])[0]
        seg = seg_x2 // 2
        end_o = o + 14
        start_o = end_o + seg_x2 + 2
        delta_o = start_o + seg_x2
        range_o = delta_o + seg_x2
        for i in range(seg):
            end = struct.unpack(">H", b[end_o + 2 * i:end_o + 2 * i + 2])[0]
            sta = struct.unpack(">H", b[start_o + 2 * i:start_o + 2 * i + 2])[0]
            delta = struct.unpack(">h", b[delta_o + 2 * i:delta_o + 2 * i + 2])[0]
            ro = struct.unpack(">H", b[range_o + 2 * i:range_o + 2 * i + 2])[0]
            if sta == 0xFFFF:
                continue
            for c in range(sta, end + 1):
                if ro == 0:
                    g = (c + delta) & 0xFFFF
                else:
                    gp = range_o + 2 * i + ro + 2 * (c - sta)
                    if gp + 2 > len(b):
                        continue
                    g = struct.unpack(">H", b[gp:gp + 2])[0]
                    if g:
                        g = (g + delta) & 0xFFFF
                if g:
                    g2u.setdefault(g, c)
    else:
        ng = struct.unpack(">I", b[o + 12:o + 16])[0]
        for i in range(ng):
            s, e, sg = struct.unpack(">III", b[o + 16 + 12 * i:o + 28 + 12 * i])
            for c in range(s, e + 1):
                g2u.setdefault(sg + (c - s), c)
    return g2u
