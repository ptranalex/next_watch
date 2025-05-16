// useShouldResetFilters.ts

export function shouldResetFilters(
  fromPath?: string,
  toPath?: string
): boolean {
  if (!fromPath || !toPath) return false;

  const stripParams = (path: string) => path.split("?")[0];

  const from = stripParams(fromPath);
  const to = stripParams(toPath);

  // Example of contexts that should reset
  const isFromHome = from === "/";
  const isToBrowse = to.startsWith("/browse");
  const isCrossContext =
    (from.startsWith("/top/") && !to.startsWith("/top/")) ||
    (from.startsWith("/genres/") && !to.startsWith("/genres/"));

  // Logic: reset if changing main context or from home
  console.log(
    "isFromHome",
    isFromHome,
    "isCrossContext",
    isCrossContext,
    "isToBrowse",
    isToBrowse
  );
  return isFromHome || isCrossContext || isToBrowse;
}
