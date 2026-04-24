"use client";
import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { api, setAuthToken } from "@/lib/api";
import { useCityStore } from "@/store/city";
import { QRUpload } from "@/components/ui/QRUpload";
import { useRouter } from "next/navigation";

export default function SellPage() {
  const { getToken } = useAuth();
  const { selectedCity } = useCityStore();
  const router = useRouter();

  const [events, setEvents] = useState<any[]>([]);
  const [eventId, setEventId] = useState("");
  const [cityId, setCityId] = useState("");
  const [price, setPrice] = useState("");
  const [origPrice, setOrigPrice] = useState("");
  const [qrFile, setQrFile] = useState<File[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const listingFee = price ? (parseFloat(price) * 0.2).toFixed(2) : "0.00";

  useEffect(() => {
    if (!selectedCity) return;
    (async () => {
      const { data } = await api.get(`/cities?name=${selectedCity}`);
      if (data?.[0]) {
        setCityId(data[0].id);
        const { data: evs } = await api.get("/events", {
          params: { city_id: data[0].id },
        });
        setEvents(evs);
      }
    })();
  }, [selectedCity]);

  const handleSubmit = async () => {
    setError("");
    if (!eventId || !cityId || !price || !origPrice) {
      setError("All fields are required.");
      return;
    }
    if (qrFile.length !== 1) {
      setError("Upload exactly 1 QR code per ticket.");
      return;
    }
    setLoading(true);
    try {
      const token = await getToken();
      setAuthToken(token);

      const form = new FormData();
      form.append("event_id", eventId);
      form.append("city_id", cityId);
      form.append("price", price);
      form.append("original_price", origPrice);
      form.append("qr_files", qrFile[0]);

      await api.post("/tickets/create", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      router.push("/dashboard");
    } catch (e: any) {
      setError(e.message ?? "Failed to create listing.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto px-4 py-16">
      <h1 className="font-display text-5xl tracking-wide text-zinc-100 mb-8">SELL A TICKET</h1>

      <div className="space-y-5">
        {/* City */}
        <div>
          <label className="block text-xs text-zinc-500 mb-1.5 tracking-wider uppercase">City</label>
          <div className="px-4 py-2.5 rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-300 text-sm">
            {selectedCity ?? "Select city from navbar first"}
          </div>
        </div>

        {/* Event */}
        <div>
          <label className="block text-xs text-zinc-500 mb-1.5 tracking-wider uppercase">Event</label>
          <select
            value={eventId}
            onChange={(e) => setEventId(e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-300 text-sm focus:outline-none focus:border-zinc-500"
          >
            <option value="">Select event</option>
            {events.map((ev) => (
              <option key={ev.id} value={ev.id}>{ev.name}</option>
            ))}
          </select>
        </div>

        {/* Prices */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-zinc-500 mb-1.5 tracking-wider uppercase">Original Price (₹)</label>
            <input
              type="number"
              value={origPrice}
              onChange={(e) => setOrigPrice(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-zinc-500"
              placeholder="0"
            />
          </div>
          <div>
            <label className="block text-xs text-zinc-500 mb-1.5 tracking-wider uppercase">Selling Price (₹)</label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="w-full px-4 py-2.5 rounded-lg bg-zinc-800 border border-zinc-700 text-zinc-100 font-mono text-sm focus:outline-none focus:border-zinc-500"
              placeholder="0"
            />
          </div>
        </div>

        {/* Listing fee */}
        {price && (
          <div className="flex items-center justify-between px-4 py-3 rounded-lg bg-zinc-900 border border-zinc-800 text-sm">
            <span className="text-zinc-500">Listing fee (20%)</span>
            <span className="text-amber-400 font-mono">₹{listingFee}</span>
          </div>
        )}

        {/* QR Upload */}
        <div>
          <label className="block text-xs text-zinc-500 mb-1.5 tracking-wider uppercase">QR Code</label>
          <QRUpload count={1} onChange={setQrFile} />
        </div>

        {error && (
          <p className="text-red-400 text-sm bg-red-400/10 border border-red-400/20 px-4 py-2 rounded-lg">
            {error}
          </p>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full py-3 rounded-lg bg-amber-500 text-zinc-950 font-medium hover:bg-amber-400 transition-colors disabled:opacity-50"
        >
          {loading ? "Submitting..." : "List Ticket"}
        </button>
      </div>
    </div>
  );
}
