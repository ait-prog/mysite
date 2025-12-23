"use client";

import { navItems } from "@/data";
import { motion } from "framer-motion";
import Link from "next/link";
import { useState } from "react";

const NavBar = () => {
	const [active, setActive] = useState("About");

	return (
		<nav className="fixed top-0 left-0 right-0 z-50 bg-[#120012]/80 backdrop-blur-md border-b border-white/10">
			<div className="flex justify-center items-center py-4">
				<div className="flex gap-2 md:gap-8">
					{navItems.map((item) => (
						<Link
							key={item.name}
							href={item.link}
							onClick={() => setActive(item.name)}
							className="relative px-4 py-2"
						>
							{active === item.name && (
								<motion.div
									layoutId="activeTab"
									className="absolute inset-0 bg-purple/20 rounded-lg border border-purple/50"
									transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
								/>
							)}
							<span className="relative z-10 text-sm md:text-base font-medium">
								{item.name}
							</span>
						</Link>
					))}
				</div>
			</div>
		</nav>
	);
};

export default NavBar;

