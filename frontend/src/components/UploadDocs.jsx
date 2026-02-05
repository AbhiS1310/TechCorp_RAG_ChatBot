import { useState } from "react";
import { uploadDocument } from "../services/api.js";

export default function UploadDocs() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setStatus(null);

    try {
      const response = await uploadDocument(file);
      setStatus({ type: response.status, message: response.message });
    } catch (error) {
      setStatus({ type: "error", message: "Upload failed." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="rounded-3xl border border-ink/10 bg-white/80 p-6">
      <h2 className="font-display text-xl text-moss">Upload documents</h2>
      <p className="mt-1 text-sm text-ink/70">
        Add new .txt policy files to update the knowledge base.
      </p>
      <label className="mt-6 flex cursor-pointer flex-col items-start gap-3 rounded-2xl border border-dashed border-ink/30 bg-stone/40 p-4 text-sm text-ink/70">
        <input
          type="file"
          accept=".txt"
          className="hidden"
          onChange={handleUpload}
        />
        <span className="rounded-full bg-moss px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-white">
          {loading ? "Uploading..." : "Choose file"}
        </span>
        <span>Only .txt files are accepted.</span>
      </label>
      {status && (
        <div
          className={`mt-4 rounded-2xl px-4 py-3 text-sm ${
            status.type === "success"
              ? "bg-moss/10 text-moss"
              : "bg-amber/20 text-ink"
          }`}
        >
          {status.message}
        </div>
      )}
    </aside>
  );
}
