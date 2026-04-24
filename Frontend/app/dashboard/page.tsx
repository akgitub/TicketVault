"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api, setAuthToken } from "@/lib/api";
import Link from "next/link";
import clsx from "clsx";

const STATUS_COLOR: Record<string, string> = {
  available:            "text-emerald-400 bg-emerald-400/10",
  locked:               "text-yellow-400 bg-yellow-400/10",
  pending_confirmation: "text-amber-400 bg-amber-400/10",
  sold:                 "text-zinc-400 bg-zinc-400/10",
  cancelled:            "text-red-400 bg-red-400/10",
};

export default function DashboardPage() {
  const { getToken } = useAuth();
  const [listings, setListings] = useState<any[]>([]);
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const token = await getToken();
      setAuthToken(token);
      try {
        const [me, ticketRes] = await Promise.all([
          api.get("/users/me"),
          api.get("/tickets"),
        ]);
        // Filter to current user's listings
        const myListings = ticketRes.data.filter(
          (t: any) => t.seller_id === me.data.id
        );
        setListings(myListings);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="font-display text-5xl tracking-wide text-zinc-100 mb-10">DASHBOARD</h1>

      <section className="mb-12">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display text-2xl tracking-wide text-zinc-300">MY LISTINGS</h2>
          <Link href="/sell" className="text-xs text-amber-400 hover:text-amber-300 transition-colors">
            + New listing
          </Link>
        </div>

        {loading ? (
          <div className="space-y-2">
            {Array(3).fill(0).map((_, i) => (
              <div key={i} className="h-14 rounded-lg bg-zinc-800 animate-pulse" />
            ))}
          </div>
        ) : listings.length === 0 ? (
          <div className="text-center py-12 text-zinc-600 border border-zinc-800 rounded-xl">
            <p className="font-display text-2xl tracking-wide">NO LISTINGS YET</p>
            <Link href="/sell" className="text-amber-400 text-sm mt-2 block hover:text-amber-300">
              Create your first listing →
            </Link>
          </div>
        ) : (
          <div className="space-y-2">
            {listings.map((t) => (
              <div
                key={t.id}
                className="flex items-center justify-between px-4 py-3 rounded-lg bg-zinc-900 border border-zinc-800"
              >
                <div>
                  <p className="text-zinc-200 text-sm font-medium">{t.events?.name}</p>
                  <p className="text-zinc-600 text-xs">{t.cities?.name}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-mono text-amber-400 text-sm">
                    ₹{t.price?.toLocaleString()}
                  </span>
                  <span className={clsx(
                    "text-xs px-2 py-0.5 rounded-full",
                    STATUS_COLOR[t.status] ?? "text-zinc-400"
                  )}>
                    {t.status?.replace(/_/g, " ")}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
