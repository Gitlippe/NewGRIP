from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np

from .models import ParamSpec, PipelineNode


@dataclass
class OperationDescriptor:
    key: str
    category: str
    label: str
    execute_op: str
    output_type: str
    params: list[ParamSpec]
    inputs: list[dict[str, str]] | None = None
    outputs: list[dict[str, str]] | None = None


def _params(node: PipelineNode) -> dict[str, Any]:
    return {p.name: p.value for p in node.params}


def _ensure_image(value: Any) -> np.ndarray:
    if isinstance(value, np.ndarray):
        return value
    raise ValueError("Expected image matrix input.")


class OperationRegistry:
    def __init__(self) -> None:
        self._ops = {
            "source.image": self.source_image,
            "opencv.noop": self.noop,
            "opencv.blur": self.blur,
            "opencv.gaussianBlur": self.blur,
            "opencv.medianBlur": self.median_blur,
            "opencv.threshold": self.threshold,
            "opencv.adaptiveThreshold": self.adaptive_threshold,
            "opencv.thresholdInverse": self.threshold_inverse,
            "opencv.canny": self.canny,
            "opencv.sobel": self.sobel,
            "opencv.laplacian": self.laplacian,
            "opencv.erode": self.erode,
            "opencv.dilate": self.dilate,
            "opencv.hsvThreshold": self.hsv_threshold,
            "opencv.rgbToGray": self.rgb_to_gray,
            "opencv.findContours": self.find_contours,
            "opencv.filterContours": self.filter_contours,
            "opencv.convexHulls": self.convex_hulls,
            "nn.classify_stub": self.nn_classify_stub,
            # Arithmetic
            "opencv.add": self.add,
            "opencv.subtract": self.subtract,
            "opencv.absdiff": self.absdiff,
            "opencv.multiply": self.multiply,
            "opencv.divide": self.divide,
            "opencv.addWeighted": self.add_weighted,
            "opencv.min": self.img_min,
            "opencv.max": self.img_max,
            # Bitwise
            "opencv.bitwiseAnd": self.bitwise_and,
            "opencv.bitwiseOr": self.bitwise_or,
            "opencv.bitwiseXor": self.bitwise_xor,
            "opencv.bitwiseNot": self.bitwise_not,
            # Transform
            "opencv.crop": self.crop,
            "opencv.resize": self.resize,
            "opencv.flip": self.flip,
            "opencv.normalize": self.normalize,
            "opencv.extractChannel": self.extract_channel,
            "opencv.transpose": self.transpose,
            # Color / Threshold expansion
            "opencv.hslThreshold": self.hsl_threshold,
            "opencv.rgbThreshold": self.rgb_threshold,
            # Feature detection
            "opencv.findLines": self.find_lines,
            "opencv.findBlobs": self.find_blobs,
            # Advanced
            "opencv.mask": self.mask,
            "opencv.distanceTransform": self.distance_transform,
            "opencv.watershed": self.watershed,
        }

    @staticmethod
    def catalog() -> list[OperationDescriptor]:
        def p(name: str, view: str, value: Any, min_v: float | None = None, max_v: float | None = None, options: list[str] | None = None) -> ParamSpec:
            return ParamSpec(name=name, view=view, value=value, min=min_v, max=max_v, options=options)

        single_in = [{"name": "in", "type": "image"}]
        dual_in = [{"name": "in1", "type": "image"}, {"name": "in2", "type": "image"}]

        return [
            OperationDescriptor("gaussian-blur", "Filtering", "Gaussian Blur", "opencv.gaussianBlur", "image", [p("kernel", "slider", 5, 1, 31)], single_in),
            OperationDescriptor("median-blur", "Filtering", "Median Blur", "opencv.medianBlur", "image", [p("kernel", "slider", 7, 1, 31)], single_in),
            OperationDescriptor("box-blur", "Filtering", "Box Blur", "opencv.blur", "image", [p("kernel", "slider", 9, 1, 31)], single_in),
            OperationDescriptor("threshold-binary", "Thresholding", "Threshold Binary", "opencv.threshold", "image", [p("value", "slider", 130, 0, 255)], single_in, [{"name": "out", "type": "image"}, {"name": "value", "type": "json"}]),
            OperationDescriptor("threshold-inverse", "Thresholding", "Threshold Inverse", "opencv.thresholdInverse", "image", [p("value", "slider", 120, 0, 255)], single_in),
            OperationDescriptor("adaptive-threshold", "Thresholding", "Adaptive Threshold", "opencv.adaptiveThreshold", "image", [p("window", "slider", 11, 3, 45)], single_in),
            OperationDescriptor("canny-edges", "Edges", "Canny Edges", "opencv.canny", "image", [p("low", "slider", 60, 0, 255), p("high", "slider", 170, 0, 255)], single_in),
            OperationDescriptor("sobel-gradient", "Edges", "Sobel Gradient", "opencv.sobel", "image", [p("scale", "slider", 1, 1, 8)], single_in),
            OperationDescriptor("laplacian", "Edges", "Laplacian", "opencv.laplacian", "image", [p("ksize", "slider", 3, 1, 7)], single_in),
            OperationDescriptor("find-contours", "Contours", "Find Contours", "opencv.findContours", "image", [p("externalOnly", "checkbox", True)], single_in, [{"name": "out", "type": "image"}, {"name": "contours", "type": "json"}]),
            OperationDescriptor("convex-hulls", "Contours", "Convex Hulls", "opencv.convexHulls", "image", [p("enabled", "checkbox", True)], single_in, [{"name": "out", "type": "image"}, {"name": "hulls", "type": "json"}]),
            OperationDescriptor("filter-contours", "Contours", "Filter Contours", "opencv.filterContours", "image", [p("minArea", "slider", 5000, 0, 20000)], single_in, [{"name": "out", "type": "image"}, {"name": "contours", "type": "json"}]),
            OperationDescriptor("erode", "Morphology", "Erode", "opencv.erode", "image", [p("iterations", "slider", 1, 1, 8)], single_in),
            OperationDescriptor("dilate", "Morphology", "Dilate", "opencv.dilate", "image", [p("iterations", "slider", 1, 1, 8)], single_in),
            OperationDescriptor("hsv-threshold", "Color", "HSV Threshold", "opencv.hsvThreshold", "image", [p("value", "slider", 115, 0, 255)], single_in),
            OperationDescriptor("rgb-to-gray", "Color", "RGB to Gray", "opencv.rgbToGray", "image", [p("enabled", "checkbox", True)], single_in),
            OperationDescriptor("nn-classify-stub", "Neural", "NN Classify Stub", "nn.classify_stub", "json", [p("model", "select", "mobilenet", options=["mobilenet", "resnet18"])], single_in),
            # Arithmetic - dual input ops
            OperationDescriptor("add", "Arithmetic", "Add", "opencv.add", "image", [p("scale", "slider", 1.0, 0.0, 2.0)], dual_in),
            OperationDescriptor("subtract", "Arithmetic", "Subtract", "opencv.subtract", "image", [p("scale", "slider", 1.0, 0.0, 2.0)], dual_in),
            OperationDescriptor("absdiff", "Arithmetic", "Absolute Difference", "opencv.absdiff", "image", [p("enabled", "checkbox", True)], dual_in),
            OperationDescriptor("multiply", "Arithmetic", "Multiply", "opencv.multiply", "image", [p("scale", "slider", 1.0, 0.1, 5.0)], single_in),
            OperationDescriptor("divide", "Arithmetic", "Divide", "opencv.divide", "image", [p("scale", "slider", 1.0, 0.1, 5.0)], single_in),
            OperationDescriptor("add-weighted", "Arithmetic", "Add Weighted", "opencv.addWeighted", "image", [p("alpha", "slider", 0.5, 0.0, 1.0), p("beta", "slider", 0.5, 0.0, 1.0), p("gamma", "slider", 0.0, -128.0, 128.0)], dual_in),
            OperationDescriptor("min", "Arithmetic", "Min", "opencv.min", "image", [p("enabled", "checkbox", True)], dual_in),
            OperationDescriptor("max", "Arithmetic", "Max", "opencv.max", "image", [p("enabled", "checkbox", True)], dual_in),
            # Bitwise - dual input ops (except NOT)
            OperationDescriptor("bitwise-and", "Bitwise", "Bitwise AND", "opencv.bitwiseAnd", "image", [p("enabled", "checkbox", True)], dual_in),
            OperationDescriptor("bitwise-or", "Bitwise", "Bitwise OR", "opencv.bitwiseOr", "image", [p("enabled", "checkbox", True)], dual_in),
            OperationDescriptor("bitwise-xor", "Bitwise", "Bitwise XOR", "opencv.bitwiseXor", "image", [p("enabled", "checkbox", True)], dual_in),
            OperationDescriptor("bitwise-not", "Bitwise", "Bitwise NOT", "opencv.bitwiseNot", "image", [p("enabled", "checkbox", True)], single_in),
            # Transform
            OperationDescriptor("crop", "Transform", "Crop", "opencv.crop", "image", [p("x", "slider", 0, 0, 1000), p("y", "slider", 0, 0, 1000), p("w", "slider", 100, 1, 2000), p("h", "slider", 100, 1, 2000)], single_in),
            OperationDescriptor("resize", "Transform", "Resize", "opencv.resize", "image", [p("width", "slider", 320, 1, 4096), p("height", "slider", 240, 1, 4096)], single_in),
            OperationDescriptor("flip", "Transform", "Flip", "opencv.flip", "image", [p("flipCode", "select", "0", options=["0", "1", "-1"])], single_in),
            OperationDescriptor("normalize", "Transform", "Normalize", "opencv.normalize", "image", [p("alpha", "slider", 0, 0, 255), p("beta", "slider", 255, 0, 255)], single_in),
            OperationDescriptor("extract-channel", "Transform", "Extract Channel", "opencv.extractChannel", "image", [p("channel", "select", "0", options=["0", "1", "2"])], single_in),
            OperationDescriptor("transpose", "Transform", "Transpose", "opencv.transpose", "image", [p("enabled", "checkbox", True)], single_in),
            # Color / Threshold expansion
            OperationDescriptor("hsl-threshold", "Color", "HSL Threshold", "opencv.hslThreshold", "image", [p("hMin", "slider", 0, 0, 179), p("hMax", "slider", 179, 0, 179), p("sMin", "slider", 0, 0, 255), p("sMax", "slider", 255, 0, 255), p("lMin", "slider", 0, 0, 255), p("lMax", "slider", 255, 0, 255)], single_in),
            OperationDescriptor("rgb-threshold", "Color", "RGB Threshold", "opencv.rgbThreshold", "image", [p("rMin", "slider", 0, 0, 255), p("rMax", "slider", 255, 0, 255), p("gMin", "slider", 0, 0, 255), p("gMax", "slider", 255, 0, 255), p("bMin", "slider", 0, 0, 255), p("bMax", "slider", 255, 0, 255)], single_in),
            # Feature Detection
            OperationDescriptor("find-lines", "Detection", "Find Lines", "opencv.findLines", "image", [p("threshold", "slider", 50, 1, 200), p("minLineLength", "slider", 50, 1, 500), p("maxLineGap", "slider", 10, 1, 100)], single_in, [{"name": "out", "type": "image"}, {"name": "lines", "type": "json"}]),
            OperationDescriptor("find-blobs", "Detection", "Find Blobs", "opencv.findBlobs", "image", [p("minArea", "slider", 100, 1, 10000), p("maxArea", "slider", 5000, 1, 50000)], single_in, [{"name": "out", "type": "image"}, {"name": "keypoints", "type": "json"}]),
            # Advanced
            OperationDescriptor("mask", "Advanced", "Mask", "opencv.mask", "image", [p("threshold", "slider", 127, 0, 255)], single_in),
            OperationDescriptor("distance-transform", "Advanced", "Distance Transform", "opencv.distanceTransform", "image", [p("maskSize", "select", "3", options=["3", "5"])], single_in, [{"name": "out", "type": "image"}, {"name": "distances", "type": "json"}]),
            OperationDescriptor("watershed", "Advanced", "Watershed", "opencv.watershed", "image", [p("threshold", "slider", 127, 0, 255)], single_in, [{"name": "out", "type": "image"}, {"name": "segments", "type": "json"}]),
        ]

    def run(
        self,
        op: str,
        node: PipelineNode,
        inputs: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        if op not in self._ops:
            raise ValueError(f"Unsupported operation: {op}")
        return self._ops[op](node, inputs, context)

    @staticmethod
    def source_image(_node: PipelineNode, _inputs: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        import base64 as _b64
        img = None

        # Prefer base64 data sent directly from the frontend
        b64_data = context.get("inputImageBase64")
        if b64_data:
            raw = _b64.b64decode(b64_data)
            img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)

        # Fall back to path-based loading
        if img is None:
            path = context.get("inputImagePath")
            if path:
                if path.startswith(("http://", "https://")):
                    import urllib.request
                    try:
                        req = urllib.request.Request(path, headers={"User-Agent": "NewGRIP/1.0"})
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            data = resp.read()
                        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                    except Exception:
                        img = None
                else:
                    from pathlib import Path as _Path
                    resolved = _Path(path)
                    if not resolved.is_file():
                        public_dir = _Path(__file__).resolve().parents[4] / "apps" / "web" / "public"
                        resolved = public_dir / path.lstrip("/")
                    img = cv2.imread(str(resolved))

        if img is not None:
            return {"out": img}
        # fallback gradient
        img = np.zeros((240, 320, 3), dtype=np.uint8)
        gradient = np.tile(np.linspace(0, 255, 320, dtype=np.uint8), (240, 1))
        img[:, :, 0] = gradient
        img[:, :, 1] = 255 - gradient
        img[:, :, 2] = 180
        return {"out": img}

    @staticmethod
    def noop(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        return {"out": inputs.get("in")}

    @staticmethod
    def blur(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        kernel = int(params.get("kernel", 5))
        if kernel % 2 == 0:
            kernel += 1
        blurred = cv2.GaussianBlur(image, (kernel, kernel), 0)
        return {"out": blurred}

    @staticmethod
    def median_blur(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        kernel = int(params.get("kernel", 7))
        if kernel % 2 == 0:
            kernel += 1
        return {"out": cv2.medianBlur(image, kernel)}

    @staticmethod
    def threshold(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        value = int(params.get("value", 127))
        _, out = cv2.threshold(gray, value, 255, cv2.THRESH_BINARY)
        out_color = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
        return {"out": out_color, "value": {"thresholdUsed": value}}

    @staticmethod
    def threshold_inverse(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        value = int(params.get("value", 120))
        _, out = cv2.threshold(gray, value, 255, cv2.THRESH_BINARY_INV)
        return {"out": cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)}

    @staticmethod
    def adaptive_threshold(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        window = int(params.get("window", 11))
        if window % 2 == 0:
            window += 1
        out = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            max(window, 3),
            2,
        )
        return {"out": cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)}

    @staticmethod
    def canny(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        low = int(params.get("low", 50))
        high = int(params.get("high", 150))
        edges = cv2.Canny(gray, low, high)
        out = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return {"out": out}

    @staticmethod
    def sobel(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        scale = int(params.get("scale", 1))
        grad_x = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3, scale=scale)
        grad_y = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3, scale=scale)
        abs_x = cv2.convertScaleAbs(grad_x)
        abs_y = cv2.convertScaleAbs(grad_y)
        out = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)
        return {"out": cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)}

    @staticmethod
    def laplacian(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ksize = int(params.get("ksize", 3))
        if ksize % 2 == 0:
            ksize += 1
        lap = cv2.Laplacian(gray, cv2.CV_16S, ksize=max(1, ksize))
        out = cv2.convertScaleAbs(lap)
        return {"out": cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)}

    @staticmethod
    def erode(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        iterations = int(params.get("iterations", 1))
        kernel = np.ones((3, 3), np.uint8)
        return {"out": cv2.erode(image, kernel, iterations=max(1, iterations))}

    @staticmethod
    def dilate(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        iterations = int(params.get("iterations", 1))
        kernel = np.ones((3, 3), np.uint8)
        return {"out": cv2.dilate(image, kernel, iterations=max(1, iterations))}

    @staticmethod
    def hsv_threshold(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        if "hMin" in params:
            lower = np.array([int(params["hMin"]), int(params.get("sMin", 0)), int(params.get("vMin", 0))])
            upper = np.array([int(params["hMax"]), int(params.get("sMax", 255)), int(params.get("vMax", 255))])
        else:
            v = int(params.get("value", 115))
            lower = np.array([0, 0, max(0, v - 40)])
            upper = np.array([179, 255, min(255, v + 40)])
        mask = cv2.inRange(hsv, lower, upper)
        return {"out": cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)}

    @staticmethod
    def rgb_to_gray(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return {"out": cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)}

    @staticmethod
    def find_contours(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        out = image.copy()
        cv2.drawContours(out, contours, -1, (0, 255, 255), 2)
        contour_data = {
            "count": len(contours),
            "areas": [float(cv2.contourArea(c)) for c in contours],
            "boundingRects": [list(cv2.boundingRect(c)) for c in contours],
        }
        return {"out": out, "contours": contour_data}

    @staticmethod
    def filter_contours(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        min_area = float(params.get("minArea", 5000))
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered = [c for c in contours if cv2.contourArea(c) >= min_area]
        out = image.copy()
        cv2.drawContours(out, filtered, -1, (255, 0, 255), 2)
        contour_data = {
            "count": len(filtered),
            "areas": [float(cv2.contourArea(c)) for c in filtered],
            "boundingRects": [list(cv2.boundingRect(c)) for c in filtered],
        }
        return {"out": out, "contours": contour_data}

    @staticmethod
    def convex_hulls(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hulls = [cv2.convexHull(c) for c in contours]
        out = image.copy()
        cv2.drawContours(out, hulls, -1, (0, 255, 0), 2)
        hull_data = {
            "count": len(hulls),
            "areas": [float(cv2.contourArea(h)) for h in hulls],
        }
        return {"out": out, "hulls": hull_data}

    @staticmethod
    def nn_classify_stub(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        model = params.get("model", "mobilenet")
        image = inputs.get("in")
        score = 0.71 if isinstance(image, np.ndarray) else 0.5
        return {"out": {"label": "object", "score": score, "model": model}}

    # ---- Arithmetic operations ----

    @staticmethod
    def add(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        in1 = inputs.get("in1") if "in1" in inputs else inputs.get("in")
        in2 = inputs.get("in2")
        img1 = _ensure_image(in1)
        if in2 is not None:
            img2 = _ensure_image(in2)
            return {"out": cv2.add(img1, img2)}
        params = _params(node)
        scalar = float(params.get("scale", 1.0))
        second = np.full_like(img1, int(128 * scalar))
        return {"out": cv2.add(img1, second)}

    @staticmethod
    def subtract(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        in1 = inputs.get("in1") if "in1" in inputs else inputs.get("in")
        in2 = inputs.get("in2")
        img1 = _ensure_image(in1)
        if in2 is not None:
            img2 = _ensure_image(in2)
            return {"out": cv2.subtract(img1, img2)}
        params = _params(node)
        scalar = float(params.get("scale", 1.0))
        second = np.full_like(img1, int(64 * scalar))
        return {"out": cv2.subtract(img1, second)}

    @staticmethod
    def absdiff(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        in1 = inputs.get("in1") if "in1" in inputs else inputs.get("in")
        in2 = inputs.get("in2")
        img1 = _ensure_image(in1)
        if in2 is not None:
            img2 = _ensure_image(in2)
            return {"out": cv2.absdiff(img1, img2)}
        inverted = cv2.bitwise_not(img1)
        return {"out": cv2.absdiff(img1, inverted)}

    @staticmethod
    def multiply(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        params = _params(node)
        scale = float(params.get("scale", 1.0))
        result = cv2.multiply(image, np.array([scale], dtype=np.float64))
        return {"out": np.clip(result, 0, 255).astype(np.uint8)}

    @staticmethod
    def divide(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        params = _params(node)
        scale = max(float(params.get("scale", 1.0)), 0.01)
        result = (image.astype(np.float64) / scale)
        return {"out": np.clip(result, 0, 255).astype(np.uint8)}

    @staticmethod
    def add_weighted(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        in1 = inputs.get("in1") if "in1" in inputs else inputs.get("in")
        in2 = inputs.get("in2")
        img1 = _ensure_image(in1)
        params = _params(node)
        alpha = float(params.get("alpha", 0.5))
        beta = float(params.get("beta", 0.5))
        gamma = float(params.get("gamma", 0.0))
        if in2 is not None:
            img2 = _ensure_image(in2)
            return {"out": cv2.addWeighted(img1, alpha, img2, beta, gamma)}
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return {"out": cv2.addWeighted(img1, alpha, gray_bgr, beta, gamma)}

    @staticmethod
    def img_min(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        in1 = inputs.get("in1") if "in1" in inputs else inputs.get("in")
        in2 = inputs.get("in2")
        img1 = _ensure_image(in1)
        if in2 is not None:
            img2 = _ensure_image(in2)
            return {"out": cv2.min(img1, img2)}
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return {"out": cv2.min(img1, gray_bgr)}

    @staticmethod
    def img_max(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        in1 = inputs.get("in1") if "in1" in inputs else inputs.get("in")
        in2 = inputs.get("in2")
        img1 = _ensure_image(in1)
        if in2 is not None:
            img2 = _ensure_image(in2)
            return {"out": cv2.max(img1, img2)}
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return {"out": cv2.max(img1, gray_bgr)}

    # ---- Bitwise operations ----

    @staticmethod
    def bitwise_and(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        in1 = inputs.get("in1") if "in1" in inputs else inputs.get("in")
        in2 = inputs.get("in2")
        img1 = _ensure_image(in1)
        if in2 is not None:
            img2 = _ensure_image(in2)
            return {"out": cv2.bitwise_and(img1, img2)}
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        return {"out": cv2.bitwise_and(img1, mask_bgr)}

    @staticmethod
    def bitwise_or(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        in1 = inputs.get("in1") if "in1" in inputs else inputs.get("in")
        in2 = inputs.get("in2")
        img1 = _ensure_image(in1)
        if in2 is not None:
            img2 = _ensure_image(in2)
            return {"out": cv2.bitwise_or(img1, img2)}
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        return {"out": cv2.bitwise_or(img1, mask_bgr)}

    @staticmethod
    def bitwise_xor(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        in1 = inputs.get("in1") if "in1" in inputs else inputs.get("in")
        in2 = inputs.get("in2")
        img1 = _ensure_image(in1)
        if in2 is not None:
            img2 = _ensure_image(in2)
            return {"out": cv2.bitwise_xor(img1, img2)}
        inverted = cv2.bitwise_not(img1)
        return {"out": cv2.bitwise_xor(img1, inverted)}

    @staticmethod
    def bitwise_not(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        return {"out": cv2.bitwise_not(image)}

    # ---- Transform operations ----

    @staticmethod
    def crop(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        params = _params(node)
        h_img, w_img = image.shape[:2]
        x = max(0, min(int(params.get("x", 0)), w_img - 1))
        y = max(0, min(int(params.get("y", 0)), h_img - 1))
        w = max(1, int(params.get("w", 100)))
        h = max(1, int(params.get("h", 100)))
        x2 = min(x + w, w_img)
        y2 = min(y + h, h_img)
        cropped = image[y:y2, x:x2].copy()
        if cropped.size == 0:
            cropped = image.copy()
        return {"out": cropped}

    @staticmethod
    def resize(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        params = _params(node)
        width = max(1, int(params.get("width", 320)))
        height = max(1, int(params.get("height", 240)))
        return {"out": cv2.resize(image, (width, height))}

    @staticmethod
    def flip(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        params = _params(node)
        flip_code = int(params.get("flipCode", 0))
        return {"out": cv2.flip(image, flip_code)}

    @staticmethod
    def normalize(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        params = _params(node)
        alpha = float(params.get("alpha", 0))
        beta = float(params.get("beta", 255))
        result = cv2.normalize(image, None, alpha=alpha, beta=beta, norm_type=cv2.NORM_MINMAX)
        return {"out": result}

    @staticmethod
    def extract_channel(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        params = _params(node)
        channel = int(params.get("channel", 0))
        channel = max(0, min(channel, 2))
        single = image[:, :, channel]
        return {"out": cv2.cvtColor(single, cv2.COLOR_GRAY2BGR)}

    @staticmethod
    def transpose(_node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        image = _ensure_image(inputs.get("in"))
        return {"out": cv2.transpose(image)}

    # ---- Color / Threshold expansion ----

    @staticmethod
    def hsl_threshold(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        hls = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        h_min = int(params.get("hMin", 0))
        h_max = int(params.get("hMax", 179))
        s_min = int(params.get("sMin", 0))
        s_max = int(params.get("sMax", 255))
        l_min = int(params.get("lMin", 0))
        l_max = int(params.get("lMax", 255))
        lower = np.array([h_min, l_min, s_min])
        upper = np.array([h_max, l_max, s_max])
        mask = cv2.inRange(hls, lower, upper)
        return {"out": cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)}

    @staticmethod
    def rgb_threshold(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        r_min = int(params.get("rMin", 0))
        r_max = int(params.get("rMax", 255))
        g_min = int(params.get("gMin", 0))
        g_max = int(params.get("gMax", 255))
        b_min = int(params.get("bMin", 0))
        b_max = int(params.get("bMax", 255))
        lower = np.array([b_min, g_min, r_min])
        upper = np.array([b_max, g_max, r_max])
        mask = cv2.inRange(image, lower, upper)
        return {"out": cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)}

    # ---- Feature detection ----

    @staticmethod
    def find_lines(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        threshold = int(params.get("threshold", 50))
        min_line_length = int(params.get("minLineLength", 50))
        max_line_gap = int(params.get("maxLineGap", 10))
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold, minLineLength=min_line_length, maxLineGap=max_line_gap)
        out = image.copy()
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(out, (x1, y1), (x2, y2), (0, 0, 255), 2)
        line_data = {"count": 0, "endpoints": []}
        if lines is not None:
            line_data["count"] = len(lines)
            line_data["endpoints"] = [[int(v) for v in line[0]] for line in lines]
        return {"out": out, "lines": line_data}

    @staticmethod
    def find_blobs(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        blob_params = cv2.SimpleBlobDetector_Params()
        blob_params.filterByArea = True
        blob_params.minArea = float(params.get("minArea", 100))
        blob_params.maxArea = float(params.get("maxArea", 5000))
        detector = cv2.SimpleBlobDetector_create(blob_params)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        keypoints = detector.detect(gray)
        out = cv2.drawKeypoints(image, keypoints, np.array([]), (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        kp_data = {
            "count": len(keypoints),
            "centers": [[kp.pt[0], kp.pt[1]] for kp in keypoints],
            "sizes": [kp.size for kp in keypoints],
        }
        return {"out": out, "keypoints": kp_data}

    # ---- Advanced operations ----

    @staticmethod
    def mask(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh_val = int(params.get("threshold", 127))
        _, mask_img = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
        return {"out": cv2.bitwise_and(image, image, mask=mask_img)}

    @staticmethod
    def distance_transform(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        mask_size = int(params.get("maskSize", 3))
        if mask_size not in (3, 5):
            mask_size = 3
        dist = cv2.distanceTransform(binary, cv2.DIST_L2, mask_size)
        dist_norm = cv2.normalize(dist, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        dist_data = {
            "maxDistance": float(dist.max()),
            "meanDistance": float(dist.mean()),
        }
        return {"out": cv2.cvtColor(dist_norm, cv2.COLOR_GRAY2BGR), "distances": dist_data}

    @staticmethod
    def watershed(node: PipelineNode, inputs: dict[str, Any], _context: dict[str, Any]) -> dict[str, Any]:
        params = _params(node)
        image = _ensure_image(inputs.get("in"))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh_val = int(params.get("threshold", 127))
        _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
        dist = cv2.distanceTransform(binary, cv2.DIST_L2, 3)
        _, sure_fg = cv2.threshold(dist, 0.5 * dist.max() if dist.max() > 0 else 0, 255, cv2.THRESH_BINARY)
        sure_fg = sure_fg.astype(np.uint8)
        sure_bg = cv2.dilate(binary, np.ones((3, 3), np.uint8), iterations=3)
        unknown = cv2.subtract(sure_bg, sure_fg)
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        out = image.copy()
        markers = cv2.watershed(out, markers)
        out[markers == -1] = [0, 0, 255]
        unique_labels = set(markers.flatten())
        unique_labels.discard(-1)
        unique_labels.discard(0)
        unique_labels.discard(1)
        seg_data = {"count": len(unique_labels)}
        return {"out": out, "segments": seg_data}
