"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      {user && (
        <p className="text-gray-600">
          Signed in as <span className="font-medium">{user.email}</span>
        </p>
      )}
      <button
        onClick={handleLogout}
        className="rounded-md border px-4 py-2 text-sm font-medium hover:bg-gray-50"
      >
        Sign out
      </button>
    </main>
  );
}
