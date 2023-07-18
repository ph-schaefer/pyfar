import numpy as np
import numpy.testing as npt
import pytest

import pyfar as pf


def test_find_nearest_simple():
    """Test returns of find_nearest_k"""
    # 1D cartesian, nearest point
    x = np.arange(6)
    coords = pf.Coordinates(x, 0, 0)
    find = pf.Coordinates(1, 0, 0)
    i, d = coords.find_nearest(find)
    assert i == 1
    assert d == 0


def test_find_nearest_2d():
    # 1D spherical, nearest point
    coords = pf.samplings.sph_gaussian(sh_order=47)

    find = pf.Coordinates.from_spherical_elevation(
        np.array([[0, np.pi/2], [np.pi, 3*np.pi/2]]), 0, 1)
    i, d = coords.find_nearest(find)
    npt.assert_equal(i.shape, d.shape)
    npt.assert_equal(i.shape, (2, 2))


def test_find_nearest_2d_k3():
    # 1D spherical, nearest point
    coords = pf.samplings.sph_gaussian(sh_order=47)
    k = 5
    find = pf.Coordinates.from_spherical_elevation(
        np.array([[0, np.pi/2], [np.pi, 3*np.pi/2]]), 0, 1)
    i, d = coords.find_nearest(find, k=k)
    npt.assert_equal(i.shape, d.shape)
    npt.assert_equal(i.shape, (2, 2, k))
    for ii in range(k):
        actual_distance = np.sqrt(np.sum(
            (coords[i].cartesian[..., ii, :] - find.cartesian)**2, axis=-1))
        npt.assert_equal(actual_distance, d[..., ii])


def test_find_nearest_error():
    coords = pf.samplings.sph_gaussian(sh_order=47)
    find = pf.Coordinates(1, 0, 0)

    # test out of range parameters
    with pytest.raises(ValueError):
        coords.find_nearest(find, -1)

    # test Coordinate object as input
    with pytest.raises(ValueError):
        coords.find_nearest(5, 1)

    # test wrong string for distance measure
    with pytest.raises(ValueError):
        coords.find_nearest(find, 1, 'bla')

    # test wrong type for distance measure
    with pytest.raises(ValueError):
        coords.find_nearest(find, 1, 5)
