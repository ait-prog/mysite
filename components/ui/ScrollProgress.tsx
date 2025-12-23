"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const ScrollProgress = () => {
	const [scrollProgress, setScrollProgress] = useState(0);

	useEffect(() => {
		const updateScrollProgress = () => {
			const scrollPx = document.documentElement.scrollTop;
			const winHeightPx =
				document.documentElement.scrollHeight -
				document.documentElement.clientHeight;
			const scrolled = (scrollPx / winHeightPx) * 100;
			setScrollProgress(scrolled);
		};

		window.addEventListener("scroll", updateScrollProgress);
		return () => window.removeEventListener("scroll", updateScrollProgress);
	}, []);

	return (
		<motion.div
			className="fixed top-0 left-0 right-0 h-1 bg-purple/30 z-50 origin-left"
			style={{ scaleX: scrollProgress / 100 }}
		/>
	);
};

export default ScrollProgress;

