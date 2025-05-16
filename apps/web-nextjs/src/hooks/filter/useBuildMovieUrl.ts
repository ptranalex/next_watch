import useMovieFilterStore from "@/store/movieFilterStore";

export function useBuildMovieUrl() {
  const { filters } = useMovieFilterStore();

  function buildUrl(basePath: string): string {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        params.set(key, String(value));
      }
    });

    const query = params.toString();
    return `${basePath}${query ? `?${query}` : ""}`;
  }

  return buildUrl;
}

export default useBuildMovieUrl;
