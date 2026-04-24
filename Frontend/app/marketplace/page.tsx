"use client";
declare global {
  interface Window {
    Razorpay: any;
  }
}
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useCityStore } from "@/store/city";
import { api, setAuthToken } from "@/lib/api";
import { TicketCard } from "@/components/ui/TicketCard";
import { useRouter } from "next/navigation";

export default function MarketplacePage() {
  const { selectedCity } = useCityStore();
  const { getToken } = useAuth();
  const router = useRouter();
  const [tickets, setTickets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const token = await getToken();
        setAuthToken(token);
        const params: Record<string, string> = {};
        if (selectedCity) {
          const { data: cities } = await api.get(`/cities?name=${selectedCity}`);
          if (cities?.[0]) params.city_id = cities[0].id;
        }
        const { data } = await api.get("/tickets", { params });
        setTickets(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, [selectedCity]);


  const handleBuy = async (ticketId: string) => {
  try {
    const token = await getToken();
    setAuthToken(token);

    const { data } = await api.post("/orders/initiate", { ticket_id: ticketId });

    console.log("Razorpay Key:", process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID);
    const options = {
      key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
      amount: data.amount,
      currency: "INR",
      name: "TicketVault",
      description: "Concert Ticket Purchase",
      order_id: data.razorpay_order_id,

      handler: async function (response: any) {
        try {
          await api.post("/orders/verify", {
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
          });

          alert("Payment successful 🎉");
          router.push(`/orders/${data.order_id}/confirm`);
        } catch (err) {
          alert("Payment verification failed");
        }
      },

      modal: {
        ondismiss: function () {
          alert("Payment cancelled ❌");
        },
      },

      theme: {
        color: "#f59e0b",
      },
    };

    if (!(window as any).Razorpay) {
      alert("Razorpay SDK not loaded");
      return;
    }
    const rzp = new (window as any).Razorpay(options);
    rzp.open();

  } catch (e: any) {
    alert(e.message);
  }
};

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="font-display text-5xl tracking-wide text-zinc-100">
          {selectedCity ? `${selectedCity.toUpperCase()} TICKETS` : "ALL TICKETS"}
        </h1>
        <p className="text-zinc-500 mt-1 text-sm">
          {tickets.length} listing{tickets.length !== 1 ? "s" : ""} available
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array(6).fill(0).map((_, i) => (
            <div key={i} className="h-48 rounded-xl bg-zinc-800 animate-pulse" />
          ))}
        </div>
      ) : tickets.length === 0 ? (
        <div className="text-center py-24 text-zinc-600">
          <p className="font-display text-3xl tracking-wide">NO TICKETS FOUND</p>
          <p className="text-sm mt-2">Try selecting a different city</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {tickets.map((t) => (
            <TicketCard key={t.id} ticket={t} onBuy={handleBuy} />
          ))}
        </div>
      )}
    </div>
  );
}
