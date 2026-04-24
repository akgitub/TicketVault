"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api, setAuthToken } from "@/lib/api";
import { CountdownTimer } from "@/components/ui/CountdownTimer";
import { useRouter } from "next/navigation";

export default function ConfirmPage({ params }: { params: { id: string } }) {
  const { getToken } = useAuth();
  const router = useRouter();
  const [order, setOrder] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      const token = await getToken();
      setAuthToken(token);
      const { data } = await api.get(`/orders/${params.id}`);
      setOrder(data);
      setLoading(false);
    })();
  }, []);

  const act = async (action: "confirm" | "dispute") => {
    setActing(true);
    setError("");
    try {
      const token = await getToken();
      setAuthToken(token);
      if (action === "confirm") {
        await api.post(`/confirmations/${params.id}/confirm`);
      } else {
        await api.post(`/confirmations/${params.id}/dispute`, {
          reason: "Issue reported by buyer",
        });
      }
      router.push("/dashboard");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setActing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const item = order?.order_items?.[0];
  const ticket = item?.tickets;

  return (
    <div className="max-w-lg mx-auto px-4 py-16">
      <h1 className="font-display text-5xl tracking-wide text-zinc-100 mb-2">CONFIRM TICKET</h1>
      <p className="text-zinc-500 text-sm mb-8">Verify your ticket and confirm receipt within 2 hours.</p>

      {/* Ticket info */}
      {ticket && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 mb-6 space-y-2">
          <p className="font-display text-2xl tracking-wide">{ticket.events?.name}</p>
          <p className="text-zinc-500 text-sm">{ticket.events?.venue} · {ticket.cities?.name}</p>
          <p className="text-amber-400 font-mono text-lg">₹{ticket.price?.toLocaleString()}</p>
        </div>
      )}

      {/* QR Code */}
      {item?.qr_signed_url && (
        <div className="mb-6">
          <p className="text-xs text-zinc-500 mb-2 tracking-wider uppercase">Your QR Code</p>
          <img
            src={item.qr_signed_url}
            alt="QR Code"
            className="w-48 h-48 rounded-xl border border-zinc-700 bg-zinc-800"
          />
        </div>
      )}

      {/* Countdown */}
      {order?.confirmation_deadline && (
        <div className="mb-8">
          <p className="text-xs text-zinc-500 mb-3 tracking-wider uppercase">Time remaining to confirm</p>
          <CountdownTimer deadline={order.confirmation_deadline} />
        </div>
      )}

      {error && (
        <p className="text-red-400 text-sm bg-red-400/10 border border-red-400/20 px-4 py-2 rounded-lg mb-4">
          {error}
        </p>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={() => act("confirm")}
          disabled={acting}
          className="flex-1 py-3 rounded-lg bg-amber-500 text-zinc-950 font-medium hover:bg-amber-400 transition-colors disabled:opacity-50"
        >
          ✓ Confirm Received
        </button>
        <button
          onClick={() => act("dispute")}
          disabled={acting}
          className="flex-1 py-3 rounded-lg border border-red-500/50 text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50"
        >
          ✗ Report Issue
        </button>
      </div>
    </div>
  );
}
