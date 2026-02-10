import { describe, expect, it } from "vitest";
import { fallbackTemplates, FALLBACK_OPERATION_COUNT } from "./App";

describe("fallback operation catalog", () => {
  it("has at least 17 operations", () => {
    expect(FALLBACK_OPERATION_COUNT).toBeGreaterThanOrEqual(17);
  });

  it("count matches actual template array length", () => {
    expect(FALLBACK_OPERATION_COUNT).toBe(fallbackTemplates.length);
  });

  it("every template has executeOp matching displayOp (no proxy mismatches)", () => {
    for (const t of fallbackTemplates) {
      expect(t.executeOp).toBe(
        t.displayOp,
      );
    }
  });

  it("no template keys contain -proxy suffix", () => {
    for (const t of fallbackTemplates) {
      expect(t.key).not.toContain("-proxy");
    }
  });

  it("every template has at least one param", () => {
    for (const t of fallbackTemplates) {
      expect(t.params.length).toBeGreaterThanOrEqual(1);
    }
  });

  it("all templates have required fields", () => {
    for (const t of fallbackTemplates) {
      expect(t.key).toBeTruthy();
      expect(t.label).toBeTruthy();
      expect(t.category).toBeTruthy();
      expect(t.displayOp).toBeTruthy();
      expect(t.executeOp).toBeTruthy();
      expect(["image", "json"]).toContain(t.outputType);
    }
  });

  it("has unique keys for all templates", () => {
    const keys = fallbackTemplates.map((t) => t.key);
    expect(new Set(keys).size).toBe(keys.length);
  });

  it("every template has inputs and outputs arrays", () => {
    for (const t of fallbackTemplates) {
      expect(Array.isArray(t.inputs)).toBe(true);
      expect(t.inputs.length).toBeGreaterThanOrEqual(1);
      expect(Array.isArray(t.outputs)).toBe(true);
      expect(t.outputs.length).toBeGreaterThanOrEqual(1);
    }
  });
});
