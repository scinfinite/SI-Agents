export const API_VERSION = "v1" as const;

export type ApiError = { error: string; message: string; request_id: string };
export type Run = { id: string; action: string; status: string; subject: string; [key: string]: unknown };
export type Event = { id: string; event_type: string; subject: string; timestamp: string; metadata: Record<string, string> };
export type Page<T> = { items: T[]; next_cursor: string | null; limit: number };
export type Subscription = { id: string; event_types: string[]; subject: string | null; transport: "sse" | "webhook"; status: string };

export class SIError extends Error {
  readonly status: number;
  readonly details: ApiError;
  constructor(status: number, details: ApiError) {
    super(`${details.error}: ${details.message}`);
    this.name = "SIError";
    this.status = status;
    this.details = details;
  }
}

export type ClientOptions = {
  baseUrl?: string;
  token?: string;
  subject?: string;
  project?: string;
  fetchImpl?: typeof fetch;
  maxConcurrency?: number;
};

export class SIClient {
  private readonly baseUrl: string;
  private readonly token?: string;
  private readonly subject?: string;
  private readonly project?: string;
  private readonly fetchImpl: typeof fetch;
  private readonly maxConcurrency: number;

  constructor(options: ClientOptions = {}) {
    this.baseUrl = (options.baseUrl ?? "http://127.0.0.1:8787").replace(/\/$/, "");
    this.token = options.token;
    this.subject = options.subject;
    this.project = options.project;
    this.fetchImpl = options.fetchImpl ?? fetch;
    this.maxConcurrency = Math.min(32, Math.max(1, options.maxConcurrency ?? 8));
  }

  private headers(idempotencyKey?: string): Headers {
    const headers = new Headers({ Accept: "application/json", "User-Agent": "si-agents-typescript-sdk/0.1" });
    if (this.token) headers.set("Authorization", `Bearer ${this.token}`);
    if (this.subject) headers.set("X-SI-Subject", this.subject);
    if (this.project) headers.set("X-SI-Project", this.project);
    if (idempotencyKey) headers.set("X-Idempotency-Key", idempotencyKey);
    return headers;
  }

  async request<T>(method: string, path: string, body?: unknown, idempotencyKey?: string): Promise<T> {
    const headers = this.headers(idempotencyKey);
    if (body !== undefined) headers.set("Content-Type", "application/json");
    const response = await this.fetchImpl(`${this.baseUrl}${path}`, {
      method, headers, body: body === undefined ? undefined : JSON.stringify(body),
    });
    const text = await response.text();
    let payload: unknown = undefined;
    if (text) {
      try { payload = JSON.parse(text); } catch { throw new SIError(response.status, { error: "invalid_json", message: "server returned invalid JSON", request_id: response.headers.get("X-Request-ID") ?? "" }); }
    }
    if (!response.ok) {
      const details = (payload && typeof payload === "object" ? payload : {}) as Partial<ApiError>;
      throw new SIError(response.status, { error: details.error ?? "http_error", message: details.message ?? response.statusText, request_id: details.request_id ?? response.headers.get("X-Request-ID") ?? "" });
    }
    return payload as T;
  }

  health(): Promise<Record<string, unknown>> { return this.request("GET", `/api/${API_VERSION}/health`); }
  snapshot(): Promise<Record<string, unknown>> { return this.request("GET", `/api/${API_VERSION}`); }
  createRun(payload: Record<string, unknown>, idempotencyKey?: string): Promise<Run> { return this.request("POST", `/api/${API_VERSION}/runs`, payload, idempotencyKey); }
  getRun(id: string): Promise<Run> { return this.request("GET", `/api/${API_VERSION}/runs/${encodeURIComponent(id)}`); }

  async list<T = Record<string, unknown>>(resource: string, options: { limit?: number; cursor?: string; query?: string; filters?: Record<string, string> } = {}): Promise<Page<T>> {
    const limit = options.limit ?? 100;
    if (limit < 1 || limit > 1000) throw new RangeError("limit must be between 1 and 1000");
    const params = new URLSearchParams({ limit: String(limit) });
    if (options.cursor) params.set("cursor", options.cursor);
    if (options.query) params.set("q", options.query);
    for (const [key, value] of Object.entries(options.filters ?? {})) params.set(`filter.${key}`, value);
    const result = await this.request<unknown>("GET", `/api/${API_VERSION}/${resource}?${params}`);
    if (Array.isArray(result)) return { items: result as T[], next_cursor: null, limit: result.length };
    return result as Page<T>;
  }

  async *paginate<T = Record<string, unknown>>(resource: string, options: { pageSize?: number; query?: string; filters?: Record<string, string> } = {}): AsyncGenerator<T> {
    let cursor: string | undefined;
    do {
      const page = await this.list<T>(resource, { limit: options.pageSize ?? 100, cursor, query: options.query, filters: options.filters });
      for (const item of page.items) yield item;
      cursor = page.next_cursor ?? undefined;
    } while (cursor);
  }

  events(options: { limit?: number; cursor?: string; query?: string; filters?: Record<string, string> } = {}): Promise<Page<Event>> { return this.list<Event>("events", options); }

  subscribe(input: { eventTypes?: string[]; subject?: string; transport?: "sse" | "webhook" }): Promise<Subscription> {
    return this.request("POST", `/api/${API_VERSION}/subscriptions`, { event_types: input.eventTypes ?? [], subject: input.subject, transport: input.transport ?? "sse" });
  }

  eventsSseUrl(after = 0): string { return `${this.baseUrl}/api/${API_VERSION}/events/stream?after=${encodeURIComponent(after)}`; }

  async *streamEvents(after = 0, signal?: AbortSignal): AsyncGenerator<Event> {
    const response = await this.fetchImpl(this.eventsSseUrl(after), { headers: this.headers(), signal });
    if (!response.ok || !response.body) throw new SIError(response.status, { error: "stream_error", message: response.statusText, request_id: response.headers.get("X-Request-ID") ?? "" });
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const part = await reader.read();
      if (part.done) return;
      buffer += decoder.decode(part.value, { stream: true });
      const frames = buffer.split("\n\n");
      buffer = frames.pop() ?? "";
      for (const frame of frames) {
        const line = frame.split("\n").find((value) => value.startsWith("data:"));
        if (line) yield JSON.parse(line.slice(5).trim()) as Event;
      }
    }
  }

  eventsWebSocketUrl(): string { return this.baseUrl.replace(/^http/, "ws") + `/api/${API_VERSION}/events/ws`; }

  openWebSocket(onEvent: (event: Event) => void, onError?: (error: globalThis.Event) => void): WebSocket {
    const socket = new WebSocket(this.eventsWebSocketUrl());
    socket.onmessage = (message) => onEvent(JSON.parse(String(message.data)) as Event);
    if (onError) socket.onerror = onError;
    return socket;
  }

  async mapConcurrent<T>(items: readonly T[], worker: (item: T, index: number) => Promise<void>): Promise<void> {
    let next = 0;
    const run = async (): Promise<void> => {
      while (true) {
        const index = next++;
        if (index >= items.length) return;
        await worker(items[index] as T, index);
      }
    };
    await Promise.all(Array.from({ length: Math.min(this.maxConcurrency, items.length) }, run));
  }
}
