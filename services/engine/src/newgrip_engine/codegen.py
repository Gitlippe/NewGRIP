from __future__ import annotations

from typing import Any

from .models import PipelineDocumentV1, PipelineNode
from .validator import topological_order


def _params(node: PipelineNode) -> dict[str, Any]:
    return {p.name: p.value for p in node.params}


# ---------------------------------------------------------------------------
# Python code-generation helpers
# ---------------------------------------------------------------------------

def _py_skip(_node: PipelineNode, _p: dict[str, Any]) -> str | None:
    return None


def _py_gaussian_blur(_node: PipelineNode, p: dict[str, Any]) -> str:
    k = int(p.get("kernel", 5))
    if k % 2 == 0:
        k += 1
    return f"current = cv2.GaussianBlur(current, ({k}, {k}), 0)"


def _py_median_blur(_node: PipelineNode, p: dict[str, Any]) -> str:
    k = int(p.get("kernel", 7))
    if k % 2 == 0:
        k += 1
    return f"current = cv2.medianBlur(current, {k})"


def _py_blur(_node: PipelineNode, p: dict[str, Any]) -> str:
    k = int(p.get("kernel", 9))
    if k % 2 == 0:
        k += 1
    return f"current = cv2.blur(current, ({k}, {k}))"


def _py_threshold(_node: PipelineNode, p: dict[str, Any]) -> str:
    v = int(p.get("value", 130))
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        f"        _, thresh = cv2.threshold(gray, {v}, 255, cv2.THRESH_BINARY)\n"
        "        current = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)"
    )


def _py_threshold_inverse(_node: PipelineNode, p: dict[str, Any]) -> str:
    v = int(p.get("value", 120))
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        f"        _, thresh = cv2.threshold(gray, {v}, 255, cv2.THRESH_BINARY_INV)\n"
        "        current = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)"
    )


def _py_adaptive_threshold(_node: PipelineNode, p: dict[str, Any]) -> str:
    w = int(p.get("window", 11))
    if w % 2 == 0:
        w += 1
    w = max(w, 3)
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        f"        at = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, {w}, 2)\n"
        "        current = cv2.cvtColor(at, cv2.COLOR_GRAY2BGR)"
    )


def _py_canny(_node: PipelineNode, p: dict[str, Any]) -> str:
    low = int(p.get("low", 60))
    high = int(p.get("high", 170))
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        f"        edges = cv2.Canny(gray, {low}, {high})\n"
        "        current = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)"
    )


def _py_sobel(_node: PipelineNode, p: dict[str, Any]) -> str:
    scale = int(p.get("scale", 1))
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        f"        grad_x = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3, scale={scale})\n"
        f"        grad_y = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3, scale={scale})\n"
        "        abs_x = cv2.convertScaleAbs(grad_x)\n"
        "        abs_y = cv2.convertScaleAbs(grad_y)\n"
        "        current = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)\n"
        "        current = cv2.cvtColor(current, cv2.COLOR_GRAY2BGR)"
    )


def _py_laplacian(_node: PipelineNode, p: dict[str, Any]) -> str:
    ksize = int(p.get("ksize", 3))
    if ksize % 2 == 0:
        ksize += 1
    ksize = max(1, ksize)
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        f"        lap = cv2.Laplacian(gray, cv2.CV_16S, ksize={ksize})\n"
        "        current = cv2.convertScaleAbs(lap)\n"
        "        current = cv2.cvtColor(current, cv2.COLOR_GRAY2BGR)"
    )


def _py_erode(_node: PipelineNode, p: dict[str, Any]) -> str:
    n = int(p.get("iterations", 1))
    return f"current = cv2.erode(current, np.ones((3, 3), np.uint8), iterations={max(1, n)})"


def _py_dilate(_node: PipelineNode, p: dict[str, Any]) -> str:
    n = int(p.get("iterations", 1))
    return f"current = cv2.dilate(current, np.ones((3, 3), np.uint8), iterations={max(1, n)})"


def _py_hsv_threshold(_node: PipelineNode, p: dict[str, Any]) -> str:
    v = int(p.get("value", 115))
    lo = max(0, v - 40)
    hi = min(255, v + 40)
    return (
        "hsv = cv2.cvtColor(current, cv2.COLOR_BGR2HSV)\n"
        f"        mask = cv2.inRange(hsv, np.array([0, 0, {lo}]), np.array([179, 255, {hi}]))\n"
        "        current = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)"
    )


def _py_rgb_to_gray(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return (
        "current = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        "        current = cv2.cvtColor(current, cv2.COLOR_GRAY2BGR)"
    )


def _py_find_contours(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        "        _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)\n"
        "        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)\n"
        "        cv2.drawContours(current, contours, -1, (0, 255, 255), 2)"
    )


def _py_filter_contours(_node: PipelineNode, p: dict[str, Any]) -> str:
    min_area = int(float(p.get("minArea", 5000)))
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        "        _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)\n"
        "        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)\n"
        f"        contours = [c for c in contours if cv2.contourArea(c) >= {min_area}]\n"
        "        cv2.drawContours(current, contours, -1, (255, 0, 255), 2)"
    )


def _py_convex_hulls(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        "        _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)\n"
        "        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)\n"
        "        hulls = [cv2.convexHull(c) for c in contours]\n"
        "        cv2.drawContours(current, hulls, -1, (0, 255, 0), 2)"
    )


def _py_noop(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return "pass  # noop"


# Arithmetic operations
def _py_add(_node: PipelineNode, p: dict[str, Any]) -> str:
    scale = float(p.get("scale", 1.0))
    return (
        f"second = np.full_like(current, int(128 * {scale}))\n"
        f"        current = cv2.add(current, second)"
    )


def _py_subtract(_node: PipelineNode, p: dict[str, Any]) -> str:
    scale = float(p.get("scale", 1.0))
    return (
        f"second = np.full_like(current, int(64 * {scale}))\n"
        f"        current = cv2.subtract(current, second)"
    )


def _py_absdiff(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return (
        "inverted = cv2.bitwise_not(current)\n"
        "        current = cv2.absdiff(current, inverted)"
    )


def _py_multiply(_node: PipelineNode, p: dict[str, Any]) -> str:
    scale = float(p.get("scale", 1.0))
    return (
        f"current = cv2.multiply(current, np.array([{scale}], dtype=np.float64))\n"
        "        current = np.clip(current, 0, 255).astype(np.uint8)"
    )


def _py_divide(_node: PipelineNode, p: dict[str, Any]) -> str:
    scale = max(float(p.get("scale", 1.0)), 0.01)
    return (
        f"current = (current.astype(np.float64) / {scale})\n"
        "        current = np.clip(current, 0, 255).astype(np.uint8)"
    )


def _py_add_weighted(_node: PipelineNode, p: dict[str, Any]) -> str:
    alpha = float(p.get("alpha", 0.5))
    beta = float(p.get("beta", 0.5))
    gamma = float(p.get("gamma", 0.0))
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        "        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)\n"
        f"        current = cv2.addWeighted(current, {alpha}, gray_bgr, {beta}, {gamma})"
    )


def _py_img_min(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        "        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)\n"
        "        current = cv2.min(current, gray_bgr)"
    )


def _py_img_max(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        "        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)\n"
        "        current = cv2.max(current, gray_bgr)"
    )


# Bitwise operations
def _py_bitwise_and(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return "current = cv2.bitwise_and(current, current)"


def _py_bitwise_or(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return "current = cv2.bitwise_or(current, current)"


def _py_bitwise_xor(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return "current = cv2.bitwise_xor(current, current)"


def _py_bitwise_not(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return "current = cv2.bitwise_not(current)"


# Transform operations
def _py_crop(_node: PipelineNode, p: dict[str, Any]) -> str:
    x = int(p.get("x", 0))
    y = int(p.get("y", 0))
    w = int(p.get("w", 100))
    h = int(p.get("h", 100))
    return f"current = current[{y}:{y}+{h}, {x}:{x}+{w}].copy()"


def _py_resize(_node: PipelineNode, p: dict[str, Any]) -> str:
    width = int(p.get("width", 320))
    height = int(p.get("height", 240))
    return f"current = cv2.resize(current, ({width}, {height}))"


def _py_flip(_node: PipelineNode, p: dict[str, Any]) -> str:
    fc = int(p.get("flipCode", 0))
    return f"current = cv2.flip(current, {fc})"


def _py_normalize(_node: PipelineNode, p: dict[str, Any]) -> str:
    alpha = float(p.get("alpha", 0))
    beta = float(p.get("beta", 255))
    return f"current = cv2.normalize(current, None, alpha={alpha}, beta={beta}, norm_type=cv2.NORM_MINMAX)"


def _py_extract_channel(_node: PipelineNode, p: dict[str, Any]) -> str:
    ch = int(p.get("channel", 0))
    return (
        f"ch = current[:, :, {ch}]\n"
        "        current = cv2.cvtColor(ch, cv2.COLOR_GRAY2BGR)"
    )


def _py_transpose(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return "current = cv2.transpose(current)"


# Color thresholds
def _py_hsl_threshold(_node: PipelineNode, p: dict[str, Any]) -> str:
    h_min = int(p.get("hMin", 0))
    h_max = int(p.get("hMax", 179))
    s_min = int(p.get("sMin", 0))
    s_max = int(p.get("sMax", 255))
    l_min = int(p.get("lMin", 0))
    l_max = int(p.get("lMax", 255))
    return (
        "hls = cv2.cvtColor(current, cv2.COLOR_BGR2HLS)\n"
        f"        mask = cv2.inRange(hls, np.array([{h_min}, {l_min}, {s_min}]), np.array([{h_max}, {l_max}, {s_max}]))\n"
        "        current = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)"
    )


def _py_rgb_threshold(_node: PipelineNode, p: dict[str, Any]) -> str:
    r_min = int(p.get("rMin", 0))
    r_max = int(p.get("rMax", 255))
    g_min = int(p.get("gMin", 0))
    g_max = int(p.get("gMax", 255))
    b_min = int(p.get("bMin", 0))
    b_max = int(p.get("bMax", 255))
    return (
        f"mask = cv2.inRange(current, np.array([{b_min}, {g_min}, {r_min}]), np.array([{b_max}, {g_max}, {r_max}]))\n"
        "        current = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)"
    )


# Feature detection
def _py_find_lines(_node: PipelineNode, p: dict[str, Any]) -> str:
    threshold = int(p.get("threshold", 50))
    min_len = int(p.get("minLineLength", 50))
    max_gap = int(p.get("maxLineGap", 10))
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        f"        edges = cv2.Canny(gray, 50, 150)\n"
        f"        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, {threshold}, minLineLength={min_len}, maxLineGap={max_gap})\n"
        "        if lines is not None:\n"
        "            for line in lines:\n"
        "                x1, y1, x2, y2 = line[0]\n"
        "                cv2.line(current, (x1, y1), (x2, y2), (0, 0, 255), 2)"
    )


def _py_find_blobs(_node: PipelineNode, p: dict[str, Any]) -> str:
    min_area = float(p.get("minArea", 100))
    max_area = float(p.get("maxArea", 5000))
    return (
        "params = cv2.SimpleBlobDetector_Params()\n"
        "        params.filterByArea = True\n"
        f"        params.minArea = {min_area}\n"
        f"        params.maxArea = {max_area}\n"
        "        detector = cv2.SimpleBlobDetector_create(params)\n"
        "        gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        "        keypoints = detector.detect(gray)\n"
        "        current = cv2.drawKeypoints(current, keypoints, np.array([]), (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)"
    )


# Advanced operations
def _py_mask(_node: PipelineNode, p: dict[str, Any]) -> str:
    thresh = int(p.get("threshold", 127))
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        f"        _, mask = cv2.threshold(gray, {thresh}, 255, cv2.THRESH_BINARY)\n"
        "        current = cv2.bitwise_and(current, current, mask=mask)"
    )


def _py_distance_transform(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        "        _, bw = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)\n"
        "        dist = cv2.distanceTransform(bw, cv2.DIST_L2, 5)\n"
        "        current = cv2.normalize(dist, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)\n"
        "        current = cv2.cvtColor(current, cv2.COLOR_GRAY2BGR)"
    )


def _py_watershed(_node: PipelineNode, _p: dict[str, Any]) -> str:
    return (
        "gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)\n"
        "        _, bw = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)\n"
        "        dist = cv2.distanceTransform(bw, cv2.DIST_L2, 5)\n"
        "        _, markers = cv2.threshold(dist, 0.5 * dist.max(), 255, cv2.THRESH_BINARY)\n"
        "        markers = markers.astype(np.int32)\n"
        "        cv2.watershed(current, markers)\n"
        "        current[markers == -1] = [0, 0, 255]"
    )


PYTHON_CODEGEN_MAP: dict[str, object] = {
    "source.image": _py_skip,
    "opencv.noop": _py_noop,
    "opencv.gaussianBlur": _py_gaussian_blur,
    "opencv.medianBlur": _py_median_blur,
    "opencv.blur": _py_blur,
    "opencv.threshold": _py_threshold,
    "opencv.thresholdInverse": _py_threshold_inverse,
    "opencv.adaptiveThreshold": _py_adaptive_threshold,
    "opencv.canny": _py_canny,
    "opencv.sobel": _py_sobel,
    "opencv.laplacian": _py_laplacian,
    "opencv.erode": _py_erode,
    "opencv.dilate": _py_dilate,
    "opencv.hsvThreshold": _py_hsv_threshold,
    "opencv.rgbToGray": _py_rgb_to_gray,
    "opencv.findContours": _py_find_contours,
    "opencv.filterContours": _py_filter_contours,
    "opencv.convexHulls": _py_convex_hulls,
    "opencv.add": _py_add,
    "opencv.subtract": _py_subtract,
    "opencv.absdiff": _py_absdiff,
    "opencv.multiply": _py_multiply,
    "opencv.divide": _py_divide,
    "opencv.addWeighted": _py_add_weighted,
    "opencv.min": _py_img_min,
    "opencv.max": _py_img_max,
    "opencv.bitwiseAnd": _py_bitwise_and,
    "opencv.bitwiseOr": _py_bitwise_or,
    "opencv.bitwiseXor": _py_bitwise_xor,
    "opencv.bitwiseNot": _py_bitwise_not,
    "opencv.crop": _py_crop,
    "opencv.resize": _py_resize,
    "opencv.flip": _py_flip,
    "opencv.normalize": _py_normalize,
    "opencv.extractChannel": _py_extract_channel,
    "opencv.transpose": _py_transpose,
    "opencv.hslThreshold": _py_hsl_threshold,
    "opencv.rgbThreshold": _py_rgb_threshold,
    "opencv.findLines": _py_find_lines,
    "opencv.findBlobs": _py_find_blobs,
    "opencv.mask": _py_mask,
    "opencv.distanceTransform": _py_distance_transform,
    "opencv.watershed": _py_watershed,
    "nn.classify_stub": _py_noop,
}


def _needs_numpy(ops: list[str]) -> bool:
    numpy_ops = {
        "opencv.erode", "opencv.dilate", "opencv.hsvThreshold",
        "opencv.hslThreshold", "opencv.rgbThreshold",
        "opencv.findLines", "opencv.distanceTransform", "opencv.watershed",
        "opencv.add", "opencv.subtract", "opencv.multiply", "opencv.divide",
        "opencv.findBlobs", "opencv.mask", "opencv.absdiff",
        "opencv.addWeighted", "opencv.min", "opencv.max",
    }
    return bool(set(ops) & numpy_ops)


def _ordered_nodes(pipeline: PipelineDocumentV1) -> list[PipelineNode]:
    order = topological_order(pipeline)
    node_map = {n.id: n for n in pipeline.nodes}
    return [node_map[nid] for nid in order]


# ---------------------------------------------------------------------------
# Python generator
# ---------------------------------------------------------------------------

def generate_python(pipeline: PipelineDocumentV1, class_name: str) -> str:
    nodes = _ordered_nodes(pipeline)
    ops = [n.op for n in nodes]

    imports = ["import cv2"]
    if _needs_numpy(ops):
        imports.append("import numpy as np")

    lines = imports + ["", f"class {class_name}:", "    def run(self, image):", "        current = image"]

    for node in nodes:
        p = _params(node)
        gen_fn = PYTHON_CODEGEN_MAP.get(node.op)
        if gen_fn is not None:
            code = gen_fn(node, p)
            if code is not None:
                lines.append(f"        {code}")
        else:
            lines.append(f"        # {node.id}:{node.op} (unsupported)")

    lines.append("        return current")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Java code-generation helpers
# ---------------------------------------------------------------------------

def _java_code(node: PipelineNode, p: dict[str, Any]) -> str | None:
    op = node.op
    if op == "source.image":
        return None
    if op in ("opencv.gaussianBlur", "opencv.blur"):
        k = int(p.get("kernel", 5))
        if k % 2 == 0:
            k += 1
        return f"Imgproc.GaussianBlur(src, dst, new Size({k}, {k}), 0); src = dst.clone();"
    if op == "opencv.medianBlur":
        k = int(p.get("kernel", 7))
        if k % 2 == 0:
            k += 1
        return f"Imgproc.medianBlur(src, dst, {k}); src = dst.clone();"
    if op == "opencv.threshold":
        v = int(p.get("value", 130))
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            f"        Imgproc.threshold(gray, dst, {v}, 255, Imgproc.THRESH_BINARY);\n"
            "        Imgproc.cvtColor(dst, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.thresholdInverse":
        v = int(p.get("value", 120))
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            f"        Imgproc.threshold(gray, dst, {v}, 255, Imgproc.THRESH_BINARY_INV);\n"
            "        Imgproc.cvtColor(dst, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.adaptiveThreshold":
        w = int(p.get("window", 11))
        if w % 2 == 0:
            w += 1
        w = max(w, 3)
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            f"        Imgproc.adaptiveThreshold(gray, dst, 255, Imgproc.ADAPTIVE_THRESH_GAUSSIAN_C, Imgproc.THRESH_BINARY, {w}, 2);\n"
            "        Imgproc.cvtColor(dst, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.canny":
        low = int(p.get("low", 60))
        high = int(p.get("high", 170))
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            f"        Imgproc.Canny(gray, dst, {low}, {high});\n"
            "        Imgproc.cvtColor(dst, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.sobel":
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.Sobel(gray, dst, CvType.CV_8U, 1, 0, 3);\n"
            "        Imgproc.cvtColor(dst, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.laplacian":
        ksize = int(p.get("ksize", 3))
        if ksize % 2 == 0:
            ksize += 1
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            f"        Imgproc.Laplacian(gray, dst, CvType.CV_16S, {max(1, ksize)});\n"
            "        Core.convertScaleAbs(dst, src);\n"
            "        Imgproc.cvtColor(src, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.erode":
        n = int(p.get("iterations", 1))
        return f"Imgproc.erode(src, dst, new Mat(), new Point(-1, -1), {max(1, n)}); src = dst.clone();"
    if op == "opencv.dilate":
        n = int(p.get("iterations", 1))
        return f"Imgproc.dilate(src, dst, new Mat(), new Point(-1, -1), {max(1, n)}); src = dst.clone();"
    if op == "opencv.rgbToGray":
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.cvtColor(gray, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.findContours":
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.threshold(gray, dst, 80, 255, Imgproc.THRESH_BINARY);\n"
            "        List<MatOfPoint> contours = new ArrayList<>();\n"
            "        Imgproc.findContours(dst, contours, new Mat(), Imgproc.RETR_EXTERNAL, Imgproc.CHAIN_APPROX_SIMPLE);\n"
            "        Imgproc.drawContours(src, contours, -1, new Scalar(0, 255, 255), 2);"
        )
    if op == "opencv.bitwiseNot":
        return "Core.bitwise_not(src, src);"
    if op == "opencv.bitwiseAnd":
        return "Core.bitwise_and(src, src, src);"
    if op == "opencv.bitwiseOr":
        return "Core.bitwise_or(src, src, src);"
    if op == "opencv.bitwiseXor":
        return "Core.bitwise_xor(src, src, src);"
    if op == "opencv.flip":
        fc = int(p.get("flipCode", 0))
        return f"Core.flip(src, dst, {fc}); src = dst.clone();"
    if op == "opencv.transpose":
        return "Core.transpose(src, dst); src = dst.clone();"
    if op == "opencv.normalize":
        alpha = float(p.get("alpha", 0))
        beta = float(p.get("beta", 255))
        return f"Core.normalize(src, dst, {alpha}, {beta}, Core.NORM_MINMAX); src = dst.clone();"
    if op == "opencv.resize":
        width = int(p.get("width", 320))
        height = int(p.get("height", 240))
        return f"Imgproc.resize(src, dst, new Size({width}, {height})); src = dst.clone();"
    if op == "opencv.crop":
        x = int(p.get("x", 0))
        y = int(p.get("y", 0))
        w = int(p.get("w", 100))
        h = int(p.get("h", 100))
        return f"src = new Mat(src, new Rect({x}, {y}, {w}, {h})).clone();"
    if op == "opencv.hsvThreshold":
        h_min = int(p.get("hMin", 0))
        h_max = int(p.get("hMax", 179))
        s_min = int(p.get("sMin", 0))
        s_max = int(p.get("sMax", 255))
        v_min = int(p.get("vMin", 0))
        v_max = int(p.get("vMax", 255))
        return (
            "Imgproc.cvtColor(src, dst, Imgproc.COLOR_BGR2HSV);\n"
            f"        Core.inRange(dst, new Scalar({h_min}, {s_min}, {v_min}), new Scalar({h_max}, {s_max}, {v_max}), dst);\n"
            "        Imgproc.cvtColor(dst, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.hslThreshold":
        h_min = int(p.get("hMin", 0))
        h_max = int(p.get("hMax", 179))
        s_min = int(p.get("sMin", 0))
        s_max = int(p.get("sMax", 255))
        l_min = int(p.get("lMin", 0))
        l_max = int(p.get("lMax", 255))
        return (
            "Imgproc.cvtColor(src, dst, Imgproc.COLOR_BGR2HLS);\n"
            f"        Core.inRange(dst, new Scalar({h_min}, {l_min}, {s_min}), new Scalar({h_max}, {l_max}, {s_max}), dst);\n"
            "        Imgproc.cvtColor(dst, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.rgbThreshold":
        r_min = int(p.get("rMin", 0))
        r_max = int(p.get("rMax", 255))
        g_min = int(p.get("gMin", 0))
        g_max = int(p.get("gMax", 255))
        b_min = int(p.get("bMin", 0))
        b_max = int(p.get("bMax", 255))
        return (
            f"Core.inRange(src, new Scalar({b_min}, {g_min}, {r_min}), new Scalar({b_max}, {g_max}, {r_max}), dst);\n"
            "        Imgproc.cvtColor(dst, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.add":
        scale = float(p.get("scale", 1.0))
        return (
            f"Mat second = new Mat(src.size(), src.type(), new Scalar({int(128 * scale)}, {int(128 * scale)}, {int(128 * scale)}));\n"
            "        Core.add(src, second, src);"
        )
    if op == "opencv.subtract":
        scale = float(p.get("scale", 1.0))
        return (
            f"Mat second = new Mat(src.size(), src.type(), new Scalar({int(64 * scale)}, {int(64 * scale)}, {int(64 * scale)}));\n"
            "        Core.subtract(src, second, src);"
        )
    if op == "opencv.absdiff":
        return (
            "Core.bitwise_not(src, dst);\n"
            "        Core.absdiff(src, dst, src);"
        )
    if op == "opencv.multiply":
        scale = float(p.get("scale", 1.0))
        return f"Core.multiply(src, new Scalar({scale}, {scale}, {scale}), src); src.convertTo(src, CvType.CV_8U);"
    if op == "opencv.divide":
        scale = max(float(p.get("scale", 1.0)), 0.01)
        return f"Core.divide(src, new Scalar({scale}, {scale}, {scale}), src); src.convertTo(src, CvType.CV_8U);"
    if op == "opencv.addWeighted":
        alpha = float(p.get("alpha", 0.5))
        beta = float(p.get("beta", 0.5))
        gamma = float(p.get("gamma", 0.0))
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.cvtColor(gray, dst, Imgproc.COLOR_GRAY2BGR);\n"
            f"        Core.addWeighted(src, {alpha}, dst, {beta}, {gamma}, src);"
        )
    if op == "opencv.min":
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.cvtColor(gray, dst, Imgproc.COLOR_GRAY2BGR);\n"
            "        Core.min(src, dst, src);"
        )
    if op == "opencv.max":
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.cvtColor(gray, dst, Imgproc.COLOR_GRAY2BGR);\n"
            "        Core.max(src, dst, src);"
        )
    if op == "opencv.mask":
        thresh = int(p.get("threshold", 127))
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            f"        Imgproc.threshold(gray, dst, {thresh}, 255, Imgproc.THRESH_BINARY);\n"
            "        Core.bitwise_and(src, src, src, dst);"
        )
    if op == "opencv.distanceTransform":
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.threshold(gray, dst, 80, 255, Imgproc.THRESH_BINARY);\n"
            "        Mat dist = new Mat();\n"
            "        Imgproc.distanceTransform(dst, dist, Imgproc.DIST_L2, 5);\n"
            "        Core.normalize(dist, dist, 0, 255, Core.NORM_MINMAX);\n"
            "        dist.convertTo(gray, CvType.CV_8U);\n"
            "        Imgproc.cvtColor(gray, src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.watershed":
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.threshold(gray, dst, 80, 255, Imgproc.THRESH_BINARY);\n"
            "        Mat dist = new Mat();\n"
            "        Imgproc.distanceTransform(dst, dist, Imgproc.DIST_L2, 5);\n"
            "        Mat markers = new Mat();\n"
            "        Imgproc.threshold(dist, markers, 0.5 * 255, 255, Imgproc.THRESH_BINARY);\n"
            "        markers.convertTo(markers, CvType.CV_32S);\n"
            "        Imgproc.watershed(src, markers);"
        )
    if op == "opencv.findLines":
        threshold = int(p.get("threshold", 50))
        min_len = int(p.get("minLineLength", 50))
        max_gap = int(p.get("maxLineGap", 10))
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.Canny(gray, dst, 50, 150);\n"
            "        Mat lines = new Mat();\n"
            f"        Imgproc.HoughLinesP(dst, lines, 1, Math.PI / 180, {threshold}, {min_len}, {max_gap});\n"
            "        for (int i = 0; i < lines.rows(); i++) {\n"
            "            double[] l = lines.get(i, 0);\n"
            "            Imgproc.line(src, new Point(l[0], l[1]), new Point(l[2], l[3]), new Scalar(0, 0, 255), 2);\n"
            "        }"
        )
    if op == "opencv.findBlobs":
        return (
            "FeatureDetector detector = FeatureDetector.create(FeatureDetector.SIMPLEBLOB);\n"
            "        Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        MatOfKeyPoint keypoints = new MatOfKeyPoint();\n"
            "        detector.detect(gray, keypoints);\n"
            "        Features2d.drawKeypoints(src, keypoints, src);"
        )
    if op == "opencv.filterContours":
        min_area = int(float(p.get("minArea", 5000)))
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.threshold(gray, dst, 80, 255, Imgproc.THRESH_BINARY);\n"
            "        List<MatOfPoint> contours = new ArrayList<>();\n"
            "        Imgproc.findContours(dst, contours, new Mat(), Imgproc.RETR_EXTERNAL, Imgproc.CHAIN_APPROX_SIMPLE);\n"
            "        List<MatOfPoint> filtered = new ArrayList<>();\n"
            "        for (MatOfPoint c : contours) {\n"
            f"            if (Imgproc.contourArea(c) >= {min_area}) filtered.add(c);\n"
            "        }\n"
            "        Imgproc.drawContours(src, filtered, -1, new Scalar(255, 0, 255), 2);"
        )
    if op == "opencv.convexHulls":
        return (
            "Imgproc.cvtColor(src, gray, Imgproc.COLOR_BGR2GRAY);\n"
            "        Imgproc.threshold(gray, dst, 80, 255, Imgproc.THRESH_BINARY);\n"
            "        List<MatOfPoint> contours = new ArrayList<>();\n"
            "        Imgproc.findContours(dst, contours, new Mat(), Imgproc.RETR_EXTERNAL, Imgproc.CHAIN_APPROX_SIMPLE);\n"
            "        List<MatOfPoint> hulls = new ArrayList<>();\n"
            "        for (MatOfPoint c : contours) {\n"
            "            MatOfInt hullIdx = new MatOfInt();\n"
            "            Imgproc.convexHull(c, hullIdx);\n"
            "            MatOfPoint hull = new MatOfPoint();\n"
            "            hull.fromArray(hullIdx.toArray().length > 0 ? new Point[0] : new Point[0]);\n"
            "            hulls.add(c);\n"
            "        }\n"
            "        Imgproc.drawContours(src, hulls, -1, new Scalar(0, 255, 0), 2);"
        )
    if op == "opencv.extractChannel":
        ch = int(p.get("channel", 0))
        return (
            "List<Mat> channels = new ArrayList<>();\n"
            "        Core.split(src, channels);\n"
            f"        Imgproc.cvtColor(channels.get({ch}), src, Imgproc.COLOR_GRAY2BGR);"
        )
    if op == "opencv.noop":
        return "// noop"
    # fallback
    return f"// {node.id}:{op} (unsupported)"


def generate_java(pipeline: PipelineDocumentV1, class_name: str) -> str:
    nodes = _ordered_nodes(pipeline)

    header = (
        "import org.opencv.core.*;\n"
        "import org.opencv.imgproc.Imgproc;\n"
        "import java.util.ArrayList;\n"
        "import java.util.List;\n\n"
        f"public class {class_name} {{\n"
        "    public Mat run(Mat image) {\n"
        "        Mat src = image.clone();\n"
        "        Mat dst = new Mat();\n"
        "        Mat gray = new Mat();\n"
    )

    body_lines: list[str] = []
    for node in nodes:
        p = _params(node)
        code = _java_code(node, p)
        if code is not None:
            body_lines.append(f"        {code}")

    footer = (
        "        return src;\n"
        "    }\n"
        "}\n"
    )

    return header + "\n".join(body_lines) + ("\n" if body_lines else "") + footer


# ---------------------------------------------------------------------------
# C++ code-generation helpers
# ---------------------------------------------------------------------------

def _cpp_code(node: PipelineNode, p: dict[str, Any]) -> str | None:
    op = node.op
    if op == "source.image":
        return None
    if op in ("opencv.gaussianBlur", "opencv.blur"):
        k = int(p.get("kernel", 5))
        if k % 2 == 0:
            k += 1
        return f"cv::GaussianBlur(src, dst, cv::Size({k}, {k}), 0); src = dst.clone();"
    if op == "opencv.medianBlur":
        k = int(p.get("kernel", 7))
        if k % 2 == 0:
            k += 1
        return f"cv::medianBlur(src, dst, {k}); src = dst.clone();"
    if op == "opencv.threshold":
        v = int(p.get("value", 130))
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            f"    cv::threshold(gray, dst, {v}, 255, cv::THRESH_BINARY);\n"
            "    cv::cvtColor(dst, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.thresholdInverse":
        v = int(p.get("value", 120))
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            f"    cv::threshold(gray, dst, {v}, 255, cv::THRESH_BINARY_INV);\n"
            "    cv::cvtColor(dst, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.adaptiveThreshold":
        w = int(p.get("window", 11))
        if w % 2 == 0:
            w += 1
        w = max(w, 3)
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            f"    cv::adaptiveThreshold(gray, dst, 255, cv::ADAPTIVE_THRESH_GAUSSIAN_C, cv::THRESH_BINARY, {w}, 2);\n"
            "    cv::cvtColor(dst, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.canny":
        low = int(p.get("low", 60))
        high = int(p.get("high", 170))
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            f"    cv::Canny(gray, dst, {low}, {high});\n"
            "    cv::cvtColor(dst, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.sobel":
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::Sobel(gray, dst, CV_8U, 1, 0, 3);\n"
            "    cv::cvtColor(dst, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.laplacian":
        ksize = int(p.get("ksize", 3))
        if ksize % 2 == 0:
            ksize += 1
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            f"    cv::Laplacian(gray, dst, CV_16S, {max(1, ksize)});\n"
            "    cv::convertScaleAbs(dst, src);\n"
            "    cv::cvtColor(src, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.erode":
        n = int(p.get("iterations", 1))
        return f"cv::erode(src, dst, cv::Mat(), cv::Point(-1, -1), {max(1, n)}); src = dst.clone();"
    if op == "opencv.dilate":
        n = int(p.get("iterations", 1))
        return f"cv::dilate(src, dst, cv::Mat(), cv::Point(-1, -1), {max(1, n)}); src = dst.clone();"
    if op == "opencv.rgbToGray":
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::cvtColor(gray, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.findContours":
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::threshold(gray, dst, 80, 255, cv::THRESH_BINARY);\n"
            "    std::vector<std::vector<cv::Point>> contours;\n"
            "    cv::findContours(dst, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);\n"
            "    cv::drawContours(src, contours, -1, cv::Scalar(0, 255, 255), 2);"
        )
    if op == "opencv.bitwiseNot":
        return "cv::bitwise_not(src, src);"
    if op == "opencv.bitwiseAnd":
        return "cv::bitwise_and(src, src, src);"
    if op == "opencv.bitwiseOr":
        return "cv::bitwise_or(src, src, src);"
    if op == "opencv.bitwiseXor":
        return "cv::bitwise_xor(src, src, src);"
    if op == "opencv.flip":
        fc = int(p.get("flipCode", 0))
        return f"cv::flip(src, dst, {fc}); src = dst.clone();"
    if op == "opencv.transpose":
        return "cv::transpose(src, dst); src = dst.clone();"
    if op == "opencv.normalize":
        alpha = float(p.get("alpha", 0))
        beta = float(p.get("beta", 255))
        return f"cv::normalize(src, dst, {alpha}, {beta}, cv::NORM_MINMAX); src = dst.clone();"
    if op == "opencv.resize":
        width = int(p.get("width", 320))
        height = int(p.get("height", 240))
        return f"cv::resize(src, dst, cv::Size({width}, {height})); src = dst.clone();"
    if op == "opencv.crop":
        x = int(p.get("x", 0))
        y = int(p.get("y", 0))
        w = int(p.get("w", 100))
        h = int(p.get("h", 100))
        return f"src = src(cv::Rect({x}, {y}, {w}, {h})).clone();"
    if op == "opencv.hsvThreshold":
        h_min = int(p.get("hMin", 0))
        h_max = int(p.get("hMax", 179))
        s_min = int(p.get("sMin", 0))
        s_max = int(p.get("sMax", 255))
        v_min = int(p.get("vMin", 0))
        v_max = int(p.get("vMax", 255))
        return (
            "cv::cvtColor(src, dst, cv::COLOR_BGR2HSV);\n"
            f"    cv::inRange(dst, cv::Scalar({h_min}, {s_min}, {v_min}), cv::Scalar({h_max}, {s_max}, {v_max}), dst);\n"
            "    cv::cvtColor(dst, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.hslThreshold":
        h_min = int(p.get("hMin", 0))
        h_max = int(p.get("hMax", 179))
        s_min = int(p.get("sMin", 0))
        s_max = int(p.get("sMax", 255))
        l_min = int(p.get("lMin", 0))
        l_max = int(p.get("lMax", 255))
        return (
            "cv::cvtColor(src, dst, cv::COLOR_BGR2HLS);\n"
            f"    cv::inRange(dst, cv::Scalar({h_min}, {l_min}, {s_min}), cv::Scalar({h_max}, {l_max}, {s_max}), dst);\n"
            "    cv::cvtColor(dst, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.rgbThreshold":
        r_min = int(p.get("rMin", 0))
        r_max = int(p.get("rMax", 255))
        g_min = int(p.get("gMin", 0))
        g_max = int(p.get("gMax", 255))
        b_min = int(p.get("bMin", 0))
        b_max = int(p.get("bMax", 255))
        return (
            f"cv::inRange(src, cv::Scalar({b_min}, {g_min}, {r_min}), cv::Scalar({b_max}, {g_max}, {r_max}), dst);\n"
            "    cv::cvtColor(dst, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.add":
        scale = float(p.get("scale", 1.0))
        val = int(128 * scale)
        return (
            f"cv::Mat second = cv::Mat(src.size(), src.type(), cv::Scalar({val}, {val}, {val}));\n"
            "    cv::add(src, second, src);"
        )
    if op == "opencv.subtract":
        scale = float(p.get("scale", 1.0))
        val = int(64 * scale)
        return (
            f"cv::Mat second = cv::Mat(src.size(), src.type(), cv::Scalar({val}, {val}, {val}));\n"
            "    cv::subtract(src, second, src);"
        )
    if op == "opencv.absdiff":
        return (
            "cv::bitwise_not(src, dst);\n"
            "    cv::absdiff(src, dst, src);"
        )
    if op == "opencv.multiply":
        scale = float(p.get("scale", 1.0))
        return f"src.convertTo(src, -1, {scale}, 0);"
    if op == "opencv.divide":
        scale = max(float(p.get("scale", 1.0)), 0.01)
        return f"src.convertTo(src, -1, {1.0 / scale}, 0);"
    if op == "opencv.addWeighted":
        alpha = float(p.get("alpha", 0.5))
        beta = float(p.get("beta", 0.5))
        gamma = float(p.get("gamma", 0.0))
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::cvtColor(gray, dst, cv::COLOR_GRAY2BGR);\n"
            f"    cv::addWeighted(src, {alpha}, dst, {beta}, {gamma}, src);"
        )
    if op == "opencv.min":
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::cvtColor(gray, dst, cv::COLOR_GRAY2BGR);\n"
            "    cv::min(src, dst, src);"
        )
    if op == "opencv.max":
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::cvtColor(gray, dst, cv::COLOR_GRAY2BGR);\n"
            "    cv::max(src, dst, src);"
        )
    if op == "opencv.mask":
        thresh = int(p.get("threshold", 127))
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            f"    cv::threshold(gray, dst, {thresh}, 255, cv::THRESH_BINARY);\n"
            "    cv::bitwise_and(src, src, src, dst);"
        )
    if op == "opencv.distanceTransform":
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::threshold(gray, dst, 80, 255, cv::THRESH_BINARY);\n"
            "    cv::Mat dist;\n"
            "    cv::distanceTransform(dst, dist, cv::DIST_L2, 5);\n"
            "    cv::normalize(dist, dist, 0, 255, cv::NORM_MINMAX);\n"
            "    dist.convertTo(gray, CV_8U);\n"
            "    cv::cvtColor(gray, src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.watershed":
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::threshold(gray, dst, 80, 255, cv::THRESH_BINARY);\n"
            "    cv::Mat dist;\n"
            "    cv::distanceTransform(dst, dist, cv::DIST_L2, 5);\n"
            "    cv::Mat markers;\n"
            "    cv::threshold(dist, markers, 0.5 * 255, 255, cv::THRESH_BINARY);\n"
            "    markers.convertTo(markers, CV_32S);\n"
            "    cv::watershed(src, markers);"
        )
    if op == "opencv.findLines":
        threshold = int(p.get("threshold", 50))
        min_len = int(p.get("minLineLength", 50))
        max_gap = int(p.get("maxLineGap", 10))
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::Canny(gray, dst, 50, 150);\n"
            "    std::vector<cv::Vec4i> lines;\n"
            f"    cv::HoughLinesP(dst, lines, 1, CV_PI / 180, {threshold}, {min_len}, {max_gap});\n"
            "    for (const auto& l : lines) {\n"
            "        cv::line(src, cv::Point(l[0], l[1]), cv::Point(l[2], l[3]), cv::Scalar(0, 0, 255), 2);\n"
            "    }"
        )
    if op == "opencv.findBlobs":
        min_area = float(p.get("minArea", 100))
        max_area = float(p.get("maxArea", 5000))
        return (
            "cv::SimpleBlobDetector::Params params;\n"
            "    params.filterByArea = true;\n"
            f"    params.minArea = {min_area};\n"
            f"    params.maxArea = {max_area};\n"
            "    cv::Ptr<cv::SimpleBlobDetector> detector = cv::SimpleBlobDetector::create(params);\n"
            "    cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    std::vector<cv::KeyPoint> keypoints;\n"
            "    detector->detect(gray, keypoints);\n"
            "    cv::drawKeypoints(src, keypoints, src, cv::Scalar(0, 255, 0), cv::DrawMatchesFlags::DRAW_RICH_KEYPOINTS);"
        )
    if op == "opencv.filterContours":
        min_area = int(float(p.get("minArea", 5000)))
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::threshold(gray, dst, 80, 255, cv::THRESH_BINARY);\n"
            "    std::vector<std::vector<cv::Point>> contours;\n"
            "    cv::findContours(dst, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);\n"
            "    std::vector<std::vector<cv::Point>> filtered;\n"
            "    for (const auto& c : contours) {\n"
            f"        if (cv::contourArea(c) >= {min_area}) filtered.push_back(c);\n"
            "    }\n"
            "    cv::drawContours(src, filtered, -1, cv::Scalar(255, 0, 255), 2);"
        )
    if op == "opencv.convexHulls":
        return (
            "cv::cvtColor(src, gray, cv::COLOR_BGR2GRAY);\n"
            "    cv::threshold(gray, dst, 80, 255, cv::THRESH_BINARY);\n"
            "    std::vector<std::vector<cv::Point>> contours;\n"
            "    cv::findContours(dst, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);\n"
            "    std::vector<std::vector<cv::Point>> hulls(contours.size());\n"
            "    for (size_t i = 0; i < contours.size(); i++) {\n"
            "        cv::convexHull(contours[i], hulls[i]);\n"
            "    }\n"
            "    cv::drawContours(src, hulls, -1, cv::Scalar(0, 255, 0), 2);"
        )
    if op == "opencv.extractChannel":
        ch = int(p.get("channel", 0))
        return (
            "std::vector<cv::Mat> channels;\n"
            "    cv::split(src, channels);\n"
            f"    cv::cvtColor(channels[{ch}], src, cv::COLOR_GRAY2BGR);"
        )
    if op == "opencv.noop":
        return "// noop"
    # fallback
    return f"// {node.id}:{op} (unsupported)"


def generate_cpp(pipeline: PipelineDocumentV1, class_name: str) -> str:
    nodes = _ordered_nodes(pipeline)

    header = (
        "#include <opencv2/opencv.hpp>\n"
        "#include <vector>\n\n"
        f"class {class_name} {{\n"
        "public:\n"
        "  cv::Mat run(const cv::Mat& image) {\n"
        "    cv::Mat src = image.clone();\n"
        "    cv::Mat dst, gray;\n"
    )

    body_lines: list[str] = []
    for node in nodes:
        p = _params(node)
        code = _cpp_code(node, p)
        if code is not None:
            body_lines.append(f"    {code}")

    footer = (
        "    return src;\n"
        "  }\n"
        "};\n"
    )

    return header + "\n".join(body_lines) + ("\n" if body_lines else "") + footer


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_code(pipeline: PipelineDocumentV1, language: str, class_name: str) -> tuple[str, str]:
    if language == "python":
        return f"{class_name}.py", generate_python(pipeline, class_name)
    if language == "java":
        return f"{class_name}.java", generate_java(pipeline, class_name)
    if language == "cpp":
        return f"{class_name}.cpp", generate_cpp(pipeline, class_name)
    raise ValueError(f"Unsupported language: {language}")
