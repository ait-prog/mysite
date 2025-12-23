"use client";

import { motion } from "framer-motion";
import Reveal from "./ui/Reveal";
import { socialMedia } from "@/data";
import Image from "next/image";

const Hero = () => {
	return (
		<section id="hero" className="min-h-screen flex flex-col justify-center items-center relative">
			<Reveal>
				<div className="flex flex-col items-center justify-center gap-10">
					<motion.div
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ duration: 0.5 }}
						className="flex flex-col items-center gap-5"
					>
						<h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-extrabold text-center">
							Hi, I&apos;m{" "}
							<span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
								Alibek
							</span>
						</h1>
						<p className="text-xl sm:text-2xl md:text-3xl text-center font-light">
							MLOps / ML Engineer
						</p>
					</motion.div>

					<motion.div
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ duration: 0.5, delay: 0.2 }}
						className="flex gap-5"
					>
						{socialMedia.map((item) => (
							<a
								key={item.id}
								href={item.link}
								target="_blank"
								rel="noopener noreferrer"
								className="cursor-pointer group/link"
							>
								<div className="bg-white/10 backdrop-blur-sm rounded-lg p-2 hover:bg-purple/30 border border-white/20 hover:border-purple/50 transition-all duration-300 hover:scale-110 shadow-lg">
									<Image
										src={item.img}
										alt={`Social media ${item.id}`}
										width={24}
										height={24}
										className="min-w-6 transform transition-all duration-300 ease-in-out"
									/>
								</div>
							</a>
						))}
					</motion.div>
				</div>
			</Reveal>
		</section>
	);
};

export default Hero;

