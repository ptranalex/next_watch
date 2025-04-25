import { useEffect, useState, useRef, RefObject } from "react";

interface IntersectionObserverOptions {
  root?: Element | null;
  rootMargin?: string;
  threshold?: number | number[];
}

/**
 * Hook that observes when an element enters the viewport
 *
 * @param options - IntersectionObserver options
 * @returns [ref, isIntersecting] - The reference to attach to the observed element and whether it's intersecting
 */
function useIntersectionObserver<T extends Element>({
  root = null,
  rootMargin = "200px",
  threshold = 0.1,
}: IntersectionObserverOptions = {}): [RefObject<T>, boolean] {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const ref = useRef<T>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
      },
      { root, rootMargin, threshold }
    );

    const currentElement = ref.current;
    if (currentElement) {
      observer.observe(currentElement);
    }

    return () => {
      if (currentElement) {
        observer.unobserve(currentElement);
      }
    };
  }, [root, rootMargin, threshold]);

  return [ref, isIntersecting];
}

export default useIntersectionObserver;
