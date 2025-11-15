/*
 * extractConcepts
 * ----------------
 * Lightweight helper to extract a list of concepts from a JSON-LD / RDF-like
 * `kg_data` payload returned with a learning path. The function attempts to
 * be resilient to a few common shapes of JSON-LD we store and receive:
 *
 * - `kg_data` is expected to be an array of node objects (JSON-LD expanded
 *   form). If a non-array is provided the function treats it as invalid.
 * - Concept detection: nodes that represent concepts typically have an
 *   `@type` (or `type`) field that contains a URI ending in `#Concept` or a
 *   simple string like `Concept`. We detect both single-string and
 *   array-valued `@type` fields.
 * - Label extraction: labels are commonly stored under
 *   `http://learnora.ai/ont#label` in expanded JSON-LD (an array of value
 *   objects), but fallback keys include `label` and `rdfs:label`.
 *   The helper will extract a human-friendly string from these shapes and
 *   falls back to the node id if no label is found.
 *
 * Normalization / fallbacks performed:
 * - Accepts either `@id` or `id` as the concept identifier.
 * - Supports label entries that are either an array with objects like
 *   `{ "@value": "Label" }` or a plain string.
 * - If no label can be derived, returns the `id` as the label so UI still
 *   has a meaningful option text.
 *
 * Example input (trimmed):
 * [
 *   {
 *     "@id": "http://learnora.ai/ont#python_programming_fundamentals",
 *     "@type": ["http://learnora.ai/ont#Concept"],
 *     "http://learnora.ai/ont#label": [{"@value": "Python Programming Fundamentals"}]
 *   },
 *   ...
 * ]
 *
 * Return value: array of objects { id, label } suitable for populating UI
 * selection components (Autocomplete, selects, etc.). The function is
 * intentionally permissive but not a full JSON-LD parser — it only handles
 * the shapes we use in the app and provides robust fallbacks.
 */
export const extractConcepts = (kgData: unknown): { id: string; label: string }[] => {
    if (!kgData) return [];
    const items = Array.isArray(kgData) ? kgData : (kgData as any[]);
    if (!Array.isArray(items)) return [];

    return items
        .filter((it: any) => {
            const type = it?.['@type'] ?? it?.type;
            if (!type) return false;
            if (Array.isArray(type)) return type.some((t: string) => String(t).includes('#Concept') || String(t).endsWith('Concept'));
            return String(type).includes('#Concept') || String(type).endsWith('Concept');
        })
        .map((it: any) => {
            const id = it['@id'] || it.id || '';
            const labelField = it['http://learnora.ai/ont#label'] || it['label'] || it['rdfs:label'];
            let label = '';
            if (Array.isArray(labelField) && labelField[0]) {
                label = labelField[0]['@value'] ?? labelField[0]?.value ?? String(labelField[0]);
            } else if (typeof labelField === 'string') {
                label = labelField;
            }
            if (!label) label = id;
            return { id, label };
        });
};