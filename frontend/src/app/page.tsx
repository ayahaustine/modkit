import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-4xl font-bold tracking-tight">ModKit</h1>
      <p className="text-gray-500 text-center max-w-sm">
        Full-stack starter template — FastAPI · Next.js · PostgreSQL
      </p>
      <div className="flex gap-3">
        <Link
          href="/login"
          className="rounded-md bg-black px-5 py-2 text-sm font-medium text-white hover:bg-gray-800"
        >
          Sign in
        </Link>
        <Link
          href="/register"
          className="rounded-md border px-5 py-2 text-sm font-medium hover:bg-gray-50"
        >
          Register
        </Link>
      </div>
    </main>
  );
}
