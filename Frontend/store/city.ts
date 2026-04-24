import { create } from "zustand";
import { persist } from "zustand/middleware";

export const CITIES = [
  "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
  "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
  "Kochi", "Chandigarh", "Goa", "Surat", "Indore",
] as const;

export type City = typeof CITIES[number];

interface CityStore {
  selectedCity: City | null;
  setCity: (city: City) => void;
}

export const useCityStore = create<CityStore>()(
  persist(
    (set) => ({
      selectedCity: null,
      setCity: (city) => set({ selectedCity: city }),
    }),
    { name: "ticketvault-city" }
  )
);
