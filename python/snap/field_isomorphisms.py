"""
This module includes functions to express one algebraic number given in terms of powers
of a root of an irreducible polynomial (over the rational numbers) in terms of powers
of roots of another polynomial.

Sage theoretically has this functionality, but as of 9.1, it doesn't actually compute
the isomorphism correctly when one of the defining polynomials is not monic and
integral.  The reason is that sage's implementation converts to PARI using
pari_polynomial which is always monic and integral.  That said, sage can factor
polynomials over number fields correctly, and those factorizations can be used to
compute the isomorphisms.
"""

from sage.all import CC, I, NumberField, PolynomialRing, conjugate, factor, var


def isomorphisms_between_number_fields(domain_field, codomain_field):
    """
    Takes in two sage number fields are returns a list of isomorphisms between them.
    The algorithm is simple, but its speed relies on how quickly the factorizations
    can be computed.  There are other algorithms for computing field isomorphisms,
    and they might be added to this module in some form at sometime in the future.
    For fields arising from Kleinian groups (which are often of degree less than 100
    with discriminants that are tractable), this function should be reasonably fast.

    7-Aug-2020
    """
    if domain_field.degree() != codomain_field.degree():
        return []
    else:
        polynomial_ring_over_codomain_field = PolynomialRing(codomain_field, "x")
        domain_min_poly = domain_field.defining_polynomial().change_variable_name("x")
        poly_to_factor = polynomial_ring_over_codomain_field.coerce(domain_min_poly)
        factorization = factor(poly_to_factor)
        iso_list = []
        for factor_with_multiplicity in factorization:
            if factor_with_multiplicity[0].degree() == 1:
                iso_list.append(domain_field.hom([-factor_with_multiplicity[0](0)]))
        return iso_list


def special_isomorphism(domain_field, codomain_field, domain_anchors, codomain_anchors):
    """
    Given isomorphic NumberFields and an element of each one (the anchors), returns the
    isomorphism that takes one anchor to the other, or returns set() if there is no such
    isomorphism. The anchors can be iterables

    There are some corner cases to be cautious of, particularly when the anchors are
    Galois conjugates of each other.
    """
    try:
        iter(domain_anchors)
    except TypeError:
        domain_anchors = [domain_anchors]
    try:
        iter(codomain_anchors)
    except TypeError:
        codomain_anchors = [codomain_anchors]
    isos = isomorphisms_between_number_fields(domain_field, codomain_field)
    special_isos = list()
    for iso in isos:
        if set(iso(elt) for elt in domain_anchors) == set(
            elt for elt in codomain_anchors
        ):
            special_isos.append(iso)
    if len(special_isos) != 1:
        raise RuntimeError("Did not find a unique isomorphism.")
    return special_isos[0]


def canonical_embedding(field_with_embedding):
    """
    It seems sage doesn't have a built-in way to get this map.
    """
    return min(
        field_with_embedding.complex_embeddings(),
        key=lambda embedding: abs(
            CC(field_with_embedding.gen_embedding()) - CC(embedding.im_gens()[0])
        ),
    )


def same_subfield_of_CC(field1, field2, up_to_conjugation=False):
    try:
        iso = isomorphisms_between_number_fields(field1, field2)[0]
    except IndexError:
        return False
    gen1 = field1.gen()
    transfered_gen = iso(gen1)
    automorphisms = field2.automorphisms()
    orbit = [automorphism(transfered_gen) for automorphism in automorphisms]
    embedding2 = canonical_embedding(field2)
    embedded_orbit = [embedding2(elt) for elt in orbit]
    all_im_gens = [embedding.im_gens()[0] for embedding in field1.complex_embeddings()]
    found_elts = [
        min(all_im_gens, key=lambda x: abs(CC(x) - CC(elt))) for elt in embedded_orbit
    ]
    leftovers = [elt for elt in all_im_gens if elt not in found_elts]
    coerced_elt = min(
        all_im_gens, key=lambda x: abs(CC(x) - CC(field1.gen_embedding()))
    )
    if coerced_elt in leftovers:
        if up_to_conjugation:
            coerced_elt_conjugate = min(
                all_im_gens,
                key=lambda x: abs(CC(x) - conjugate(CC(field1.gen_embedding()))),
            )
            if coerced_elt_conjugate in leftovers:
                return False
            elif coerced_elt_conjugate in found_elts:
                return True
            else:
                raise
        else:
            return False
    elif coerced_elt in found_elts:
        return True
    else:
        raise