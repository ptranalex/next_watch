import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/services/hooks/core/useAuth";
import { fetchData } from "@/services/api/core/api-client";

interface SidebarLink {
  id: string;
  label: string;
  href: string;
  icon?: string;
}

interface SidebarFilters {
  show: boolean;
  defaults: {
    rating_imdb: number | null;
    year: number | null;
  };
  locked: string[];
}

interface SidebarGenre {
  id: number;
  name: string;
  href: string;
}

interface SidebarMetadata {
  layout: string;
  version: string;
  user_authenticated: boolean;
}

interface SidebarData {
  home: {
    label: string;
    href: string;
  };
  user_links: SidebarLink[];
  top_links: SidebarLink[];
  filters: SidebarFilters;
  genres: SidebarGenre[];
  metadata: SidebarMetadata;
}

/**
 * Hook to fetch sidebar data from BFF API
 *
 * Provides dynamic sidebar configuration including:
 * - User-specific navigation links (when authenticated)
 * - Top movies navigation
 * - Genre navigation
 * - Filter configuration
 * - Layout metadata
 */
export function useSidebarData() {
  const { currentUser } = useAuth();

  return useQuery<SidebarData>({
    queryKey: ["sidebar", currentUser?.id],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (currentUser?.id) params.append("user_id", currentUser.id.toString());

      return fetchData<SidebarData>(`/bff/v1/sidebar?${params.toString()}`);
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: (failureCount, error) => {
      // Don't retry on 502 (Backend service unavailable)
      if (error instanceof Error && error.message.includes("502")) {
        return false;
      }
      return failureCount < 3;
    },
  });
}
