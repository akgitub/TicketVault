"use client";
import { ClerkProvider, useAuth } from "@clerk/nextjs";
import { useEffect } from "react";
import { setAuthToken } from "@/lib/api";

function TokenSync() {
  const { getToken } = useAuth();
  useEffect(() => {
    getToken().then(setAuthToken);
  }, [getToken]);
  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <TokenSync />
      {children}
    </ClerkProvider>
  );
}
