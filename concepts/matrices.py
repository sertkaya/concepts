# matrices.py - boolean matrices as row bitsets and column bitsets

"""Boolean matrices as collections of row and column vectors."""

from itertools import imap, izip

import bitsets

__all__ = ['relation']


Vector = bitsets.bases.MemberBits
"""Single row or column of a boolean matrix as bit vector."""


class Vectors(bitsets.series.Tuple):
    """Paired collection of rows or columns of a boolean matrix relation."""

    def _pair_with(self, relation, index, other):
        if hasattr(self, 'prime'):
            raise RuntimeError('%r attempt _pair_with' % self)

        self.relation = relation
        self.relation_index = index

        _prime = other.BitSet.frombools
        _double = self.BitSet.frombools

        def prime(bitset):
            """FCA derivation operator (extent->intent, intent->extent)."""
            return _prime(bitset & b == bitset for b in self)

        def double(bitset):
            """FCA double derivation operator (extent->extent, intent->intent)."""
            prime = _prime(bitset & b == bitset for b in self)
            return _double(prime & b == prime for b in other)

        self.prime = self.BitSet.prime = prime
        self.double = self.BitSet.double = double

    def __reduce__(self):
        return self.relation, (self.relation_index,)
    

class relation(tuple):
    """Binary relation as interconnected pair of bitset collections.

    >>> br = relation('Condition', 'Symbol',
    ... ('TT', 'TF', 'FT', 'FF'), ('->', '<-'),
    ... [(True, False, True, True), (True, True, False, True)])

    >>> br
    <relation(ConditionVectors('1011', '1101'), SymbolVectors('11', '01', '10', '11'))>

    >>> br[1].BitSet.frommembers(('->', '<-')).prime().members()
    ('TT', 'FF')
    """ 

    __slots__ = ()

    def __new__(cls, xname, yname, xmembers, ymembers, xbools, _ids=None):
        if _ids is not None:
            # unpickle reconstruction
            xid, yid = _ids
            X = bitsets.meta.bitset(xname, xmembers, xid, Vector, None, Vectors)
            Y = bitsets.meta.bitset(yname, ymembers, yid, Vector, None, Vectors)
        else:
            X = bitsets.bitset(xname, xmembers, Vector, tuple=Vectors)
            Y = bitsets.bitset(yname, ymembers, Vector, tuple=Vectors)

        x = X.Tuple.frombools(xbools)
        y = Y.Tuple.frombools(izip(*x.bools()))

        self = super(relation, cls).__new__(cls, (x, y))

        x._pair_with(self, 0, y)
        y._pair_with(self, 1, x)

        return self

    __call__ = tuple.__getitem__

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self[0], self[1])

    def __reduce__(self):
        X, Y = (v.BitSet for v in self)
        bools = self[0].bools()
        ids = (X._id, Y._id)
        args = (X.__name__, Y.__name__, X._members, Y._members, bools, ids)
        return relation, args
