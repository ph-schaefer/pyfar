import numpy as np
import numpy.testing as npt
import pytest
import re
from pyfar import TransmissionMatrix
from pyfar import FrequencyData

@pytest.fixture(scope="module")
def frequencies():
    return [100, 200]
@pytest.fixture(scope="module")
def A_list():
    """Test data for a matrix-entry (e.g. A) using a list type"""
    return [1, 1]
@pytest.fixture(scope="module")
def A_np(A_list):
    """Test data for a matrix-entry (e.g. A) using an np.ndarray"""
    return np.array(A_list)
@pytest.fixture(scope="module")
def A_FreqDat(A_np, frequencies):
    """Test data for a matrix-entry (e.g. A) using a FrequencyData object"""
    return FrequencyData(A_np, frequencies)

def _expect_data_with_wrong_abcd_dims(data: np.ndarray, frequencies):
    error_msg = re.escape("'data' must have a shape like "
                          "(..., 2, 2, n_bins), e.g. (2, 2, 100).")
    with pytest.raises(ValueError, match=error_msg):
        TransmissionMatrix(data, frequencies)
    with pytest.raises(ValueError, match=error_msg):
        TransmissionMatrix.from_tmatrix(data, frequencies)
    with pytest.raises(ValueError, match=error_msg):
        TransmissionMatrix(np.ndarray.tolist(data), frequencies)
    with pytest.raises(ValueError, match=error_msg):
        TransmissionMatrix.from_tmatrix(np.ndarray.tolist(data), frequencies)

def test_tmatrix_init():
    frequencies = [100, 200, 300]
    num_bins = len(frequencies)
    TransmissionMatrix(np.ones([2, 2, num_bins]), frequencies)
    TransmissionMatrix(np.ones([4, 2, 2, num_bins]), frequencies)
    TransmissionMatrix.from_tmatrix(np.ones([2, 2, num_bins]), frequencies)
    TransmissionMatrix.from_tmatrix(np.ones([4, 2, 2, num_bins]), frequencies)

    _expect_data_with_wrong_abcd_dims(
        np.ones([2, num_bins]), frequencies)
    _expect_data_with_wrong_abcd_dims(
        np.ones([3, 2, num_bins]), frequencies)
    _expect_data_with_wrong_abcd_dims(
        np.ones([2, 5, num_bins]), frequencies)
    _expect_data_with_wrong_abcd_dims(
        np.ones([7, 4, 2, num_bins]), frequencies)
    _expect_data_with_wrong_abcd_dims(
        np.ones([7, 8, 4, 2, num_bins]), frequencies)

def _expect_error_abcd_same_type(A, B, C, D):
    with pytest.raises(
        ValueError, match=
                    "If using FrequencyData objects, all matrix entries "
                    "A, B, C, D, must be FrequencyData objects."):
        TransmissionMatrix.from_abcd(A, B, C, D, 1000)

def test_tmatrix_from_abcd_input_types(frequencies, A_list, A_np, A_FreqDat):
    TransmissionMatrix.from_abcd(A_list, A_list,
                                 A_list, A_list, frequencies)
    TransmissionMatrix.from_abcd(A_np, A_np, A_list, A_np, frequencies)
    TransmissionMatrix.from_abcd(A_np, A_np, A_np, A_np, frequencies)
    TransmissionMatrix.from_abcd(A_FreqDat, A_FreqDat, A_FreqDat, A_FreqDat)

    _expect_error_abcd_same_type(A_np, A_np, A_np, A_FreqDat)
    _expect_error_abcd_same_type(A_np, A_np, A_FreqDat, A_np)
    _expect_error_abcd_same_type(A_np, A_FreqDat, A_np, A_np)
    _expect_error_abcd_same_type(A_FreqDat, A_np, A_np, A_np)

def test_tmatrix_from_abcd_optional_frequencies(A_list, A_FreqDat):
    TransmissionMatrix.from_abcd(A_FreqDat, A_FreqDat, A_FreqDat, A_FreqDat)
    with pytest.raises(ValueError, match="'frequencies' must be specified if "
                       "not using 'FrequencyData' objects as input"
    ):
        TransmissionMatrix.from_abcd(A_list, A_list, A_list, A_list)


# -------------------------
# TESTS FOR HIGHER DIM DATA
# -------------------------
@pytest.fixture(scope="module")
def abcd_data_3x2():
    """ABCD matrices with 2 frequency bins and one additional
    dimension of size 3"""
    frequencies = [100, 200]
    A = FrequencyData([[1, 1], [1, 1], [1, 1]], frequencies)
    B = FrequencyData([[2, 2], [2, 2], [2, 2]], frequencies)
    C = FrequencyData([[3, 3], [3, 3], [3, 3]], frequencies)
    D = FrequencyData([[4, 4], [4, 4], [4, 4]], frequencies)
    tmat = TransmissionMatrix.from_abcd(A, B, C, D)
    return tmat, A, B, C, D
@pytest.fixture(scope="module")
def abcd_data_3x3x1():
    """ABCD matrices with 1 frequency bin and two additional
    dimensions of size 3"""
    A = FrequencyData(
        [[[1.1], [1.1], [1.1]], [[1.2], [1.2], [1.2]], [[1.3], [1.3], [1.3]]],
        100)
    B = A + 1
    C = A + 2
    D = A + 3
    tmat = TransmissionMatrix.from_abcd(A, B, C, D)
    return tmat, A, B, C, D

def _compare_tmat_vs_abcd(tmat, A, B, C, D):
    if isinstance(A, FrequencyData):
        assert tmat.A == A
        assert tmat.B == B
        assert tmat.C == C
        assert tmat.D == D
    else:
        assert np.all(tmat.A.freq == A)
        assert np.all(tmat.B.freq == B)
        assert np.all(tmat.C.freq == C)
        assert np.all(tmat.D.freq == D)

def test_tmatrix_abcd_cshape(abcd_data_3x2, abcd_data_3x3x1):
    tmat, A, __, __, __ = abcd_data_3x2
    assert tmat.abcd_cshape == A.cshape
    tmat, A, __, __, __  = abcd_data_3x3x1
    assert tmat.abcd_cshape == A.cshape

def test_tmatrix_abcd_entries(abcd_data_3x2, abcd_data_3x3x1):
    tmat, A, B, C, D = abcd_data_3x2
    _compare_tmat_vs_abcd(tmat, A, B, C, D)

    tmat, A, B, C, D = abcd_data_3x3x1
    _compare_tmat_vs_abcd(tmat, A, B, C, D)



@pytest.mark.parametrize("abcd_cshape", [(), (4,), (4, 5)])
def test_tmatrix_create_identity(abcd_cshape):
    frequencies = [100,200,300]
    identity_tmat = TransmissionMatrix.create_identity(frequencies,abcd_cshape)
    if abcd_cshape == ():
        abcd_cshape = (1,)
    assert identity_tmat.abcd_cshape == abcd_cshape
    _compare_tmat_vs_abcd(identity_tmat, 1, 0, 0, 1)

def test_tmatrix_create_series_impedance(abcd_cshape = (4,5)):
    with pytest.raises(ValueError, match = "Number of channels for "
                       "'impedance' must be 1."):
        TransmissionMatrix.create_series_impedance(
            FrequencyData([[1,2], [3,4]],[10,20]))

    frequencies = [100,200,300]
    Z = FrequencyData([10, 20, 30], frequencies)
    tmat = TransmissionMatrix.create_series_impedance(Z, abcd_cshape)
    assert tmat.abcd_cshape == abcd_cshape
    _compare_tmat_vs_abcd(tmat, 1, Z.freq, 0, 1)

def test_tmatrix_create_shunt_admittance(abcd_cshape = (4,5)):
    with pytest.raises(ValueError, match = "Number of channels for "
                       "'admittance' must be 1."):
        TransmissionMatrix.create_shunt_admittance(
            FrequencyData([[1,2], [3,4]],[10,20]))

    frequencies = [100,200,300]
    Y = FrequencyData([10, 20, 30], frequencies)
    tmat = TransmissionMatrix.create_shunt_admittance(Y, abcd_cshape)
    assert tmat.abcd_cshape == abcd_cshape
    _compare_tmat_vs_abcd(tmat, 1, 0, Y.freq, 1)

@pytest.mark.parametrize("transducer_contant", [2.5, (2.5)])
def test_tmatrix_create_transformer(transducer_contant, frequencies):
    error_msg = "'transducer_constant' must be a numerical scalar"
    with pytest.raises(ValueError, match = error_msg):
        TransmissionMatrix.create_transformer([1,1])

    N = transducer_contant
    tmat = TransmissionMatrix.create_transformer(N)

    Zl = 100
    Zin_expected = N*N * Zl
    tmat_obj = TransmissionMatrix.create_identity(frequencies) @ tmat
    Zin = tmat_obj.input_impedance(Zl)
    npt.assert_allclose(Zin.freq, Zin_expected, atol = 1e-15)

@pytest.mark.parametrize("transducer_contant", [2.5, (2.5)])
def test_tmatrix_create_gyrator(transducer_contant, frequencies):
    error_msg = "'transducer_constant' must be a numerical scalar"
    with pytest.raises(ValueError, match = error_msg):
        TransmissionMatrix.create_gyrator([1,1])

    N = transducer_contant
    tmat = TransmissionMatrix.create_gyrator(N)

    Zl = 100
    Zin_expected = N*N / Zl
    tmat_obj = TransmissionMatrix.create_identity(frequencies) @ tmat
    Zin = tmat_obj.input_impedance(Zl)
    npt.assert_allclose(Zin.freq, Zin_expected, atol = 1e-15)
