import typing

from .._common import Concept, ConceptList

from .common import iterunion
from .fcbo import fast_generate_from, fcbo_dual
from .lindig import lattice, neighbors
from .duquenne_guigues import dg_basis, dg_basis_optimized

__all__ = ['iterunion',
           'fast_generate_from', 'fcbo_dual',
           'lattice', 'neighbors',
           'dg_basis', 'dg_basis_optimized',
           'iterconcepts', 'get_concepts']


def iterconcepts(context) -> typing.Iterator[Concept]:
    iterconcepts = fast_generate_from(context)
    return map(Concept._make, iterconcepts)


def get_concepts(context) -> typing.List[Concept]:
    iterconcepts = fast_generate_from(context)
    return ConceptList.frompairs(iterconcepts)
