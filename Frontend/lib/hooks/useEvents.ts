"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api, setAuthToken } from "@/lib/api";

export function useEvents(cityId?: string) {
  const { getToken } = useAuth();
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const token = await getToken();
        setAuthToken(token);
        const { data } = await api.get("/events", {
          params: cityId ? { city_id: cityId } : {},
        });
        setEvents(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, [cityId]);

  return { events, loading, error };
}
