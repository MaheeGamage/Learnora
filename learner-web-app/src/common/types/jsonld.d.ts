declare module 'jsonld' {
  export interface JsonLdDocument {
    '@context'?: string | object | Array<string | object>;
    '@id'?: string;
    '@type'?: string | string[];
    '@value'?: string | number | boolean;
    [key: string]: unknown;
  }

  export interface ExpandOptions {
    base?: string;
    expandContext?: object;
    keepFreeFloatingNodes?: boolean;
    documentLoader?: (url: string) => Promise<{ document: unknown }>;
  }

  export interface CompactOptions {
    base?: string;
    compactArrays?: boolean;
    graph?: boolean;
    skipExpansion?: boolean;
    documentLoader?: (url: string) => Promise<{ document: unknown }>;
  }

  export function expand(
    input: JsonLdDocument | JsonLdDocument[],
    options?: ExpandOptions
  ): Promise<JsonLdDocument[]>;

  export function compact(
    input: JsonLdDocument | JsonLdDocument[],
    ctx: object,
    options?: CompactOptions
  ): Promise<JsonLdDocument>;

  export function flatten(
    input: JsonLdDocument | JsonLdDocument[],
    ctx?: object | null,
    options?: object
  ): Promise<JsonLdDocument>;

  export function frame(
    input: JsonLdDocument | JsonLdDocument[],
    frame: object,
    options?: object
  ): Promise<JsonLdDocument>;

  const jsonld: {
    expand: typeof expand;
    compact: typeof compact;
    flatten: typeof flatten;
    frame: typeof frame;
  };

  export default jsonld;
}
