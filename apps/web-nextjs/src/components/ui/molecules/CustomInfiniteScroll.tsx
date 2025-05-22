import React, { useEffect, useRef, useState } from "react";
import { Box, Text } from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("CustomInfiniteScroll");

interface CustomInfiniteScrollProps {
  children: React.ReactNode;
  onLoadMore: () => Promise<any>;
  hasMore: boolean;
  isLoading?: boolean;
  loader?: React.ReactNode;
  endMessage?: React.ReactNode;
  scrollThreshold?: number; // Between 0 and 1
  className?: string;
  style?: React.CSSProperties;
  initialDelay?: number; // Delay before first load check in ms
  requireScroll?: boolean; // Whether to require user scroll before loading more
  debug?: boolean; // Enable debug logging
  disableAutoLoading?: boolean; // Completely disable automatic loading
}

/**
 * CustomInfiniteScroll - A reliable infinite scroll component that works with any layout
 *
 * Uses IntersectionObserver to detect when more content should be loaded
 * Handles proper cleanup and prevents duplicate load calls
 */
const CustomInfiniteScroll: React.FC<CustomInfiniteScrollProps> = ({
  children,
  onLoadMore,
  hasMore,
  isLoading = false,
  loader = null,
  endMessage = null,
  scrollThreshold = 0.8, // Default to 80% of the way down
  className = "",
  style = {},
  initialDelay = 500, // Reduced initial delay
  requireScroll = false, // Changed to false by default
  debug = false, // Debug mode
  disableAutoLoading = false, // Default is auto-loading enabled
}) => {
  const [hasUserScrolled, setHasUserScrolled] = useState(!requireScroll);
  const [observerReady, setObserverReady] = useState(false);
  const [lastLoadTime, setLastLoadTime] = useState(0);
  const loadingRef = useRef(false);
  const triggerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  // Initialize logging
  useEffect(() => {
    if (debug) {
      logger.info("CustomInfiniteScroll initialized", {
        hasMore,
        isLoading,
        requireScroll,
        initialDelay,
        disableAutoLoading,
      });
    }
  }, [
    debug,
    hasMore,
    isLoading,
    requireScroll,
    initialDelay,
    disableAutoLoading,
  ]);

  // Monitor scroll and automatically set scroll state
  useEffect(() => {
    if (!requireScroll) {
      setHasUserScrolled(true);
      return;
    }

    // Debug parent elements to identify potential scroll containers
    if (debug && contentRef.current) {
      let parent = contentRef.current.parentElement;
      let depth = 0;
      const scrollableParents = [];

      console.log("🔍 Checking parent elements for scroll containers");

      while (parent && depth < 10) {
        const style = window.getComputedStyle(parent);
        const isScrollable =
          style.overflow === "auto" ||
          style.overflow === "scroll" ||
          style.overflowY === "auto" ||
          style.overflowY === "scroll";

        const hasFixedHeight =
          style.height !== "auto" &&
          style.height !== "" &&
          !style.height.includes("100%");

        if (isScrollable) {
          scrollableParents.push({
            element: parent,
            id: parent.id,
            className: parent.className,
            depth,
            style: {
              overflow: style.overflow,
              overflowY: style.overflowY,
              height: style.height,
              position: style.position,
            },
          });

          // Add scroll listeners to potential scroll containers
          const currentDepth = depth;
          const currentParent = parent;
          currentParent.addEventListener(
            "scroll",
            () => {
              console.log(
                `📜 Scroll detected in parent at depth ${currentDepth}`,
                {
                  id: currentParent.id || "no-id",
                  className: currentParent.className || "no-class",
                  scrollTop: currentParent.scrollTop,
                  scrollHeight: currentParent.scrollHeight,
                  clientHeight: currentParent.clientHeight,
                }
              );
            },
            { passive: true }
          );
        }

        parent = parent.parentElement;
        depth++;
      }

      console.log("📑 Potentially scrollable parents:", scrollableParents);
    }

    const handleScroll = () => {
      console.log("🔍 handleScroll", {
        hasUserScrolled,
        windowScrollY: window.scrollY,
      });
      if (!hasUserScrolled && window.scrollY > 50) {
        // Reduced scroll threshold
        if (debug) {
          logger.info("📜 User scrolled, enabling auto-loading");
          console.log("📜 User scrolled, enabling auto-loading");
        }
        setHasUserScrolled(true);
      }
    };

    // Monitor both window scroll and document scroll
    window.addEventListener("scroll", handleScroll, { passive: true });

    // Also try to detect scroll on document level
    document.addEventListener(
      "scroll",
      (e) => {
        console.log("📜 Document scroll detected", {
          source: e.target,
          windowScrollY: window.scrollY,
        });
      },
      { passive: true }
    );

    // Also monitor wheel events as an alternative to detect scrolling
    const handleWheel = (e: WheelEvent) => {
      console.log("🖱️ Wheel event detected", {
        deltaY: e.deltaY,
        target: e.target,
        currentTarget: e.currentTarget,
      });

      // If wheel event indicates scrolling down and user hasn't scrolled yet
      if (!hasUserScrolled && e.deltaY > 0) {
        if (debug) {
          logger.info("🖱️ Wheel detected, enabling auto-loading");
          console.log("🖱️ Wheel detected, enabling auto-loading");
        }
        setHasUserScrolled(true);
      }
    };

    window.addEventListener("wheel", handleWheel, { passive: true });

    // Also add manual document-level listener for clicking to help debug
    if (debug) {
      document.addEventListener("click", () => {
        console.log("🔍 Current scroll state:", {
          windowScrollY: window.scrollY,
          documentHeight: document.documentElement.scrollHeight,
          windowHeight: window.innerHeight,
          hasUserScrolled,
        });
      });
    }

    return () => {
      window.removeEventListener("scroll", handleScroll);
      document.removeEventListener("scroll", handleScroll);
      window.removeEventListener("wheel", handleWheel);
    };
  }, [hasUserScrolled, requireScroll, debug]);

  // Initialize observer after a delay
  useEffect(() => {
    if (debug) {
      logger.info("⏱️ Setting initial delay", { initialDelay });
      console.log("⏱️ Setting initial delay", { initialDelay });
    }

    const timer = setTimeout(() => {
      setObserverReady(true);
      if (debug) {
        logger.info("🔍 Observer ready");
        console.log("🔍 Observer ready");
      }
    }, initialDelay);

    return () => clearTimeout(timer);
  }, [initialDelay, debug]);

  // Periodically check if we should load more (safety net)
  useEffect(() => {
    // Skip completely if auto-loading is disabled
    if (disableAutoLoading) {
      if (debug) {
        logger.info("⏸️ Auto-loading is disabled");
        console.log("⏸️ Auto-loading is disabled");
      }
      return;
    }

    if (!hasMore || isLoading || !hasUserScrolled || !observerReady) return;

    // Check if we're near the bottom of the page
    const checkIfNearBottom = () => {
      if (loadingRef.current) return;

      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const scrollBottom = scrollTop + windowHeight;
      const scrollPercentage = scrollBottom / documentHeight;

      // If we're within threshold of the bottom and not already loading
      if (
        scrollPercentage > scrollThreshold &&
        hasMore &&
        !loadingRef.current
      ) {
        if (debug) {
          logger.info("📏 Near bottom, loading more", {
            scrollPercentage,
            threshold: scrollThreshold,
          });
          console.log("📏 Near bottom, loading more", {
            scrollPercentage,
            threshold: scrollThreshold,
          });
        }
        handleLoadMore();
      }
    };

    // Set up interval to periodically check
    const intervalId = setInterval(checkIfNearBottom, 1000);
    return () => clearInterval(intervalId);
  }, [
    hasMore,
    isLoading,
    hasUserScrolled,
    observerReady,
    scrollThreshold,
    debug,
    disableAutoLoading,
  ]);

  // Helper function to avoid duplication
  const handleLoadMore = async () => {
    // Prevent loading too frequently
    const now = Date.now();
    if (now - lastLoadTime < 500) return;

    // Set loading state
    loadingRef.current = true;
    setLastLoadTime(now);

    if (debug) {
      logger.info("⬆️ Loading more content");
      console.log("⬆️ Loading more content");
    }

    try {
      await onLoadMore();
    } catch (error) {
      logger.error("❌ Error loading more content", error);
      console.error("❌ Error loading more content", error);
    } finally {
      // Small delay to prevent rapid loading
      setTimeout(() => {
        loadingRef.current = false;
      }, 300);
    }
  };

  // Set up intersection observer
  useEffect(() => {
    // Skip if auto-loading is disabled
    if (disableAutoLoading) return;

    if (
      !observerReady ||
      !hasMore ||
      isLoading ||
      (requireScroll && !hasUserScrolled)
    ) {
      return;
    }

    const target = triggerRef.current;
    if (!target) {
      if (debug) {
        logger.warn("⚠️ No trigger element found");
        console.warn("⚠️ No trigger element found");
      }
      return;
    }

    if (debug) {
      logger.info("🔍 Setting up IntersectionObserver");
      console.log("🔍 Setting up IntersectionObserver");
    }

    const options = {
      root: null, // Use viewport
      rootMargin: "300px", // Increased margin
      threshold: 0.1, // Trigger when 10% visible
    };

    const handleIntersection = (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;

      if (debug) {
        logger.info("👁️ Intersection detected", {
          isIntersecting: entry.isIntersecting,
          hasMore,
          isLoading: loadingRef.current,
        });
        console.log("👁️ Intersection detected", {
          isIntersecting: entry.isIntersecting,
          hasMore,
          isLoading: loadingRef.current,
        });
      }

      if (entry.isIntersecting && hasMore && !loadingRef.current) {
        handleLoadMore();
      }
    };

    const observer = new IntersectionObserver(handleIntersection, options);
    observer.observe(target);

    return () => {
      observer.disconnect();
    };
  }, [
    hasMore,
    isLoading,
    hasUserScrolled,
    requireScroll,
    observerReady,
    debug,
    onLoadMore,
    disableAutoLoading,
  ]);

  // Check if we need to load more content when component mounts
  useEffect(() => {
    // Skip if auto-loading is disabled
    if (disableAutoLoading) return;

    // Only check once observer is ready
    if (!observerReady || !hasMore || isLoading || loadingRef.current) return;

    // If the content doesn't fill the screen, load more
    const checkContentHeight = () => {
      if (!contentRef.current) return;

      const contentHeight = contentRef.current.offsetHeight;
      const windowHeight = window.innerHeight;

      if (debug) {
        logger.info("📏 Checking content height", {
          contentHeight,
          windowHeight,
          shouldLoadMore: contentHeight < windowHeight * 1.2,
        });
        console.log("📏 Checking content height", {
          contentHeight,
          windowHeight,
          shouldLoadMore: contentHeight < windowHeight * 1.2,
        });
      }

      // If content is less than 120% of the window height, load more
      if (
        contentHeight < windowHeight * 1.2 &&
        hasMore &&
        !loadingRef.current
      ) {
        if (debug) {
          logger.info("📏 Content too short, loading more");
          console.log("📏 Content too short, loading more");
        }
        handleLoadMore();
      }
    };

    // Wait for content to render then check
    const timer = setTimeout(checkContentHeight, 200);
    return () => clearTimeout(timer);
  }, [
    hasMore,
    isLoading,
    observerReady,
    debug,
    onLoadMore,
    disableAutoLoading,
  ]);

  // Monitor for scroll events on container parents (if window scroll isn't triggering)
  useEffect(() => {
    // Skip if not debug mode or auto-loading is disabled
    if (!contentRef.current || disableAutoLoading) {
      return undefined;
    }

    // Find scrollable parent containers
    let scrollableParent: HTMLElement | null = null;
    let parentElement = contentRef.current.parentElement;

    while (parentElement) {
      const style = window.getComputedStyle(parentElement);
      if (
        style.overflow === "auto" ||
        style.overflow === "scroll" ||
        style.overflowY === "auto" ||
        style.overflowY === "scroll"
      ) {
        scrollableParent = parentElement;
        break;
      }
      parentElement = parentElement.parentElement;
    }

    if (scrollableParent) {
      // If we found a scrollable parent, attach scroll listener
      const handleParentScroll = () => {
        if (!hasUserScrolled) {
          if (debug) {
            logger.info("📜 Parent scroll detected, enabling auto-loading");
            console.log("📜 Parent scroll detected, enabling auto-loading");
          }
          setHasUserScrolled(true);
        }

        // Also check if we're near the bottom
        if (
          hasMore &&
          !loadingRef.current &&
          hasUserScrolled &&
          observerReady
        ) {
          const container = scrollableParent;
          if (!container) return;

          const scrollPosition = container.scrollTop;
          const scrollHeight = container.scrollHeight;
          const clientHeight = container.clientHeight;

          // Calculate how close to bottom we are (0 to 1)
          const scrollPercentage =
            (scrollPosition + clientHeight) / scrollHeight;

          if (debug) {
            console.log("Scroll check in parent container:", {
              scrollPercentage,
              threshold: scrollThreshold,
              scrollPosition,
              scrollHeight,
              clientHeight,
            });
          }

          if (scrollPercentage > scrollThreshold) {
            if (debug) {
              logger.info("📏 Near bottom of parent container, loading more", {
                scrollPercentage,
                threshold: scrollThreshold,
              });
              console.log("📏 Near bottom of parent container, loading more", {
                scrollPercentage,
                threshold: scrollThreshold,
              });
            }
            handleLoadMore();
          }
        }
      };

      // Add scroll listener to the parent
      if (debug) {
        logger.info("🔍 Found scrollable parent, attaching scroll listener", {
          parent:
            scrollableParent.className || scrollableParent.id || "unknown",
        });
      }
      scrollableParent.addEventListener("scroll", handleParentScroll, {
        passive: true,
      });

      return () => {
        scrollableParent?.removeEventListener("scroll", handleParentScroll);
      };
    }

    return undefined;
  }, [
    contentRef,
    hasUserScrolled,
    hasMore,
    loadingRef,
    observerReady,
    debug,
    disableAutoLoading,
    scrollThreshold,
    handleLoadMore,
  ]);

  return (
    <Box
      ref={contentRef}
      className={`custom-infinite-scroll ${className}`}
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        ...style,
      }}
      data-testid="infinite-scroll-container"
    >
      {/* Debug info */}
      {debug && (
        <Box
          position="fixed"
          top="10px"
          right="10px"
          bg="rgba(0,0,0,0.7)"
          color="white"
          p={2}
          borderRadius="md"
          fontSize="10px"
          zIndex={9999}
        >
          <Text>hasMore: {hasMore ? "Yes" : "No"}</Text>
          <Text>isLoading: {isLoading ? "Yes" : "No"}</Text>
          <Text>hasScrolled: {hasUserScrolled ? "Yes" : "No"}</Text>
          <Text>observerReady: {observerReady ? "Yes" : "No"}</Text>
          <Text>loadingRef: {loadingRef.current ? "Yes" : "No"}</Text>
          <Text>disableAutoLoading: {disableAutoLoading ? "Yes" : "No"}</Text>
          <Text
            as="button"
            onClick={() => hasMore && !loadingRef.current && handleLoadMore()}
            textDecoration="underline"
            cursor="pointer"
            bg="blue.500"
            px={2}
            py={1}
            mt={1}
            borderRadius="sm"
            disabled={!hasMore || loadingRef.current}
            opacity={!hasMore || loadingRef.current ? 0.5 : 1}
          >
            Load More Manually
          </Text>
        </Box>
      )}

      {/* Render children */}
      {children}

      {/* Loading indicator */}
      {isLoading && loader}

      {/* Invisible trigger element - positioned higher in the page */}
      {hasMore && (
        <Box
          ref={triggerRef}
          data-testid="infinite-scroll-trigger"
          height="30px"
          width="100%"
          marginTop="10px"
          position="relative" // Change position to ensure it's in the flow
          opacity={debug ? 0.5 : 0} // Make slightly visible in debug mode
          bg={debug ? "red.500" : "transparent"}
          textAlign="center"
          fontSize="10px"
          color="white"
        >
          {debug && "Load trigger"}
        </Box>
      )}

      {/* End message */}
      {!hasMore && endMessage}
    </Box>
  );
};

export default CustomInfiniteScroll;
