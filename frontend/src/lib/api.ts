const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

type FetchOptions = RequestInit & { json?: unknown };

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { json, ...rest } = options;
  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    credentials: "include", // always send httpOnly cookies
    headers: {
      "Content-Type": "application/json",
      ...rest.headers,
    },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, error.detail ?? "Request failed");
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export default apiFetch;
