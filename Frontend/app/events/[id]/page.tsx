"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api, setAuthToken } from "@/lib/api";
import { TicketCard } from "@/components/ui/TicketCard";
import { useRouter } from "next/navigation";
import { Calendar, MapPin } from "lucide-react";

export default function EventPage({ params }: { params: { id: string } }) {
  const { getToken } = useAuth();
  const router = useRouter();
  const [event, setEvent] = useState<any>(null);
  const [tickets, setTickets] = useState<any[]>([]);
  const [loadingTickets, setLoadingTickets] = useState(true);

  useEffect(() => {
    (async () => {
      const token = await getToken();
      setAuthToken(token);
      const { data } = await api.get(`/events/${params.id}`);
      setEvent(data);

      const { data: ticketData } = await api.get("/tickets", {
        params: { event_id: params.id },
      });
      setTickets(ticketData);
      setLoadingTickets(false);
    })();
  }, [params.id]);

  const handleBuy = async (ticketId: string) => {
    try {
      const token = await getToken();
      setAuthToken(token);
      const { data } = await api.post("/orders/initiate", { ticket_id: ticketId });
      router.push(`/checkout/${data.order_id}?secret=${data.client_secret}&amount=${data.amount}`);
    } catch (e: any) {
      alert(e.message);
    }
  };

  const date = event
    ? new Date(event.date).toLocaleDateString("en-IN", {
        weekday: "long", day: "numeric", month: "long", year: "numeric",
      })
    : "";

  return (
    <div>
      <div className="relative h-72 md:h-96 overflow-hidden">
        {event?.image_url ? (
          <img
            src={event.image_url}
            alt={event.name}
            className="w-full h-full object-cover opacity-40"
          />
        ) : (
          <div className="w-full h-full bg-zinc-900" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-zinc-950 to-transparent" />
        <div className="absolute bottom-0 left-0 max-w-7xl mx-auto px-4 pb-8 w-full">
          <h1 className="font-display text-5xl md:text-7xl tracking-wide text-zinc-100">
            {event?.name ?? "Loading..."}
          </h1>
          <div className="flex gap-4 mt-3 text-zinc-400 text-sm">
            {date && (
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />{date}
              </span>
            )}
            {event?.venue && (
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />{event.venue}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-12">
        <h2 className="font-display text-3xl tracking-wide text-zinc-100 mb-6">
          AVAILABLE TICKETS
        </h2>
        {loadingTickets ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array(3).fill(0).map((_, i) => (
              <div key={i} className="h-48 rounded-xl bg-zinc-800 animate-pulse" />
            ))}
          </div>
        ) : tickets.length === 0 ? (
          <p className="text-zinc-600 text-sm">No tickets listed for this event yet.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {tickets.map((t) => (
              <TicketCard key={t.id} ticket={t} onBuy={handleBuy} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
