"use client";

import { socialMedia } from "@/data";
import Image from "next/image";

const Footer = () => {
	return (
		<footer className="py-10 border-t border-white/10 mt-20">
			<div className="flex flex-col md:flex-row justify-between items-center gap-5 px-5 md:px-10 lg:px-40">
				<p className="text-sm opacity-60 text-center md:text-left">
					Made with love by Alibek Aitbekov
				</p>
				<div className="flex gap-5">
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
				</div>
			</div>
		</footer>
	);
};

export default Footer;

