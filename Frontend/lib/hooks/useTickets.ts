"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api, setAuthToken } from "@/lib/api";

export function useTickets(cityId?: string, eventId?: string) {
  const { getToken } = useAuth();
  const [tickets, setTickets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const token = await getToken();
        setAuthToken(token);
        const { data } = await api.get("/tickets", {
          params: {
            ...(cityId && { city_id: cityId }),
            ...(eventId && { event_id: eventId }),
          },
        });
        setTickets(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [cityId, eventId]);

  return { tickets, loading, error };
}
