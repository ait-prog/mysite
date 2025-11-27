"use client";

import { useEffect, useState, useRef } from "react";

const ScrollProgress = () => {
  const [scrollProgress, setScrollProgress] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const updateScrollProgress = () => {
      // Find the scrollable container
      const scrollContainer = document.querySelector('.overflow-y-auto');
      if (!scrollContainer) return;

      const scrollTop = scrollContainer.scrollTop;
      const scrollHeight = scrollContainer.scrollHeight;
      const clientHeight = scrollContainer.clientHeight;
      const scrolled = scrollHeight > clientHeight 
        ? (scrollTop / (scrollHeight - clientHeight)) * 100 
        : 0;
      setScrollProgress(Math.min(100, Math.max(0, scrolled)));
    };

    const scrollContainer = document.querySelector('.overflow-y-auto');
    if (scrollContainer) {
      scrollContainer.addEventListener("scroll", updateScrollProgress);
      // Initial calculation
      updateScrollProgress();
      return () => scrollContainer.removeEventListener("scroll", updateScrollProgress);
    }
  }, []);

  return (
    <div className="fixed top-0 left-0 w-full h-1 bg-black/20 z-50" ref={containerRef}>
      <div
        className="h-full bg-gradient-to-r from-purple to-red-700 transition-all duration-150 ease-out"
        style={{ 
          width: `${scrollProgress}%`,
          boxShadow: '0 0 10px rgba(155, 77, 150, 0.5)'
        }}
      />
    </div>
  );
};

export default ScrollProgress;

