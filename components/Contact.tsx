"use client";

import Reveal from "./ui/Reveal";
import Sparkle from "./ui/Sparkle";

const Contact = () => {
	return (
		<section id="contact" className="py-20 relative">
			<Reveal>
				<h3 className="mb-4">
					Get in{" "}
					<span className="bg-gradient-to-r from-purple to-red-700 bg-clip-text text-transparent">
						touch.
					</span>
				</h3>
			</Reveal>
			<Sparkle>
				<div className="bg-purple-900/[0.5] backdrop-blur-xl border border-white/[0.1] rounded-2xl p-8 md:p-12">
					<div className="space-y-6 text-center">
						<p className="text-lg md:text-xl">
							I&apos;m always open to discussing new projects, creative ideas, or opportunities to be part of your visions.
						</p>
						<a
							href="mailto:aitbekovalibek@gmail.com"
							className="inline-block bg-purple/30 hover:bg-purple/50 border border-purple/50 rounded-lg px-8 py-4 text-lg font-semibold transition-all duration-300 hover:scale-105 shadow-lg"
						>
							Email Me
						</a>
					</div>
				</div>
			</Sparkle>
		</section>
	);
};

export default Contact;

