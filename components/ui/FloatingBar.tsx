"use client";

import DownloadCV from "./DownloadCV";
import { navItems } from "@/data";
import Link from "next/link";
import { motion } from "framer-motion";

const FloatingBar = () => {
	return (
		<div className="fixed right-5 top-1/2 -translate-y-1/2 z-40 hidden lg:flex flex-col gap-5">
			<motion.div
				initial={{ opacity: 0, x: 20 }}
				animate={{ opacity: 1, x: 0 }}
				transition={{ duration: 0.5 }}
				className="bg-white/10 backdrop-blur-sm rounded-full p-4 border border-white/20 shadow-lg"
			>
				<div className="flex flex-col gap-4">
					{navItems.map((item, index) => (
						<Link
							key={item.name}
							href={item.link}
							className="w-12 h-12 flex items-center justify-center rounded-full hover:bg-purple/30 border border-white/20 hover:border-purple/50 transition-all duration-300 hover:scale-110"
							title={item.name}
						>
							<span className="text-xs font-semibold">{item.name.charAt(0)}</span>
						</Link>
					))}
					<DownloadCV />
				</div>
			</motion.div>
		</div>
	);
};

export default FloatingBar;

