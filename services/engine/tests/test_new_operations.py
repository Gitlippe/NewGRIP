"""Tests for all newly added operations (arithmetic, bitwise, transform, color, detection, advanced)."""

import cv2
import numpy as np
import pytest

from newgrip_engine.models import ParamSpec, PipelineNode, SocketSpec
from newgrip_engine.operations import OperationRegistry


def _node(op: str, params: list[ParamSpec] | None = None) -> PipelineNode:
    return PipelineNode(
        id="n1",
        op=op,
        inputs=[SocketSpec(name="in", type="image")],
        outputs=[SocketSpec(name="out", type="image")],
        params=params or [],
    )


def _param(name: str, value) -> ParamSpec:
    return ParamSpec(name=name, view="slider", value=value)


@pytest.fixture
def registry():
    return OperationRegistry()


@pytest.fixture
def test_image():
    """64x64 BGR image: black background with a white rectangle."""
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    img[10:50, 20:44] = (200, 200, 200)
    return img


def _assert_bgr_image(result: dict, key: str = "out"):
    """Verify the output is a valid BGR 3-channel uint8 ndarray."""
    assert key in result
    out = result[key]
    assert isinstance(out, np.ndarray), f"Expected ndarray, got {type(out)}"
    assert out.dtype == np.uint8, f"Expected uint8, got {out.dtype}"
    assert len(out.shape) == 3, f"Expected 3D array, got shape {out.shape}"
    assert out.shape[2] == 3, f"Expected 3 channels, got {out.shape[2]}"
    return out


# ---- Arithmetic ----

class TestArithmetic:
    def test_add_single(self, registry, test_image):
        result = registry.run("opencv.add", _node("opencv.add", [_param("scale", 1.0)]), {"in": test_image}, {})
        _assert_bgr_image(result)

    def test_add_dual(self, registry, test_image):
        img2 = np.full_like(test_image, 50)
        result = registry.run("opencv.add", _node("opencv.add", [_param("scale", 1.0)]), {"in1": test_image, "in2": img2}, {})
        out = _assert_bgr_image(result)
        expected = cv2.add(test_image, img2)
        np.testing.assert_array_equal(out, expected)

    def test_subtract_single(self, registry, test_image):
        result = registry.run("opencv.subtract", _node("opencv.subtract", [_param("scale", 1.0)]), {"in": test_image}, {})
        _assert_bgr_image(result)

    def test_subtract_dual(self, registry, test_image):
        img2 = np.full_like(test_image, 50)
        result = registry.run("opencv.subtract", _node("opencv.subtract", [_param("scale", 1.0)]), {"in1": test_image, "in2": img2}, {})
        out = _assert_bgr_image(result)
        expected = cv2.subtract(test_image, img2)
        np.testing.assert_array_equal(out, expected)

    def test_absdiff_single(self, registry, test_image):
        result = registry.run("opencv.absdiff", _node("opencv.absdiff"), {"in": test_image}, {})
        _assert_bgr_image(result)

    def test_absdiff_dual(self, registry, test_image):
        img2 = np.full_like(test_image, 100)
        result = registry.run("opencv.absdiff", _node("opencv.absdiff"), {"in1": test_image, "in2": img2}, {})
        out = _assert_bgr_image(result)
        expected = cv2.absdiff(test_image, img2)
        np.testing.assert_array_equal(out, expected)

    def test_multiply(self, registry, test_image):
        result = registry.run("opencv.multiply", _node("opencv.multiply", [_param("scale", 1.5)]), {"in": test_image}, {})
        out = _assert_bgr_image(result)
        assert out.max() <= 255

    def test_divide(self, registry, test_image):
        result = registry.run("opencv.divide", _node("opencv.divide", [_param("scale", 2.0)]), {"in": test_image}, {})
        _assert_bgr_image(result)

    def test_add_weighted(self, registry, test_image):
        result = registry.run(
            "opencv.addWeighted",
            _node("opencv.addWeighted", [_param("alpha", 0.7), _param("beta", 0.3), _param("gamma", 0.0)]),
            {"in": test_image},
            {},
        )
        _assert_bgr_image(result)

    def test_min(self, registry, test_image):
        result = registry.run("opencv.min", _node("opencv.min"), {"in": test_image}, {})
        _assert_bgr_image(result)

    def test_max(self, registry, test_image):
        result = registry.run("opencv.max", _node("opencv.max"), {"in": test_image}, {})
        _assert_bgr_image(result)


# ---- Bitwise ----

class TestBitwise:
    def test_and_single_input(self, registry, test_image):
        """Single-input fallback: AND with threshold mask."""
        result = registry.run("opencv.bitwiseAnd", _node("opencv.bitwiseAnd"), {"in": test_image}, {})
        _assert_bgr_image(result)

    def test_and_dual_input(self, registry, test_image):
        """Dual-input: AND of two images."""
        img2 = np.full_like(test_image, 128)
        result = registry.run("opencv.bitwiseAnd", _node("opencv.bitwiseAnd"), {"in1": test_image, "in2": img2}, {})
        out = _assert_bgr_image(result)
        expected = cv2.bitwise_and(test_image, img2)
        np.testing.assert_array_equal(out, expected)

    def test_or_single_input(self, registry, test_image):
        """Single-input fallback: OR with threshold mask."""
        result = registry.run("opencv.bitwiseOr", _node("opencv.bitwiseOr"), {"in": test_image}, {})
        _assert_bgr_image(result)

    def test_or_dual_input(self, registry, test_image):
        """Dual-input: OR of two images."""
        img2 = np.full_like(test_image, 128)
        result = registry.run("opencv.bitwiseOr", _node("opencv.bitwiseOr"), {"in1": test_image, "in2": img2}, {})
        out = _assert_bgr_image(result)
        expected = cv2.bitwise_or(test_image, img2)
        np.testing.assert_array_equal(out, expected)

    def test_xor_single_input(self, registry, test_image):
        """Single-input fallback: XOR with inverted image."""
        result = registry.run("opencv.bitwiseXor", _node("opencv.bitwiseXor"), {"in": test_image}, {})
        out = _assert_bgr_image(result)
        # XOR with inverted = all 255
        assert out.max() == 255

    def test_xor_dual_input(self, registry, test_image):
        """Dual-input: XOR of identical images yields zero."""
        result = registry.run("opencv.bitwiseXor", _node("opencv.bitwiseXor"), {"in1": test_image, "in2": test_image}, {})
        out = _assert_bgr_image(result)
        assert out.max() == 0

    def test_not(self, registry, test_image):
        result = registry.run("opencv.bitwiseNot", _node("opencv.bitwiseNot"), {"in": test_image}, {})
        out = _assert_bgr_image(result)
        expected = 255 - test_image
        np.testing.assert_array_equal(out, expected)


# ---- Transform ----

class TestTransform:
    def test_crop(self, registry, test_image):
        result = registry.run(
            "opencv.crop",
            _node("opencv.crop", [_param("x", 10), _param("y", 10), _param("w", 30), _param("h", 30)]),
            {"in": test_image},
            {},
        )
        out = _assert_bgr_image(result)
        assert out.shape == (30, 30, 3)

    def test_crop_clamps_bounds(self, registry, test_image):
        result = registry.run(
            "opencv.crop",
            _node("opencv.crop", [_param("x", 60), _param("y", 60), _param("w", 100), _param("h", 100)]),
            {"in": test_image},
            {},
        )
        out = _assert_bgr_image(result)
        assert out.shape[0] > 0 and out.shape[1] > 0

    def test_resize(self, registry, test_image):
        result = registry.run(
            "opencv.resize",
            _node("opencv.resize", [_param("width", 128), _param("height", 96)]),
            {"in": test_image},
            {},
        )
        out = _assert_bgr_image(result)
        assert out.shape == (96, 128, 3)

    def test_flip_vertical(self, registry, test_image):
        result = registry.run("opencv.flip", _node("opencv.flip", [_param("flipCode", 0)]), {"in": test_image}, {})
        out = _assert_bgr_image(result)
        assert out.shape == test_image.shape

    def test_flip_horizontal(self, registry, test_image):
        result = registry.run("opencv.flip", _node("opencv.flip", [_param("flipCode", 1)]), {"in": test_image}, {})
        _assert_bgr_image(result)

    def test_normalize(self, registry, test_image):
        result = registry.run(
            "opencv.normalize",
            _node("opencv.normalize", [_param("alpha", 0), _param("beta", 255)]),
            {"in": test_image},
            {},
        )
        _assert_bgr_image(result)

    def test_extract_channel(self, registry, test_image):
        result = registry.run(
            "opencv.extractChannel",
            _node("opencv.extractChannel", [_param("channel", 1)]),
            {"in": test_image},
            {},
        )
        out = _assert_bgr_image(result)
        assert out.shape == test_image.shape

    def test_transpose(self, registry, test_image):
        result = registry.run("opencv.transpose", _node("opencv.transpose"), {"in": test_image}, {})
        out = _assert_bgr_image(result)
        assert out.shape == (64, 64, 3)


# ---- Color / Threshold expansion ----

class TestColorThreshold:
    def test_hsl_threshold(self, registry, test_image):
        result = registry.run(
            "opencv.hslThreshold",
            _node("opencv.hslThreshold", [
                _param("hMin", 0), _param("hMax", 179),
                _param("sMin", 0), _param("sMax", 255),
                _param("lMin", 0), _param("lMax", 255),
            ]),
            {"in": test_image},
            {},
        )
        out = _assert_bgr_image(result)
        assert out.max() == 255  # all-pass filter

    def test_rgb_threshold(self, registry, test_image):
        result = registry.run(
            "opencv.rgbThreshold",
            _node("opencv.rgbThreshold", [
                _param("rMin", 100), _param("rMax", 255),
                _param("gMin", 100), _param("gMax", 255),
                _param("bMin", 100), _param("bMax", 255),
            ]),
            {"in": test_image},
            {},
        )
        out = _assert_bgr_image(result)
        assert out.max() == 255  # white rectangle pixels pass

    def test_hsv_threshold_6param(self, registry, test_image):
        """Test upgraded hsvThreshold with 6-param mode."""
        result = registry.run(
            "opencv.hsvThreshold",
            _node("opencv.hsvThreshold", [
                _param("hMin", 0), _param("hMax", 179),
                _param("sMin", 0), _param("sMax", 255),
                _param("vMin", 100), _param("vMax", 255),
            ]),
            {"in": test_image},
            {},
        )
        _assert_bgr_image(result)

    def test_hsv_threshold_legacy(self, registry, test_image):
        """Test backward compat with legacy single 'value' param."""
        result = registry.run(
            "opencv.hsvThreshold",
            _node("opencv.hsvThreshold", [_param("value", 115)]),
            {"in": test_image},
            {},
        )
        _assert_bgr_image(result)


# ---- Feature Detection ----

class TestFeatureDetection:
    def test_find_lines(self, registry):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[50, 10:90] = (255, 255, 255)  # horizontal white line
        result = registry.run(
            "opencv.findLines",
            _node("opencv.findLines", [_param("threshold", 10), _param("minLineLength", 10), _param("maxLineGap", 5)]),
            {"in": img},
            {},
        )
        _assert_bgr_image(result)

    def test_find_blobs(self, registry, test_image):
        result = registry.run(
            "opencv.findBlobs",
            _node("opencv.findBlobs", [_param("minArea", 10), _param("maxArea", 50000)]),
            {"in": test_image},
            {},
        )
        _assert_bgr_image(result)


# ---- Advanced ----

class TestAdvanced:
    def test_mask(self, registry, test_image):
        result = registry.run(
            "opencv.mask",
            _node("opencv.mask", [_param("threshold", 100)]),
            {"in": test_image},
            {},
        )
        out = _assert_bgr_image(result)
        # black region stays black, white region stays (masked in)
        assert out[0, 0].sum() == 0  # background should be zero

    def test_distance_transform(self, registry, test_image):
        result = registry.run(
            "opencv.distanceTransform",
            _node("opencv.distanceTransform", [_param("maskSize", 3)]),
            {"in": test_image},
            {},
        )
        _assert_bgr_image(result)

    def test_watershed(self, registry, test_image):
        result = registry.run(
            "opencv.watershed",
            _node("opencv.watershed", [_param("threshold", 100)]),
            {"in": test_image},
            {},
        )
        _assert_bgr_image(result)


# ---- Catalog completeness ----

class TestCatalog:
    def test_catalog_count_at_least_40(self):
        catalog = OperationRegistry.catalog()
        assert len(catalog) >= 40, f"Expected >=40 catalog entries, got {len(catalog)}"

    def test_new_categories_present(self):
        catalog = OperationRegistry.catalog()
        categories = {c.category for c in catalog}
        assert "Arithmetic" in categories
        assert "Bitwise" in categories
        assert "Transform" in categories
        assert "Detection" in categories
        assert "Advanced" in categories

    def test_all_catalog_ops_are_registered(self):
        """Every execute_op in the catalog must exist in the registry."""
        reg = OperationRegistry()
        catalog = OperationRegistry.catalog()
        for desc in catalog:
            assert desc.execute_op in reg._ops, f"{desc.execute_op} not registered"

    def test_all_registered_ops_run(self):
        """Smoke test: every registered op can run without crashing."""
        reg = OperationRegistry()
        img = np.zeros((64, 64, 3), dtype=np.uint8)
        img[10:50, 20:44] = (200, 200, 200)

        skip = {"source.image"}  # needs context, not image input
        for op_key in reg._ops:
            if op_key in skip:
                continue
            node = _node(op_key)
            result = reg.run(op_key, node, {"in": img}, {})
            assert "out" in result, f"{op_key} did not return 'out'"
