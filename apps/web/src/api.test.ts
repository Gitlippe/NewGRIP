import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { loadCatalog } from "./api";

describe("loadCatalog", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    globalThis.fetch = vi.fn();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("parses operations from backend response", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        operations: [
          {
            key: "blur",
            label: "Blur",
            category: "Filtering",
            executeOp: "opencv.blur",
            outputType: "image",
            params: [{ name: "kernel", view: "slider", value: 5 }],
          },
        ],
      }),
    });

    const result = await loadCatalog();
    expect(result).toHaveLength(1);
    expect(result[0].key).toBe("blur");
    expect(result[0].displayOp).toBe("opencv.blur");
    expect(result[0].executeOp).toBe("opencv.blur");
  });

  it("defaults category to General when missing", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        operations: [{ key: "test", label: "Test", executeOp: "test.op" }],
      }),
    });

    const result = await loadCatalog();
    expect(result[0].category).toBe("General");
  });

  it("defaults outputType to image when not json", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        operations: [{ key: "test", label: "Test", outputType: "image" }],
      }),
    });

    const result = await loadCatalog();
    expect(result[0].outputType).toBe("image");
  });

  it("returns empty array when no operations field", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    const result = await loadCatalog();
    expect(result).toEqual([]);
  });

  it("propagates fetch errors", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error("Network failure"),
    );

    await expect(loadCatalog()).rejects.toThrow("Network failure");
  });

  it("parses inputs and outputs from backend response", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        operations: [
          {
            key: "find-contours",
            label: "Find Contours",
            category: "Contours",
            executeOp: "opencv.findContours",
            outputType: "image",
            params: [],
            inputs: [{ name: "in", type: "image" }],
            outputs: [
              { name: "out", type: "image" },
              { name: "contours", type: "json" },
            ],
          },
        ],
      }),
    });

    const result = await loadCatalog();
    expect(result).toHaveLength(1);
    expect(result[0].inputs).toEqual([{ name: "in", type: "image" }]);
    expect(result[0].outputs).toEqual([
      { name: "out", type: "image" },
      { name: "contours", type: "json" },
    ]);
  });

  it("defaults inputs and outputs when not provided", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        operations: [
          {
            key: "blur",
            label: "Blur",
            executeOp: "opencv.blur",
            outputType: "image",
            params: [],
          },
        ],
      }),
    });

    const result = await loadCatalog();
    expect(result[0].inputs).toEqual([{ name: "in", type: "image" }]);
    expect(result[0].outputs).toEqual([{ name: "out", type: "image" }]);
  });
});
